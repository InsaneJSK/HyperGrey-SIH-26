"""Optimization demo API.

Three things a planner would actually ask, in the language they would ask them:
what is the best plan, what happens if I tighten this specification, and where
does it stop being affordable.

Nothing here decides which solver runs; that lives in solve.py alone.
"""
import os
import re
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import (MAX_MODEL_BYTES, MAX_REQUEST_BYTES, MAX_ROWS, MAX_COLUMNS,
                    MAX_NONZEROS, MAX_SWEEP_POINTS, SENSITIVITY_TIME_LIMIT,
                    SOLVE_TIMEOUT_GRACE)
from limits import RequestLimitsMiddleware
import solve

EXAMPLES = Path(__file__).resolve().parent / 'examples'
# Only this one coefficient of row R39 moves; everything else is the published model.
SULFUR_PATTERN = re.compile(r'( sale_fueloil R39 -)([0-9.]+)')


@asynccontextmanager
async def lifespan(app):
    app.state.solver = solve.validate_engine()
    yield


app = FastAPI(title='Optimization demo platform', version='0.2', lifespan=lifespan)
app.add_middleware(RequestLimitsMiddleware)
app.add_middleware(CORSMiddleware,
                   allow_origins=[s.strip() for s in os.getenv('CORS_ORIGINS', '*').split(',') if s.strip()],
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type'],
                   expose_headers=['Retry-After'])


@app.exception_handler(RequestValidationError)
async def invalid_request(request, error):
    # Pydantic may include NaN/Infinity in the rejected input. Do not echo it (or
    # multi-megabyte models) into a JSON error response.
    errors = [{'loc': item['loc'], 'msg': item['msg'], 'type': item['type']}
              for item in error.errors()]
    return JSONResponse({'detail': errors}, status_code=422)


class SolveRequest(BaseModel):
    model: Optional[str] = Field(None, description='MPS text, or leave empty and name an example')
    example: Optional[str] = Field(None, max_length=128, description='One of the names from GET /examples')
    integer: bool = False
    time_limit: Optional[float] = Field(None, gt=0, allow_inf_nan=False)


class SensitivityRequest(BaseModel):
    values: List[Annotated[float, Field(ge=0, allow_inf_nan=False)]] = Field(
                                default=[3.5, 3.48, 3.46, 3.44, 3.42, 3.4],
                                min_length=1, max_length=MAX_SWEEP_POINTS,
                                description='Fuel-oil sulfur maxima to try, in specification units')


def _example_path(name):
    if not re.fullmatch(r'[A-Za-z0-9_\-]+', name or ''):
        raise HTTPException(400, 'example names are letters, digits, dashes and underscores')
    path = EXAMPLES / (name + '.mps')
    if not path.exists():
        raise HTTPException(404, f'no example named {name!r}')
    return path


def _solve_text(text, integer, limit):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'model.mps'
        path.write_text(text, encoding='utf-8')
        return solve.solve(path, integer, limit)


def _profit(result):
    """The refinery objective is cost minus revenue, so profit is its negation."""
    value = result['objective']
    return None if value is None else -value + 0.0  # + 0.0 turns -0.0 into 0.0


@app.get('/health')
def health():
    return {'ok': True, 'engine': solve.engine_name()}


@app.get('/capabilities')
def capabilities():
    return {'engine': solve.engine_name(), 'solver': app.state.solver,
            'formats': ['mps'], 'max_model_bytes': MAX_MODEL_BYTES,
            'max_request_bytes': MAX_REQUEST_BYTES, 'max_rows': MAX_ROWS,
            'max_columns': MAX_COLUMNS, 'max_nonzeros': MAX_NONZEROS,
            'solve_time_limit': solve.DEFAULT_LIMIT, 'max_concurrent_requests': 1,
            'max_sweep_points': MAX_SWEEP_POINTS,
            'sensitivity_time_limit': SENSITIVITY_TIME_LIMIT}


@app.get('/examples')
def examples():
    return {'examples': sorted(p.stem for p in EXAMPLES.glob('*.mps'))}


@app.post('/solve')
def run_solve(request: SolveRequest):
    if request.model is not None and request.example is not None:
        raise HTTPException(400, 'supply model text or an example name, not both')
    if request.model is not None:
        if not request.model.strip():
            raise HTTPException(400, 'model text must not be empty')
        try:
            size = len(request.model.encode('utf-8'))
        except UnicodeEncodeError:
            raise HTTPException(400, 'model text must be valid UTF-8')
        if size > MAX_MODEL_BYTES:
            raise HTTPException(413, f'model exceeds {MAX_MODEL_BYTES} bytes')
        return _solve_text(request.model, request.integer, request.time_limit)
    if request.example:
        return solve.solve(_example_path(request.example), request.integer, request.time_limit)
    raise HTTPException(400, 'supply either model text or an example name')


@app.post('/refinery/plan')
def refinery_plan():
    result = solve.solve(_example_path('marco_refinery'), False)
    return {**result, 'profit': _profit(result),
            'reading': 'Profit from the base plan, at the published fuel-oil sulfur maximum of 3.5.'}


@app.post('/refinery/sensitivity')
def refinery_sensitivity(request: SensitivityRequest):
    """Sweep the fuel-oil sulfur maximum and report where profit reaches zero.

    A tighter specification can never increase profit; that is checked, not
    assumed, and a violation is returned rather than hidden.
    """
    base = _example_path('marco_refinery').read_text(encoding='utf-8')
    if not SULFUR_PATTERN.search(base):
        raise HTTPException(500, 'the refinery model does not carry the expected sulfur coefficient')
    curve, monotone = [], True
    deadline = time.perf_counter() + SENSITIVITY_TIME_LIMIT
    ordered = sorted(request.values, reverse=True)  # loosest specification first
    previous = None
    for value in ordered:
        value += 0.0  # Normalize -0.0 before adding the MPS coefficient's minus sign.
        # Leave room for worker startup/parsing inside the total sweep budget.
        remaining = deadline - time.perf_counter() - SOLVE_TIMEOUT_GRACE
        if remaining <= 0:
            result = solve._empty(solve.engine_name(), 'time_limit', 'sensitivity time budget exhausted')
        else:
            variant = SULFUR_PATTERN.sub(lambda m: f'{m.group(1)}{value:.17g}', base, count=1)
            result = _solve_text(variant, False, min(remaining, solve.DEFAULT_LIMIT))
        profit = _profit(result)
        if previous is not None and profit is not None and profit > previous + 1e-6:
            monotone = False
        if profit is not None:
            previous = profit
        curve.append({'sulfur_limit': value, 'profit': profit, 'status': result['status'],
                      'seconds': result['seconds']})
    complete = all(p['status'] == 'optimal' and p['profit'] is not None for p in curve)
    paying = [p['sulfur_limit'] for p in curve if p['status'] == 'optimal' and p['profit'] is not None and p['profit'] > 1e-9]
    dead = [p['sulfur_limit'] for p in curve if p['status'] == 'optimal' and p['profit'] is not None and p['profit'] <= 1e-9]
    break_even = [min(paying), max(dead)] if complete and monotone and paying and dead and min(paying) > max(dead) else None
    return {'engine': solve.engine_name(), 'curve': curve, 'break_even_between': break_even,
            'monotone': monotone if complete else None, 'complete': complete,
            'reading': ('Profit falls with the specification and reaches zero once no in-spec plan pays, '
                        'because residual sulfur has nowhere else to go. That is a planning limit, '
                        'not a solver failure.') if complete and monotone else
                       'Some results are incomplete or inconsistent; no reliable trend or break-even band is established.'}
