# Focused Kaggle MILP return — audited

14 September 2026. The notebook completed successfully on Kaggle CPU. The
returned archive matches source snapshot
`a200a445026c9d27487fc69087b8765cd161aa22e9b4f95ee1e848d6ad3ee591`.
All 140 packaged files and 71 runtime source hashes match; CMake configuration
was CPU-only. Hardware metadata reports two physical / four logical CPUs,
33,659,383,808 bytes RAM and Python 3.12.13 / GCC 11.4.0. No GPU performance
claim is made or needed for this experiment.

All three CTest groups and all 160 generated binary/mixed checks passed.
The four hard-case incumbents were freshly rechecked locally with HiGHS 1.12's
independent original-MPS reader, without a new optimization run. All are within
the unchanged 1e-7 absolute feasibility/integrality acceptance tolerance.
The archive, submitted source, notebook, raw logs and independent checks are
preserved here. `AUDIT.json` contains exact hashes and machine-readable results.

## Same-budget strategy comparison

Every run requested 180 seconds, 250,000 nodes and gap tolerance 1e-6. All
objectives below are minimization; lower is better. These are single runs,
with alternating strategy order by model, not a repeated performance study.

| Model | Current fractionality strategy | Experimental reliability strategy |
| --- | --- | --- |
| markshare_4_0 | Objective approximately 5; gap 83.33%; 250,000 nodes; node limit at 164.17 s | Objective approximately 7; gap 87.50%; 224,488 nodes; time limit at 180.04 s |
| blend2 | No incumbent; bound 7.468466; LP iteration limit at 41.27 s / 3,762 nodes | No incumbent; bound 7.546468; LP iteration limit at 53.92 s / 3,399 nodes |
| binkar10_1 | Objective 7297.320029; bound 6665.380419; gap 8.6587%; 5,749 nodes / 180.02 s | Same objective; bound 6671.539533; gap 8.5743%; 3,980 nodes / 180.02 s |

Reliability branching is **not promoted to default**. It improves the
binkar bound slightly, but the longer markshare run reverses the short local
ranking: the established strategy produces the better final incumbent.
Reliability's explicit markshare probing costs only 0.175 seconds, but its
search performs about 41.5 LP iterations per node versus about 33.7 for the
control; the entire changed search path matters, not just probe overhead.

The independent reference finishes blend2 optimally at 7.598985. It times out
on markshare with incumbent 3 and on binkar with incumbent 6746.760023. Those
two reference incumbents are not known optima from these runs. None of our six
hard runs completes an optimality proof. The original proof gaps remain open.

## What the longer run exposed

### blend2 stops at an internal LP limit, not at 180 seconds

Both returned raw messages report `iteration_limit` and an unchecked/incomplete
LP relaxation. The archived source defaults `Options::iteration_limit` to
10,000 (`include/solver.hpp`); no command overrides it. `src/sparse_lp.cpp`
returns when that cap is reached, and `src/milp_v2.cpp` requeues that tree node
and terminates the solve when its LP does not return a verified optimum.
The optional dense recovery currently covers numerical errors/stalls, not an
iteration-limit result.

The 10,000 value is a **per-relaxation** limit, not the aggregate `lp_iterations`
field in the MILP output. The 250-iteration trial-probe limit is separate and
cannot directly terminate the tree search. A stop on one actual tree LP explains
why blend2 leaves 126-139 seconds of the requested solve budget unused.

This identifies the termination mechanism, not why the particular LP needs so
many pivots. The failing relaxation/basis must be captured to distinguish slow
convergence, degeneracy, numerical trouble or cycling. Simply increasing all
limits would not establish that the underlying problem is fixed.

### binkar does not improve its first incumbent

Both strategies find 7297.320029 at about 14.3 seconds, then record no further
incumbent improvement through 180 seconds. The trace directly supports this;
the experiment did not merely miss a final objective change.

The earlier local 15-second result 7127.780038 was not reproduced. Its root
path retained 15 cuts after one rollback and used two pump projections/one
restart; Kaggle retains 18 cuts, no rollback, and one pump projection. Thus
the different budgets/root states are observable, and more allotted time does
not guarantee the same heuristic trajectory. These data suggest investigating
incumbent-improvement/restart policy, not claiming a new binkar speedup.

## Next bounded iteration

1. Capture failing tree relaxations and add bounded LP recovery/retry under the
   remaining global deadline. Keep unresolved nodes and valid parent bounds;
   never treat a limit or numerical failure as proof of infeasibility.
2. Add a tested incumbent-improvement mechanism after the first feasible MILP
   solution, with explicit time budgets and the unchanged original-model checks.
3. Compare the resulting configurations on these same models before broadening
   claims. Keep fractionality as the established default for now.

No numerical core or default changed during this audit. There is no need to
rerun this unchanged notebook. The result confirms that the Kaggle workflow
works, not that all hard MILP instances are solved. Industrial validation,
broader benchmark coverage and final submission evidence remain open.
