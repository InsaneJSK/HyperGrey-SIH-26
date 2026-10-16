# 14-refinery-blending

Refinery planning, crude blending and process scheduling

## What this folder supports

MRPL context, refinery material/quality balances, time-dependent scheduling and boundaries between LP/MILP and MINLP.

**Problem-statement mapping:** PS-13 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [docs/INDUSTRIAL_CASES.md](../../02-software/solver/docs/INDUSTRIAL_CASES.md)
- [scripts/industrial_cases.py](../../02-software/solver/scripts/industrial_cases.py)
- [examples/industrial/manifest.json](../../02-software/solver/examples/industrial/manifest.json)

## Scope note

MARCO is a teaching/literature case, not MRPL plant data. Nonlinear blending papers motivate extensions and engineering review.

## Sources (4; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2026 | MARCO: Mini Oil Refining Model | GAMS Model Library | [note](2026-marco-mini-oil-refining-model.source.md) / reference only | [source](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html) |
| 2025 | Mangalore Refinery and Petrochemicals Limited: Annual Report 2024-25 | Company report filed with the National Stock Exchange of India | [PDF](2025-mangalore-refinery-and-petrochemicals-limited-annual-report-2024-25.pdf) / [note](2025-mangalore-refinery-and-petrochemicals-limited-annual-report-2024-25.source.md) | [source](https://nsearchives.nseindia.com/annual_reports/AR_27132_MRPL_2024_2025_A_28072025171020.pdf) |
| 2017 | Crude-Oil Blend Scheduling Optimization of an Industrial-Sized Refinery: A Discrete-Time Benchmark | FOCAPO 2017 author manuscript | [PDF](2017-crude-oil-blend-scheduling-optimization-of-an-industrial-sized-refinery-a-discrete-time-benchmark.pdf) / [note](2017-crude-oil-blend-scheduling-optimization-of-an-industrial-sized-refinery-a-discrete-time-benchmark.source.md) | [source](https://egon.cheme.cmu.edu/Papers/Kelly_CBSO_paper.pdf) |
| 2021 | Modeling for Integrated Refinery Planning with Crude-Oil Scheduling | CMU Grossmann research group manuscript | [PDF](2021-modeling-for-integrated-refinery-planning-with-crude-oil-scheduling.pdf) / [note](2021-modeling-for-integrated-refinery-planning-with-crude-oil-scheduling.source.md) | [source](https://egon.cheme.cmu.edu/Papers/Su_IntegratedRefineryPlanning-2.pdf) |

## Reading notes

- **marco:** Primary source for the project's refinery/blending LP and tighter sulfur what-if scenario.
- **mrpl-annual:** Official industrial context for the sponsoring refinery and its operations.
- **crude-scheduling:** Separates logistics MILP decisions from nonlinear quality calculations in a realistic refinery scheduling workflow.
- **integrated-refinery:** Shows why planning and scheduling interact through refinery process and quality constraints.

[Back to the research index](../README.md)
