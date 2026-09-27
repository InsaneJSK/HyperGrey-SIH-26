# 01-foundations-duality

Foundations, duality and optimality

## What this folder supports

LP/QP formulations, weak and strong duality, KKT conditions and the distinction between a feasible point and a proof of optimality.

**Problem-statement mapping:** PS-01, PS-02, PS-04, PS-15 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/solver.cpp](../../04-software/solver/src/solver.cpp)
- [src/qp.cpp](../../04-software/solver/src/qp.cpp)
- [docs/ALGORITHMS.md](../../04-software/solver/docs/ALGORITHMS.md)

## Scope note

Core mathematical reference; citations do not certify the implementation.

## Sources (3; 2 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2004 | Convex Optimization | Cambridge University Press | [note](2004-convex-optimization.source.md) / reference only | [source](https://web.stanford.edu/~boyd/cvxbook/) |
| 2009 | Geometry of Linear Programming | MIT OpenCourseWare 6.251J / 15.081, Recitation 3 | [PDF](2009-geometry-of-linear-programming.pdf) / [note](2009-geometry-of-linear-programming.source.md) | [source](https://ocw.mit.edu/courses/6-251j-introduction-to-mathematical-programming-fall-2009/resources/mit6_251jf09_rec03/) |
| 2009 | Duality Theory | MIT OpenCourseWare 6.251J / 15.081, Recitation 5 | [PDF](2009-duality-theory.pdf) / [note](2009-duality-theory.source.md) | [source](https://ocw.mit.edu/courses/6-251j-introduction-to-mathematical-programming-fall-2009/resources/mit6_251jf09_rec05/) |

## Reading notes

- **boyd-convex:** Chapters 4-5 and 9-11 support convex formulation, duality, KKT conditions and Newton/interior-point methods.
- **lp-geometry:** Supports bases, polyhedra and extreme-point reasoning behind revised simplex.
- **lp-duality:** Concise reference for primal/dual bounds and complementary slackness used in solution verification.

[Back to the research index](../README.md)
