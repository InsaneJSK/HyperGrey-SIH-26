"""Consistency checks for the bounded dual-simplex accounting in MILP output.

These checks do not re-solve anything. They confirm that the reported counters
are internally coherent and that a disabled engine did no work, so a result
cannot silently mix engines or hide unverified relaxations.
"""
import json
import sys
from pathlib import Path

COUNTS = ('calls', 'warm', 'cold', 'optimal', 'infeasible', 'cutoffs', 'cutoff_nodes', 'failures', 'fallbacks',
          'iterations', 'dual_iterations', 'primal_iterations', 'flips', 'refactors', 'cleanups', 'artificial',
          'singular_repairs', 'farkas_rejected', 'verification_rejected', 'prepared')


def check(result):
    section = result.get('bounded_lp')
    if section is None:
        raise AssertionError('Missing bounded_lp section')
    for key in COUNTS:
        value = section.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AssertionError(f'Invalid bounded_lp.{key}: {value!r}')
    seconds = section.get('seconds')
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not seconds >= 0 or seconds == float('inf'):
        raise AssertionError('Invalid bounded_lp.seconds')
    if not section['enabled']:
        if any(section[key] for key in COUNTS):
            raise AssertionError('Disabled bounded LP engine reported work')
        return {'enabled': False, 'all_checks_pass': True}
    if section['warm'] > section['calls']:
        raise AssertionError('More warm starts than bounded calls')
    outcomes = section['optimal'] + section['infeasible'] + section['cutoffs'] + section['failures']
    if outcomes > section['calls']:
        raise AssertionError('More bounded outcomes than calls')
    if section['fallbacks'] > section['failures']:
        raise AssertionError('A fallback requires an unverified bounded outcome')
    if section['cutoff_nodes'] > section['cutoffs']:
        raise AssertionError('Cutoff nodes exceed verified cutoff results')
    if section['dual_iterations'] + section['primal_iterations'] > section['iterations'] + section['flips']:
        raise AssertionError('Phase iterations exceed the reported total')
    if section['calls'] and not section['prepared']:
        raise AssertionError('Bounded calls without a prepared model')
    if result.get('status') in ('optimal', 'gap_limit') and result.get('lp_iterations', 0) < 0:
        raise AssertionError('Invalid LP iteration total')
    return {'enabled': True, 'calls': section['calls'], 'fallbacks': section['fallbacks'], 'all_checks_pass': True}


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(name, json.dumps(check(json.loads(Path(name).read_text()))))
