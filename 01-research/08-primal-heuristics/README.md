# 08-primal-heuristics

Primal heuristics and neighborhood search

## What this folder supports

Feasibility pumps, diving, rounding, repair and budgeted neighborhood searches for early feasible incumbents.

**Problem-statement mapping:** PS-03, PS-10 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [docs/SEARCH_HEURISTICS.md](../../02-software/solver/docs/SEARCH_HEURISTICS.md)
- [docs/PUMP_GUIDED_DIVING.md](../../02-software/solver/docs/PUMP_GUIDED_DIVING.md)
- [docs/MILP_NEIGHBORHOOD_METHOD.md](../../02-software/solver/docs/MILP_NEIGHBORHOOD_METHOD.md)

## Scope note

A heuristic incumbent must pass original-model validation and does not prove optimality.

## Sources (4; 4 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2018 | Ten years of Feasibility Pump, and counting | Author survey manuscript | [PDF](2018-ten-years-of-feasibility-pump-and-counting.pdf) / [note](2018-ten-years-of-feasibility-pump-and-counting.source.md) | [source](https://www.dei.unipd.it/~salvagni/pdf/10yearsFP.pdf) |
| 2018 | Adaptive Large Neighborhood Search for Mixed Integer Programming | ZIB Report 18-60 | [PDF](2018-adaptive-large-neighborhood-search-for-mixed-integer-programming.pdf) / [note](2018-adaptive-large-neighborhood-search-for-mixed-integer-programming.source.md) | [source](https://www.zib.de/userpage/hendel/publication/adaptive-large-neighborhood-search-for-mixed-integer-programming/) |
| 2021 | Learning to Schedule Heuristics in Branch-and-Bound | NeurIPS 2021, volume 34, 24235-24246 | [PDF](2021-learning-to-schedule-heuristics-in-branch-and-bound.pdf) / [note](2021-learning-to-schedule-heuristics-in-branch-and-bound.source.md) | [source](https://arxiv.org/abs/2103.10294) |
| 2005 | The Feasibility Pump | Mathematical Programming 104, 91-104 | [PDF](2005-the-feasibility-pump.pdf) / [note](2005-the-feasibility-pump.source.md) | [source](https://doi.org/10.1007/s10107-004-0570-3) |

## Reading notes

- **pump-survey:** Maps pump variants, cycling mitigation and objective/feasibility tradeoffs to the project's staged pump work.
- **adaptive-lns:** Supports adaptive allocation of a fixed heuristic budget across local branching, RINS and related neighborhoods.
- **heuristic-scheduling:** Motivates measuring and scheduling heuristics by solution quality achieved over a shared time budget.
- **feasibility-pump:** Original alternating LP-distance and rounding heuristic for finding feasible MIP incumbents.

[Back to the research index](../README.md)
