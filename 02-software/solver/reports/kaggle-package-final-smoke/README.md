# Sovereign optimization solver

## V2 candidate — current development version

V2 adds sparse revised simplex, reusable LP bases, MILP bound propagation,
cover cuts and diving heuristics, a scaled constrained-QP method, multicore
operations, and an optional CUDA box-QP backend. The separate Kaggle notebook
contains the same source snapshot and collects GPU evidence when run there.

Start with [V2 build and reproduction](docs/V2_REPRODUCE.md),
[architecture and exact scope](docs/V2_ARCHITECTURE.md),
[industrial cases](docs/INDUSTRIAL_CASES.md), and
[remaining submission requirements](docs/V2_REMAINING.md).

The material below records V1. V1 results are historical and must not be used
as current binary hashes or GPU evidence. The active build is `build-v2`.

First-version research solver for SIH problem 26119 (MRPL). The C++ optimization
algorithms are implemented here without linking an existing solver or numerical
library. Reference packages are used only by separate test processes.

## Current version

- **LP:** dense two-phase simplex, scaling, numerical primal/dual checks, MPS
  input, bound standardization and original-variable reconstruction.
- **MILP:** best-bound branch-and-bound, integer/binary variables, validated
  incumbents, bounds/gaps and time/node limits.
- **Convex QP subset:** sparse projected-gradient / primal-dual algorithms,
  QPLIB input, conservative curvature checks and KKT residuals.
- JSON CLI output, analytical/generated tests, public datasets, reference
  comparisons and preserved failure reports.

This is not an industrial replacement for CPLEX, Gurobi or Xpress. Sparse LP
factorization, cuts, warm starts, GPU/multicore execution and general large-scale
robustness remain outstanding. See the [V1 report](reports/V1_REPORT.md),
[PS requirements matrix](docs/PS_REQUIREMENTS.md) and [limitations](docs/LIMITATIONS.md).

## Build and run

Tested locally in PowerShell with MinGW GCC 6.3:

```powershell
./scripts/build.ps1
./build/solver_cli.exe examples/blending.lpmini --json
./build/solver_cli.exe examples/production.mps --milp --json
./build/solver_cli.exe examples/dispatch.qplib --json
./build/solver_cli.exe datasets/netlib/afiro.mps --json --time-limit 30
```

CMake configuration is also provided, but was not run in this environment:

```text
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Python/reference packages are not needed to build or run the core.

## Input formats

MPS supports continuous row/column bounds, objective sense/offset, ranges and
integer declarations. Use `--milp` explicitly for integer models; a MILP is never
silently solved as an LP relaxation. Unsupported features produce errors.

QPLIB support is restricted to continuous quadratic objectives with linear or
box constraints. See [algorithm and format details](docs/ALGORITHMS.md).

The original `.lpmini` format contains whitespace-separated numbers without
comments: variable and row counts, objective coefficients, then one row of
coefficients and its RHS per constraint. It means minimize c*x subject to
A*x <= b and x >= 0. Encode >= by negation and equalities by two inequalities.
Its dimensions are capped at 1000 each; MPS has a separate allocation guard.

## Illustrative examples

- **Blending LP:** feed costs 40 and 60; demand at least 100; availability 80 each;
  sulfur fractions 3% and 1%, blended limit 2%. With additive mass and linear sulfur
  mixing, the optimum is 50 units of each feed, cost 5,000.
- **Production MILP:** per-unit costs 3 and 2, activation costs 100 and 150,
  capacities 50 and 70, demand 80. Activate both machines, produce 10 and 70 units,
  cost 420.
- **Dispatch QP:** costs 0.01*x1^2 + 10*x1 and 0.02*x2^2 + 8*x2, total dispatch
  100, each generator bounded by 0 and 80. Optimum approximately 33.3333 and
  66.6667, cost 966.6667.

These are synthetic illustrations, not validated industrial case studies.

## Documentation

- [Reproduce downloads and validation](docs/REPRODUCE.md)
- [Algorithms, input scope and numerical checks](docs/ALGORITHMS.md)
- [Phase-by-phase record](docs/PHASES.md)
- [Decisions and organizer questions](docs/DECISIONS.md)
- [Remaining PS obligations](docs/PS_REQUIREMENTS.md)
- [Limitations and regressions](docs/LIMITATIONS.md)
- [First-version report](reports/V1_REPORT.md)

The [original development scope](docs/SCOPE.md) is retained as planning history.
