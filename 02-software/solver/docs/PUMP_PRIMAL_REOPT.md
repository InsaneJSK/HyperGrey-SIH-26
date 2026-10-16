# Private pump reoptimization (experimental)

`--pump-primal-reopt` is optional and defaults off. It affects only the
feasibility pump's objective-changing projection LPs. It does not alter tree
relaxations, exact integer-fixing solves, the private distance dive, tolerances,
cut policy, or the shared heuristic budgets. CPU-local; no Kaggle needed.

The pump already carried the preceding projection basis. Previously every
warm attempt used dual simplex: a changed objective could invalidate reduced
costs and trigger a fresh Phase I even with a primal-feasible basis.

The new path retains an immutable, exact canonical structure alongside bases
created by an enabled call: ordered matrix rows, variable mapping, equality
flags, column count and compact-equality mode. Costs and RHS are allowed to
change; same dimensions alone do not suffice. It rejects different structures,
reduced-bound representations, repeated/out-of-range/artificial columns and
singular factorizations. Untagged initial root bases keep dual-only behavior;
they cannot trigger the new primal restart.

For a compatible tagged basis, recompute primal values and reduced costs for
the current model, applying existing residual corrections when enabled. Prefer
dual simplex when dual feasible. Otherwise use primal simplex only if primal
feasible. Neither-feasible bases use the existing cold fallback. Final scaled
primal/dual/gap checks are unchanged; pump candidates still need original-model
absolute feasibility and MILP integrality checks before acceptance. These are
numerical checks, not general exact proof certificates.

No projection objective or dual bound is exported to the search tree or distance
dive. By default no projection basis is exported either. The separately enabled
[private distance handoff](PUMP_DISTANCE_REOPT.md) may offer a separately typed,
guarded basis to the private dive, never to tree proof state. `PumpDiveSeed`
still carries only a checked point.
The low-level `Options.primal_warm_start` is for LP tests/replays; `solve_milp`
rejects setting that generic option, directing callers to the private flag.

Enabled-call time includes canonicalization. The same remaining pump slice
caps the call; this is cooperative accounting, not hard process containment.
Telemetry reports canonicalization, factorization and pricing seconds, Phase I
pivots, compatible/rejected basis counts, primal/dual starts and verified warm
outcomes. Refinement remains in existing work telemetry. It is not a complete
wall-time decomposition. Compact fallback can count two LP calls per projection.

With `--capture-feasibility`, retain at most the first actual primal-restart
model and input basis, capped at 10,000 columns, 20,000 rows and 200,000 original
nonzeros. Its exact canonical structure is also retained. Diagnostic replay
uses the raw ordered model and input basis; independent MPS validation uses an
equivalent formulation. Neither replay nor a reference solution feeds the solver.

Iteration22's protocol/evidence lives in `reports/milp-iteration-22`. All 27
models are development data. A faster LP replay is not by itself better MILP
coverage or a smaller optimality gap. The initial cold distance-dive LP is a
separate bottleneck; this flag alone does not reuse a pump basis there.
