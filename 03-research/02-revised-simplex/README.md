# 02-revised-simplex

Revised simplex and basis updates

## What this folder supports

Primal/dual revised simplex, bounded variables, hyper-sparse pivots and reusable basis representations.

**Problem-statement mapping:** PS-02, PS-06, PS-09 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/sparse_lp.cpp](../../04-software/solver/src/sparse_lp.cpp)
- [src/bounded_simplex.cpp](../../04-software/solver/src/bounded_simplex.cpp)
- [docs/BOUNDED_SIMPLEX.md](../../04-software/solver/docs/BOUNDED_SIMPLEX.md)

## Scope note

Current LP and node-relaxation work. Parallel simplex is a research direction, not an implemented claim.

## Sources (3; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2018 | Parallelizing the dual revised simplex method | Mathematical Programming Computation 10, 119-142 | [PDF](2018-parallelizing-the-dual-revised-simplex-method.pdf) / [note](2018-parallelizing-the-dual-revised-simplex-method.source.md) | [source](https://arxiv.org/abs/1503.01889) |
| 2015 | Novel update techniques for the revised simplex method | Computational Optimization and Applications 60, 587-608 | [PDF](2015-novel-update-techniques-for-the-revised-simplex-method.pdf) / [note](2015-novel-update-techniques-for-the-revised-simplex-method.source.md) | [source](https://webhomes.maths.ed.ac.uk/hall/HuHa12/) |
| 2005 | Hyper-sparsity in the revised simplex method and how to exploit it | Computational Optimization and Applications 32, 259-283 | [PDF](2005-hyper-sparsity-in-the-revised-simplex-method-and-how-to-exploit-it.pdf) / [note](2005-hyper-sparsity-in-the-revised-simplex-method-and-how-to-exploit-it.source.md) | [source](https://webhomes.maths.ed.ac.uk/hall/Publications.html) |

## Reading notes

- **dual-simplex:** Study dual-simplex pricing, suboptimization and the limits of intra-iteration versus multi-iteration parallelism.
- **basis-updates:** Compare product-form and Forrest-Tomlin basis updates for repeated sparse node relaxations.
- **hyper-sparsity:** Sparse inputs alone are insufficient: exploit sparse intermediate solve vectors and pricing operations.

[Back to the research index](../README.md)
