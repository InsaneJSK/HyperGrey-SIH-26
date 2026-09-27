# 09-convex-quadratic-programming

Convex QP and operator splitting

## What this folder supports

ADMM, projected/proximal methods, semidefinite Hessians and primal/dual stopping conditions.

**Problem-statement mapping:** PS-04, PS-09 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/qp.cpp](../../04-software/solver/src/qp.cpp)
- [src/qp_admm.cpp](../../04-software/solver/src/qp_admm.cpp)
- [src/qp_dual_newton.cpp](../../04-software/solver/src/qp_dual_newton.cpp)
- [docs/DIAGONAL_QP_METHOD.md](../../04-software/solver/docs/DIAGONAL_QP_METHOD.md)

## Scope note

Continuous convex QP is the relevant scope; MIQP, nonconvex QP and nonlinear constraints require additional algorithms.

## Sources (4; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2020 | OSQP: An Operator Splitting Solver for Quadratic Programs | Mathematical Programming Computation 12, 637-672 | [PDF](2020-osqp-an-operator-splitting-solver-for-quadratic-programs.pdf) / [note](2020-osqp-an-operator-splitting-solver-for-quadratic-programs.source.md) | [source](https://web.stanford.edu/~boyd/papers/osqp.html) |
| 2014 | Proximal Algorithms | Foundations and Trends in Optimization 1(3), 123-231 | [PDF](2014-proximal-algorithms.pdf) / [note](2014-proximal-algorithms.source.md) | [source](https://web.stanford.edu/~boyd/papers/prox_algs.html) |
| 2026 | OSQP solver documentation: The solver | Official algorithm documentation | [note](2026-osqp-solver-documentation-the-solver.source.md) / reference only | [source](https://osqp.org/docs/solver/index.html) |
| 2011 | Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers | Foundations and Trends in Machine Learning 3(1), 1-122 | [PDF](2011-distributed-optimization-and-statistical-learning-via-the-alternating-direction-method-of-multipliers.pdf) / [note](2011-distributed-optimization-and-statistical-learning-via-the-alternating-direction-method-of-multipliers.source.md) | [source](https://web.stanford.edu/~boyd/papers/admm_distr_stats.html) |

## Reading notes

- **osqp:** Reference for ADMM QP updates, scaling, stopping residuals, infeasibility tests and solution polishing.
- **proximal-algorithms:** Provides projection/proximal interpretations and convergence assumptions for box-QP and splitting methods.
- **osqp-algorithm-docs:** Practical reference for primal/dual residual definitions, infeasibility certificates and polishing.
- **admm-foundations:** Mathematical foundation for ADMM updates, residual balancing and convergence requirements.

[Back to the research index](../README.md)
