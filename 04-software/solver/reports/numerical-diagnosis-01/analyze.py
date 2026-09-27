"""Independent numerical checks of saved diagnostic matrices and QP points."""
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tools/reference/qp'), str(ROOT / 'tools/reference/python')]
import numpy as np
from qp_certificate import check
from validate_binary_proof import save


def main():
    out = BASE / 'analysis'
    out.mkdir(exist_ok=False)
    facts = {}
    for name in ('bandm.default', 'bandm.refined', 'bandm.compact'):
        events = [json.loads(line) for line in (BASE / 'results' / (name + '.stderr.log')).read_text().splitlines() if line.startswith('{')]
        rows = []
        for event in events:
            if event['event'] != 'refactor_failed':
                continue
            columns = event['basis_columns']
            matrix = np.zeros((len(columns), len(columns)))
            for j, column in enumerate(columns):
                for i, value in column:
                    matrix[i, j] += value
            u, singular, vh = np.linalg.svd(matrix)
            vector = vh[-1]
            rows.append({'iteration': event['iterations'], 'dimension': len(columns),
                         'rank_at_numpy_default_threshold': int(np.linalg.matrix_rank(matrix)),
                         'largest_singular_value': float(singular[0]), 'smallest_singular_values': singular[-6:].tolist(),
                         'null_residual_inf': float(np.max(np.abs(matrix @ vector))),
                         'null_dominant_terms': [[event['basis'][int(j)], float(vector[j])] for j in np.argsort(np.abs(vector))[-8:]],
                         'duplicate_basis_columns': len(event['basis']) - len(set(event['basis']))})
            save(out / (name + '.near-null.json'), {'canonical_basis_indices': event['basis'], 'null_vector': vector.tolist()})
        facts[name] = rows
    model = ROOT / 'reports/cpu-validation-2026-09-17/results/inputs/qplib/9002.qplib'
    for tol in ('1e-7', '1e-10', '1e-12'):
        name = '9002.' + tol
        events = [json.loads(line) for line in (BASE / 'results' / (name + '.stderr.log')).read_text().splitlines() if line.startswith('{')]
        specialist = [e for e in events if e['event'] == 'specialist_exit'][0]
        certificate = check(model, specialist)
        save(out / (name + '.specialist.kkt.json'), certificate)
        steps = [e for e in events if e['event'] == 'qp_step']
        facts[name] = {'specialist_status': specialist['status'], 'specialist_iterations': specialist['iterations'],
                       'specialist_certificate': certificate, 'zero_inner_steps': sum(e['inner'] == 0 for e in steps),
                       'steps_with_length_below_1e-4': sum(e['length'] < 1e-4 for e in steps),
                       'last_steps': steps[-4:], 'last_iterations': [e for e in events if e['event'] == 'qp_iteration'][-4:]}
    save(out / 'FACTS.json', facts)
    for name, value in facts.items():
        print(name, json.dumps(value if name.startswith('bandm') else {k:v for k,v in value.items() if not k.startswith('last_')}), flush=True)


if __name__ == '__main__':
    main()
