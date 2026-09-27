# 04-numerics-certificates

Numerical stability and trustworthy certificates

## What this folder supports

Scaling, residual checks, iterative refinement, safe pruning and exact-versus-tolerance-based verification.

**Problem-statement mapping:** PS-09, PS-15 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/bounded_simplex.cpp](../../04-software/solver/src/bounded_simplex.cpp)
- [docs/PRIMAL_RATIO_STABILITY.md](../../04-software/solver/docs/PRIMAL_RATIO_STABILITY.md)
- [docs/PRIVATE_DUAL_CERTIFICATE.md](../../04-software/solver/docs/PRIVATE_DUAL_CERTIFICATE.md)
- [docs/MILP_BINARY_PROOF.md](../../04-software/solver/docs/MILP_BINARY_PROOF.md)

## Scope note

General exact rational solving and verified cut certificates are future work; restricted exact binary checks do not establish general exactness.

## Sources (5; 4 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2016 | Iterative Refinement for Linear Programming | INFORMS Journal on Computing 28(3), 449-464 | [PDF](2016-iterative-refinement-for-linear-programming.pdf) / [note](2016-iterative-refinement-for-linear-programming.source.md) | [source](https://doi.org/10.1287/ijoc.2016.0692) |
| 2023 | Combining Precision Boosting with LP Iterative Refinement for Exact Linear Optimization | arXiv preprint | [PDF](2023-combining-precision-boosting-with-lp-iterative-refinement-for-exact-linear-optimization.pdf) / [note](2023-combining-precision-boosting-with-lp-iterative-refinement-for-exact-linear-optimization.source.md) | [source](https://arxiv.org/abs/2311.08037) |
| 2025 | Analyzing the numerical correctness of branch-and-bound decisions for mixed-integer programming | CPAIOR 2025; arXiv author version | [PDF](2025-analyzing-the-numerical-correctness-of-branch-and-bound-decisions-for-mixed-integer-programming.pdf) / [note](2025-analyzing-the-numerical-correctness-of-branch-and-bound-decisions-for-mixed-integer-programming.source.md) | [source](https://arxiv.org/abs/2412.14710) |
| 2021 | A Computational Status Update for Exact Rational Mixed Integer Programming | IPCO 2021; arXiv author report | [PDF](2021-a-computational-status-update-for-exact-rational-mixed-integer-programming.pdf) / [note](2021-a-computational-status-update-for-exact-rational-mixed-integer-programming.source.md) | [source](https://arxiv.org/abs/2101.09141) |
| 2026 | Tolerances and User-Scaling | Gurobi Optimizer Reference Manual | [note](2026-tolerances-and-user-scaling.source.md) / reference only | [source](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/tolerances_scaling.html) |

## Reading notes

- **lp-refinement:** Separates high-accuracy LP refinement from merely reducing a basis-system residual.
- **precision-boosting:** Research path for fallback precision when floating-point LP refinement cannot recover a trustworthy answer.
- **branch-numerics:** Audit incumbent acceptance, infeasibility declarations and bound pruning independently.
- **exact-mip:** Explains the extra machinery needed for exact MIP, including rational LP solves and verifiable certificates.
- **gurobi-numerics:** Use units, coefficient ranges and original-model residuals to diagnose scaling-dependent feasibility.

[Back to the research index](../README.md)
