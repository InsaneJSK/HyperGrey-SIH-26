"""Summarize iteration 30 records: every observation, control vs candidate.

Published optimal values appear only as reading context; they never enter a
solve, a validation decision or the category counts.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
SETS = [('development-30s', 'Development, 27 reused models, two repeats'),
        ('holdout28-30s', 'Iteration 28 holdout, 6 models'),
        ('fresh-30s', 'Fresh untouched holdout, 15 models')]
PUBLISHED = {'p0033': 3089, 'enigma': 0, 'flugpl': 1201500, 'stein27': 18, 'markshare_4_0': 1,
             'blend2': 7.598985, 'binkar10_1': 6742.200024, 'egout': 568.1007, 'gt2': 21166, 'lseu': 1120,
             'mod008': 307, 'p0201': 7615, 'p0282': 258411, 'misc03': 3360, 'misc07': 2810, 'pk1': 11,
             'rgn': 82.19999924, 'gen-ip002': -4783.733392, 'assign1-5-8': 212, 'lotsize': 1480195,
             'eil33-2': 934.007916, 'mas74': 11801.18573, 'gen-ip054': 6840.966, 'neos859080': 'infeasible',
             'danoint': 65.66666667, 'rout': 1077.56, 'mas76': 40005.05414,
             'vpm1': 20, 'vpm2': 13.75, 'bell3a': 878430.316, 'bell5': 8966406.49152,
             'gesa2': 25779856.3717, 'noswot': -41,
             'dcmulti': 188182, 'dsbmip': -305.198, 'fiber': 405935.18, 'fixnet6': 3983,
             'khb05250': 106940226, 'l152lav': 4722, 'misc06': 12850.8607, 'mod010': 6548, 'p0548': 8691,
             'pp08a': 7350, 'qiu': -132.873137, 'set1ch': 54537.75, 'stein45': 30, 'gesa3': 27991042.648,
             'modglob': 20740508.1}
COMPLETE = {'numerical_completion_checked', 'exact_proof_checked', 'terminal_status_crosschecked'}


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
        bounded = ours.get('bounded_lp', {})
        rows.append({**r, 'first_point': ours.get('first_incumbent_seconds'),
                     'lp_iterations': ours.get('lp_iterations'),
                     'peak_ws_mib': monitor.get('peak_working_set_bytes', 0) / 2 ** 20,
                     'peak_commit_mib': monitor.get('peak_commit_bytes', 0) / 2 ** 20,
                     'bounded_calls': bounded.get('calls', 0), 'bounded_fallbacks': bounded.get('fallbacks', 0),
                     'bounded_cutoff_nodes': bounded.get('cutoff_nodes', 0), 'message': ours.get('message', '')})
    return rows


def summarize(rows):
    out = {}
    for profile in ('control', 'candidate'):
        sel = [r for r in rows if r.get('profile') == profile]
        cats = Counter(r.get('category') for r in sel)
        out[profile] = {
            'observations': len(sel),
            'completions': sum(cats[c] for c in COMPLETE),
            'checked_points': sum(1 for r in sel if r.get('objective') is not None and r.get('category') != 'validation_failure'),
            'no_incumbent_limits': cats['no_incumbent_limit'],
            'validation_failures': cats['validation_failure'],
            'process_failures': cats['process_failure'] + cats['input_rejected'],
            'categories': dict(cats),
            'fallbacks': sum(r.get('bounded_fallbacks', 0) for r in sel),
            'peak_commit_mib': max((r.get('peak_commit_mib', 0) for r in sel), default=0),
        }
    return out


def main():
    lines = ['# Iteration 30 model ledger', '',
             'Every observation, both profiles. `Published` is literature context only.', '']
    summary = {}
    comparison = ['# Control versus candidate by model', '',
                  'Each cell: status / objective / gap. Completions are checked by the independent reference.', '']
    for folder, title in SETS:
        rows = load(folder)
        if not rows:
            continue
        summary[folder] = summarize(rows)
        lines += [f'## {title}', '',
                  '| Run | Category | Objective | Bound | Gap | First point s | Nodes | LP iterations | Bounded calls | Fallbacks | Peak commit MiB | Published |',
                  '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in rows:
            if 'key' not in r:
                lines.append(f"| {r['name']} | {r.get('category')} | - | - | - | - | - | - | - | - | - | - |")
                continue
            lines.append(f"| {r['key']} | {r.get('category')} | {fmt(r.get('objective'))} | {fmt(r.get('best_bound'))} | "
                         f"{fmt(r.get('gap'), 4)} | {fmt(r.get('first_point'), 4)} | {fmt(r.get('nodes'))} | "
                         f"{fmt(r.get('lp_iterations'))} | {r.get('bounded_calls')} | {r.get('bounded_fallbacks')} | "
                         f"{r.get('peak_commit_mib'):.1f} | {fmt(PUBLISHED.get(r['name']))} |")
            if r.get('validation_errors'):
                lines.append(f"|  | errors: {'; '.join(r['validation_errors'])} | | | | | | | | | | |")
        lines.append('')
        by_model = defaultdict(lambda: defaultdict(list))
        for r in rows:
            if 'key' in r:
                by_model[r['name']][r['profile']].append(r)
        comparison += [f'## {title}', '', '| Model | Control | Candidate | Published |', '|---|---|---|---:|']
        for name, profiles in by_model.items():
            cell = lambda rs: '<br>'.join(f"{'done' if x.get('category') in COMPLETE else x.get('status')} / "
                                          f"{fmt(x.get('objective'), 8)} / {fmt(x.get('gap'), 3)}" for x in rs)
            comparison.append(f"| {name} | {cell(profiles['control'])} | {cell(profiles['candidate'])} | {fmt(PUBLISHED.get(name))} |")
        s = summary[folder]
        comparison += ['', f"Control: {s['control']['completions']} completions, {s['control']['checked_points']} checked points, "
                           f"{s['control']['validation_failures']} validation failures. Candidate: {s['candidate']['completions']} completions, "
                           f"{s['candidate']['checked_points']} checked points, {s['candidate']['validation_failures']} validation failures.", '']
    (BASE / 'MODEL_LEDGER.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (BASE / 'COMPARISON.md').write_text('\n'.join(comparison) + '\n', encoding='utf-8')
    (BASE / 'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
