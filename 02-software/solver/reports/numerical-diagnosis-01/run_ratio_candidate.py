"""Check the predeclared LP refresh candidate; references run after own solves."""
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
from validate_binary_proof import sha, save


def main():
    out = BASE / 'ratio-candidate-results'
    out.mkdir(exist_ok=False)
    binary = ROOT / 'build-lp-ratio-01/solver_cli.exe'
    for name, digest in json.loads((ROOT / 'reports/milp-iteration-29/RUNTIME_DEPENDENCIES.json').read_text()).items():
        source = ROOT / 'reports/milp-iteration-29' / name
        assert sha(source) == digest
        shutil.copy2(source, binary.parent / name)
    os.environ['PATH'] = str(binary.parent) + os.pathsep + os.environ['PATH']
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    wrapper = ROOT / 'reports/milp-iteration-29/run_contained.py'
    spec = importlib.util.spec_from_file_location('candidate_monitor', wrapper)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    prior = ROOT / 'reports/cpu-validation-2026-09-17/results'
    jobs = [r for r in json.loads((prior / 'ledger.json').read_text()) if r['family'] != 'qp' and r['profile'] == 'default']
    jobs.sort(key=lambda r: r['name'] != 'bandm')
    for row in jobs:
        row['flags'] = []
    bandm = next(row for row in jobs if row['name'] == 'bandm')
    jobs += [dict(bandm, key='bandm.refined', flags=['--refine-basis', '--refine-at-checks']),
             dict(bandm, key='bandm.compact', flags=['--compact-equalities', '--refine-basis', '--refine-at-checks'])]
    save(out / 'metadata.json', {'binary_sha256': sha(binary), 'runner_sha256': sha(Path(__file__)),
         'candidate_identity_sha256': sha(BASE / 'RATIO_CANDIDATE_IDENTITY.json'), 'own_before_references': True})
    records = []
    for job in jobs:
        key = job['key']
        model = prior / job['model']
        result = monitor.monitor([str(binary), str(model), '--json', '--time-limit', '30', *job['flags']], out / key, 45, 1536)
        own = dict(result['native_result'] or {}, status=result['status'])
        names = json.loads((prior / (job['name'] + '.default.reference-candidate.json')).read_text())['variable_names']
        save(out / (key + '.candidate.json'), dict(own, variable_names=names))
        events = [json.loads(line) for line in (out / (key + '.stderr.log')).read_text().splitlines() if line.startswith('{')]
        records.append(dict(key=key, model=str(model), status=own['status'], objective=own.get('objective'),
            iterations=own.get('iterations'), refreshes=sum(e['event'] == 'refresh_small_pivot' for e in events)))
        save(out / 'ledger.json', records)
        print(key, own['status'], own.get('iterations'), 'refreshes', records[-1]['refreshes'], flush=True)
    for row in records:
        key = row['key']
        own = json.loads((out / (key + '.candidate.json')).read_text())
        ref = timed([sys.executable, '-B', str(ROOT / 'scripts/benchmark_lp.py'), '--reference', row['model'],
                     '--candidate', str(out / (key + '.candidate.json')), '--limit', '30'], 45, out / (key + '.reference'))
        save(out / (key + '.reference.json'), ref)
        row['checked_completion'] = bool(own['status'] == 'optimal' and own.get('optimality_verified') and ref.get('status') == 'Optimal'
            and ref.get('candidate_scaled_violation', 1) <= 1e-8 and own.get('objective') is not None
            and abs(own['objective'] - ref['objective']) <= 1e-6 * (1 + abs(ref['objective']))
            and abs(own['objective'] - ref['candidate_recomputed_objective']) <= 1e-6 * (1 + abs(own['objective'])))
        row['absolute_violation'] = ref.get('candidate_max_violation')
        row['scaled_violation'] = ref.get('candidate_scaled_violation')
        save(out / 'ledger.json', records)
    summary = {'records': len(records), 'checked_completions': sum(r['checked_completion'] for r in records),
               'all_pass': all(r['checked_completion'] for r in records), 'binary_sha256': sha(binary)}
    save(out / 'SUMMARY.json', summary)
    shutil.copy2(binary, BASE / 'ratio_candidate_cli.exe')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
