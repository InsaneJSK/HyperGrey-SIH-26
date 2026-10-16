"""Retry pending independent checks without changing saved own-solver runs."""
import json
from pathlib import Path
import sys
from benchmark_lp import ROOT
from milp_robustness import timed
from validate_binary_proof import sha, save
from validate_milp_frontier import verify


def main():
    if not __debug__:
        raise RuntimeError('Assertions required')
    wave = ROOT / 'reports/milp-iteration-14/wave-30s'
    out = ROOT / 'reports/milp-iteration-14/supplemental-references'
    out.mkdir(parents=True, exist_ok=False)
    meta = json.loads((wave / 'metadata.json').read_text())
    helper = ROOT / 'scripts/milp_robustness.py'
    helper_sha = sha(helper)
    assert helper_sha == meta['source_sha256']['scripts/milp_robustness.py']
    rows = json.loads((wave / 'results.json').read_text())
    pending = [r for r in rows if r['category'] == 'incumbent_reference_pending']
    assert len(pending) == 2 and {r['name'] for r in pending} == {'eil33-2'}
    records = []
    for r in pending:
        key = r['key']
        model, own_path = ROOT / r['model'], wave / (key + '.ours.json')
        assert sha(model) == r['model_sha256'] and sha(own_path) == r['ours_sha256']
        assert sha(wave / (key + '.reference.json')) == r['reference_sha256']
        own = json.loads(own_path.read_text())
        command = [sys.executable, '-X', 'utf8', str(helper), '--reference', str(model),
                   '--candidate', str(own_path), '--reference-limit', '5']
        # Keep HiGHS's five-second solve limit. Only the external allowance for
        # importing, parsing and checking the already saved vector is larger.
        ref = timed(command, 150, out / (key + '.reference'))
        ref_path = out / (key + '.reference.json')
        save(ref_path, ref)
        category, errors, checks = verify(model, own, ref, out, key, meta['plan'].get('gap', 1e-6))
        valid = not errors and category == 'feasible_limit' and ref.get('candidate_checked') is True
        records.append({'key': key, 'model': r['model'], 'model_sha256': sha(model),
                        'ours_sha256': sha(own_path), 'original_reference_sha256': r['reference_sha256'],
                        'reference_sha256': sha(ref_path), 'command': command,
                        'category': category, 'validation_errors': errors, 'all_pass': valid,
                        'reference_status': ref['status'], 'external_watchdog_seconds': 150})
        save(out / 'results.json', records)
        print(key, category, 'PASS' if valid else 'FAIL', flush=True)
    assert sha(helper) == helper_sha
    assert all(r['all_pass'] for r in records)
    summary = {'all_pass': True, 'records': len(records), 'helper_sha256': helper_sha,
               'runner_sha256': sha(Path(__file__)), 'results_sha256': sha(out / 'results.json'),
               'original_results_sha256': sha(wave / 'results.json'),
               'own_solver_reruns': 0, 'reference_solve_limit_seconds': 5,
               'note': 'Original pending records are preserved. Only the independent process watchdog changes from 25 to 150 seconds.'}
    save(out / 'SUMMARY.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
