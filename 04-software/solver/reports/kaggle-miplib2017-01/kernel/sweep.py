"""MIPLIB 2017 benchmark sweep for the SIH26119 solver (Kaggle CPU session).

Builds the solver from the attached source dataset, downloads the complete
benchmark list, solves each instance at a fixed budget, then checks every
returned point with an independent HiGHS process on the original file.

Outcomes only: concurrent workers make wall-clock times unsuitable for any
speed claim, and this script makes none. Every failure is recorded.
"""
import concurrent.futures as futures
import gzip
import io
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

WORK = Path('/kaggle/working')
INPUT = Path('/kaggle/input')
BUILD = WORK / 'build'
MODELS = WORK / 'instances'
RESULTS = WORK / 'results'
LIST_URL = 'https://miplib.zib.de/downloads/benchmark-v2.test'
INSTANCE_URL = 'https://miplib.zib.de/WebData/instances/{}.mps.gz'
LIMIT = 60.0
WATCHDOG = 90.0
MEMORY_KB = 6 * 1024 * 1024
WORKERS = 3
FLAGS = ['--milp', '--json', '--lp-recovery', '--improve-incumbent', '--repair-candidates',
         '--repair-heuristic-candidates', '--late-lifted-covers', '--late-compact-equalities',
         '--late-reduced-bound-lp', '--binary-proof', '--objective-lattice', '--raw-lp-priority',
         '--refine-basis', '--refine-at-checks', '--pump-guided-diving', '--pump-distance-diving',
         '--pump-primal-reopt', '--pump-distance-reopt', '--pump-distance-stage',
         '--bounded-lp', '--tree-dives', '--fix-propagate',
         '--time-limit', str(LIMIT), '--node-limit', '250000000', '--gap', '1e-6']
KEEP = ('status', 'message', 'objective', 'best_bound', 'gap', 'nodes', 'lp_iterations', 'total_seconds',
        'rows', 'columns', 'first_incumbent_seconds', 'warm_starts', 'heuristic_solves', 'cuts')


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def find_source():
    """Locate the attached source tree (Kaggle extracts uploaded archives)."""
    for marker in sorted(INPUT.rglob('src/mps.cpp')):
        root = marker.parent.parent
        print('source tree:', root)
        return root
    for archive in sorted(INPUT.rglob('source.zip')):
        root = WORK / 'source'
        if root.exists():
            shutil.rmtree(root)
        root.mkdir(parents=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(root)
        print('source archive:', archive)
        return root
    print('input tree:', [str(p) for p in sorted(INPUT.rglob('*'))[:40]])
    raise SystemExit('solver source not found under /kaggle/input')


def build(src):
    BUILD.mkdir(exist_ok=True)
    sources = [str(p) for p in sorted((src / 'src').glob('*.cpp'))
               if p.name not in ('scale_benchmark.cpp', 'milp.cpp')]
    binary = BUILD / 'solver_cli'
    command = ['g++', '-O2', '-std=c++11', '-fopenmp', '-I', str(src / 'include'), '-o', str(binary), *sources]
    done = subprocess.run(command, capture_output=True, text=True)
    print('compiler exit', done.returncode)
    if done.returncode != 0:
        print(done.stderr[-4000:])
        raise SystemExit('build failed')
    print('solver sha256', sha256(binary))
    print(subprocess.run([str(binary), '--version'], capture_output=True, text=True).stdout.strip())
    return binary


def instance_names():
    with urllib.request.urlopen(LIST_URL, timeout=60) as response:
        names = [line.strip().decode().replace('.mps.gz', '') for line in response if line.strip()]
    print('benchmark instances listed:', len(names))
    return names


def fetch(name):
    target = MODELS / (name + '.mps')
    if target.exists():
        return target, None
    try:
        with urllib.request.urlopen(INSTANCE_URL.format(name), timeout=300) as response:
            raw = response.read()
        with gzip.open(io.BytesIO(raw)) as stream:
            target.write_bytes(stream.read())
        return target, None
    except Exception as error:  # retained, never hidden
        return None, repr(error)[:200]


def run_solver(binary, model):
    started = time.time()
    try:
        # ulimit through a shell wrapper: preexec_fn is not safe with threads.
        quoted = ' '.join(f"'{part}'" for part in [str(binary), str(model), *FLAGS])
        done = subprocess.run(['bash', '-c', f'ulimit -v {MEMORY_KB}; exec {quoted}'],
                              capture_output=True, text=True, timeout=WATCHDOG)
    except subprocess.TimeoutExpired:
        return {'status': 'external_timeout', 'wall_seconds': time.time() - started}
    record = {'wall_seconds': time.time() - started, 'exit_code': done.returncode}
    try:
        parsed = json.loads(done.stdout)
        record.update({k: parsed.get(k) for k in KEEP})
        record['primal'] = parsed.get('primal') or []
    except ValueError:
        record['status'] = 'process_error'
        record['stderr'] = done.stderr.strip()[:400]
    return record


def reference(model, record):
    """Independent HiGHS solve and check of our returned point."""
    import highspy
    import numpy as np
    h = highspy.Highs()
    for key, value in {'output_flag': False, 'threads': 1, 'random_seed': 0, 'time_limit': LIMIT,
                       'mip_rel_gap': 1e-9, 'mip_feasibility_tolerance': 1e-8}.items():
        h.setOptionValue(key, value)
    if h.readModel(str(model)) == highspy.HighsStatus.kError:
        return {'status': 'reference_read_failed'}
    h.run()
    h.ensureColwise()
    lp, info = h.getLp(), h.getInfo()
    out = {'status': h.modelStatusToString(h.getModelStatus()), 'objective': None,
           'best_bound': float(info.mip_dual_bound) if info.mip_dual_bound is not None else None,
           'rows': lp.num_row_, 'columns': lp.num_col_, 'seconds': h.getRunTime()}
    if h.getSolution().value_valid:
        out['objective'] = float(h.getObjectiveValue())
    x = np.asarray(record.get('primal') or [], dtype=float)
    if len(x) == lp.num_col_ and np.all(np.isfinite(x)):
        matrix = lp.a_matrix_
        activity = np.zeros(lp.num_row_)
        for j in range(lp.num_col_):
            for k in range(matrix.start_[j], matrix.start_[j + 1]):
                activity[matrix.index_[k]] += matrix.value_[k] * x[j]
        violation = 0.0
        for values, lows, ups in ((x, lp.col_lower_, lp.col_upper_), (activity, lp.row_lower_, lp.row_upper_)):
            for value, lo, up in zip(values, lows, ups):
                violation = max(violation, lo - value, value - up)
        integrality = max((abs(x[j] - round(x[j])) for j, kind in enumerate(lp.integrality_)
                           if kind != highspy.HighsVarType.kContinuous), default=0.0)
        out.update(candidate_checked=True, candidate_max_violation=float(violation),
                   candidate_integer_violation=float(integrality),
                   candidate_objective=float(np.dot(lp.col_cost_, x) + lp.offset_))
    return out


def one(binary, name):
    model, error = fetch(name)
    if model is None:
        return {'name': name, 'status': 'download_failed', 'error': error}
    record = run_solver(binary, model)
    try:
        check = reference(model, record)
    except Exception as error:  # noqa: BLE001
        check = {'status': 'reference_error', 'error': repr(error)[:200]}
    point = record.pop('primal', [])
    row = {'name': name, 'model_sha256': sha256(model), 'bytes': model.stat().st_size, **record,
           'reference': check}
    ok = check.get('candidate_checked')
    row['point_validated'] = bool(ok and check.get('candidate_max_violation', 9) <= 1e-6
                                  and check.get('candidate_integer_violation', 9) <= 1e-6)
    row['returned_point'] = bool(point)
    (RESULTS / (name + '.json')).write_text(json.dumps(row), encoding='utf-8')
    model.unlink(missing_ok=True)  # keep the session disk small
    return row


def install_reference():
    done = subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'highspy==1.12.0'],
                          capture_output=True, text=True)
    print('highspy install exit', done.returncode, done.stderr.strip()[-200:] if done.returncode else '')
    import highspy
    print('highspy version', highspy.Highs().version())


def main():
    install_reference()
    for folder in (MODELS, RESULTS):
        folder.mkdir(parents=True, exist_ok=True)
    source_root = find_source()
    binary = build(source_root)
    names = instance_names()
    rows = []
    started = time.time()
    with futures.ThreadPoolExecutor(WORKERS) as pool:
        for row in pool.map(lambda n: one(binary, n), names):
            rows.append(row)
            (WORK / 'results.json').write_text(json.dumps(rows), encoding='utf-8')
            print(f"[{len(rows):3d}/{len(names)}] {row['name'][:32]:32s} {str(row.get('status'))[:22]:22s}"
                  f" obj={str(row.get('objective'))[:14]:>14s} gap={str(row.get('gap'))[:8]:>8s}"
                  f" ref={str(row.get('reference', {}).get('status'))[:14]:14s} valid={row.get('point_validated')}"
                  f" [{time.time() - started:.0f}s]", flush=True)
    summary = {'instances': len(rows), 'flags': FLAGS, 'limit_seconds': LIMIT, 'workers': WORKERS,
               'solver_sha256': sha256(binary), 'source_files': sorted(p.name for p in (source_root / 'src').glob('*.cpp')),
               'returned_point': sum(bool(r.get('returned_point')) for r in rows),
               'point_validated': sum(bool(r.get('point_validated')) for r in rows),
               'completed': sum(r.get('status') in ('optimal', 'gap_limit') for r in rows),
               'infeasible_claimed': sum(r.get('status') == 'infeasible' for r in rows),
               'download_failed': sum(r.get('status') == 'download_failed' for r in rows),
               'process_error': sum(r.get('status') in ('process_error', 'external_timeout') for r in rows),
               'reference_optimal': sum((r.get('reference') or {}).get('status') == 'Optimal' for r in rows),
               'elapsed_seconds': time.time() - started,
               'caveat': 'Concurrent workers on shared cloud vCPUs: fixed-budget outcomes only, no speed claim.'}
    (WORK / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1))
    shutil.rmtree(MODELS, ignore_errors=True)
    shutil.rmtree(WORK / 'source', ignore_errors=True)


if __name__ == '__main__':
    main()
