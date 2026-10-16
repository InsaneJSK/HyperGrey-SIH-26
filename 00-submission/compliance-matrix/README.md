# Requirements and supporting evidence

This guide connects the main SIH26119 requirements to inspectable implementation and retained results.

| Requirement area | Implementation or evidence |
|---|---|
| Independent numerical core | [C++ source](../../02-software/solver/src/), [public headers](../../02-software/solver/include/), and [architecture](../../02-software/solver/docs/V2_ARCHITECTURE.md) |
| LP, MILP and convex QP | [CLI/C++ API](../../02-software/solver/docs/CLI_API.md) and [numerical methods](../../02-software/solver/docs/) |
| Sparse numerical engineering | [Bounded simplex](../../02-software/solver/docs/BOUNDED_SIMPLEX.md), [LP safeguard results](../../02-software/solver/reports/lp-pivot-iteration-01/REPORT.md), and regression tests |
| Recognized benchmarks | [Complete historical MIPLIB 2017 campaign](../../02-software/solver/reports/miplib2017-benchmark/REPORT.md) and [benchmark navigation](../../04-validation/benchmark-results/README.md) |
| Measured GPU acceleration | [Repeated Tesla T4 box-QP experiment](../../02-software/solver/reports/kaggle-gpu-03/REPORT.md) through one million variables |
| Industrial applications | [Refinery, transportation and production models](../../02-software/solver/docs/INDUSTRIAL_CASES.md) |
| API and reproducibility | [FastAPI service](../../02-software/backend/README.md), [test and reproduction guide](../../04-validation/test-plan/README.md), and [Kaggle packages](../../02-software/kaggle_delivery/README.md) |

The [original statement](../../02-software/solver/Problem%20Statement.txt), [V1 matrix](../../02-software/solver/docs/PS_REQUIREMENTS.md), and [V2 coverage record](../../02-software/solver/docs/V2_REQUIREMENTS.md) preserve the requirement and development history. Results belong to the versions, problem families and budgets identified in their reports.
