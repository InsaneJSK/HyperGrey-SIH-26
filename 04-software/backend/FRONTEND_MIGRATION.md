# Frontend handoff: Hugging Face to EC2

This describes the AWS preparation changes made on 26 September 2026. No
frontend source is present in this repository, so frontend work below must be
applied in that project's code and deployment settings.

## Required frontend checks

| Area | Current backend behavior | Frontend action |
|---|---|---|
| API URL | Public address will be `https://YOUR_API_DOMAIN`; port 8000 is internal. | Replace the HF base URL. Use the hostname root, without `:8000` or `/api`. Rebuild a frontend whose API URL is set at build time. |
| Existing routes | `/health`, `/examples`, `/solve`, `/refinery/plan`, `/refinery/sensitivity`, `/docs` remain. | Keep existing methods and paths. Prefer exact paths without trailing slashes. |
| Solver identity | HiGHS 1.12.0 is still `engine: "reference"`. Configuration accepts `highs` as an alias, but responses retain `reference`. | Label it HiGHS. If there is a solver selector, expose only the available hosted solver. There is no per-request engine selector. |
| Busy server | One compute request runs at a time across all users and all three POST routes. Overlap returns 429 and `Retry-After: 2`. | Show a busy state and permit retry after that delay. Disable duplicate submissions. A sensitivity sweep occupies the slot for the whole sweep. |
| Input choice | `/solve` rejects simultaneous non-null `model` and `example`. | Send one. Omit the unused field; do not send an empty string placeholder alongside the chosen input. |
| Model upload | Nonblank valid UTF-8 MPS text, at most 20,000,000 encoded bytes; entire JSON body at most 21,000,000 bytes. | Keep JSON upload, not multipart. Check `new TextEncoder().encode(text).length`. Avoid character-count-only checks. |
| Solve time | Omitted/null uses 20 seconds. A supplied value must be positive and finite; values above 20 are capped. | Reject zero, negative and nonfinite values locally. Use a maximum of 20 in the control. |
| Sensitivity input | Between 1 and 12 finite, nonnegative values. Invalid list lengths now produce 422 rather than 400. | Validate length/range and handle 422. Values are returned sorted from loosest to tightest as before. |
| Sensitivity output | New `complete: boolean`; `monotone` is now `boolean \| null`. Break-even is null unless the sweep is complete and monotone with a sampled crossing. | Update types and distinguish `true`, `false` and `null`. A null value is unknown, not a failed monotonicity check. |
| Missing results | Nonfinite/missing objective, bound or gap serialize as null. No usable point means an empty `primal` list and no objective. | Render unavailable values explicitly. Do not coerce null to zero; a real zero objective/profit remains a valid result. |
| Solver outcomes | HTTP 200 can carry `infeasible`, `unbounded`, `input_rejected`, `time_limit`, `memory_limit`, `numerical_error` or `engine_error`. | Inspect `status` before showing success. A time-limit result may have a feasible point; a forcibly stopped worker has none. |
| Validation errors | 422 returns `detail` as an array of objects containing `loc`, `msg`, `type`; rejected input and validation context are no longer echoed. Other errors generally have a string `detail`. | Support both formats. Do not depend on `detail[].input` or `detail[].ctx`. |
| CORS | Compose reads explicit frontend origins from `CORS_ORIGINS`; GET/POST and Content-Type are allowed. Credentials are not enabled. Retry-After is exposed. | Configure every real frontend origin on EC2. Use JSON requests without cookies or unnecessary custom headers. Adding Authorization/custom headers requires a separate backend CORS/auth change. |
| Timeouts | Upload has a 30-second budget. Normal solve work is capped at 20 seconds plus 5 for setup; the whole sweep has a 30-second budget. | If the client has an explicit request timeout, allow about 75 seconds including upload and transport. A browser abort is not server-side solver cancellation. |

`GET /capabilities` is new and optional for the frontend. It reports solver
identity/version, current model/time limits and the one-request concurrency
limit. It can replace hard-coded UI limits. Backend configuration is authoritative.

The current structural limits are 50,000 rows, 50,000 columns and 1,000,000
nonzero coefficients. They are checked after parsing and produce an
`input_rejected` result, not a request-validation status code.

## Error and response examples

Busy response, HTTP 429 (with `Retry-After: 2`):

```json
{"detail": "solver is busy; retry shortly"}
```

Validation response, HTTP 422:

```json
{
  "detail": [
    {
      "loc": ["body", "time_limit"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

The sensitivity result type should accommodate:

```ts
type SensitivityResult = {
  engine: string;
  complete: boolean;
  monotone: boolean | null;
  break_even_between: [number, number] | null;
  curve: Array<{
    sulfur_limit: number;
    profit: number | null;
    status: string;
    seconds: number;
  }>;
  reading: string;
};
```

For display, check `complete === false` first, then distinguish
`monotone === true` from `monotone === false`. Do not chart a missing profit as
zero or show a break-even band when it is null. The band is a sampled interval,
not an exact threshold.

HTTP handling should also cover 400 (bad/ambiguous input), 404 (unknown example),
408 (slow upload), 413 (oversized request/model), and 503 (Uvicorn connection
capacity). A proxy error can be non-JSON; do not assume every unsuccessful
response can be parsed as JSON. Errors during an active compute request may
return 429 before input validation because admission happens first.

`integer` still defaults to false; send true to enforce the production example's
integer variables. Inputs remain MPS; no new QPLIB, lpmini, multipart-upload,
job-polling or cancellation endpoint was added. `seconds` normally measures
solver execution, excluding worker startup and parsing; forced-timeout records
measure observed wall time. Use a client timer for the user's elapsed wait.

## Full change inventory

| File(s) | Changes |
|---|---|
| `app.py` | Startup validation, API version 0.2, optional capabilities route, configurable CORS, safe 422 responses, stricter model/example/time/sweep validation, UTF-8 byte counting, bounded sensitivity duration, more precise sulfur coefficients, negative-zero handling, and honest incomplete-sweep reporting. |
| `solve.py` | HiGHS worker process adapter, `highs` configuration alias, startup dependency checks, fixed thread allowance, model-size checks, finite JSON output, feasible-point checks, wall-clock timeout/crash handling, monotonic timers, and normalized C++ timeout handling. |
| `config.py` | Central positive/finite configuration validation; time, thread, memory, upload, row, column, nonzero and sweep limits. |
| `limits.py` | One compute request at a time, 429/Retry-After, bounded bodies including chunked uploads, 30-second upload timeout, Content-Length checks and smaller non-compute body allowance. |
| `worker.py` | Disposable HiGHS process, Linux 1024 MiB address-space ceiling, structured failures, strict JSON output. |
| `Dockerfile` | Python 3.12 slim Bookworm, ARM64/x86 support, binary-only dependency installation, unprivileged app user, explicit runtime copies, port 8000, health check, single Uvicorn worker, process signal handling, connection/keep-alive/shutdown limits and proxy header support. |
| `compose.yaml` | API plus Caddy, restarts, health dependency, read-only API filesystem, 64 MiB temporary filesystem, 1400 MiB API and 128 MiB proxy memory caps, 1.5 API CPUs, 64-process allowance, dropped capabilities, persistent certificate volumes and rotating logs. No direct public API port. |
| `Caddyfile` | Reverse proxy and compression, hostname-based automatic HTTPS, 45-second upstream response-header timeout. |
| `.env.example` | API hostname and allowed frontend origins; initial HTTP-only test configuration. |
| `deploy/ec2-user-data.sh` | Ubuntu 24.04 bootstrap for Docker/Compose and deployment directory. |
| `requirements.txt` | FastAPI 0.115.6 → 0.141.1, Uvicorn 0.34.0 standard extras → 0.54.0 base package, Pydantic 2.10.4 → 2.13.5. Explicit Starlette 1.7.0 and NumPy 2.5.3 pins. HiGHS stays 1.12.0. |
| `requirements-dev.txt`, `tests/test_api.py` | Test dependencies and 35 regressions for results, invalid requests, overload, timeouts, worker failures and startup errors. |
| `smoke_test.py` | EC2/local defaults, 45-second network timeout, standard-library HTTP client instead of requests, discovery checks and stronger production-objective/input checks. |
| `README.md`, `DEPLOY.md`, `VERIFICATION.md` | Removed HF metadata and instructions, documented EC2 deployment and API limits, and recorded actual Windows/Linux/ARM64-emulation checks. |
| `THIRD_PARTY_NOTICES.md`, `licences/HiGHS.txt` | Supplied the missing notices and HiGHS license; documented teaching-model provenance. |
| `backend/.dockerignore` | Excluded environment files, development/test/deployment content and unnecessary documentation from image context; kept required notices. |
| Root `.gitignore`, `.gitattributes` | Ignore local environment files while preserving the example, and enforce LF for Linux bootstrap scripts. |

The AWS preparation did not modify the C++ solver sources or the bundled model
data. The C++ adapter is available only with a separately supplied executable;
the EC2 image deliberately runs HiGHS. No per-user history, persistent queue,
login or API-key system was introduced.

This handoff file and the expanded Windows/manual deployment directions were
added afterward to explain those changes; they do not change API behavior.
