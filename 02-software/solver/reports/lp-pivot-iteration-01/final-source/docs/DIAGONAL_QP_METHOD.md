# Diagonal equality QP iteration

This is a structure-specific improvement, not support for nonconvex QP, MIQP,
NLP or MINLP. The C++ implementation uses our sparse products and conjugate
gradient method; it does not call OSQP, HiGHS, NumPy or SciPy. Those packages
are used only in independent validation processes.

## Eligibility and scaling

Normalize maximization by negating the objective. The specialist requires a
strictly positive diagonal Hessian H, continuous variables, finite equality
rows A x = b, and box bounds l <= x <= u. It no longer excludes models above
512 variables. General constrained convex QPs retain the ADMM-PCG path.

Let D[j] = 1/sqrt(H[j,j]), and E[i] be the reciprocal maximum absolute entry
in row i of A D (one for an all-zero row). First whiten curvature. Then choose
s >= 1 from the largest absolute whitened cost, scaled RHS, and component of
zero projected onto the whitened box. With x = s D z, divide the objective by
s^2 and the already row-normalized equality by s:

```text
H_scaled = I
c_scaled = D c / s
A_scaled = E A D
b_scaled = E b / s
l_scaled = D^-1 l / s, u_scaled = D^-1 u / s
x_original = s D z
y_original = s E y_scaled
```

The multiplier conversion is essential: normalizing only the primal values
would invalidate original-model stationarity. No original coefficient is
dropped, and published QPLIB starting points are ignored.

For a scaled dual vector y, the Lagrangian minimizer is
z(y) = clip(-(c_scaled + A_scaled^T y), l_scaled, u_scaled).
Its dual gradient is A_scaled z(y) - b_scaled. A matrix-free Newton step uses
A_scaled diag(free variables) A_scaled^T plus a small diagonal regularizer,
Jacobi-preconditioned CG, and backtracking on the dual objective. Equality-row
redundancy is allowed but remains a numerical conditioning concern.

The specialist receives at most 2 s / 20% of the budget on small models, or
10 s / 50% on larger models. Unsuccessful attempts fall back to ADMM within
the original overall deadline. The existing 500-Newton-iteration cap remains.
No name-based dispatch or QPLIB-specific starting solution is used.

## Original-model acceptance and numerical bound

Original relative feasibility, projected stationarity and complementarity
must still each satisfy the requested tolerance (default 1e-7). For strictly
positive diagonal models, the checker now also requires relative dual gap
<= tolerance. This strengthens acceptance; no tolerance was loosened.

For any row multiplier y, let t[i] be the upper row endpoint when y[i] >= 0,
otherwise the lower endpoint. Terms with y[i] = 0 contribute zero even if the
endpoint is infinite. In minimization sense, define:

```text
d = c + A^T y
w[j] = clip(-d[j]/H[j,j], l[j], u[j])
dual_bound = offset - sum(y[i]*t[i]) + sum(0.5*H[j,j]*w[j]^2 + d[j]*w[j])
relative_gap = abs(objective_minimization - dual_bound) / (1 + abs(objective))
```

This is the separable Lagrangian minimum, not a solver estimate or an imported
reference objective. It remains finite for unbounded variable endpoints when
H is strictly positive; the old affine-tangent bound often became -infinity.
Nonfinite/wrong-shaped candidate vectors clear any previous acceptance flag.
General Hessians keep the prior tangent bound and KKT gate.

These are floating-point numerical checks, not interval-arithmetic proofs.
A tiny objective gap does not make an infeasible point acceptable. The checker
records absolute violations as well as normalized ones; coefficients/activities
around 1e11 can make small relative errors non-negligible in absolute units.

## Independent validation

`scripts/qp_certificate.py` independently parses original QPLIB coefficients,
recomputes primal/dual residuals and the diagonal bound without trusting the
C++ status, objective or reported residuals. Seven adversarial checker tests
include infeasibility, incorrect duals, nonfinite vectors, objective spoofing,
maximization, and a tiny-gradient / large-objective-error counterexample.

The 21 new generated tests contain 20 planted-KKT problems and one known
infeasible equality system. They cover 12 orders of curvature, large/small
magnitudes, nonzero costs/RHS/offsets, positive/negative bounds, fixed variables,
infinite endpoints, redundant rows and models above the old dimension cutoff.
They supplement the 230 previous generated cases, not replace them.

The public `qplib` comparison gate remains unchanged: the reference solver must
also complete optimally. A new, separately labeled `qplib_independent_kkt` group
reports candidate checks; diagonal bounds/gaps are separate fields. Reference
timeouts remain incomplete comparisons even when our candidate is certified.

## Background

Lagrangian dual bounds and KKT conditions follow the standard framework in
[Boyd and Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/).
The retained general ADMM comparison background is
[Stellato et al., OSQP (2020)](https://web.stanford.edu/~boyd/papers/osqp.html).
The scaling and separable bound formulas above are derived explicitly for this
implementation; no external solver code is incorporated into the C++ core.
