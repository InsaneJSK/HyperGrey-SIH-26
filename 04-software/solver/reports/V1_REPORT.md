# V1 implementation and validation report

Prepared 2026-09-14, Asia/Calcutta. Tests span 2026-09-13/14 local time; raw
metadata uses UTC. This is the first version for the user's two-day deadline,
not completion of the full industrial solver ambition.

## Outcome

| Area | Implemented and tested | Result |
| --- | --- | --- |
| Build and C++ checks | LP, MPS, MILP, QP, invalid input, cycling, limits | Passed; no compiler warnings in final build log |
| Generated LP tests | 120 known primal/dual certificate cases, 60 with extreme row scaling | 120/120 passed |
| Generated MILP tests | 40 seven-variable binary models checked by exhaustive enumeration | 40/40 passed |
| Generated QP tests | 30 positive-definite QPs with planted KKT optima; half have linear constraints | 30/30 passed |
| Netlib LP | Declared 12-instance subset | 12/12 passed |
| Historical MIPLIB 3.0 | Four declared cases | 1/4 completed within limits; three incomplete |
| QPLIB | Two box QPs and one constrained QP | 2/3 passed; one incomplete |
| Industrial illustrations | Blending LP, production MILP, dispatch QP | All three solved to expected numerical results |

"Passed" requires the stated termination/verification checks, not merely a
finite objective. Dataset selections are small smoke/stress sets, not full
library coverage. Large box-QP success does not imply general large-scale LP,
MILP or constrained-QP performance.

## LP phase

The core now reads the declared MPS subset, transforms bounds and row senses,
scales rows/objective, solves a two-phase dense simplex problem, reconstructs
original variables and checks numerical primal/dual residuals and objective gap.
HiGHS independently parses the original MPS for reference solving and validation.

Passed instances: adlittle, afiro, blend, boeing2, degen2, kb2, sc105, sc205,
sc50a, sc50b, share2b, stocfor1. Objectives match HiGHS and the published Netlib
values under the declared tolerances.

The final `degen2` run has 444 constraint rows, 534 columns and 3,978 constraint
nonzeros. It took 2,196 pivots and about 7.66 seconds in our core versus about
0.016 seconds in HiGHS. This is direct evidence of a performance gap, not a
speedup. The Netlib source row count includes the objective row, whereas our
reported constraint count does not.

Earlier Bland-only runs hit 10,000 pivots on boeing2 and stocfor1. Pricing was
changed to most-negative reduced cost with Bland fallback on a repeated basis.
Both then passed. Earlier runs and generated dual-roundoff failures remain
under `phase1/` for traceability.

## MILP phase

Implemented own branch-and-bound around own LP solver, best-bound node selection,
fractional-variable branching, checked integer incumbents, numerical Farkas
checks for infeasible relaxations, and explicit bounds/gap/limits.

| Instance | V1 result | Incumbent | Reference optimum | Interpretation |
| --- | --- | ---: | ---: | --- |
| p0033 | gap_limit, 7,643 nodes, reported gap 0 | 3,089 | 3,089 | Completed to numerical tolerance |
| enigma | time_limit | None found | 0 | No feasible incumbent found within 15 seconds |
| flugpl | node_limit, 10,000 nodes | 1,201,500 | 1,201,500 | Incumbent matches reference; own remaining gap about 0.1748%, so not counted as completed |
| stein27 | time_limit | None found | 18 | No feasible incumbent found within 15 seconds |

These are historical MIPLIB **3.0** cases. No claim is made about the modern
MIPLIB 2017 benchmark set. The next bottlenecks are lack of LP warm starts,
primal heuristics, cutting planes and efficient search/factorization.

## QP phase

Implemented a continuous convex subset using sparse products: accelerated
projected gradient for box constraints, and projected primal-dual iterations for
linear constraints. Curvature checks are sufficient/conservative, and stopping
uses numerical KKT residuals. Published starting points are not used.

| QPLIB instance | Dimensions | V1 status | V1 objective | Reference result |
| --- | --- | --- | ---: | --- |
| 8792 | 15,129 variables; box constraints | optimal, 50 iterations | 3,593.5162939294105 | OSQP optimal, objective agreement about 1.5e-15 relative |
| 8991 | 14,400 variables; box constraints | optimal, 25 iterations | -0.0016678673619609666 | OSQP optimal, objective agreement about 1.6e-11 relative |
| 9002 | 2,890 variables; 1,649 linear rows | time_limit | Candidate iterate only | OSQP also reaches 15-second time limit; no validated reference optimum from this run |

The `9002` iterate is not a validated solution. Do not compare its candidate
objective with the unfinished reference iterate as an optimality error or use
their objective ordering to claim that one solver is better.

Reference correction: the default HiGHS reader of the official `9002` LP export
filters 92 small Hessian entries (largest difference about 9.93e-10). That is
material when variables are large. Final OSQP comparisons use an independent
Python reader of the **original QPLIB** data with no coefficient dropping;
HiGHS export discrepancies are still audited. The corrected run reproduces our
`9002` candidate objective from the original coefficients, but convergence
remains unresolved. Earlier reference attempts are retained as diagnostics.

## Demonstrations

| Demo | Interpretation | Result |
| --- | --- | --- |
| blending.lpmini | Linear cost/availability/sulfur mixing | 50 + 50 units, cost 5,000 |
| production.mps | Continuous production plus binary activation | Both machines active; 10 + 70 units, cost 420 |
| dispatch.qplib | Convex quadratic generation cost with demand balance | Approximately 33.3334 + 66.6666 units, cost 966.6666664 |

These cases demonstrate solver usage and mathematically stated assumptions.
They are not sourced/validated refinery or power-system deployments.

## Reproducibility and evidence

Final core validation directory: [v1-2026-09-14](v1-2026-09-14/).

- [Build and analytical test log](v1-2026-09-14/build.log)
- [Generated LP summary](v1-2026-09-14/generated-lp/summary.json)
- [Netlib report](v1-2026-09-14/netlib/REPORT.md) and [metadata](v1-2026-09-14/netlib/metadata.json)
- [MILP enumeration](v1-2026-09-14/milp/enumeration.json) and [dataset results](v1-2026-09-14/milp/results.json)
- [Final QP generated checks](v1-2026-09-14/qp-corrected-reference/generated.json) and [corrected-reference results](v1-2026-09-14/qp-corrected-reference/results.json)
- [Blending](v1-2026-09-14/blending.json), [production](v1-2026-09-14/production.json), [dispatch](v1-2026-09-14/dispatch.json)

The `qp/` subdirectory records the earlier reference route; the final QP evidence
is `qp-corrected-reference/`. The solver executable was unchanged between these
QP runs. Source/input hashes and per-instance raw JSON are preserved. See
[reproduction instructions](../docs/REPRODUCE.md) for commands and criteria.

Environment: Windows 11, processor identifier Intel64 Family 6 Model 154,
12 reported logical processors, MinGW GCC 6.3, Python 3.12.14. Core and reference
tests are sequential; core execution is single-threaded. Actual RAM/GPU were
not measured. User hardware targets are documented separately. Peak memory,
repeated performance samples and high-resolution native timing remain missing.

## What remains required by the PS

The [requirements matrix](../docs/PS_REQUIREMENTS.md) and
[limitation register](../docs/LIMITATIONS.md) track every currently known gap.
Highest priorities after this first version are:

1. MILP warm starts and heuristics; improve the preserved failed cases.
2. Constrained QP preconditioning/robustness, beginning with `9002`.
3. Sparse revised simplex/factorization to remove the LP/MILP dense bottleneck.
4. Broader modern MIPLIB and Mittelmann coverage, memory measurements and fair
   repeated comparisons; no Mittelmann set has been run yet.
5. GPU/multicore implementation and end-to-end evidence on confirmed hardware.
6. A literature-sourced industrial case and organizer clarification on numerical
   dependencies and convex-QP scope. The user confirms that the supplied PS's
   final dataset paragraph was already truncated. A web search did not recover
   a verified continuation; see [source verification](../docs/PS_SOURCE_CHECK.md).

This V1 provides three working solver paths and honest test evidence. It does
not satisfy the PS's general industrial-scale robustness/performance ambition,
nor demonstrate a sovereign commercial-solver replacement.
