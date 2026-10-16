"""Consistency checks for tree-dive and fix-and-propagate accounting.

Heuristics may only supply points that pass the solver's own acceptance; they
never export bounds. These checks confirm coherent counters and that disabled
heuristics did no work.
"""
import json
import math
import sys
from pathlib import Path


def _count(section, key):
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AssertionError(f'Invalid counter {key}: {value!r}')
    return value


def _seconds(section):
    value = section.get('seconds')
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise AssertionError('Invalid seconds')
    return value


def check(result):
    dives = result.get('tree_dives')
    fixes = result.get('fix_propagate')
    if dives is None or fixes is None:
        raise AssertionError('Missing tree_dives/fix_propagate sections')
    calls, improvements = _count(dives, 'calls'), _count(dives, 'improvements')
    seconds = _seconds(dives)
    if not isinstance(dives.get('enabled'), bool):
        raise AssertionError('tree_dives.enabled must be boolean')
    if not dives['enabled'] and (calls or improvements or seconds):
        raise AssertionError('Disabled tree dives reported work')
    if improvements > calls:
        raise AssertionError('More tree-dive improvements than calls')
    f_calls, fixings, lps, successes = (_count(fixes, k) for k in ('calls', 'fixings', 'lps', 'successes'))
    f_seconds = _seconds(fixes)
    if not isinstance(fixes.get('enabled'), bool):
        raise AssertionError('fix_propagate.enabled must be boolean')
    if not fixes['enabled'] and (f_calls or fixings or lps or successes or f_seconds):
        raise AssertionError('Disabled fix-and-propagate reported work')
    if lps > f_calls or successes > lps:
        raise AssertionError('Fix-and-propagate outcomes exceed calls')
    if successes and not result.get('primal'):
        raise AssertionError('Accepted fix-and-propagate point without an incumbent')
    if calls and result.get('first_incumbent_seconds') is None:
        raise AssertionError('Tree dives require an existing incumbent')
    return {'all_pass': True, 'tree_dive_calls': calls, 'tree_dive_improvements': improvements,
            'fix_propagate_calls': f_calls, 'fix_propagate_successes': successes}


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(name, json.dumps(check(json.loads(Path(name).read_text()))))
