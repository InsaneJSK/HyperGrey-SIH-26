"""Fixed-work equivalence: the trail representation must change nothing.

Same models, same fixed node limit, heuristics off so nothing is time-dependent.
Node counts, bounds, objectives and bound tightenings must match the iteration 32
binary exactly. Any difference is a semantic change, not a representation change.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('D:/sih-2026/SIH-backup-solver/SIH-backup-solver')
OLD = ROOT / 'reports/milp-iteration-32/final_solver_cli.exe'
NEW = ROOT / 'build-milp-iter32/solver_cli.exe'
FIELDS = ('status', 'objective', 'best_bound', 'nodes', 'lp_iterations', 'bound_tightenings', 'cuts')
MODELS = ['p0033', 'flugpl', 'stein27', 'egout', 'lseu', 'mod008', 'p0201', 'misc03',
          'pk1', 'rgn', 'gen-ip002', 'blend2', 'gt2', 'mas74', 'p0282', 'binkar10_1']
NODES = sys.argv[1] if len(sys.argv) > 1 else '3000'


def find(name):
    for folder in sorted((ROOT / 'datasets').iterdir()):
        if (folder / (name + '.mps')).exists():
            return folder / (name + '.mps')
    return None


def run(binary, model, extra):
    command = [str(binary), str(model), '--json', '--milp', '--time-limit', '600',
               '--node-limit', NODES, '--gap', '0', '--no-heuristics', '--bounded-lp', *extra]
    done = subprocess.run(command, capture_output=True, text=True, timeout=900)
    try:
        d = json.loads(done.stdout)
    except ValueError:
        return {'status': 'process_error', 'stderr': done.stderr[-200:]}
    return {k: d.get(k) for k in FIELDS}


mismatch = 0
for profile, extra in (('plain', []), ('cuts', ['--lifted-covers', '--gomory-cuts'])):
    for name in MODELS:
        model = find(name)
        if model is None:
            print(f'{name}: not found')
            continue
        a, b = run(OLD, model, extra), run(NEW, model, extra)
        same = a == b
        mismatch += not same
        flag = 'MATCH  ' if same else 'DIFFER '
        print(f"{flag}{profile:6s} {name:12s} nodes={a.get('nodes')}/{b.get('nodes')}"
              f" obj={a.get('objective')}/{b.get('objective')}"
              f" bound={a.get('best_bound')}/{b.get('best_bound')}"
              f" tighten={a.get('bound_tightenings')}/{b.get('bound_tightenings')}", flush=True)
        if not same:
            for k in FIELDS:
                if a.get(k) != b.get(k):
                    print(f'    {k}: old={a.get(k)!r} new={b.get(k)!r}')
print(f'\nmismatches: {mismatch} of {2 * len(MODELS)}')
sys.exit(1 if mismatch else 0)
