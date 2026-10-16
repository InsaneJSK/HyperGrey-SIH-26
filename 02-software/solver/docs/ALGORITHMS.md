# Implemented algorithms and numerical contract

Historical V1 description. For the current solver, start with
[V2 architecture](V2_ARCHITECTURE.md), [candidate repair](MILP_CANDIDATE_REPAIR.md),
[neighbourhood experiments](MILP_NEIGHBORHOOD_METHOD.md) and the
[current limitations](V2_LIMITATIONS.md). Statements below about missing
warm starts, sparse factorization or heuristics describe V1, not current V2.

## LP

The canonical model is minimize c^T x, with A x <= b and x >= 0. MPS variable
lower bounds are shifted, upper-only variables are reflected, free variables
are split into nonnegative differences, and finite upper bounds become rows.
Equalities/ranges become opposite/paired inequalities. Reconstruction returns
the original variables, objective sense and constant.

The core uses a dense two-phase tableau. Negative RHS rows receive artificial
variables; Phase I minimizes their sum. Phase II minimizes the actual cost.
Most-negative reduced-cost pricing is the default. A repeated basis switches
to Bland pricing; another repetition under that rule reports numerical_stall.
Basic variables are excluded from entering candidates.

Rows are divided by their largest absolute coefficient; the objective is
divided by its largest absolute coefficient. There is no column equilibration,
basis refactorization, sparse factorization or presolve. Default pivot tolerance
is 1e-9, with at most 10,000 pivots and a 30-second internal solve limit.

For a candidate optimum, the core reconstructs canonical dual multipliers y
with y <= 0 and checks c - A^T y >= 0. Tiny positive row-dual roundoff is projected
to zero, then the complete residual and objective-gap checks are performed.
Row residuals are divided by 1 + |b_i| + sum_j |a_ij*x_j|. Dual stationarity
uses 1 + |c_j| + sum_i |a_ij*y_i|. The gap is |c*x-b*y| divided by
1 + max(|c*x|, |b*y|). The validation threshold is 10 times the pivot tolerance.
Original-model primal feasibility is also checked after reconstruction.

LP infeasibility uses a numerical Farkas check: y <= 0, A^T y <= 0, b^T y > 0,
rechecked after undoing row scaling. An unverifiable candidate becomes a
numerical error. Unboundedness currently relies on the tableau ratio test and
does not export an independently verified ray. These are floating-point
checks, not exact proofs.

## MILP

The separate branch-and-bound driver reads integrality from MPS. Each node
solves an LP relaxation using our own LP core. It branches on the variable
furthest from an integer, selects the smallest normalized minimization bound,
and retains unresolved nodes when a numerical/time/resource limit occurs.
Maximization is internally negated and final bounds are restored to that sense.

LP-infeasible nodes are pruned only after the numerical Farkas check succeeds.
Integer-looking solutions are rounded and rechecked against original row and
variable bounds before becoming incumbents. Node lower bounds come from LP
dual objectives with a 100*tolerance*(1+|bound|) numerical margin. This is not
interval certification. The default integrality tolerance is 1e-7; relative
gap is (incumbent-bound)/(1+|incumbent|), default target 1e-6; node cap is 10,000.

No incumbent on timeout means no feasible integer solution was found, not that
the model is infeasible. `unbounded_relaxation` does not claim MILP unboundedness.
`gap_limit` means the requested numerical gap was reached; it is distinct from
exhausting the tree. Warm starts, cutting planes, strong branching, parallel
search and primal heuristics are not implemented.

## Convex QP

The model is minimize 0.5*x^T H*x + c^T*x + offset, with row and variable bounds.
Maximization is accepted only when negating the objective passes the convexity
check. Sparse lower-triangle Hessian entries are mirrored during products.

QPLIB's stored lower-triangle polynomial uses a factor of one half on the whole
quadratic expression. Off-diagonal file entries therefore contribute half their
listed value to each side of the symmetric Hessian; diagonal entries are used
unchanged. The independent reference reader uses the same published convention,
and the box-case results were also checked against official LP-format exports.

Large models pass a nonnegative diagonal-dominance sufficient PSD test. For
matrices of at most 200 variables, a conservative dense LDL check can accept
additional PSD cases. `unsupported_curvature` means the model was not accepted
by this implementation; it is not necessarily a proof of nonconvexity.

Box-only problems use accelerated projected gradient with step 1/L, where L is
the Hessian absolute-row-sum bound. Linear-constraint problems use projected
primal-dual iterations: project a dual step through the row-bound interval,
take a primal gradient step through the variable-bound box, and extrapolate
the primal iterate. Step sizes use conservative row/column-sum norm bounds.
There is no sophisticated preconditioning or convergence recovery.

Stopping checks are original feasibility, projected stationarity
|x-proj_box(x-(H*x+c+A^T*y))|/(1+|x|), and row multiplier/slack complementarity
scaled by 1+|objective|. Default tolerance is 1e-7, iteration cap 200,000. These
KKT residuals are not a rigorous bound on objective error. Supplied QPLIB starting
points are ignored: runs begin at zero projected onto variable bounds.

## Input and output limitations

- MPS: whitespace-compatible fixed/free records, one objective row, one RHS,
  range and bound set; L/G/E rows; LO/UP/FX/FR/MI/PL/BV/LI/UI bounds; integer
  markers. Some fixed-column conventions, SOS, semivariables, multiple data sets
  and quadratic sections are rejected. Negative upper bounds need an explicit
  lower bound to avoid implementation-dependent defaults.
- QPLIB: continuous quadratic objectives with box/linear constraints; no
  quadratic constraints, MIQP or general nonconvex optimization. Counts have
  resource caps and malformed/unsupported input fails explicitly.
- For limit/failure results, a returned QP iterate may be infeasible. A finite
  objective is not by itself evidence of a usable solution. Residual fields on
  LP results without a primal vector are not evidence of feasibility.
- The C++ APIs throw on invalid models. The CLI prints an error and exits 2 for
  parsing/argument errors, 1 for solver limits/failures, and 0 for optimal results
  or MILP gap_limit. JSON uses null for unavailable/non-finite numeric values.

Sources: [Netlib](https://netlib.org/lp/data/readme),
[QPLIB definition](https://qplib.zib.de/doc.html),
[QPLIB paper including format tables](https://pages.di.unipi.it/frangio/papers/QPLIB.pdf).
