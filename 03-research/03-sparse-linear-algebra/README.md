# 03-sparse-linear-algebra

Sparse linear algebra and preconditioning

## What this folder supports

Sparse products, LU fill, triangular solves, Krylov methods and preconditioners for the LP and QP engines.

**Problem-statement mapping:** PS-06, PS-09, PS-10 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/sparse_lp.cpp](../../04-software/solver/src/sparse_lp.cpp)
- [src/qp_dual_newton.cpp](../../04-software/solver/src/qp_dual_newton.cpp)
- [docs/SPARSE_BASIS_REFINEMENT.md](../../04-software/solver/docs/SPARSE_BASIS_REFINEMENT.md)

## Scope note

Algorithmic study only: external numerical packages are not proposed as replacements for the from-scratch core.

## Sources (3; 2 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 1994 | Templates for the Solution of Linear Systems: Building Blocks for Iterative Methods, Second Edition | SIAM / Netlib | [PDF](1994-templates-for-the-solution-of-linear-systems-building-blocks-for-iterative-methods-second-edition.pdf) / [note](1994-templates-for-the-solution-of-linear-systems-building-blocks-for-iterative-methods-second-edition.source.md) | [source](https://www.netlib.org/linalg/html_templates/Templates.html) |
| 2003 | Iterative Methods for Sparse Linear Systems, Second Edition | SIAM / author-hosted book | [note](2003-iterative-methods-for-sparse-linear-systems-second-edition.source.md) / reference only | [source](https://www-users.cse.umn.edu/~saad/books.html) |
| 2026 | UMFPACK User Guide | SuiteSparse official documentation | [PDF](2026-umfpack-user-guide.pdf) / [note](2026-umfpack-user-guide.source.md) | [source](https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/dev/UMFPACK/Doc/UMFPACK_UserGuide.pdf) |

## Reading notes

- **templates-linear-systems:** Reference for CG, GMRES, stopping criteria and preconditioners used in sparse QP linear solves.
- **saad-iterative:** Detailed Krylov, preconditioning and sparse storage reference for difficult QP/Newton systems.
- **umfpack-guide:** Understand symbolic/numeric sparse LU, pivot control, fill growth and numerical diagnostics.

[Back to the research index](../README.md)
