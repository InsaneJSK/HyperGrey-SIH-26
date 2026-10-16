"""Exact arithmetic check of the captured basis dependence, not LP infeasibility."""
from fractions import Fraction
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
records = []
for name in ('bandm.default', 'bandm.refined'):
    events = [json.loads(line) for line in (BASE / 'results' / (name + '.stderr.log')).read_text().splitlines()]
    event = next(e for e in events if e['event'] == 'refactor_failed')
    witness = [Fraction(0) for _ in event['basis']]
    witness[500] = witness[501] = Fraction(1)
    products = [sum((Fraction(value) * witness[i] for i, value in col), Fraction(0)) for col in event['basis_columns']]
    rhs = sum((Fraction(value) * y for value, y in zip(event['rhs'], witness)), Fraction(0))
    assert all(value == 0 for value in products) and rhs == 0
    records.append({'capture': name, 'dimension': len(witness), 'rows': [500, 501],
                    'multipliers': [1, 1], 'every_basis_column_exactly_zero': True,
                    'rhs_exactly_zero': True, 'rank_upper_bound': len(witness) - 1,
                    'scope': 'Nonzero left null vector proves this captured basis singular. It does not prove the LP infeasible.'})
(BASE / 'analysis/EXACT_SINGULARITY.json').write_text(json.dumps(records, indent=2) + '\n')
print('Both captured bases have an exact nonzero left null vector.')
