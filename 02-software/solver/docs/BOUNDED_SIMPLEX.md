# Bounded dual simplex for MILP relaxations

`src/bounded_simplex.cpp` is an independently written LP engine used by
`--bounded-lp` (MILP) and `--lp-method bounded` (pure LP). It replaces the
relaxation algorithm only. MILP search, acceptance, repair, heuristics and all
proof rules are unchanged, and the existing sparse engine still decides any LP
this engine cannot verify.

## Why a second engine

The original sparse simplex canonicalizes each call into nonnegative
variables, adds one row per finite variable bound, recomputes every primal and
dual value on each pivot, and restarts from a cold phase one when its warm dual
simplex stalls or meets an infeasible child. Iteration 28 work data showed
tree LPs averaging about 2,300 pivots on misc07, 1,400 on pk1 and 6,800 on
danoint, so most of the 30-second budget went to relaxations.

## Formulation

For `row_lower <= A x <= row_upper`, `lower <= x <= upper`, the engine solves
`min c'x` subject to `A x - r = 0` with one logical `r_i` per row carrying the
row bounds. Every variable keeps its own bounds; a nonbasic variable sits at a
bound (or at zero if free). Branching and propagation therefore change only
bounds, and a child reuses its parent's basis statuses directly. New cut rows
extend a stored basis with basic logicals.

Rows and columns are scaled by powers of two (geometric passes), and the
objective by a power of two, so unscaling is exact.

## Algorithm

- Basis factorization: left-looking sparse LU (Gilbert-Peierls) with threshold
  partial pivoting and a sparsity tie-break, product-form updates, refactor
  after 64 updates or eta growth. Singular columns are replaced by logicals.
- Dual phase: dual steepest-edge pricing (Forrest-Goldfarb update), row-wise
  pivot-row computation, bound-flipping ratio test with Harris tolerances and a
  preference for large pivots. Boxed variables pass breakpoints by flipping.
- Dual infeasibility at a start is repaired by bound flips; a side without a
  finite bound receives a temporary artificial bound of 1e7.
- Small wrong-signed reduced costs left by Harris steps are removed by cost
  shifts. Cleanup restores the original costs and removes artificial bounds,
  then a primal phase (Devex pricing, Harris ratio test, entering-variable bound
  flips) restores optimality from the primal feasible basis.
- Tolerances are set per variable from original-space targets
  (`tolerance * (1 + |bound|)` for primal, cost-relative for dual), so column,
  row and cost scaling cannot hide an unscaled violation.
- A leaving row whose remaining violation is rounding-sized and cannot be
  repaired (no entering candidate, no verified infeasibility) is skipped until
  the next refactor; the final original-model check still judges the point.

## What is verified before a result is used

- Optimal: the unscaled point is checked on the ORIGINAL rows and the node
  bounds (absolute and scaled violation), dual feasibility and the relative
  primal-dual gap are recomputed from the original rows in extended precision,
  with the same acceptance thresholds as `solve_sparse_lp`.
- Infeasible: the final BTRAN row is used as a Farkas multiplier, normalized,
  and the interval of `y'(A x - r)` over the true variable and row bounds is
  evaluated on the original rows; it must exclude zero by a relative margin.
  Rays relying on artificial bounds or tiny coefficients on infinite bounds are
  rejected.
- Cutoff: when the objective of the current basis passes the incumbent, a
  Lagrangian bound valid for ANY multipliers is computed from the original rows
  in extended precision (`sum y_i * row side + sum d_j * bound side`); only if
  it reaches `incumbent + 200 * tolerance * (1 + |incumbent|)` does the node stop.
  The node bound itself is this same Lagrangian bound.

Any other outcome (numerical error, rejected ray, failed verification,
iteration limit) is reported as such; the MILP code then solves that LP with
the existing engine and its recovery path. Time limits are returned as limits.

## Tests

`tests/test_bounded_simplex.cpp` solves 3,000 random bounded LPs (fixed,
free, one-sided and boxed variables; ranged, equality, one-sided and free rows;
MIN and MAX; feasible, infeasible and unbounded cases) with both engines and
requires matching objectives, consistent infeasibility claims, reproducible
violations, valid safe bounds, warm/cold agreement after branching-style bound
changes and after an added cutting row, and correct cutoff behavior.
`scripts/check_bounded_lp.py` checks the MILP accounting of every run, and the
correctness gate runs the generated and retained MILP suites with the engine.

## Limits

- No presolve, no hypersparse solves, no parallelism; dense work vectors of
  row length are used per iteration.
- Unbounded LPs are reported without a verified ray; the existing engine is
  used when a certificate is needed.
- Bounds are numerical certificates in the project's sense, not exact rational
  proofs. The extended-precision recomputation and margins reduce, but do not
  eliminate, floating-point risk.
- Faster nodes grow the frontier. With the flag, an open-node memory guard
  (960 MiB estimate by default) stops the search with `node_limit` and the
  message `Open-node memory guard` instead of exhausting the process budget.
