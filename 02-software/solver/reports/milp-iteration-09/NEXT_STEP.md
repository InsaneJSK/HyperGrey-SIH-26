# Next bounded investigation — not yet implemented

The 180s paired result shows that compact equations alone do not materially
close Binkar's gap. Do not multiply strategy flags and call that progress.

One concrete LP-size lead remains: the compact root still has 3342 canonical
rows after ordinary covers. Those comprise 1016 equations, 10 original
inequalities, 18 retained cuts and 2298 variable upper-bound rows. Binkar's
2128 continuous columns originally have no finite upper bounds; propagation
derives finite upper bounds which then become extra LP rows.

Investigate whether redundant, propagation-derived continuous upper-bound
rows can be safely omitted from selected LP relaxations while retaining all
original constraints, all user-specified domains and all integer branch
decisions. This is a hypothesis, not a proven speedup or implemented feature.
Bound provenance must be explicit; arbitrary original upper bounds cannot
be removed. An unbounded relaxed LP must not become a false unboundedness
claim for a more restricted original model. Original feasibility gates and
valid global bounds must remain intact in warm, cold, repair and heuristic
sub-solves. Test min/max, finite original bounds, free columns, infeasible and
unbounded cases before any public timing.

If that screen is useful, retain the established incumbent-search phase and
compare at equal budgets with varied order/repeats. Stronger general cuts and
bound progress still need work independently of LP speed. The completed 600s
attempt in REPORT.md should inform whether this is a good next priority.

No new user file, GPU or Kaggle run is required for this investigation.
