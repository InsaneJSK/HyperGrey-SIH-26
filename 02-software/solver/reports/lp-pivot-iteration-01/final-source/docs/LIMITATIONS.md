# Limitation register

This register describes V1. See [V2_LIMITATIONS.md](V2_LIMITATIONS.md) for the
current candidate; V1 entries are retained for traceability.

Severity: **critical** prevents a claim about the intended problem class;
**high** limits reliability or practical performance; **medium** limits tooling
or evidence. This register is part of the deliverable, not an optional disclaimer.

| ID | Severity | Current limitation / reproducer | Planned response |
| --- | --- | --- | --- |
| L-01 | Critical | LP/MILP are dense. `degen2` is materially slower than HiGHS. The 16M-cell guard limits individual dense allocations, not total memory. | Sparse revised simplex, basis factorization, memory accounting |
| L-02 | High | MILP rebuilds every LP from scratch. `enigma`, `stein27` time out; `flugpl` reaches its node limit despite finding the reference objective. | Basis warm starts, primal heuristics, cuts, better branching; preserve the same failure cases |
| L-03 | High | MIP bounds use floating-point dual solutions with a numerical margin. They are not interval-certified or exact proofs. | Stronger dual feasibility repair and validated bound computation |
| L-04 | High | LP unbounded status does not yet export/check a ray. Farkas infeasibility checks and LP optimality checks are numerical within tolerance. | Ray certificates, wider certificate regression suite, exact/interval validation where required |
| L-05 | High | QP is convex continuous only. Large Hessians must be symmetric diagonally dominant with nonnegative diagonal; other large PSD Hessians are rejected. Small Hessians use a conservative LDL check. | More general sparse PSD checks; explicitly define nonconvex scope with MRPL |
| L-06 | High | Constrained-QP first-order convergence is weak on QPLIB `9002`; currently reaches the time limit. | Scaling/preconditioning, stronger algorithm and stopping diagnostics, constrained-QP benchmark expansion |
| L-07 | High | QP optimality uses feasibility, projected stationarity and row complementarity tolerances; no reported global objective-error bound. Infeasibility/unboundedness generally terminate as limits rather than certificates. | Dual-gap/error bounds and homogeneous/certificate methods |
| L-08 | Critical | No GPU or multicore implementation, no GPU speedup evidence. | Hardware confirmation, profiling, then targeted implementation |
| L-09 | High | No million-variable demonstration or general industrial-scale LP/MILP success. Large tested QPs are box-constrained, not general industrial models. | Add progressively larger sparse cases after architectural changes |
| L-10 | Medium | MPS reader is a documented subset. Embedded-space names, multiple objective/free rows, multiple data sets, SOS, semivariable bounds and quadratic MPS are unsupported. Ambiguous negative upper bounds require explicit lower bounds. | Expand parser with independent cross-reader tests; continue rejecting unsupported features |
| L-11 | Medium | QPLIB reader accepts a restricted continuous quadratic/linear-or-box form. Input initial solutions are parsed but ignored. | Broader format support after solver-class support exists |
| L-12 | Medium | Benchmark sets are small, selected smoke/stress sets. MIPLIB cases are 3.0 historical cases, not the 2017 benchmark set. Mittelmann runs are pending. | Predeclare a broader selection including failures, avoid performance cherry-picking |
| L-13 | Medium | Short-run MinGW timers can read zero. Python process timings include startup/import time. Peak memory and repeated timing distributions are not collected. | High-resolution native timer, repeated runs, peak resident memory and fair timing protocol |
| L-14 | High | Demos are synthetic and use simplified linear mixing, capacity and convex cost assumptions. | Add literature-sourced case studies and validate with a domain expert |
| L-15 | Medium | Time limits are checked between numerical iterations (QP every 25); parsing, allocation and individual expensive steps can exceed the nominal limit. Harness has a separate process timeout. | End-to-end cancellation checks and resource budgets |
| L-16 | Medium | Toolchain tested locally is old MinGW GCC 6.3, Windows. CMake config exists but CMake was not available for local validation. | Modern compiler and cross-platform CI |

## Resolved findings retained as history

- **R-01:** Tiny row coefficients could cause a bounded LP to be called unbounded.
  Row normalization and a regression now cover this case.
- **R-02:** Initial results checked only primal feasibility. LP dual sign,
  stationarity and primal/dual gap checks now accompany a candidate optimum.
- **R-03:** `boeing2` and `stocfor1` hit 10,000 pivots under the original Bland-only
  pricing. Most-negative reduced-cost pricing with Bland fallback solved both.
  Original runs remain under `reports/phase1/run01` and `run02`.
- **R-04:** Undoing extreme row scaling amplified positive roundoff in zero dual
  multipliers. Projection onto the row dual sign constraint, followed by all
  residual/gap checks, fixed two generated regressions (97 and 113).
- **R-05:** HiGHS QP reference runs timed out on the large box-QP subset. The
  original attempts remain in `reports/phase3/run01`; OSQP provides the sparse
  reference comparison in subsequent runs. This is not a solver speedup claim.
- **R-06:** The default HiGHS LP reader filters some tiny Hessian coefficients
  in `9002`, changing the reference objective. Final QP comparisons instead use
  an independent Python QPLIB reader with no coefficient dropping, and report
  the export/reader discrepancy explicitly. Earlier `9002` export comparisons
  are diagnostic failures, not valid objective-quality measurements.
