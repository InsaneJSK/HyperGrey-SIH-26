# 06-branch-bound-search

Branch-and-bound and search strategies

## What this folder supports

Relaxation bounds, reliability branching, node selection, conflict reasoning and modular solver architecture.

**Problem-statement mapping:** PS-03, PS-05, PS-10 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/milp_v2.cpp](../../04-software/solver/src/milp_v2.cpp)
- [docs/MILP_FRONTIER.md](../../04-software/solver/docs/MILP_FRONTIER.md)
- [docs/MILP_WORK_BUDGETS.md](../../04-software/solver/docs/MILP_WORK_BUDGETS.md)

## Scope note

SCIP literature is architecture and algorithm background, not permission to embed its solver core.

## Sources (3; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2005 | Branching Rules Revisited | Operations Research Letters 33(1), 42-54 | [PDF](2005-branching-rules-revisited.pdf) / [note](2005-branching-rules-revisited.source.md) | [source](https://doi.org/10.1016/j.orl.2004.04.002) |
| 2025 | The SCIP Optimization Suite 10.0 | arXiv technical report | [PDF](2025-the-scip-optimization-suite-10-0.pdf) / [note](2025-the-scip-optimization-suite-10-0.source.md) | [source](https://arxiv.org/abs/2511.18580) |
| 2025 | Cut-based Conflict Analysis in Mixed Integer Programming | INFORMS Journal on Computing; arXiv author version | [PDF](2025-cut-based-conflict-analysis-in-mixed-integer-programming.pdf) / [note](2025-cut-based-conflict-analysis-in-mixed-integer-programming.source.md) | [source](https://arxiv.org/abs/2410.15110) |

## Reading notes

- **reliability-branching:** Supports strong-branching/pseudocost tradeoffs and reliability initialization.
- **scip10:** Architecture reference for coordinating presolve, branching, cuts, heuristics and extensible problem classes.
- **conflict-analysis:** Research path for learning useful constraints from local infeasibility rather than discarding failed subproblems.

[Back to the research index](../README.md)
