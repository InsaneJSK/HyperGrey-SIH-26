"""Guard re-run: the 17 guard-stopped MIPLIB instances, old build against new.

Declared in PLAN.md before any run. For each model the old and new executables
start at the same moment and run side by side, so machine load hits both
together. Every returned point is checked by an independent HiGHS reader and
every objective compared with MIPLIB's published solution file.
"""
import concurrent.futures as futures
import gzip
import hashlib
import importlib.util
import io
import json
import sys

import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
DATA = ROOT / 'datasets/miplib2017-guard17'
OUT = BASE / 'runs'
BUILDS = {'old': ROOT / 'reports/milp-iteration-32/final_solver_cli.exe',
          'new': ROOT / 'reports/milp-iteration-33/final_solver_cli.exe'}
MODELS = ['50v-10', 'binkar10_1', 'exp-1-500-5-5', 'fiball', 'gen-ip054', 'glass4', 'gmu-35-40',
          'gmu-35-50', 'h80x6320d', 'irp', 'markshare2', 'mas74', 'mas76', 'neos-2657525-crna',
          'neos-3004026-krka', 'neos-3046615-murg', 'neos-3381206-awhea']
LIMIT = 300
# Exactly the flag list the Kaggle sweep used for batches 1 and 2.
FLAGS = ['--milp', '--json', '--lp-recovery', '--improve-incumbent', '--repair-candidates',
         '--repair-heuristic-candidates', '--late-lifted-covers', '--late-compact-equalities',
         '--late-reduced-bound-lp', '--binary-proof', '--objective-lattice', '--raw-lp-priority',
         '--refine-basis', '--refine-at-checks', '--pump-guided-diving', '--pump-distance-diving',
         '--pump-primal-reopt', '--pump-distance-reopt', '--pump-distance-stage',
         '--bounded-lp', '--tree-dives', '--fix-propagate',
         '--time-limit', str(LIMIT), '--node-limit', '100000000', '--gap', '1e-6']
SOLU = 'https://miplib.zib.de/downloads/miplib2017-v32.solu'
EXTERNAL_MEMORY_MIB = 6144  # safety net only; the solver's own guard is what is under test

spec = importlib.util.spec_from_file_location('contained', ROOT / 'reports/milp-iteration-33/run_contained.py')
contained = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contained)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch_models():
    DATA.mkdir(parents=True, exist_ok=True)
    manifest_path = DATA / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'instances': []}
    known = {row['name']: row for row in manifest['instances']}
    for name in MODELS:
        if name in known and (ROOT / known[name]['model']).exists():
            continue
        url = f'https://miplib.zib.de/WebData/instances/{name}.mps.gz'
        with urllib.request.urlopen(url, timeout=600) as response:
            raw = response.read()
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            data = stream.read()
        model = DATA / (name + '.mps')
        model.write_bytes(data)
        known[name] = {'name': name, 'url': url, 'status': 'ready',
                       'model': model.relative_to(ROOT).as_posix(), 'model_sha256': sha(model), 'bytes': len(data)}
        manifest['instances'] = [known[n] for n in MODELS if n in known]
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print('downloaded', name, len(data), flush=True)
    return {n: ROOT / known[n]['model'] for n in MODELS}


def published():
    with urllib.request.urlopen(SOLU, timeout=120) as response:
        text = response.read().decode()
    table = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            table[parts[1]] = {'kind': parts[0].strip('='), 'value': float(parts[2]) if len(parts) > 2 else None}
    return table


def check_point(model, native):
    # The project's pinned reference install, the same one every iteration uses.
    sys.path.insert(0, str(ROOT / 'tools/reference/python'))
    import highspy
    import numpy as np
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    if h.readModel(str(model)) == highspy.HighsStatus.kError:
        return {'status': 'reference_read_failed'}
    h.ensureColwise()
    lp = h.getLp()
    x = np.asarray((native or {}).get('primal') or [], dtype=float)
    if len(x) != lp.num_col_ or not np.all(np.isfinite(x)):
        return {'status': 'no_point', 'columns': lp.num_col_}
    matrix = lp.a_matrix_
    activity = np.zeros(lp.num_row_)
    for j in range(lp.num_col_):
        for k in range(matrix.start_[j], matrix.start_[j + 1]):
            activity[matrix.index_[k]] += matrix.value_[k] * x[j]
    violation = 0.0
    for values, lows, ups in ((x, lp.col_lower_, lp.col_upper_), (activity, lp.row_lower_, lp.row_upper_)):
        violation = max(violation, float(np.max(lows - values)), float(np.max(values - ups)))
    integrality = max((abs(x[j] - round(x[j])) for j, kind in enumerate(lp.integrality_)
                       if kind != highspy.HighsVarType.kContinuous), default=0.0)
    return {'status': 'checked', 'max_violation': violation, 'integer_violation': float(integrality),
            'objective': float(np.dot(lp.col_cost_, x) + lp.offset_),
            'valid': bool(violation <= 1e-6 and integrality <= 1e-6)}


def run_pair(name, model):
    # A pair that already completed is read back, never re-run: the first harness
    # attempt crashed while WRITING 50v-10's results, after both solves finished.
    done = {label: OUT / f'{name}.{label}.json' for label in ('old', 'new')}
    if all(path.exists() for path in done.values()):
        return {label: json.loads(path.read_text()) for label, path in done.items()}
    def one(label):
        command = [str(BUILDS[label]), str(model), *FLAGS]
        return label, contained.monitor(command, OUT / f'{name}.{label}', LIMIT + 120, EXTERNAL_MEMORY_MIB)
    with futures.ThreadPoolExecutor(2) as pool:
        return dict(pool.map(one, ('old', 'new')))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for label, binary in BUILDS.items():
        print(label, sha(binary), flush=True)
    models = fetch_models()
    optima = published()
    rows = []
    for name in MODELS:
        pair = run_pair(name, models[name])
        target = optima.get(name, {})
        for label in ('old', 'new'):
            record = pair[label]
            native = record.get('native_result') or {}
            check = check_point(models[name], native)
            value = native.get('objective')
            row = {'name': name, 'build': label, 'status': record.get('status'),
                   'message': native.get('message', ''), 'objective': value,
                   'best_bound': native.get('best_bound'), 'gap': native.get('gap'),
                   'nodes': native.get('nodes'), 'peak_commit_mib': record.get('peak_commit_bytes', 0) / 2 ** 20,
                   'wall_seconds': record.get('wall_seconds'), 'published': target, 'check': check,
                   'guard_stop': native.get('message') == 'Open-node memory guard',
                   'proven': record.get('status') in ('optimal', 'gap_limit')}
            if value is not None and target.get('value') is not None:
                row['objective_error'] = abs(value - target['value']) / (1 + abs(target['value']))
                if row['proven'] and target.get('kind') == 'opt':
                    row['completion_agrees'] = row['objective_error'] <= 1e-6
            rows.append(row)
            (OUT / 'results.json').write_text(json.dumps(rows, indent=1), encoding='utf-8')
        o, n = rows[-2], rows[-1]
        print(f"{name:20s} old: {str(o['status'])[:11]:11s} {'GUARD' if o['guard_stop'] else '     '} "
              f"nodes={str(o['nodes']):>9s} {o['peak_commit_mib']:7.0f}MiB | "
              f"new: {str(n['status'])[:11]:11s} {'GUARD' if n['guard_stop'] else '     '} "
              f"nodes={str(n['nodes']):>9s} {n['peak_commit_mib']:7.0f}MiB", flush=True)
    summary = {}
    for label in ('old', 'new'):
        sel = [r for r in rows if r['build'] == label]
        summary[label] = {
            'guard_stops': sum(r['guard_stop'] for r in sel),
            'proven': sum(r['proven'] for r in sel),
            'completion_agrees': sum(r.get('completion_agrees') is True for r in sel),
            'completion_disagrees': [r['name'] for r in sel if r.get('completion_agrees') is False],
            'validated_points': sum(bool(r['check'].get('valid')) for r in sel),
            'rejected_points': [r['name'] for r in sel if r['check'].get('status') == 'checked'
                                and not r['check'].get('valid')],
            'nodes': sum(r['nodes'] or 0 for r in sel),
            'peak_commit_mib_max': max(r['peak_commit_mib'] for r in sel),
        }
    summary['binaries'] = {k: sha(v) for k, v in BUILDS.items()}
    summary['flags'] = FLAGS
    (OUT / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'flags'}, indent=1))


if __name__ == '__main__':
    main()
