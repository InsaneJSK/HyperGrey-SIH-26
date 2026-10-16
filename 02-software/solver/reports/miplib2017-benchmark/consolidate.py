"""Merge every MIPLIB 2017 sweep run into one complete table.

Sources, in list order: batch 1 [0:60], batch 2 [60:120], batch 3 [120:164] (the
session was cancelled at 44 of 60), final part A [164:202] and part B [202:240].
Every instance appears exactly once; the script refuses to write if any is
missing or duplicated.
"""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPORTS = BASE.parent
SOURCES = [('batch 1', REPORTS / 'kaggle-miplib2017-02/returned/results.json'),
           ('batch 2', REPORTS / 'kaggle-miplib2017-03/returned/results.json'),
           ('batch 3', REPORTS / 'kaggle-miplib2017-04/returned/results.json'),
           ('final A', REPORTS / 'kaggle-miplib2017-05/returned-a/results.json'),
           ('final B', REPORTS / 'kaggle-miplib2017-05/returned-b/results.json')]


def outcome(r):
    if r.get('status') == 'infeasible':
        return 'proven infeasible'
    if r.get('proven'):
        return 'proven optimal'
    if r.get('point_validated'):
        return 'validated point'
    if r.get('status') == 'process_error':
        return 'resource limit exit'
    if r.get('message') == 'Open-node memory guard':
        return 'memory guard, no point'
    if r.get('status') == 'unresolved_relaxations':
        return 'root LP unresolved'
    return 'no point'


def main():
    rows, seen = [], Counter()
    for label, path in SOURCES:
        for r in json.loads(path.read_text()):
            seen[r['name']] += 1
            r['run'] = label
            rows.append(r)
    duplicates = [n for n, c in seen.items() if c > 1]
    if duplicates or len(rows) != 240:
        raise SystemExit(f'expected 240 unique instances, got {len(rows)}; duplicates {duplicates}')
    for r in rows:
        r['outcome'] = outcome(r)
        r['guard'] = r.get('message') == 'Open-node memory guard'
    counts = Counter(r['outcome'] for r in rows)
    summary = {
        'instances': len(rows),
        'proven_optimal': sum(r['outcome'] == 'proven optimal' for r in rows),
        'proven_infeasible': sum(r['outcome'] == 'proven infeasible' for r in rows),
        'validated_points_including_optima': sum(bool(r.get('point_validated')) for r in rows),
        'rejected_points': [r['name'] for r in rows if r.get('objective') is not None and not r.get('point_validated')],
        'disagreeing_with_published': [r['name'] for r in rows if r.get('completion_agrees') is False],
        'memory_guard_stops': sum(r['guard'] for r in rows),
        'root_lp_unresolved': sum(r.get('status') == 'unresolved_relaxations' for r in rows),
        'resource_limit_exits': [r['name'] for r in rows if r.get('status') == 'process_error'],
        'no_point': sum(r.get('objective') is None and r['outcome'] != 'proven infeasible' for r in rows),
        'outcomes': dict(counts),
        'solver_sha256': 'e40e849f69d273777089e3cfd21fdfd7f29803f50cf0ef4f39e26691295c866c',
        'budget_seconds': 300, 'workers_per_session': 2,
        'caveat': 'Two instances shared four cloud vCPUs per session: outcomes at a fixed budget under '
                  'contention. No timing claim.',
    }
    (BASE / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    order = ['proven optimal', 'proven infeasible', 'validated point', 'memory guard, no point',
             'root LP unresolved', 'resource limit exit', 'no point']
    lines = ['| Instance | Outcome | Objective | Published | Relative error | Rows × cols | Run |',
             '|---|---|---:|---:|---:|---|---|']
    for r in sorted(rows, key=lambda x: (order.index(x['outcome']), x.get('objective_error') or 9e9, x['name'])):
        err = r.get('objective_error')
        pub = (r.get('published') or {}).get('value')
        ref = r.get('reference') or {}
        guard = ' (guard)' if r['guard'] and r['outcome'] == 'validated point' else ''
        lines.append(f"| `{r['name']}` | {r['outcome']}{guard} | "
                     f"{'-' if r.get('objective') is None else format(r['objective'], '.10g')} | "
                     f"{'-' if pub is None else format(pub, '.10g')} | "
                     f"{'-' if err is None else format(err, '.2e')} | "
                     f"{ref.get('rows', '-')} × {ref.get('columns', '-')} | {r['run']} |")
    (BASE / 'TABLE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'caveat'}, indent=1))


if __name__ == '__main__':
    main()
