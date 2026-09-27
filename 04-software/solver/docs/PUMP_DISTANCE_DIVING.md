# Private distance-objective diving

`--pump-distance-diving --pump-guided-diving` changes only the first eligible
pump-seeded heuristic dive. Both options are experimental and default off.
No pump/no heuristics means no distance dive.
With presolve disabled, an empty integer interval makes this private heuristic
ineligible; the original-model tree still decides infeasibility. The final
guard fixes a reproduced exception without introducing a new pruning rule.

The private LP minimizes the sum of absolute integer-variable deviations from
the rounded retained seed. If the whole variable domain lies on one side of its
target, the contribution is linear (including its constant offset); otherwise
an auxiliary nonnegative variable and two inequalities express absolute value.
Continuous variables remain free within their original/node bounds and rows.
The original MAX/MIN objective never enters this private distance objective.

Construction and solves spend the unchanged shared dive time slice. There is
no extra step budget, restart change or reference solution injection. Private
warm starts remain private and the failed primary branch cannot overwrite the
parent basis used by the alternate. Root bases are not imported. Pump bases
are not imported by default; the separately enabled, exact-structure-guarded
[private handoff](PUMP_DISTANCE_REOPT.md) is the iteration23 experiment.
Only verified optimal private-LP primal points enter the candidate path;
auxiliaries, objectives, dual bounds, certificates and bases are stripped.
Candidate acceptance recomputes the original objective and checks original
absolute row/bound violation and integrality, exactly as before. Distance-LP
infeasibility is never global MILP infeasibility or a pruning certificate.

The rounded target remains fixed during the dive. Tightened bounds may require
more distance, and a smaller L1 distance does not imply integer feasibility.
Telemetry separately reports nearest-integer and fixed-target distances.
Samples are bounded to eight dives; optional existing feasibility traces carry
bounded points. Independent checkers verify retained metrics; this telemetry is
not an exact LP/MILP certificate. See the frozen iteration21 report for outcomes.

Iteration21 is mixed: repeated eil33-2/rout gains coexist with a lost misc07
solution and continued lotsize/danoint failures. Keep the flag off by default.
The report separates the measured binary from the final, independently retested
presolve-off guard. The 86 earlier timings were not rerun on that patched binary.
