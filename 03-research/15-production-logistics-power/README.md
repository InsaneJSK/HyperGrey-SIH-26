# 15-production-logistics-power

Production, logistics and power applications

## What this folder supports

Transportation, lot sizing, supply-chain scheduling, economic dispatch and unit commitment as solver use cases.

**Problem-statement mapping:** PS-13, PS-04, PS-03 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [docs/INDUSTRIAL_CASES.md](../../04-software/solver/docs/INDUSTRIAL_CASES.md)
- [scripts/industrial_cases.py](../../04-software/solver/scripts/industrial_cases.py)
- [examples/industrial/manifest.json](../../04-software/solver/examples/industrial/manifest.json)

## Scope note

Check convexity and linearization explicitly; AC OPF and full industrial scheduling are not automatically LP/MILP/convex-QP problems.

## Sources (5; 2 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2026 | TRNSPORT: A Transportation Problem | GAMS Model Library | [note](2026-trnsport-a-transportation-problem.source.md) / reference only | [source](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html) |
| 2024 | MATPOWER User's Manual, Version 8.0 | MATPOWER official documentation | [PDF](2024-matpower-user-s-manual-version-8-0.pdf) / [note](2024-matpower-user-s-manual-version-8-0.source.md) | [source](https://matpower.org/docs/MATPOWER-manual-8.0.pdf) |
| 2026 | UnitCommitment.jl: Security-Constrained Unit Commitment | Official project and benchmark documentation | [note](2026-unitcommitment-jl-security-constrained-unit-commitment.source.md) / reference only | [source](https://github.com/ANL-CEEESA/UnitCommitment.jl) |
| 2010 | Dynamic capacitated lot-sizing problems: a classification and review of solution approaches | OR Spectrum 32(2), 231-261 | [note](2010-dynamic-capacitated-lot-sizing-problems-a-classification-and-review-of-solution-approaches.source.md) / reference only | [source](https://link.springer.com/article/10.1007/s00291-008-0150-7) |
| 2017 | A Novel MILP Scheduling Model for Power-Intensive Processes under Time-Sensitive Electricity Prices | Industrial & Engineering Chemistry Research author manuscript | [PDF](2017-a-novel-milp-scheduling-model-for-power-intensive-processes-under-time-sensitive-electricity-prices.pdf) / [note](2017-a-novel-milp-scheduling-model-for-power-intensive-processes-under-time-sensitive-electricity-prices.source.md) | [source](https://egon.cheme.cmu.edu/Papers/Basan_Mendez_et_al_NovelMIP_DSM_IEC.pdf) |

## Reading notes

- **transport:** Primary source for the two-plant/three-market transportation LP already used in the industrial examples.
- **matpower-manual:** Provides dispatch/network formulations and the distinction between DC OPF QP and nonlinear AC OPF.
- **unitcommitment:** Source of documented unit-commitment formulations and benchmark instances for future power-sector MILP cases.
- **lot-sizing-review:** Places the synthetic multi-period setup/inventory MILP in the broader capacitated lot-sizing literature.
- **power-intensive-production:** Industrial scheduling formulation joining production demand and time-varying electricity costs.

[Back to the research index](../README.md)
