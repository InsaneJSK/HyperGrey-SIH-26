# 13-evaluation-reproducibility

Evaluation and reproducibility

## What this folder supports

Performance profiles, full failure accounting, fair stopping criteria, repeated runs and progress over time.

**Problem-statement mapping:** PS-09, PS-11, PS-12, PS-15 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [docs/V2_REPRODUCE.md](../../02-software/solver/docs/V2_REPRODUCE.md)
- [docs/MILP_ROBUSTNESS.md](../../02-software/solver/docs/MILP_ROBUSTNESS.md)
- [docs/EXECUTION_POLICY.md](../../02-software/solver/docs/EXECUTION_POLICY.md)

## Scope note

Project speed and robustness claims must come from dated local experiments, not the external papers' results.

## Sources (4; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2002 | Benchmarking Optimization Software with Performance Profiles | Mathematical Programming 91, 201-213 | [PDF](2002-benchmarking-optimization-software-with-performance-profiles.pdf) / [note](2002-benchmarking-optimization-software-with-performance-profiles.source.md) | [source](https://arxiv.org/abs/cs/0102001) |
| 2020 | Benchmarking in Optimization: Best Practice and Open Issues | arXiv survey | [PDF](2020-benchmarking-in-optimization-best-practice-and-open-issues.pdf) / [note](2020-benchmarking-in-optimization-best-practice-and-open-issues.source.md) | [source](https://arxiv.org/abs/2007.03488) |
| 2013 | Measuring the impact of primal heuristics | Operations Research Letters 41(6), 611-614 | [PDF](2013-measuring-the-impact-of-primal-heuristics.pdf) / [note](2013-measuring-the-impact-of-primal-heuristics.source.md) | [source](https://www.sciencedirect.com/science/article/pii/S0167637713001181) |
| 2013 | Performance Variability in Mixed-Integer Programming | Theory Driven by Influential Applications, INFORMS Tutorials in Operations Research | [note](2013-performance-variability-in-mixed-integer-programming.source.md) / reference only | [source](https://pubsonline.informs.org/doi/10.1287/educ.2013.0112) |

## Reading notes

- **performance-profiles:** Use distribution-based performance profiles while retaining failed and timed-out cases.
- **benchmark-best-practice:** Supports predeclared goals, representative problems, suitable metrics and reproducible comparisons.
- **primal-integral:** Measure quality over time as well as time to optimality when evaluating pumps, dives and repair.
- **performance-variability:** Explains why row/column permutations, platform changes and small perturbations need repeated, paired evaluation.

[Back to the research index](../README.md)
