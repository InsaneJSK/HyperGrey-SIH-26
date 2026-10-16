# Demonstration guide

A concise review sequence connects the numerical engine to the planning workflow and its checked evidence.

1. Open the [live workbench](https://sovereign-solver-gilt.vercel.app/solve) and inspect model input, problem-family selection and returned diagnostics.
2. Open the [refinery case](https://sovereign-solver-gilt.vercel.app/refinery) to review the base plan and sulfur/profit sensitivity.
3. Inspect the [LP, MILP and convex-QP command-line examples](../../README.md#build-and-run), including refinery planning, lot sizing and dispatch.
4. Review the [CPU/GPU results](../../04-software/solver/reports/kaggle-gpu-03/REPORT.md) and [historical MIPLIB campaign](../../04-software/solver/reports/miplib2017-benchmark/REPORT.md).
5. Watch the [offline Android](https://www.youtube.com/watch?v=hZwr9e80-2U), [online Android](https://www.youtube.com/watch?v=S3V37uguqLI), and [architecture](https://www.youtube.com/watch?v=cg7OX9HNSFg) walkthroughs.

The existing [CLI demonstration guide](../../04-software/solver/docs/DEMO.md) and [executable harness](../../04-software/solver/scripts/demo_cli.py) retain the independently checked model sequence and per-step JSON outputs. Follow their documented binary and reference setup when reproducing that recorded demo.
