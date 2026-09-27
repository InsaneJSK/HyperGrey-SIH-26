# 05-presolve-propagation

Presolve and domain propagation

## What this folder supports

Bound tightening, substitution, formulation strengthening, postsolve reconstruction and safe parallel reductions.

**Problem-statement mapping:** PS-03, PS-06, PS-07 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/milp_v2.cpp](../../04-software/solver/src/milp_v2.cpp)
- [docs/V2_ARCHITECTURE.md](../../04-software/solver/docs/V2_ARCHITECTURE.md)

## Scope note

Includes both current propagation and possible stronger presolve; record each transformation and reconstruct the original model.

## Sources (3; 2 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2020 | Presolve Reductions in Mixed Integer Programming | INFORMS Journal on Computing 32(2), 473-506 | [note](2020-presolve-reductions-in-mixed-integer-programming.source.md) / reference only | [source](https://doi.org/10.1287/ijoc.2018.0857) |
| 2022 | PaPILO: A Parallel Presolving Library for Integer and Linear Programming with Multiprecision Support | arXiv preprint | [PDF](2022-papilo-a-parallel-presolving-library-for-integer-and-linear-programming-with-multiprecision-support.pdf) / [note](2022-papilo-a-parallel-presolving-library-for-integer-and-linear-programming-with-multiprecision-support.source.md) | [source](https://arxiv.org/abs/2206.10709) |
| 2024 | Certifying MIP-based Presolve Reductions for 0-1 Integer Linear Programs | arXiv preprint | [PDF](2024-certifying-mip-based-presolve-reductions-for-0-1-integer-linear-programs.pdf) / [note](2024-certifying-mip-based-presolve-reductions-for-0-1-integer-linear-programs.source.md) | [source](https://arxiv.org/abs/2401.09277) |

## Reading notes

- **presolve-reductions:** Taxonomy of safe single-row and multi-row reductions, coefficient strengthening and probing.
- **papilo:** Study transaction-based conflict handling and postsolve requirements when parallelizing presolve.
- **presolve-certification:** Provides a correctness framework for presolve transformations in binary integer models.

[Back to the research index](../README.md)
