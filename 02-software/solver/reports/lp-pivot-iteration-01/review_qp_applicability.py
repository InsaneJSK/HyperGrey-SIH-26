"""Correct the runner's applicability classification; retain original records.

The unchanged independent checker marks the optional diagonal certificate false
when inapplicable. This script checks actual original Hessian structure before
requiring it, and recomputes KKT on the same saved points at the same tolerance.
"""
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tools/reference/qp'), str(ROOT / 'tools/reference/python')]
import numpy as np
import scipy.sparse as sparse
from qplib_reference_reader import read
from qp_certificate import check
from validate_binary_proof import sha, save


def main():
    out = BASE / 'validation'
    rows = json.loads((out / 'ledger.json').read_text())
    audit = []
    for row in rows:
        if row['family'] != 'qp':
            continue
        model = ROOT / 'reports/cpu-validation-2026-09-17/results' / row['model']
        candidate = out / (row['key'] + '.candidate.json')
        own = json.loads(candidate.read_text())
        q = read(model, np, sparse)
        h = q['hessian']
        applicable = bool((h - sparse.diags(h.diagonal())).nnz == 0 and np.all(q['sign'] * h.diagonal() > 0))
        result = check(model, own)
        assert result == json.loads((out / (row['key'] + '.kkt.json')).read_text()), 'KKT arithmetic changed'
        row['checked_completion'] = bool(own['status'] == 'optimal' and result['independent_kkt_passed']
                                         and (not applicable or result['diagonal_certificate_passed']))
        row['unvalidated_completion'] = own['status'] == 'optimal' and not row['checked_completion']
        row['diagonal_certificate_applicable'] = applicable
        audit.append({'key': row['key'], 'diagonal_certificate_applicable': applicable,
                      'checked_completion': row['checked_completion'], 'model_sha256': sha(model),
                      'candidate_sha256': sha(candidate), 'kkt_unchanged': True})
    assert all(r['checked_completion'] for r in rows if r['profile'] in ('stable', 'stable_refined', 'compact', 'default'))
    assert not any(r['unvalidated_completion'] for r in rows)
    save(out / 'REVIEWED_LEDGER.json', rows)
    summary = json.loads((out / 'SUMMARY.json').read_text())
    summary.update(unvalidated_completions=0,
                   profiles={profile: {'records': len(selected), 'checked_completions': sum(r['checked_completion'] for r in selected)}
                             for profile in sorted({r['profile'] for r in rows})
                             for selected in [[r for r in rows if r['profile'] == profile]]},
                   ledger_sha256=sha(out / 'REVIEWED_LEDGER.json'),
                   original_summary_sha256=sha(out / 'SUMMARY.json'),
                   review_script_sha256=sha(Path(__file__)),
                   correction='Only diagonal-certificate applicability classification; original Hessians checked, KKT arithmetic/points/tolerance unchanged.')
    save(out / 'QP_APPLICABILITY_REVIEW.json', audit)
    save(out / 'REVIEWED_SUMMARY.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
