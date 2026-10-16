"""Sixteen-LP check of the frozen iteration 30 executable: default and bounded methods."""
import importlib.util
import json
import os
from pathlib import Path
import sys
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from milp_robustness import timed
from validate_binary_proof import sha, save

PROFILES = {'default': [], 'bounded': ['--lp-method', 'bounded']}


def main():
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    prior = ROOT / 'reports/cpu-validation-2026-09-17/results'
    jobs = [r for r in json.loads((prior / 'ledger.json').read_text())
            if r['family'] in ('lp', 'additional_lp') and r['profile'] == 'default']
    assert len(jobs) == 16
    out = BASE / 'lp-track'
    out.mkdir(exist_ok=False)
    binary = BASE / 'final_solver_cli.exe'
    identity = json.loads((BASE / 'SOURCE_IDENTITY.json').read_text())
    assert sha(binary) == identity['binary_sha256']
    spec = importlib.util.spec_from_file_location('lp_track_monitor', BASE / 'run_contained.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    save(out / 'metadata.json', {'binary_sha256': sha(binary), 'profiles': PROFILES, 'runner_sha256': sha(Path(__file__)),
                                 'own_before_references': True,
                                 'purpose': 'Checked LP coverage per method; not a matched-accuracy speed ranking.'})
    records = []
    for index, job in enumerate(jobs):
        names = list(PROFILES)
        order = names[index % 2:] + names[:index % 2]
        for profile in order:
            name = job['name']
            key = f'{name}.{profile}'
            model = prior / job['model']
            command = [str(binary), str(model), '--json', '--time-limit', '30', *PROFILES[profile]]
            wrapped = mod.monitor(command, out / key, 45, 1536)
            own = dict(wrapped['native_result'] or {}, status=wrapped['status'])
            save(out / (key + '.ours.json'), own)
            record = {'name': name, 'profile': profile, 'family': job['family'], 'model': str(model),
                      'model_sha256': sha(model), 'status': own['status'], 'objective': own.get('objective'),
                      'iterations': own.get('iterations'), 'solve_seconds': own.get('solve_seconds'),
                      'process_seconds': wrapped['wall_seconds'],
                      'peak_rss_mib': wrapped['peak_working_set_bytes'] / 1024 ** 2}
            records.append(record)
            save(out / 'ledger.json', records)
            print(key, own['status'], own.get('objective'), own.get('iterations'), flush=True)
    for r in records:
        key = f"{r['name']}.{r['profile']}"
        own = json.loads((out / (key + '.ours.json')).read_text())
        names = json.loads((prior / (r['name'] + '.default.reference-candidate.json')).read_text())['variable_names']
        candidate = out / (key + '.candidate.json')
        save(candidate, dict(own, variable_names=names))
        ref = timed([sys.executable, '-B', str(ROOT / 'scripts/benchmark_lp.py'), '--reference', r['model'],
                     '--candidate', str(candidate), '--limit', '30'], 45, out / (key + '.reference'))
        save(out / (key + '.reference.json'), ref)
        r['checked_completion'] = bool(
            own['status'] == 'optimal' and own.get('optimality_verified') and ref.get('status') == 'Optimal'
            and ref.get('candidate_scaled_violation', 1) <= 1e-8 and own.get('objective') is not None
            and abs(own['objective'] - ref['objective']) <= 1e-6 * (1 + abs(ref['objective']))
            and abs(own['objective'] - ref['candidate_recomputed_objective']) <= 1e-6 * (1 + abs(own['objective'])))
        r['honest_noncompletion'] = bool(not r['checked_completion'] and own['status'] != 'optimal')
        r['absolute_violation'] = ref.get('candidate_max_violation')
        r['scaled_violation'] = ref.get('candidate_scaled_violation')
        r['reference_objective'] = ref.get('objective')
        save(out / 'ledger.json', records)
    summary = {'records': len(records), 'binary_sha256': sha(binary), 'ledger_sha256': sha(out / 'ledger.json'),
               'checked_completions': {p: sum(r['checked_completion'] for r in records if r['profile'] == p) for p in PROFILES},
               'false_optimal_claims': sum(1 for r in records if r['status'] == 'optimal' and not r['checked_completion'])}
    save(out / 'SUMMARY.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
