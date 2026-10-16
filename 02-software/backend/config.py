"""Validated limits shared by the API and its isolated solver worker."""
import math
import os


def positive_number(name, default, kind=float):
    value = kind(os.environ.get(name, str(default)))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')
    return value


SOLVE_TIME_LIMIT = positive_number('SOLVE_TIME_LIMIT', 20)
SOLVE_TIMEOUT_GRACE = 5
SOLVER_THREADS = positive_number('SOLVER_THREADS', 1, int)
WORKER_MEMORY_MB = positive_number('WORKER_MEMORY_MB', 1024, int)
MAX_MODEL_BYTES = positive_number('MAX_MODEL_BYTES', 20_000_000, int)
# Bound the complete JSON body before FastAPI parses it, including chunked uploads.
MAX_REQUEST_BYTES = MAX_MODEL_BYTES + 1_000_000
MAX_ROWS = positive_number('MAX_ROWS', 50_000, int)
MAX_COLUMNS = positive_number('MAX_COLUMNS', 50_000, int)
MAX_NONZEROS = positive_number('MAX_NONZEROS', 1_000_000, int)
MAX_SWEEP_POINTS = 12
SENSITIVITY_TIME_LIMIT = positive_number('SENSITIVITY_TIME_LIMIT', 30)
COMPUTE_PATHS = frozenset(('/solve', '/refinery/plan', '/refinery/sensitivity'))
