# Development phases and completion gates

## Phase 0: original prototype

Built a dense LP correctness baseline, text CLI, tiny analytical tests and a
synthetic blending model. No public dataset comparison at that stage.

## Phase 1: LP validation and Netlib

Implemented sparse-input MPS parsing, bound/row standardization and reconstruction,
row/objective scaling, dual residual/gap validation, resource/time limits, pricing
improvements and benchmark scripts. Added 120 deterministic LPs with known
primal/dual certificates, including 60 with row multipliers from 1e-10 to 1e10.

The declared 12-instance Netlib subset passed against original MPS independently
read by HiGHS, published objectives and solution feasibility checks. Original
failed runs are preserved; this phase's completion means its small-set gate
passed, not that industrial-scale LP is complete.

## Phase 2: MILP baseline and historical MIPLIB

Implemented best-bound branch-and-bound, most-fractional branching, bound
propagation by branching, integer rounding checks, incumbent/best-bound/gap
reporting, node/time limits and numerical Farkas checks before LP-infeasible
node pruning. No cuts, warm starts, general presolve or primal heuristics.

Forty bounded binary problems matched exhaustive enumeration. A mixed continuous
production example is also exercised. The four-case historical MIPLIB run has
one certified-to-tolerance completion and three limit outcomes. This phase is
**implemented and assessed, with performance gate failures still open**.

## Phase 3: convex QP baseline and QPLIB

Implemented a restricted QPLIB reader, sparse Hessian products, conservative
curvature checks, accelerated projected gradient for box-only models and
projected primal-dual iterations for linear constraints. Thirty generated
positive-definite QPs with planted optima/KKT points passed. Two large box QPs
pass independent OSQP comparisons; one constrained case reaches its time limit.

This phase is **implemented and assessed for a limited subset**. General
constrained-QP robustness and broader PSD handling remain open.

## Phase 4: first-version consolidation

Rebuild the final source, rerun analytical/generated/dataset checks sequentially,
exercise all three demos, capture immutable reports, and map every PS obligation
to implemented evidence or remaining work. See the V1 report for final-run paths.

## Next iteration after V1

1. Recover useful MILP incumbents earlier; improve `enigma`, `stein27`, `flugpl`
   without removing them from reports.
2. Improve constrained QP on `9002`; add non-diagonally-dominant PSD cases.
3. Replace the LP dense path with sparse revised simplex and warm starts.
4. Broaden to MIPLIB 2017 and a declared Mittelmann selection, gather memory and
   repeatable performance statistics.
5. Confirm organizer decisions/hardware and implement measurable GPU/multicore
   work; acquire a literature-sourced industrial case.
