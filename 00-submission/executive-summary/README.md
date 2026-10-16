# SolveForge executive summary

**SolveForge · HyperGrey · SIH26119 · MRPL**

SolveForge provides an inspectable optimization engine for industrial planning. Its independent C++ core handles LP, MILP and continuous convex QP, with sparse numerical methods, original-model verification, structured JSON results and selective CUDA acceleration.

The project connects the engine to published refinery and transportation models, a production-planning MILP, a FastAPI service, a public web workbench and supplied online/offline Android demonstrations.

| Completed work | Supporting material |
|---|---|
| Independent LP/MILP/convex-QP algorithms | [Source and build guide](../../04-software/solver/README.md) |
| Repeated CPU/GPU scaling experiment | [45 checked T4 box-QP runs across five sizes](../../04-software/solver/reports/kaggle-gpu-03/REPORT.md) |
| Full historical 240-instance MIPLIB campaign | [Report, checked solutions and outcome table](../../04-software/solver/reports/miplib2017-benchmark/REPORT.md) |
| Refinery planning and sensitivity workflow | [Industrial examples](../../04-software/solver/docs/INDUSTRIAL_CASES.md) and [public refinery page](https://sovereign-solver-gilt.vercel.app/refinery) |
| Research and technical documentation | [Technical paper](../../07-documentation/technical-report/solver_research.pdf) and [60-source research library](../../03-research/README.md) |

[Project overview](../../README.md) · [Live workbench](https://sovereign-solver-gilt.vercel.app/solve) · [Demo playlist](https://www.youtube.com/playlist?list=PLRNv4l1yWhLs)
