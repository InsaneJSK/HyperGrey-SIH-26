# Next bounded mechanism: the first cold private distance LP

Iteration22's retained LP replays establish that a compatible primal basis can
avoid a costly cold solve after an objective change. The repeated screen also
finds checked danoint solutions and a better rout objective. This is progress
in first feasibility, not closure of their optimality gaps. Consult the final
wave ledger for all outcomes before selecting an experimental profile.

Lotsize's candidate pump seed reaches nearest-integer distance about 0.18936,
but its subsequent distance dive makes one LP call and obtains zero verified
points in both screen repeats. This identifies a concrete remaining cold-start
bottleneck. Misc07 still has no point in either profile's screen; improving
that case remains an explicit regression target, not an assumed benefit.

The full wave also exposes a quality regression: mas74 returns about 13588.56
with reoptimization versus control's 12914.44. The primal path runs on that
case. Reaching a feasible point sooner is not enough if its integer assignment
is worse and the remaining search cannot recover. Add mas74 as a repeated
quality guard; do not claim uniformly better solutions or promote this flag
as an unconditional default.

Next experiment, without more heuristic time or model-name rules:

1. Retain a separately typed private basis/structure when the pump records its
   best checked fractional point. Keep the public point-only seed and all tree
   proof state separate. A last-iteration basis is not automatically the basis
   associated with the retained best point.
2. At the first distance LP, compare exact canonical structure, mappings,
   equality/slack semantics, finite-bound orientation and auxiliary layout.
   Pump and dive auxiliary models can differ even with equal dimensions.
   Reject incompatible structures and use the existing cold path.
3. Re-evaluate the current objective/RHS and basis feasibility; choose a valid
   primal or dual restart only after those checks. Tightened dive bounds can
   invalidate the seed basis. Failed primary branches must not corrupt the
   retained parent basis used for an alternate branch.
4. Continue stripping private objectives, dual bounds, proof statuses and
   auxiliary values at the heuristic boundary. Verify accepted points against
   original rows/bounds/integrality at the unchanged absolute tolerance.
5. Gate with MIN/MAX, negative/free/general-integer bounds, changing auxiliary
   layouts, empty integer domains, invalid/duplicate/singular bases, resource
   limits and disabled-option parity. Then predeclare repeated lotsize/misc07
   tests plus danoint/rout/eil33-2/blend2/p0201/mas74 protections and the full wave.

If compatible reuse does not help a case, record that result rather than
silently increasing budgets. Missing feasible points and large remaining proof
gaps are different problems; branch/bound work still needs its own experiment.

Iteration22 is the fourth slot of the earlier ten-iteration planning budget.
Six slots remain in that plan, not six guaranteed steps to 27/27 completion.
One model in this development set is known infeasible; it should return a
correct terminal status, not a fabricated solution. Neither 27/27 here nor any
fixed number of iterations would prove coverage of every public MILP.

All CPU work stays local. Keep Kaggle separate and use it only for actual GPU
evidence. Real refinery/domain validation, hard resource containment, clean
submission packaging and unseen-model validation remain separate requirements.
No defensible competition-percentile prediction follows from these experiments.
