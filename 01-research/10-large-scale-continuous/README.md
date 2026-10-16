# 10-large-scale-continuous

Large-scale first-order and interior-point methods

## What this folder supports

PDHG restarts, interior-point systems and infeasibility detection for large sparse continuous models.

**Problem-statement mapping:** PS-02, PS-04, PS-10 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/sparse_lp.cpp](../../02-software/solver/src/sparse_lp.cpp)
- [src/accelerated_qp.cpp](../../02-software/solver/src/accelerated_qp.cpp)
- [docs/V2_REMAINING.md](../../02-software/solver/docs/V2_REMAINING.md)

## Scope note

PDLP and a general interior-point engine are research directions, not existing HyperGrey capabilities.

## Sources (4; 4 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2025 | PDLP: A Practical First-Order Method for Large-Scale Linear Programming | arXiv preprint | [PDF](2025-pdlp-a-practical-first-order-method-for-large-scale-linear-programming.pdf) / [note](2025-pdlp-a-practical-first-order-method-for-large-scale-linear-programming.source.md) | [source](https://arxiv.org/abs/2501.07018) |
| 2021 | Faster First-Order Primal-Dual Methods for Linear Programming using Restarts and Sharpness | arXiv preprint | [PDF](2021-faster-first-order-primal-dual-methods-for-linear-programming-using-restarts-and-sharpness.pdf) / [note](2021-faster-first-order-primal-dual-methods-for-linear-programming-using-restarts-and-sharpness.source.md) | [source](https://arxiv.org/abs/2105.12715) |
| 2012 | Interior Point Methods 25 Years Later | European Journal of Operational Research 218(3), 587-601 | [PDF](2012-interior-point-methods-25-years-later.pdf) / [note](2012-interior-point-methods-25-years-later.source.md) | [source](https://doi.org/10.1016/j.ejor.2011.09.017) |
| 2013 | Conic Optimization via Operator Splitting and Homogeneous Self-Dual Embedding | arXiv author preprint | [PDF](2013-conic-optimization-via-operator-splitting-and-homogeneous-self-dual-embedding.pdf) / [note](2013-conic-optimization-via-operator-splitting-and-homogeneous-self-dual-embedding.source.md) | [source](https://arxiv.org/abs/1312.3039) |

## Reading notes

- **pdlp:** Large sparse LP roadmap: adaptive PDHG, scaling, restarts, feasibility polishing and multithreading.
- **pdhg-restarts:** Theoretical basis for restart criteria and linear convergence under LP sharpness.
- **ipm-survey:** Alternative continuous-solver architecture, sparse Newton systems and matrix-free interior-point methods.
- **conic-splitting:** Shows how a first-order solver can return primal/dual points or infeasibility/unboundedness certificates.

[Back to the research index](../README.md)
