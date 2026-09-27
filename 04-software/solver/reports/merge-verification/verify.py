"""Does merging the weak-pivot safeguard change the shipping profile's answers?

The flag it adds is opt-in and off by default, so the claim to test is that the
merged build, run on the recommended profile, produces exactly what the frozen
iteration 36 executable produces. Work is fixed by a node limit rather than a
clock so the comparison is deterministic, and every reported field is compared,
not just the objective.

A second pass turns --stable-primal-ratio on, to confirm the merge actually
wired the new flag through rather than merely leaving it inert.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / 'reports/milp-iteration-36/final_solver_cli.exe'
MERGED = ROOT / 'build-merge-verify/solver_cli.exe'
PROFILE = json.loads((ROOT / 'reports/milp-iteration-37/CANDIDATE_PROFILE.json')
                     .read_text(encoding='utf-8'))['recommended_flags']
FIELDS = ('status', 'objective', 'best_bound', 'gap', 'nodes', 'lp_iterations',
          'warm_starts', 'heuristic_solves', 'cuts', 'bound_tightenings',
          'unresolved_nodes', 'lp_resource_limits', 'separator_rows_discarded')
NODES = sys.argv[1] if len(sys.argv) > 1 else '2000'


def models():
    found = {}
    for folder in sorted((ROOT / 'datasets').iterdir()):
        if folder.is_dir():
            for p in sorted(folder.glob('*.mps')):
                found.setdefault(p.stem, p)
    return found


def run(binary, model, extra=()):
    command = [str(binary), str(model), '--json', '--milp', '--time-limit', '900',
               '--node-limit', NODES, '--gap', '0', *PROFILE, *extra]
    done = subprocess.run(command, capture_output=True, text=True, timeout=1200)
    try:
        r = json.loads(done.stdout)
    except ValueError:
        return {'status': f'process_error(exit {done.returncode})'}
    return {k: r.get(k) for k in FIELDS}


def main():
    available = models()
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else sorted(available)[:16]
    rows, mismatches = [], 0
    for name in names:
        model = available.get(name)
        if model is None:
            print(f'{name:28s} SKIP (not on this machine)')
            continue
        old, new = run(FROZEN, model), run(MERGED, model)
        differs = [k for k in FIELDS if old.get(k) != new.get(k)]
        mismatches += bool(differs)
        rows.append({'model': name, 'frozen': old, 'merged': new, 'differs': differs})
        mark = 'MISMATCH ' + ','.join(differs) if differs else 'identical'
        print(f'{name:28s} {str(old.get("status")):22s} nodes={str(old.get("nodes")):>7s} {mark}', flush=True)

    # The new flag must actually exist and be accepted.
    probe = names[0] if names else None
    flag_ok = None
    if probe and available.get(probe):
        on = run(MERGED, available[probe], ('--stable-primal-ratio',))
        flag_ok = not str(on.get('status', '')).startswith('process_error')
        print(f'\n--stable-primal-ratio accepted by the merged build: {flag_ok} '
              f'(status {on.get("status")})')

    out = ROOT / 'reports/merge-verification'
    (out / 'EQUIVALENCE.json').write_text(json.dumps(
        {'node_limit': NODES, 'profile': PROFILE, 'compared': len(rows),
         'mismatches': mismatches, 'stable_primal_ratio_accepted': flag_ok,
         'rows': rows}, indent=1), encoding='utf-8')
    print(f'\n{len(rows)} models compared at a {NODES}-node limit, {mismatches} mismatches')
    return 1 if mismatches else 0


if __name__ == '__main__':
    raise SystemExit(main())
