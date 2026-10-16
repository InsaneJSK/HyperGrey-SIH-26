# Execution environments

The experiment reports record the host, compiler, runtime, thread count, GPU configuration and solver settings used for their measurements.

| Environment | Record |
|---|---|
| macOS / Apple Clang, current-source CPU check | [Fresh build and CLI verification](../readme-verification-2026-10-16.md) |
| Tesla T4, CPU 1/4-thread and CUDA comparison | [Repeated GPU experiment](../../04-software/solver/reports/kaggle-gpu-03/REPORT.md) |
| Kaggle notebook execution | [Packaged notebooks and source snapshots](../../04-software/kaggle_delivery/README.md) |
| CPU/GPU execution policy | [Solver execution guide](../../04-software/solver/docs/EXECUTION_POLICY.md) |
| FastAPI deployment profile | [Container and EC2 guide](../../04-software/backend/DEPLOY.md) |

Keep host identity, problem size, numerical accuracy, repetition count and timing boundaries alongside a performance result. New runs should use a separate output directory so archived records retain their original identity.
