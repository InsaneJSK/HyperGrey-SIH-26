# Guarded private pump-to-distance handoff

Iteration24 adds the separate optional [objective-only stage](PUMP_DISTANCE_STAGE.md)
before the first bound change. With that option off, this direct-handoff path
is unchanged. Stage/first-child captures and counters are reported separately;
`distance_reopt` continues to count branch LP work, not the extra parent stage.

`--pump-distance-reopt` is experimental and defaults off. It requires
`--pump-primal-reopt --pump-distance-diving --pump-guided-diving`.
It does nothing with the pump or heuristics disabled. CPU-local only.

`PumpDiveSeed` remains a checked point only. A separate `PumpPrivateBasis`
retains the basis from the exact projection whose point improved the seed.
Non-selected projections cannot overwrite it. A selected point without a
usable tagged basis clears stale basis state. No root/tree basis is imported.

The distance LP may have different auxiliaries from the pump projection.
The offered basis must pass the existing LP engine's exact canonical matrix,
mapping, equality/slack, column-count and bound-representation checks. Same
dimensions alone do not establish compatibility. Costs and RHS may differ;
the engine recomputes current primal values and reduced costs. It uses dual
simplex when dual feasible, primal simplex when only primal feasible, and
otherwise cold-starts. Repeated, invalid, artificial or singular bases cannot
qualify for a verified restart. Auxiliary-layout changes can correctly reject
a saved basis even if the original MILP and target point are unchanged.

Only verified optimal private LPs advance the private basis. A failed primary
branch leaves its parent's basis intact for the alternate. Distance objectives,
dual bounds, certificates, auxiliaries and basis state are stripped before a
candidate leaves the heuristic. The existing original-model absolute feasibility
and integrality checks decide whether a point can become a MILP incumbent.
Private infeasibility is never global infeasibility or a tree pruning proof.

The pump's five-second maximum and shared two-second dive slice are unchanged.
Retention, structure construction, canonicalization and solves consume those
existing budgets. These are cooperative clocks, not hard process containment.
Retaining an older best basis can retain another model-sized structure tag;
there is no new hard global memory cap.
There are no instance-name special cases or injected reference solutions.

JSON `distance_reopt` reports retained seed updates, offers, compatible/verified
seed restarts, and all private-distance reoptimization work. With
`--capture-feasibility`, a bounded first offered private model/basis is retained
for diagnostic replay. An offer is not an accepted warm start. Replay is run
outside measured MILP solves and cannot feed the solver.

Protocol, same-binary paired comparisons and final disposition are recorded in
`reports/milp-iteration-23`. All 27 public models are reused development cases,
not an unseen holdout or coverage of every MILP. LP savings alone do not prove
better MILP solutions or smaller optimality gaps.
