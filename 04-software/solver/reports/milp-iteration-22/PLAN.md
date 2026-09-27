# Iteration 22 — guarded primal reoptimization inside the pump

Declared before public measurements. CPU local. Preserve frozen21 unchanged.

The bounded hypothesis is objective-changing pump LP overhead, not a new first
distance-dive seed basis. `--pump-primal-reopt` enables primal reoptimization
only inside pump projections. Exact canonical rows, variable mappings and
equality flags must match an immutable basis tag. Untagged initial root bases
retain legacy dual-only behavior. Compatible bases with dual feasibility use
dual simplex; otherwise primal-feasible bases use primal simplex. Neither
feasible, invalid, singular or incompatible bases fall back to the old cold
path under the same call budget. No projection proof bound/basis enters the
tree or the subsequent private distance model. New path defaults off.

Pump/dive/repair budgets, cuts, restarts and tolerance checks are unchanged.
Opt-in call accounting includes canonicalization in its existing time limit.
Record canonicalization/factorization/pricing time and Phase I pivots; refinement
remains in the existing work counters. These are overlapping diagnostic work
categories, not a fully exhaustive profiler. Retain the first actual primal
restart's model, input basis and exact structure (bounded, trace mode only).
Replay it after measurements, compare cold/dual-only/adaptive, independently
check returned points. No external incumbent feeds the solver.

Before measured comparisons: full correctness gate, transformed LP tests,
negative/free/unit/general domains, incompatible-matrix and index guards,
MIN/MAX, budgets, frozen21 disabled parity, no-pump/no-heuristics inertness.

SCREEN: misc07, lotsize, danoint, eil33-2, rout, blend2, p0201, gt2, pk1;
two alternating pairs each, 30s, 250000 nodes, gap1e-6. Same-binary distance
control vs distance+reoptimization candidate; detailed trace both.
The prior guided profile is historical context, not part of this paired trial.
WAVE: same two profiles across all 27 development models, one pair each,
30s, detailed trace off. All own solves sequential; references only afterwards.
No post-screen tuning or model-name rules. Keep every failure and adverse result.

Primary: independently checked solutions, terminal statuses, completions and
objective/gap regressions. Secondary: actual primal-path activations, LP work,
first-incumbent time and node throughput. Timing-driven outcomes when the path
does not run are not evidence for it. No best-of-profile union as a single run.
No default promotion merely for a screen gain. This is planning slot four of
ten, not a promise of 27/27 optimality or top-0.1% ranking.
