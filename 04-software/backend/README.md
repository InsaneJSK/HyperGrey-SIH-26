# Refinery Planner API

FastAPI backend for the refinery planning demo, packaged for AWS EC2.
**HiGHS is the default solver.** The API keeps the engine name `reference`
for client compatibility; it does not mean the Sovereign C++ solver.
The refinery inputs are published teaching models, not operator data.

## Run locally

From `04-software/`, with Python 3.12 (run `cd 04-software` from the repository root first):

```sh
python -m pip install -r backend/requirements.txt
python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Or build the portable image (the build context must be `backend/`):

```sh
docker build -t refinery-api ./backend
docker run --rm --init -p 127.0.0.1:8000:8000 --memory=1400m --memory-swap=1400m --cpus=1.5 refinery-api
```

Run `python backend/smoke_test.py http://localhost:8000` to exercise the service.
The smoke test needs no third-party Python packages. Full regression tests:

```sh
python -m pip install -r backend/requirements-dev.txt
python -m pytest backend/tests -q
```

For EC2, HTTPS, pricing and frontend configuration, follow [DEPLOY.md](DEPLOY.md).
Frontend integration changes and the complete AWS change inventory are in
[FRONTEND_MIGRATION.md](FRONTEND_MIGRATION.md).

## API contract

| Method | Path | Returns |
|---|---|---|
| GET | `/health` | `{"ok": true, "engine": "reference"}` after startup checks the worker |
| GET | `/capabilities` | Actual solver/version and configured limits |
| GET | `/examples` | The three bundled MPS model names |
| POST | `/solve` | Normalized result from a bundled example or MPS text |
| POST | `/refinery/plan` | Base refinery plan and profit |
| POST | `/refinery/sensitivity` | Sorted sulfur/profit curve, completeness, monotonicity and break-even band |
| GET | `/docs`, `/openapi.json` | Interactive docs and API schema |

Example `POST /solve` JSON:

```json
{"example": "production_lotsizing", "integer": true, "time_limit": 10}
```

Supply exactly one of `example` or `model`. `model` is MPS **text inside JSON**,
not multipart upload or a server filename. `integer` defaults to false, solving
the continuous relaxation of integer inputs. Results include `engine`, `status`,
`objective`, `best_bound`, `gap`, `seconds`, `primal`, `names`, `nodes`,
`rows` and `columns`. Missing/nonfinite metrics are JSON `null`.
`seconds` is solver runtime; HTTP latency includes process startup and parsing.

Solver outcomes such as `infeasible`, `unbounded`, `input_rejected`, `time_limit`,
`memory_limit` and `engine_error` are HTTP 200 result records; clients must inspect
`status`. Feasible points can accompany a time limit. A forcibly stopped worker
has no retained point. Invalid fields return 422, ambiguous/empty input or invalid
example names 400, missing examples 404, and oversized bodies 413.
A busy solver returns 429 with `Retry-After: 2`; health/discovery remain available.
Uvicorn can also return 503 at its total connection limit.

Sensitivity accepts `{"values": [3.5, 3.45, 3.4]}`. Values must be finite and
nonnegative, with 1–12 points. `complete` is false if any solve did not reach an
optimal result; in that case `monotone` and `break_even_between` are null.
The break-even band is a sampled bracket, not an exact threshold.

## Resource limits

One compute request runs at a time, including an entire sensitivity sweep.
There is no persistent queue or result storage. Each HiGHS solve has its own
process, a wall-clock timeout covering imports/parsing, and a Linux
address-space ceiling. Compose adds container memory/CPU limits and bounded logs.

**Run exactly one Uvicorn worker.** Admission control is process-local; extra
workers multiply the compute allowance and memory requirement. For sustained
concurrent use, introduce a bounded job queue and resize first.

| Variable | Default | Meaning |
|---|---|---|
| `SOLVER_ENGINE` | `reference` | HiGHS; `highs` is an alias. `sovereign` needs a separately supplied executable. |
| `SOLVE_TIME_LIMIT` | `20` | Solver seconds; requests may lower it. Worker wall time adds 5 seconds for setup. |
| `SOLVER_THREADS` | `1` | HiGHS CPU threads |
| `WORKER_MEMORY_MB` | `1024` | Linux worker address-space limit in MiB; not applied on Windows |
| `MAX_MODEL_BYTES` | `20000000` | UTF-8 model limit; whole JSON body limit adds 1,000,000 bytes |
| `MAX_ROWS`, `MAX_COLUMNS` | `50000` each | Structural limits, checked after parsing |
| `MAX_NONZEROS` | `1000000` | Structural limit, checked after parsing |
| `SENSITIVITY_TIME_LIMIT` | `30` | Total sweep budget; remaining points time out if exhausted |
| `CORS_ORIGINS` | `*` locally | Comma-separated origins. Compose defaults to `http://localhost:5173`. |
| `PORT` | `8000` in Docker | Container port; Compose's proxy expects 8000 |

Only `API_ADDRESS` and `CORS_ORIGINS` are read from `.env` by Compose. Change
resource settings in `compose.yaml` together with their container limits.
Bare Uvicorn reads configuration from its environment.

The C++ adapter remains opt-in for local/research use. Its binary is absent from
the AWS image, and selecting it without an executable fails startup. The hosted
resource profile and tests target HiGHS. No fallback silently switches solvers.

Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
