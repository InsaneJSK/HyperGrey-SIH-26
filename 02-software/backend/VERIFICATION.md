# AWS preparation verification — 26 September 2026

## Fixed failures and deployment risks

- Reproduced HTTP 500 for an infeasible MILP whose bound/gap included infinity;
  unavailable metrics now serialize as JSON null.
- Reproduced HTTP 500 for NaN/Infinity sensitivity inputs; validation now returns
  422 without echoing nonfinite values or large model bodies.
- Negative solve limits previously reached HiGHS; they are now rejected.
- Added whole-request and UTF-8 model limits, unambiguous input selection,
  finite/nonnegative sensitivity values and bounded example names.
- Moved HiGHS into disposable workers with hard timeouts and Linux memory limits;
  overlapping compute requests return 429. Health remains responsive.
- Incomplete sensitivity results no longer claim a verified monotone trend or
  break-even band. Solver points are returned only when HiGHS reports feasibility.
- Replaced HF metadata, port assumptions and deployment directions with an EC2
  container/Compose configuration, Caddy HTTPS, startup validation and health checks.
- Restored the missing third-party notice/license files referenced by old docs.

## Checks performed

- Regression suite: `python -m pytest backend/tests -q`: **35 passed** on Windows
  and **35 passed** inside the Linux x86_64 image with a read-only filesystem,
  1400 MiB memory limit and 1.5 CPU limit. One test-client dependency emits a
  deprecation warning; no test failures remain.
- Live Uvicorn server: `python backend/smoke_test.py http://127.0.0.1:18000`
  returned `ALL PASS`. Base refinery profit: 6.588421476681447; production MILP
  objective: 762.0. All three bundled examples reached optimal results.
- Verified an HTTPS forwarded-header request redirects `/solve/` to an HTTPS
  `/solve` URL, preserving scheme behind the reverse proxy.
- `docker compose -f backend/compose.yaml config --quiet` passed.
- Bootstrap script passed Bash syntax checking; `pip check` found no broken
  installed dependencies.
- Resolved/downloaded every pinned runtime dependency as a CPython 3.12 Linux
  ARM64 wheel, including HiGHS, NumPy and Pydantic Core. No source build needed.
- Built the actual Dockerfile for both Linux x86_64 and Linux ARM64 successfully.
- Started the Compose API and Caddy stack on isolated local ports. Both services
  became healthy; the full smoke test through Caddy returned `ALL PASS`.
  Caddy's configuration validation passed.
- Four simultaneous sensitivity requests produced one HTTP 200 and three HTTP
  429 responses with `Retry-After: 2`. CORS headers were present and health
  remained available afterward.
- Confirmed the running API uses its unprivileged user and read-only filesystem,
  with the configured container memory/CPU limits. Confirmed the Linux worker's
  hard and soft address-space limits are both 1,073,741,824 bytes (1024 MiB).
- Ran the ARM64 image under Docker Desktop emulation and confirmed `aarch64`.
  Its full HTTP smoke test returned `ALL PASS`, with refinery profit
  6.588421476681422 and MILP objective 762.0. Emulated startup took longer than
  native startup; these timings are not EC2 performance measurements.
- `git diff --check` passed.

## Remaining deployment checks

Docker verification is complete. Native Graviton performance, the Ubuntu EC2
bootstrap, public DNS and real HTTPS certificate issuance still require the
EC2 launch check. This is not an EC2 load benchmark. Verify the largest intended
uploads against the limits before increasing traffic or reducing RAM.

No AWS resources were provisioned. Account access, a frontend origin and DNS/API
hostname are needed for launch and the final browser/HTTPS check. This repository
contains no frontend implementation to update.
