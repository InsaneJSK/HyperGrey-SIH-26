"""Declared final-binary LP profiles and unchanged-QP recheck."""
import datetime
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from milp_robustness import timed
from qp_certificate import check as qp_check
from validate_binary_proof import sha, save


def main():
    out = BASE / 'validation'
    out.mkdir(exist_ok=False)
    binary = ROOT / 'build-lp-pivot-01/solver_cli.exe'
    gate = json.loads((BASE / 'gate/SUMMARY.json').read_text())
    assert gate['all_pass'] and gate['stable_ratio'] and gate['binary_sha256'] == sha(binary)
    for rel in ('src/qp.cpp', 'src/qp_admm.cpp', 'src/qp_dual_newton.cpp', 'include/qp.hpp'):
        assert sha(ROOT / rel) == sha(ROOT / 'reports/milp-iteration-29/final-source' / rel)
    identity = {}
    for folder in ('src', 'include', 'scripts', 'tests'):
        for path in sorted((ROOT / folder).iterdir()):
            if path.is_file():
                rel = path.relative_to(ROOT)
                target = out / 'source' / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                identity[rel.as_posix()] = sha(path)
    shutil.copy2(ROOT / 'CMakeLists.txt', out / 'source/CMakeLists.txt')
    identity['CMakeLists.txt'] = sha(ROOT / 'CMakeLists.txt')
    os.environ['PATH'] = str(binary.parent) + os.pathsep + os.environ['PATH']
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    wrapper = ROOT / 'reports/milp-iteration-29/run_contained.py'
    spec = importlib.util.spec_from_file_location('final_lp_monitor', wrapper)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    prior = ROOT / 'reports/cpu-validation-2026-09-17/results'
    retained = json.loads((prior / 'ledger.json').read_text())
    inputs = [r for r in retained if r['family'] != 'qp' and r['profile'] == 'default']
    jobs = []
    for row in inputs:
        for profile, flags in [('stable', ['--stable-primal-ratio']),
                               ('stable_refined', ['--stable-primal-ratio', '--refine-basis', '--refine-at-checks'])]:
            jobs.append(dict(row, key=row['name'] + '.' + profile, profile=profile, flags=flags))
    bandm = next(r for r in inputs if r['name'] == 'bandm')
    jobs += [dict(bandm, key='bandm.control', profile='control', flags=[]),
             dict(bandm, key='bandm.control_refined', profile='control_refined', flags=['--refine-basis', '--refine-at-checks']),
             dict(bandm, key='bandm.compact', profile='compact', flags=['--compact-equalities', '--refine-basis', '--refine-at-checks'])]
    jobs += [dict(r, flags=[]) for r in retained if r['family'] == 'qp' and r['profile'] == 'default']
    metadata = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'binary_sha256': sha(binary),
                'source_sha256': identity, 'runner_sha256': sha(Path(__file__)), 'wrapper_sha256': sha(wrapper),
                'gate_sha256': sha(BASE / 'gate/SUMMARY.json'), 'prior_metadata_sha256': sha(prior / 'metadata.json'),
                'own_before_references': True, 'qp_sources_unchanged_from_frozen29': True,
                'time_limit_seconds': 30, 'watchdog_seconds': 45, 'sampled_commit_threshold_mib': 1536,
                'inputs': {r['model']: sha(prior / r['model']) for r in jobs}}
    save(out / 'metadata.json', metadata)
    records = []
    for job in jobs:
        key = job['key']
        result = monitor.monitor([str(binary), str(prior / job['model']), '--json', '--time-limit', '30', *job['flags']], out / key, 45, 1536)
        own = dict(result['native_result'] or {}, status=result['status'])
        if job['family'] != 'qp':
            own['variable_names'] = json.loads((prior / (job['name'] + '.default.reference-candidate.json')).read_text())['variable_names']
            assert own['stable_primal_ratio_enabled'] == ('--stable-primal-ratio' in job['flags'])
        save(out / (key + '.candidate.json'), own)
        records.append({'key': key, 'name': job['name'], 'profile': job['profile'], 'family': job['family'],
                        'model': job['model'], 'status': own['status'], 'objective': own.get('objective'),
                        'iterations': own.get('iterations'), 'peak_rss_mib': result['peak_working_set_bytes'] / 2**20,
                        'peak_commit_mib': result['peak_commit_bytes'] / 2**20, 'process_seconds': result['wall_seconds']})
        save(out / 'ledger.json', records)
        print(key, own['status'], own.get('iterations'), flush=True)
    for row in records:
        key = row['key']
        own = json.loads((out / (key + '.candidate.json')).read_text())
        if row['family'] == 'qp':
            ref = qp_check(prior / row['model'], own)
            save(out / (key + '.kkt.json'), ref)
            row['checked_completion'] = bool(own['status'] == 'optimal' and ref['independent_kkt_passed']
                and ('diagonal_certificate_passed' not in ref or ref['diagonal_certificate_passed']))
            row['absolute_violation'] = ref['max_violation']
            row['scaled_violation'] = ref['scaled_violation']
            row['reference_scope'] = 'Fresh original-model KKT only; no new external QP timing/reference solve.'
        else:
            ref = timed([sys.executable, '-B', str(ROOT / 'scripts/benchmark_lp.py'), '--reference', str(prior / row['model']),
                         '--candidate', str(out / (key + '.candidate.json')), '--limit', '30'], 45, out / (key + '.reference'))
            save(out / (key + '.reference.json'), ref)
            row['checked_completion'] = bool(own['status'] == 'optimal' and own.get('optimality_verified') and ref.get('status') == 'Optimal'
                and ref.get('candidate_scaled_violation', 1) <= 1e-8 and own.get('objective') is not None
                and abs(own['objective'] - ref['objective']) <= 1e-6 * (1 + abs(ref['objective']))
                and abs(own['objective'] - ref['candidate_recomputed_objective']) <= 1e-6 * (1 + abs(own['objective'])))
            row['absolute_violation'] = ref.get('candidate_max_violation')
            row['scaled_violation'] = ref.get('candidate_scaled_violation')
        row['unvalidated_completion'] = own['status'] == 'optimal' and not row['checked_completion']
        save(out / 'ledger.json', records)
    for rel, digest in identity.items():
        assert sha(ROOT / rel) == digest, rel
    assert sha(binary) == metadata['binary_sha256']
    summary = {'binary_sha256': sha(binary), 'records': len(records),
        'unvalidated_completions': sum(r['unvalidated_completion'] for r in records),
        'profiles': {profile: {'records': len(rows), 'checked_completions': sum(r['checked_completion'] for r in rows)}
                     for profile in sorted({r['profile'] for r in records})
                     for rows in [[r for r in records if r['profile'] == profile]]},
        'ledger_sha256': sha(out / 'ledger.json'), 'default_changed': False}
    save(out / 'SUMMARY.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
