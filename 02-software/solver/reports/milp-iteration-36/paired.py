"""Paired 300 s runs for iteration 35: iteration 34 executable against iteration 35, same flags.

Declared in PLAN.md. For each model the two profiles start at the same moment on
the same host, so machine load hits both together. Every returned point is
checked by an independent HiGHS reader, every objective compared with MIPLIB's
published solution file.

Usage: python paired.py <set-name> <model-folder> <model> [<model> ...]
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
ROOT = BASE.parents[1]
PROFILE = json.loads((BASE / 'CANDIDATE_PROFILE.json').read_text())
BUILDS = {'control': ROOT / 'reports/milp-iteration-35/final_solver_cli.exe',
          'candidate': BASE / 'final_solver_cli.exe'}
PROFILES = {'control': PROFILE['control_flags'], 'candidate': PROFILE['flags']}
BINARY = BUILDS['candidate']
LIMIT = 300
SOLU = 'https://miplib.zib.de/downloads/miplib2017-v32.solu'

spec = importlib.util.spec_from_file_location('contained', BASE / 'run_contained.py')
contained = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contained)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(folder, name):
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (name + '.mps')
    if not target.exists():
        with urllib.request.urlopen(f'https://miplib.zib.de/WebData/instances/{name}.mps.gz', timeout=600) as r:
            raw = r.read()
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            target.write_bytes(stream.read())
        print('downloaded', name, target.stat().st_size, flush=True)
    return target


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
        return {'status': 'no_point'}
    matrix = lp.a_matrix_
    activity = np.zeros(lp.num_row_)
    for j in range(lp.num_col_):
        for k in range(matrix.start_[j], matrix.start_[j + 1]):
            activity[matrix.index_[k]] += matrix.value_[k] * x[j]
    violation = 0.0
    for values, lows, ups in ((x, lp.col_lower_, lp.col_upper_), (activity, lp.row_lower_, lp.row_upper_)):
        violation = max(violation, float(np.max(lows - values)), float(np.max(values - ups)))
    integrality = float(max((abs(x[j] - round(x[j])) for j, kind in enumerate(lp.integrality_)
                             if kind != highspy.HighsVarType.kContinuous), default=0.0))
    return {'status': 'checked', 'max_violation': violation, 'integer_violation': integrality,
            'valid': bool(violation <= 1e-6 and integrality <= 1e-6)}


def run_pair(out, name, model):
    records = {label: out / f'{name}.{label}.json' for label in PROFILES}
    if all(p.exists() for p in records.values()):
        return {label: json.loads(p.read_text()) for label, p in records.items()}

    def one(label):
        command = [str(BUILDS[label]), str(model), '--milp', '--json', *PROFILES[label],
                   '--time-limit', str(LIMIT), '--node-limit', '100000000', '--gap', '1e-6']
        return label, contained.monitor(command, out / f'{name}.{label}', LIMIT + 120, 6144)
    with futures.ThreadPoolExecutor(2) as pool:
        return dict(pool.map(one, PROFILES))


def main():
    set_name, folder, models = sys.argv[1], ROOT / sys.argv[2], sys.argv[3:]
    out = BASE / set_name
    out.mkdir(parents=True, exist_ok=True)
    print('binary', sha(BINARY), flush=True)
    optima = published()
    paths = {name: fetch(folder, name) for name in models}
    rows = []
    for name in models:
        pair = run_pair(out, name, paths[name])
        target = optima.get(name, {})
        for label in PROFILES:
            record = pair[label]
            native = record.get('native_result') or {}
            bounded = native.get('bounded_lp') or {}
            value = native.get('objective')
            row = {'name': name, 'profile': label, 'status': record.get('status'),
                   'message': native.get('message', ''), 'objective': value,
                   'best_bound': native.get('best_bound'), 'gap': native.get('gap'),
                   'root_bound': native.get('root_bound_before_cuts'),
                   'root_solved': native.get('root_bound_before_cuts') is not None,
                   'nodes': native.get('nodes'), 'bounded_optimal': bounded.get('optimal'),
                   'bounded_cold': bounded.get('cold'), 'bounded_warm': bounded.get('warm'),
                   'fallbacks': bounded.get('fallbacks'), 'unresolved_nodes': native.get('unresolved_nodes'),
                   'basis_kept': (native.get('gomory_cuts') or {}).get('basis_kept'),
                   'peak_commit_mib': record.get('peak_commit_bytes', 0) / 2 ** 20,
                   'published': target, 'check': check_point(paths[name], native),
                   'proven': record.get('status') in ('optimal', 'gap_limit')}
            if value is not None and target.get('value') is not None:
                row['objective_error'] = abs(value - target['value']) / (1 + abs(target['value']))
                if row['proven'] and target.get('kind') == 'opt':
                    row['completion_agrees'] = bool(row['objective_error'] <= 1e-6)
            rows.append(row)
            (out / 'results.json').write_text(json.dumps(rows, indent=1), encoding='utf-8')
        c, k = rows[-2], rows[-1]
        print(f"{name:24s} control: {str(c['status'])[:22]:22s} root={'yes' if c['root_solved'] else 'no ':3s} "
              f"nodes={str(c['nodes']):>8s} | candidate: {str(k['status'])[:22]:22s} "
              f"root={'yes' if k['root_solved'] else 'no ':3s} nodes={str(k['nodes']):>8s} "
              f"obj={k['objective']} pub={target.get('value')}", flush=True)
    summary = {}
    for label in PROFILES:
        sel = [r for r in rows if r['profile'] == label]
        summary[label] = {
            'root_solved': sum(r['root_solved'] for r in sel),
            'proven': sum(r['proven'] for r in sel),
            'completion_disagrees': [r['name'] for r in sel if r.get('completion_agrees') is False],
            'validated_points': sum(bool(r['check'].get('valid')) for r in sel),
            'rejected_points': [r['name'] for r in sel if r['check'].get('status') == 'checked'
                                and not r['check'].get('valid')],
            'unresolved_root': [r['name'] for r in sel if not r['root_solved']],
            'fallbacks': sum(r['fallbacks'] or 0 for r in sel),
            'unresolved_nodes': sum(r['unresolved_nodes'] or 0 for r in sel),
            'cold_starts': sum(r['bounded_cold'] or 0 for r in sel),
            'nodes': sum(r['nodes'] or 0 for r in sel),
        }
    summary['binaries'] = {label: sha(path) for label, path in BUILDS.items()}
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == '__main__':
    main()
