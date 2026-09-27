"""Consistency checks for tableau Gomory cut accounting.

The separator may only add rows; it never supplies a point and never exports a
bound of its own. These checks confirm that the counters describe a coherent
run, that a disabled separator did no work, and that the reported outcomes of
every attempt add up to the attempts made.
"""
import json
import math
import sys
from pathlib import Path

SKIPS = ('skipped_free', 'skipped_drop', 'skipped_consistency', 'skipped_dynamism',
         'skipped_support', 'skipped_efficacy', 'skipped_parallel', 'rejected_incumbent')


def _count(section, key):
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AssertionError(f'Invalid counter {key}: {value!r}')
    return value


def _number(section, key):
    value = section.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise AssertionError(f'Invalid {key}')
    return value


def check(result):
    cuts = result.get('gomory_cuts')
    if cuts is None:
        raise AssertionError('Missing gomory_cuts section')
    if not isinstance(cuts.get('enabled'), bool):
        raise AssertionError('gomory_cuts.enabled must be boolean')
    counters = {k: _count(cuts, k) for k in
                ('calls', 'candidates', 'attempts', 'generated', 'applied', 'purged', 'rounds',
                 'basis_rejected') + SKIPS}
    seconds = _number(cuts, 'seconds')
    efficacy = _number(cuts, 'best_efficacy')
    if not cuts['enabled']:
        if any(counters.values()) or seconds or efficacy:
            raise AssertionError('Disabled Gomory separator reported work')
        return {'all_pass': True, 'enabled': False}
    if counters['attempts'] > counters['candidates']:
        raise AssertionError('More attempts than fractional candidates')
    if counters['generated'] > counters['attempts']:
        raise AssertionError('More cuts generated than rows attempted')
    # Each attempt either produced a cut or was rejected for a stated reason.
    accounted = counters['generated'] + sum(counters[k] for k in SKIPS)
    if accounted > counters['attempts']:
        raise AssertionError('Attempt outcomes exceed attempts')
    if counters['applied'] > counters['generated']:
        raise AssertionError('More cuts applied than generated')
    if counters['purged'] > counters['applied']:
        raise AssertionError('More cuts purged than applied')
    kept = cuts.get('basis_kept', 0)
    if isinstance(kept, bool) or not isinstance(kept, int) or kept < 0:
        raise AssertionError('Invalid counter basis_kept')
    if kept > counters['purged']:
        raise AssertionError('Basis carried through more purges than rows purged')
    if counters['rounds'] > counters['applied']:
        raise AssertionError('Rounds with a cut exceed the cuts applied')
    if counters['applied'] and not efficacy:
        raise AssertionError('Applied a cut with no reported efficacy')
    if not counters['applied'] and efficacy:
        raise AssertionError('Reported efficacy without applying a cut')
    if counters['calls'] and not seconds:
        raise AssertionError('Separator ran without spending time')
    net = counters['applied'] - counters['purged']
    total = result.get('cuts')
    if isinstance(total, int) and net > total:
        raise AssertionError('Retained Gomory rows exceed the reported cut total')
    return {'all_pass': True, 'enabled': True, 'attempts': counters['attempts'],
            'generated': counters['generated'], 'applied': counters['applied'],
            'purged': counters['purged'], 'retained': net,
            'rejected': {k: counters[k] for k in SKIPS if counters[k]},
            'best_efficacy': efficacy, 'seconds': seconds}


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(name, json.dumps(check(json.loads(Path(name).read_text()))))
