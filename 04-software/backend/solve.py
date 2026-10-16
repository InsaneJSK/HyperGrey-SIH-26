"""Engine routing. The only place in the platform that knows which solver runs.

Set SOLVER_ENGINE to pick one:
  reference  - HiGHS in an isolated process (default; "highs" is also accepted)
  sovereign  - run the project's own CLI binary at SOVEREIGN_BINARY

Both return the same normalized record, with statuses in one vocabulary, so
nothing above this file changes when the engine does. Every record carries the
engine that produced it.
"""
import json
import logging
import math
import os
import subprocess
import sys
import time
from pathlib import Path

from config import (MAX_COLUMNS, MAX_NONZEROS, MAX_ROWS, SOLVER_THREADS,
                    SOLVE_TIME_LIMIT, SOLVE_TIMEOUT_GRACE)

ENGINE = os.environ.get('SOLVER_ENGINE', 'reference').strip().lower()
if ENGINE == 'highs':
    ENGINE = 'reference'
BINARY = os.environ.get('SOVEREIGN_BINARY', '/app/bin/solver_cli')
DEFAULT_LIMIT = SOLVE_TIME_LIMIT
WORKER = Path(__file__).with_name('worker.py')
LOGGER = logging.getLogger(__name__)
MILP_FLAGS = ['--lp-recovery', '--improve-incumbent', '--repair-candidates',
              '--repair-heuristic-candidates', '--binary-proof', '--objective-lattice',
              '--raw-lp-priority', '--refine-basis', '--refine-at-checks', '--pump-guided-diving',
              '--pump-distance-diving', '--pump-primal-reopt', '--pump-distance-reopt',
              '--pump-distance-stage', '--lifted-covers', '--bounded-lp', '--tree-dives',
              '--fix-propagate', '--root-iteration-limit', '100000000']
# The reference library reports statuses as sentences; the API speaks one vocabulary.
REFERENCE_STATUS = {
    'Optimal': 'optimal', 'Infeasible': 'infeasible', 'Unbounded': 'unbounded',
    'Primal infeasible or unbounded': 'infeasible_or_unbounded',
    'Time limit reached': 'time_limit', 'Iteration limit reached': 'iteration_limit',
    'Solution limit reached': 'solution_limit', 'Memory limit reached': 'memory_limit',
    'Interrupted by user': 'interrupted', 'Load error': 'input_rejected',
    'Model error': 'input_rejected', 'Presolve error': 'numerical_error',
    'Solve error': 'numerical_error', 'Postsolve error': 'numerical_error',
    'Empty': 'empty', 'Not Set': 'not_set', 'Unknown': 'unknown',
}


def _empty(engine, status, message):
    return {'engine': engine, 'status': status, 'message': message, 'objective': None,
            'best_bound': None, 'gap': None, 'seconds': 0.0, 'primal': [], 'names': [],
            'nodes': None, 'rows': None, 'columns': None}


def json_safe(value):
    """Unknown bounds/gaps must be null, never non-standard JSON NaN/Infinity."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def _worker_env():
    return {**os.environ, 'OMP_NUM_THREADS': str(SOLVER_THREADS),
            'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}


def validate_engine():
    """Fail startup instead of advertising a healthy but unusable service."""
    if ENGINE == 'reference':
        result = subprocess.run([sys.executable, str(WORKER), '--check'],
                                capture_output=True, text=True, timeout=15, env=_worker_env())
        if result.returncode != 0:
            raise RuntimeError('HiGHS worker could not start; check dependencies and memory limits')
        return {'name': 'HiGHS', 'version': result.stdout.strip()}
    if ENGINE == 'sovereign':
        if not Path(BINARY).is_file() or not os.access(BINARY, os.X_OK):
            raise RuntimeError('SOVEREIGN_BINARY must name an executable for this host architecture')
        return {'name': 'Sovereign C++'}
    raise RuntimeError(f'unknown SOLVER_ENGINE {ENGINE!r}; use reference, highs or sovereign')


def _isolated_reference(path, integer, limit):
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(WORKER), str(path),
                               '1' if integer else '0', str(limit)],
                              capture_output=True, text=True, encoding='utf-8',
                              timeout=limit + SOLVE_TIMEOUT_GRACE, env=_worker_env())
    except subprocess.TimeoutExpired:
        result = _empty('reference', 'time_limit', 'worker stopped at its wall-clock limit; no solution retained')
        result['seconds'] = time.perf_counter() - started
        return result
    except OSError:
        LOGGER.exception('Unable to start HiGHS worker')
        return _empty('reference', 'engine_error', 'could not start the solver worker')
    if done.returncode != 0:
        LOGGER.error('HiGHS worker exited with code %s', done.returncode)
        return _empty('reference', 'engine_error', 'solver worker exited unexpectedly or exceeded its resource limit')
    try:
        result = json.loads(done.stdout)
        if not isinstance(result, dict) or 'status' not in result:
            raise ValueError('invalid worker result')
        return result
    except ValueError:
        LOGGER.error('HiGHS worker returned invalid JSON')
        return _empty('reference', 'engine_error', 'solver worker returned an invalid result')


def _sovereign(path, integer, limit):
    flags = ['--json', '--time-limit', str(limit)]
    flags += ['--milp', '--node-limit', '100000000', '--gap', '1e-6', *MILP_FLAGS] if integer else \
             ['--lp-method', 'bounded']
    started = time.perf_counter()
    try:
        done = subprocess.run([BINARY, str(path), *flags], capture_output=True, text=True,
                              timeout=limit + SOLVE_TIMEOUT_GRACE)
    except subprocess.TimeoutExpired:
        return _empty('sovereign', 'time_limit', 'solver stopped at its wall-clock limit; no solution retained')
    except OSError:
        return _empty('sovereign', 'engine_error', 'could not start the configured C++ binary')
    elapsed = time.perf_counter() - started
    try:
        parsed = json.loads(done.stdout)
        if not isinstance(parsed, dict):
            raise ValueError('expected a result object')
    except ValueError:
        status = 'input_rejected' if done.returncode == 2 else 'engine_error'
        return _empty('sovereign', status, (done.stderr or 'no output').strip()[:300])
    return {'engine': 'sovereign', 'status': parsed.get('status'), 'message': parsed.get('message', ''),
            'objective': parsed.get('objective'), 'best_bound': parsed.get('best_bound'),
            'gap': parsed.get('gap'), 'seconds': elapsed, 'primal': parsed.get('primal') or [],
            'names': [], 'nodes': parsed.get('nodes'), 'rows': parsed.get('rows'),
            'columns': parsed.get('columns')}


def _reference(path, integer, limit):
    import highspy
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    h.setOptionValue('time_limit', float(limit))
    h.setOptionValue('threads', SOLVER_THREADS)
    if h.readModel(str(path)) == highspy.HighsStatus.kError:
        return _empty('reference', 'input_rejected', 'model could not be read')
    lp = h.getLp()
    if lp.num_row_ > MAX_ROWS or lp.num_col_ > MAX_COLUMNS or h.getNumNz() > MAX_NONZEROS:
        return _empty('reference', 'input_rejected', 'model exceeds configured row, column or nonzero limits')
    has_integers = any(kind != highspy.HighsVarType.kContinuous for kind in lp.integrality_)
    if has_integers and not integer:
        # A continuous request on an integer model solves its relaxation, and says so.
        for j in range(lp.num_col_):
            h.changeColIntegrality(j, highspy.HighsVarType.kContinuous)
    started = time.perf_counter()
    if h.run() == highspy.HighsStatus.kError:
        return _empty('reference', 'numerical_error', 'HiGHS could not solve this model')
    elapsed = time.perf_counter() - started
    info = h.getInfo()
    raw = h.modelStatusToString(h.getModelStatus())
    solution = h.getSolution()
    feasible = (solution.value_valid and
                info.primal_solution_status == highspy.SolutionStatus.kSolutionStatusFeasible)
    values = list(solution.col_value) if feasible else []
    mip = integer and has_integers
    return {'engine': 'reference', 'status': REFERENCE_STATUS.get(raw, raw.lower().replace(' ', '_')),
            'message': '' if integer or not has_integers else 'integrality relaxed on request',
            'objective': float(h.getObjectiveValue()) if feasible else None,
            'best_bound': float(info.mip_dual_bound) if mip else None,
            'gap': float(info.mip_gap) if mip and feasible else None,
            'seconds': elapsed, 'primal': values,
            'names': [h.getColName(j)[1] for j in range(lp.num_col_)] if values else [],
            'nodes': int(info.mip_node_count) if mip else None,
            'rows': lp.num_row_, 'columns': lp.num_col_}


def solve(path: Path, integer: bool = False, limit: float = None):
    """Solve one model file and return a normalized record naming its engine."""
    limit = DEFAULT_LIMIT if limit is None else float(limit)
    if not math.isfinite(limit) or limit <= 0:
        raise ValueError('time limit must be positive and finite')
    limit = min(limit, DEFAULT_LIMIT)
    if ENGINE == 'reference':
        return json_safe(_isolated_reference(path, integer, limit))
    if ENGINE == 'sovereign':
        return json_safe(_sovereign(path, integer, limit))
    return _empty(ENGINE, 'engine_error', f'unknown SOLVER_ENGINE {ENGINE!r}')


def engine_name():
    return ENGINE
