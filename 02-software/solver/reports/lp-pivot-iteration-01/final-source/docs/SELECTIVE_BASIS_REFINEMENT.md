# Selective basis checks and refinement-work telemetry

Iteration18 retains `--refine-basis` (checks every value computation) and adds
`--refine-basis --refine-at-checks` (checks at selected decision boundaries).
Both modes remain opt-in. The second flag requires the first; contradictory
options are rejected in the CLI and LP/MILP APIs.

The algorithm is the same guarded correction introduced in
[iteration17](SPARSE_BASIS_REFINEMENT.md): actual-basis residuals, long-double
accumulation, at most two correction solves per RHS, and finite strict residual
improvement before accepting a correction. Tolerances and final certificates
are unchanged. Shared LU, dense recovery, model bounds, cut/restart decisions
and resource allowances are not replaced or relaxed.

## Selected checks

Ordinary simplex iterations compute basic primal values and dual multipliers
without a residual scan in selective mode. Before an optimality candidate,
unbounded-ray candidate, nonfinite/primal-value rejection, or dual warm-basis
rejection, the engine checks/refines those values once for the current basis.
It recomputes reduced costs and re-evaluates the decision. It cannot simply
relabel an unchecked point optimal or reload the old inaccurate values.

A retry is not another pivot or another visit for cycle detection. The local
`checked` and `recorded` guards bound retries and preserve cycle accounting.
The LP clock is rechecked after repair. Existing primal/dual/Farkas/ray checks
still decide whether a certificate is valid numerically. A numerical stall or
failed pivot is not guaranteed to be repaired by this schedule. Pivot direction
solves are not themselves refined. This is not an exact rational proof method
or a universal ill-conditioning fix.

## Optional measurement

`--capture-refinement` enables `--capture-work` automatically for MILP. The C++
MILP API requires `capture_work` when `lp.capture_refinement` is true. It does
not turn on the numerical algorithm. Without refinement the counters are zero.

The existing `work.phases` each gain a `refinement` object, and `work.refinement`
holds the sum. Fields are RHS calls split into primal/dual, residual scans,
visited matrix entries, attempted/accepted corrections and elapsed seconds.
The times are **subsets** of existing phase time, not additional wall time to
add to the ledger. Compact-equality and reduced-bound retries retain their
spent counters. All MILP-visible sparse calls, including pump, dives, probes,
neighborhood, recovery and polishing, are attributed at their actual call site.

LP JSON retains the previous attempts/accepted fields and adds detailed
`basis_refinement_work` and `capture_refinement`. Detailed scans/time are
recorded only when capture is enabled. Counters do not measure FLOPs or provide
an operating-system resource sandbox. Instrumentation can perturb wall-clock
search boundaries; fixed-node parity and paired timing controls are required.

## Evidence boundary

The separately frozen Stage A profiler establishes fixed-node semantic parity
before the schedule change. Stage B repeats the original cold/warm numerical
fixture, transformed min/max models, certificate/interruption tests, generated
MILPs and independent public-result checks. See the
[iteration18 report](../reports/milp-iteration-18/REPORT.md) for all outcomes,
including failures, runtime variation and the promotion decision.

CPU runs remain local. A Kaggle notebook is not required for this work.
