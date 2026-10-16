"""MIPLIB 2017 benchmark re-run on the iteration 36 engine (Kaggle CPU session).

Question this run answers: on a full public benchmark set, which instances can
this solver finish at all, and which does it only get a point on. Timings are
NOT a claim here: two instances run concurrently on shared cloud vCPUs, so every
outcome is "under contention at this budget" and nothing else.

Design, after batch 0 returned process_error on every instance:
  * a self-test runs first and prints raw stdout, stderr and exit code, so a
    broken invocation is visible in the first ten lines of the log instead of
    240 lines later;
  * no ulimit wrapper - the only untested part of batch 0 and the prime suspect,
    since the binary itself answered --version fine there. Memory is bounded by
    the solver's own open-node guard and by the watchdog;
  * every failure keeps its exit code and stderr, and the progress line shows
    them;
  * a fixed alphabetical slice, so four runs cover the set with no overlap;
  * anything that reaches its budget without proving optimality is written to
    carry_over.json for the next run to retry with a larger budget.

Correctness: the published MIPLIB solution file supplies the reference optimum,
and the returned point is checked for feasibility and integrality against the
original file by an independent HiGHS reader. We never feed a reference value
back into the solver.
"""
import concurrent.futures as futures
import gzip
import io
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

WORK = Path('/kaggle/working')
INPUT = Path('/kaggle/input')
BUILD = WORK / 'build'
MODELS = WORK / 'instances'
RESULTS = WORK / 'results'
LIST_URL = 'https://miplib.zib.de/downloads/benchmark-v2.test'
INSTANCE_URL = 'https://miplib.zib.de/WebData/instances/{}.mps.gz'
SLICE_START = 120
MAX_MODELS = 60  # re-run part c of 4
LIMIT = 300.0            # per instance, seconds
WATCHDOG = LIMIT + 150
WORKERS = 2
GLOBAL_GUARD = 10.0 * 3600
FLAGS = ['--milp', '--json'] + ['--capture-work', '--lp-recovery', '--improve-incumbent', '--repair-candidates', '--repair-heuristic-candidates', '--capture-lp-failure', '--capture-rejected-candidates', '--binary-proof', '--objective-lattice', '--raw-lp-priority', '--capture-cut-rounds', '--capture-refinement', '--refine-basis', '--refine-at-checks', '--pump-guided-diving', '--capture-feasibility', '--pump-distance-diving', '--pump-primal-reopt', '--pump-distance-reopt', '--pump-distance-stage', '--lifted-covers', '--bounded-lp', '--tree-dives', '--fix-propagate', '--gomory-cuts', '--root-iteration-limit', '100000000'] + [
         '--time-limit', str(LIMIT), '--node-limit', '100000000', '--gap', '1e-6']
KEEP = ('status', 'message', 'objective', 'best_bound', 'gap', 'nodes', 'lp_iterations', 'total_seconds',
        'rows', 'columns', 'first_incumbent_seconds', 'warm_starts', 'heuristic_solves', 'cuts')
UNPROVEN = ('time_limit', 'node_limit', 'iteration_limit', 'external_timeout', 'unresolved_relaxations')


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def find_source():
    for marker in sorted(INPUT.rglob('src/mps.cpp')):
        print('source tree:', marker.parent.parent, flush=True)
        return marker.parent.parent
    print('input tree:', [str(p) for p in sorted(INPUT.rglob('*'))[:40]])
    raise SystemExit('solver source not found under /kaggle/input')


def build(src):
    BUILD.mkdir(parents=True, exist_ok=True)
    sources = [str(p) for p in sorted((src / 'src').glob('*.cpp'))
               if p.name not in ('scale_benchmark.cpp', 'milp.cpp')]
    binary = BUILD / 'solver_cli'
    done = subprocess.run(['g++', '-O2', '-std=c++11', '-fopenmp', '-I', str(src / 'include'),
                           '-o', str(binary), *sources], capture_output=True, text=True)
    print('compiler exit', done.returncode, flush=True)
    if done.returncode:
        print(done.stderr[-4000:])
        raise SystemExit('build failed')
    print('solver sha256', sha256(binary))
    print(subprocess.run([str(binary), '--version'], capture_output=True, text=True).stdout.strip(), flush=True)
    return binary


def self_test(binary):
    """Solve one tiny model with the real flag list and show everything."""
    model = WORK / 'selftest.mps'
    model.write_text('\n'.join([
        'NAME SELFTEST', 'ROWS', ' N COST', ' L CAP', ' G DEM', 'COLUMNS',
        # Exactly three tokens: the reader takes name, 'MARKER', 'INTORG'.
        ' MARK0001 \'MARKER\' \'INTORG\'',
        ' X COST -3 CAP 2', ' X DEM 1', ' Y COST -5 CAP 3', ' Y DEM 1',
        ' MARK0002 \'MARKER\' \'INTEND\'',
        'RHS', ' B CAP 12 DEM 2', 'BOUNDS', ' UI B X 5', ' UI B Y 5', 'ENDATA', '']), encoding='utf-8')
    done = subprocess.run([str(binary), str(model), *FLAGS], capture_output=True, text=True, timeout=120)
    print('self-test exit', done.returncode)
    print('self-test stdout:', done.stdout.strip()[:600])
    print('self-test stderr:', done.stderr.strip()[:600], flush=True)
    try:
        parsed = json.loads(done.stdout)
    except ValueError:
        raise SystemExit('self-test produced no JSON: the invocation is broken, not the instances')
    print('self-test status', parsed.get('status'), 'objective', parsed.get('objective'), flush=True)
    model.unlink()


def published_optima():
    """MIPLIB's own solution file; the version number moves, so try a range."""
    urls = [f'https://miplib.zib.de/downloads/miplib2017-v{v}.solu' for v in range(32, 14, -1)]
    urls.append('https://miplib.zib.de/downloads/miplib2017.solu')
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                text = response.read().decode()
        except Exception:  # noqa: BLE001
            continue
        table = {}
        for line in text.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                table[parts[1]] = {'kind': parts[0].strip('='),
                                   'value': float(parts[2]) if len(parts) > 2 else None}
        print('solution file:', url, 'entries', len(table), flush=True)
        return table, url
    print('solution file: none reachable; objectives will not be compared', flush=True)
    return {}, None


def instance_names():
    with urllib.request.urlopen(LIST_URL, timeout=60) as response:
        names = [line.strip().decode().replace('.mps.gz', '') for line in response if line.strip()]
    print('benchmark instances listed:', len(names), flush=True)
    return names


def fetch(name):
    target = MODELS / (name + '.mps')
    if target.exists():
        return target, None
    try:
        with urllib.request.urlopen(INSTANCE_URL.format(name), timeout=600) as response:
            raw = response.read()
        with gzip.open(io.BytesIO(raw)) as stream:
            target.write_bytes(stream.read())
        return target, None
    except Exception as error:  # noqa: BLE001  (retained, never hidden)
        return None, repr(error)[:200]


def run_solver(binary, model):
    started = time.time()
    try:
        done = subprocess.run([str(binary), str(model), *FLAGS],
                              capture_output=True, text=True, timeout=WATCHDOG)
    except subprocess.TimeoutExpired:
        return {'status': 'external_timeout', 'wall_seconds': time.time() - started, 'exit_code': None}
    record = {'wall_seconds': time.time() - started, 'exit_code': done.returncode}
    try:
        parsed = json.loads(done.stdout)
        record.update({k: parsed.get(k) for k in KEEP})
        record['primal'] = parsed.get('primal') or []
    except ValueError:
        record['status'] = 'process_error'
        record['stderr'] = done.stderr.strip()[-600:]
        record['stdout_head'] = done.stdout.strip()[:200]
    return record


def check_point(model, record):
    """Independent feasibility and integrality check of our point, HiGHS reader."""
    import highspy
    import numpy as np
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    if h.readModel(str(model)) == highspy.HighsStatus.kError:
        return {'status': 'reference_read_failed'}
    h.ensureColwise()
    lp = h.getLp()
    out = {'status': 'read', 'rows': lp.num_row_, 'columns': lp.num_col_}
    x = np.asarray(record.get('primal') or [], dtype=float)
    if len(x) != lp.num_col_ or not np.all(np.isfinite(x)):
        return out
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
    out.update(candidate_checked=True, candidate_max_violation=float(violation),
               candidate_integer_violation=float(integrality),
               candidate_objective=float(np.dot(lp.col_cost_, x) + lp.offset_))
    return out


def one(binary, name, optima):
    model, error = fetch(name)
    if model is None:
        return {'name': name, 'status': 'download_failed', 'error': error}
    record = run_solver(binary, model)
    try:
        check = check_point(model, record)
    except Exception as error:  # noqa: BLE001
        check = {'status': 'reference_error', 'error': repr(error)[:200]}
    record.pop('primal', None)
    published = optima.get(name, {})
    row = {'name': name, 'model_sha256': sha256(model), 'bytes': model.stat().st_size,
           **record, 'reference': check, 'published': published}
    row['point_validated'] = bool(check.get('candidate_checked')
                                  and check.get('candidate_max_violation', 9) <= 1e-6
                                  and check.get('candidate_integer_violation', 9) <= 1e-6)
    value, target = row.get('objective'), published.get('value')
    if value is not None and target is not None:
        row['objective_error'] = abs(value - target) / (1 + abs(target))
        if row.get('status') in ('optimal', 'gap_limit') and published.get('kind') == 'opt':
            row['completion_agrees'] = row['objective_error'] <= 1e-6
    row['proven'] = row.get('status') in ('optimal', 'gap_limit')
    (RESULTS / (name + '.json')).write_text(json.dumps(row), encoding='utf-8')
    model.unlink(missing_ok=True)
    return row


def main():
    done = subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'highspy==1.12.0'],
                          capture_output=True, text=True)
    print('highspy install exit', done.returncode, flush=True)
    for folder in (MODELS, RESULTS):
        folder.mkdir(parents=True, exist_ok=True)
    binary = build(find_source())
    self_test(binary)
    optima, solution_url = published_optima()
    names = instance_names()
    batch = names[SLICE_START:SLICE_START + MAX_MODELS]
    print(f'batch: {len(batch)} instances, slice [{SLICE_START}:{SLICE_START + MAX_MODELS}],'
          f' {LIMIT:.0f}s each, {WORKERS} at a time', flush=True)
    rows, attempted, started = [], set(), time.time()

    def work(name):
        if time.time() - started > GLOBAL_GUARD:
            return {'name': name, 'status': 'not_attempted'}
        attempted.add(name)
        return one(binary, name, optima)

    with futures.ThreadPoolExecutor(WORKERS) as pool:
        for row in pool.map(work, batch):
            rows.append(row)
            (WORK / 'results.json').write_text(json.dumps(rows), encoding='utf-8')
            note = ''
            if row.get('status') in ('process_error', 'download_failed'):
                note = f" exit={row.get('exit_code')} err={str(row.get('stderr') or row.get('error'))[:120]}"
            print(f"[{len(rows):3d}/{len(batch)}] {row['name'][:30]:30s} {str(row.get('status'))[:18]:18s}"
                  f" obj={str(row.get('objective'))[:13]:>13s} gap={str(row.get('gap'))[:8]:>8s}"
                  f" pub={str(row.get('published', {}).get('value'))[:13]:>13s}"
                  f" valid={str(row.get('point_validated')):5s} agree={row.get('completion_agrees')}"
                  f" [{time.time() - started:.0f}s]{note}", flush=True)

    carry = [r['name'] for r in rows if r.get('status') in UNPROVEN or r.get('status') == 'not_attempted']
    (WORK / 'carry_over.json').write_text(json.dumps(
        {'next_slice_start': SLICE_START + MAX_MODELS, 'retry_with_more_time': carry,
         'suggested_limit_seconds': LIMIT * 4}, indent=1), encoding='utf-8')
    summary = {'slice': [SLICE_START, SLICE_START + MAX_MODELS], 'attempted': len(attempted),
               'instances': len(rows), 'limit_seconds': LIMIT, 'workers': WORKERS, 'flags': FLAGS,
               'solver_sha256': sha256(binary), 'solution_file': solution_url,
               'proven': sum(bool(r.get('proven')) for r in rows),
               'completion_agrees': sum(r.get('completion_agrees') is True for r in rows),
               'completion_disagrees': [r['name'] for r in rows if r.get('completion_agrees') is False],
               'point_validated': sum(bool(r.get('point_validated')) for r in rows),
               'point_rejected': [r['name'] for r in rows
                                  if r.get('objective') is not None and not r.get('point_validated')],
               'infeasible_claimed': [r['name'] for r in rows if r.get('status') == 'infeasible'],
               'process_error': [r['name'] for r in rows if r.get('status') == 'process_error'],
               'download_failed': [r['name'] for r in rows if r.get('status') == 'download_failed'],
               'carry_over': carry, 'elapsed_seconds': time.time() - started,
               'caveat': 'Two instances share four cloud vCPUs: outcomes at a fixed budget under '
                         'contention. No timing claim is made from this run.'}
    (WORK / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1))
    shutil.rmtree(MODELS, ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)


if __name__ == '__main__':
    main()
