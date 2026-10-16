# Next iteration — separate candidate generation from candidate repair

Retain the reproduced blend2 near-integer rejection and its exact fixing.
Keep repair optional, preserve frozen18/19, and never reinterpret a fixing-LP
bound as proof for its parent. Use the full report for all paired outcomes.

The new repair addresses a missing numerical recovery path. It does not solve
the problem of generating useful integer assignments when all current points
are substantially fractional. Lotsize and danoint's traces illustrate that
difference; simply adding more repair allowance cannot fix it.

The final repair wave's three no-point cases are lotsize, eil33-2 and danoint.
Keep rout as a reliability sentinel: its extra point in this wave involved zero
repairs and earlier runs differ. Blend2 must retain the new checked-point path,
but its roughly 13.6% proof gap is a separate unfinished target.

## Bounded next experiment

1. Use the retained pump/dive trajectories on the still-unsolved cases. Separate
   expensive LPs, failed fixings, repeated paths, very many fractional variables,
   near-feasible points and weak original-objective bounds. Include the now
   observed successful and failed runs of eil33-2/rout; do not cherry-pick only
   no-point executions or attribute shared-clock variation to a new algorithm.
2. Test one general feasibility-generation mechanism supported by those traces.
   Pump-guided diving remains a candidate because current dives discard pump
   fractional progress; however, a low integer distance is not evidence that
   its nearest fixing is feasible. Diagnose/reproduce that mechanism before
   implementing it, and keep it separate from changes to global proof bounds.
3. Preserve total and per-heuristic budgets, original row/bound/integrality
   checks, the numerical repair fixtures, MIN/MAX and exhaustive no-false-proof
   tests. Do not inject known optima/reference incumbents or add model-name rules.
4. Repeat equal-budget first-feasible comparisons on the targets and regression
   sentinels, then all 27 development models. Require original-model point
   validation, report first-point times, final objective/bound/gap and every
   failure. Only then predeclare new untouched cases before running them; the
   current 27 cannot be reused as fresh holdouts for tuning decisions.

## What "27/27 handled" still requires

A valid point with a large gap is not a completed optimality proof. For models
with incumbents but large gaps, diagnose relaxation strength and search
separately. A model correctly identified as infeasible has a different outcome
from a model where a time limit expires without a point. Keep those categories
explicit and state the time/node/resource envelope.

The suggested ten-iteration budget is a planning checkpoint, not a promise of
27/27 numerical completions within 30 seconds or all-public-MILP robustness.
Review progress after three focused iterations and revise the budget from
measured completion/checked-point/gap changes, not the number of features added.

Hard process time/memory containment, real MRPL/domain-expert validation,
installation and the final reproducible demo remain submission work. Historical
GPU QP results do not prove general GPU MILP performance. CPU work stays local;
no user upload or Kaggle run is needed for the next CPU experiment.
