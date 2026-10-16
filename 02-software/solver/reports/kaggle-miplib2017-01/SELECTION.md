# MIPLIB 2017 benchmark sweep, declared before any run

18 September 2026. Run the COMPLETE MIPLIB 2017 benchmark set as listed by
`https://miplib.zib.de/downloads/benchmark-v2.test` (240 instances). There is
no size filter and no hand-picking, so the set cannot be biased toward models
this solver happens to handle. Every instance that downloads is attempted and
every outcome is reported, including crashes, memory stops and time limits.

Budget per instance: 60 s solver wall clock, 250,000,000 node limit, 1e-6
relative gap, 90 s external watchdog, 6 GB address-space cap. An independent
HiGHS 1.12.0 run with a 60 s limit follows each solve on the same machine and
checks any returned point against the original model.

Profile: the iteration 31 candidate flags without the capture/diagnostic flags,
which only control recorded telemetry and would inflate the output size.

Environment: a Kaggle CPU session (about 4 vCPU, 30 GB RAM), three concurrent
worker processes. Consequences, stated before the run: wall-clock timings are
NOT comparable to the serial local measurements and support no speed claim.
Only outcomes at a fixed budget (status, objective, bound, gap, nodes) and the
independent checks are evidence. The local machine has no NVIDIA GPU, so GPU
work needs this environment regardless.

Published optimal values are not given to the solver; HiGHS results are used
only to validate returned points and to describe the instance's difficulty.
