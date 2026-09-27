"""Summarize iteration 32 records: every observation, control vs candidate.

Published optimal values appear only as reading context; they never enter a
solve, a validation decision or the category counts. The fresh holdout models
are deliberately left without published values here: this project has no
verified table for them, and the independent reference run is what validates
those records.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
SETS = [('development-30s', 'Development, 27 reused models, two repeats per profile'),
        ('holdout32-30s', 'Third fresh untouched holdout, 10 MIPLIB 3 models')]
PROFILES = ('control', 'candidate')
PUBLISHED = {'p0033': 3089, 'enigma': 0, 'flugpl': 1201500, 'stein27': 18, 'markshare_4_0': 1,
             'blend2': 7.598985, 'binkar10_1': 6742.200024, 'egout': 568.1007, 'gt2': 21166, 'lseu': 1120,
             'mod008': 307, 'p0201': 7615, 'p0282': 258411, 'misc03': 3360, 'misc07': 2810, 'pk1': 11,
             'rgn': 82.19999924, 'gen-ip002': -4783.733392, 'assign1-5-8': 212, 'lotsize': 1480195,
             'eil33-2': 934.007916, 'mas74': 11801.18573, 'gen-ip054': 6840.966, 'neos859080': 'infeasible',
             'danoint': 65.66666667, 'rout': 1077.56, 'mas76': 40005.05414}
COMPLETE = {'numerical_completion_checked', 'exact_proof_checked', 'terminal_status_crosschecked'}
BETTER = 1e-6  # relative difference below this is not a difference


def fmt(value, digits=10):
    if value is None:
        return '-'
    if isinstance(value, float):
        return f'{value:.{digits}g}'
    return str(value)


def load(folder):
    path = BASE / folder / 'results.json'
    if not path.exists():
        return []
    rows = []
    for r in json.loads(path.read_text()):
        if 'key' not in r:
            rows.append(r)
            continue
        ours = json.loads((BASE / folder / (r['key'] + '.ours.json')).read_text())
        monitor = ours.get('resource_monitor', {})
        gomory = ours.get('gomory_cuts', {})
        rows.append({**r, 'first_point': ours.get('first_incumbent_seconds'),
                     'lp_iterations': ours.get('lp_iterations'),
                     'peak_commit_mib': monitor.get('peak_commit_bytes', 0) / 2 ** 20,
                     'root_before': ours.get('root_bound_before_cuts'),
                     'root_after': ours.get('root_bound_after_cuts'),
                     'cuts': ours.get('cuts'), 'applied': gomory.get('applied', 0),
                     'purged': gomory.get('purged', 0), 'attempts': gomory.get('attempts', 0),
                     'gomory_seconds': gomory.get('seconds', 0),
                     'bounded_fallbacks': ours.get('bounded_lp', {}).get('fallbacks', 0),
                     'message': ours.get('message', '')})
    return rows


def summarize(rows):
    out = {}
    for profile in PROFILES:
        sel = [r for r in rows if r.get('profile') == profile]
        if not sel:
            continue
        cats = Counter(r.get('category') for r in sel)
        out[profile] = {
            'observations': len(sel),
            'completions': sum(cats[c] for c in COMPLETE),
            'checked_points': sum(1 for r in sel if r.get('objective') is not None
                                  and r.get('category') != 'validation_failure'),
            'no_incumbent_limits': cats['no_incumbent_limit'],
            'validation_failures': cats['validation_failure'],
            'process_failures': cats['process_failure'] + cats['input_rejected'],
            'categories': dict(cats),
            'gomory_applied': sum(r.get('applied', 0) for r in sel),
            'gomory_purged': sum(r.get('purged', 0) for r in sel),
            'gomory_seconds': round(sum(r.get('gomory_seconds', 0) for r in sel), 3),
            'fallbacks': sum(r.get('bounded_fallbacks', 0) for r in sel),
            'peak_commit_mib': round(max((r.get('peak_commit_mib', 0) for r in sel), default=0), 1),
        }
    return out


def direction(rows, name):
    """Minimization sense for this model, taken from the records themselves."""
    for r in rows:
        if r.get('name') == name and r.get('best_bound') is not None and r.get('objective') is not None:
            return 1 if r['best_bound'] <= r['objective'] else -1
    return 1


def compare_roots(rows):
    """Per model and repeat: did the candidate's root bound beat the control's?"""
    paired = defaultdict(dict)
    for r in rows:
        if 'key' in r and r.get('root_after') is not None:
            paired[(r['name'], r['repeat'])][r['profile']] = r['root_after']
    better = worse = same = 0
    detail = []
    for (name, repeat), values in sorted(paired.items()):
        if len(values) < 2:
            continue
        sense = direction(rows, name)
        control, candidate = values['control'], values['candidate']
        gain = sense * (candidate - control)
        scale = 1 + abs(control)
        verdict = 'same'
        if gain > BETTER * scale:
            better += 1
            verdict = 'better'
        elif gain < -BETTER * scale:
            worse += 1
            verdict = 'worse'
        else:
            same += 1
        detail.append({'model': name, 'repeat': repeat, 'control': control,
                       'candidate': candidate, 'verdict': verdict})
    return {'better': better, 'worse': worse, 'same': same, 'detail': detail}


def main():
    lines = ['# Iteration 32 model ledger', '',
             'Every observation, both profiles. `Published` is literature context only, and is',
             'deliberately absent for the fresh holdout.', '']
    comparison = ['# Control versus candidate by model', '',
                  'Each cell: status / objective / gap, one line per repeat.', '']
    summary = {}
    for folder, title in SETS:
        rows = load(folder)
        if not rows:
            continue
        summary[folder] = summarize(rows)
        summary[folder]['root_bound'] = compare_roots(rows)
        lines += [f'## {title}', '',
                  '| Run | Category | Objective | Bound | Gap | Root after cuts | Cuts | Gomory applied | '
                  'Purged | First point s | Nodes | Peak commit MiB | Published |',
                  '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in rows:
            if 'key' not in r:
                lines.append(f"| {r['name']} | {r.get('category')} | - | - | - | - | - | - | - | - | - | - | - |")
                continue
            lines.append(f"| {r['key']} | {r.get('category')} | {fmt(r.get('objective'))} | "
                         f"{fmt(r.get('best_bound'))} | {fmt(r.get('gap'), 4)} | {fmt(r.get('root_after'), 8)} | "
                         f"{fmt(r.get('cuts'))} | {r.get('applied')} | {r.get('purged')} | "
                         f"{fmt(r.get('first_point'), 4)} | {fmt(r.get('nodes'))} | "
                         f"{r.get('peak_commit_mib'):.1f} | {fmt(PUBLISHED.get(r['name']))} |")
            if r.get('validation_errors'):
                lines.append(f"|  | errors: {'; '.join(r['validation_errors'])} | | | | | | | | | | | |")
        lines.append('')
        by_model = defaultdict(lambda: defaultdict(list))
        for r in rows:
            if 'key' in r:
                by_model[r['name']][r['profile']].append(r)
        comparison += [f'## {title}', '', '| Model | Control | Candidate | Root bound C -> K | Published |',
                       '|---|---|---|---|---:|']
        roots = {(d['model'], d['repeat']): d for d in summary[folder]['root_bound']['detail']}
        for name, profiles in by_model.items():
            def cell(rs):
                return '<br>'.join(f"{'done' if x.get('category') in COMPLETE else x.get('status')} / "
                                   f"{fmt(x.get('objective'), 8)} / {fmt(x.get('gap'), 3)}" for x in rs)
            root_cells = '<br>'.join(
                f"{fmt(roots[(name, rep)]['control'], 8)} -> {fmt(roots[(name, rep)]['candidate'], 8)}"
                f" ({roots[(name, rep)]['verdict']})"
                for rep in sorted({r['repeat'] for r in profiles['control']}) if (name, rep) in roots)
            comparison.append(f"| {name} | {cell(profiles['control'])} | {cell(profiles['candidate'])} | "
                              f"{root_cells or '-'} | {fmt(PUBLISHED.get(name))} |")
        s = summary[folder]
        root = s['root_bound']
        comparison += ['', ' '.join(f"{p}: {v['completions']} completions, {v['checked_points']} checked points,"
                                    f" {v['validation_failures']} validation failures."
                                    for p, v in s.items() if p in PROFILES),
                       f"Root bound: candidate better on {root['better']}, worse on {root['worse']},"
                       f" unchanged on {root['same']} paired observations.", '']
    (BASE / 'MODEL_LEDGER.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (BASE / 'COMPARISON.md').write_text('\n'.join(comparison) + '\n', encoding='utf-8')
    (BASE / 'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({k: {p: v for p, v in s.items() if p in PROFILES or p == 'root_bound'}
                      for k, s in summary.items()}, indent=2, default=str)[:3000])


if __name__ == '__main__':
    main()
