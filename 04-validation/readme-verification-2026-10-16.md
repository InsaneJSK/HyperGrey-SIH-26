# README verification — 16 October 2026

A fresh CPU build and command-line smoke check of the repository's C++ solver
were performed on macOS while preparing the project overview. The build and all
four CLI smoke cases succeeded. **27 of 29 CTest groups passed**; two historical
sparse-basis fixtures stopped at an assertion requiring their old cold-control
failure to recur. No solver source, test or retained benchmark record was changed.

## Environment and build identity

| Item | Observed value |
|---|---|
| Repository baseline | `ebdeb423d7b457bcd832efe90b6023a9e8049dc8` |
| Platform | macOS 26.6.2, build `25G83`, ARM64 |
| Compiler | Apple Clang 17.0.0 (`clang-1700.6.3.2`) |
| Compiler target | `arm64-apple-darwin25.6.0` |
| Language standard | C++11, as declared by the project's CMake definition |
| CMake | 4.4.0 |
| Configuration | Release, default CPU build |
| Build directory | `/tmp/solveforge-readme-build` |
| OpenMP detection | Not found; the project's optional CPU fallback was built |
| `solver_cli` SHA-256 | `9974a22a1e1870c46124b9a1f43444b26b78dfe7d509865faef6585a58a0eaf8` |
| `solver_scale` SHA-256 | `65134e7b2d063bf3bc55169e44a998f294bef0f889ad93443f2ca7d56a1bdf6e` |

Executed from the repository root:

```sh
cmake -S 02-software/solver -B /tmp/solveforge-readme-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/solveforge-readme-build -j 4
ctest --test-dir /tmp/solveforge-readme-build --output-on-failure
```

CMake configured successfully and the build reached 100%, including the CLI,
scale driver and regression executables. The CTest command returned exit code 8
because of the two fixture expectations documented below. Build products were
kept outside the repository.

## Fresh CLI smoke results

Each command returned exit code 0. Values below are selected fields from the
actual JSON outputs; solution vectors and subsystem counters are omitted here.

### Refinery planning LP

```sh
/tmp/solveforge-readme-build/solver_cli 02-software/solver/examples/industrial/marco_refinery.mps --lp-method bounded --json
```

```json
{
  "status": "optimal",
  "algorithm": "bounded_dual_simplex",
  "rows": 40,
  "columns": 57,
  "nonzeros": 209,
  "iterations": 54,
  "objective": -6.588421476681309,
  "max_primal_violation": 7.105427357601002e-15,
  "scaled_primal_violation": 9.522228623080845e-17,
  "scaled_dual_violation": 1.133579885821764e-16,
  "relative_gap": 1.4747530988639371e-14,
  "optimality_verified": true
}
```

This is the [MARCO literature model](../02-software/solver/docs/INDUSTRIAL_CASES.md).
Its objective is cost minus revenue, corresponding to model profit of
6.588421476681309.

### Production and lot-sizing MILP

```sh
/tmp/solveforge-readme-build/solver_cli 02-software/solver/examples/industrial/production_lotsizing.mps --milp --bounded-lp --json
```

```json
{
  "status": "optimal",
  "rows": 13,
  "columns": 18,
  "objective": 762,
  "best_bound": 762,
  "gap": 0,
  "nodes": 7,
  "lp_iterations": 73,
  "warm_starts": 11,
  "unresolved_nodes": 0,
  "bounded_lp": {
    "enabled": true,
    "calls": 12,
    "warm": 11,
    "cold": 1,
    "cutoffs": 3,
    "fallbacks": 0
  }
}
```

The case is the project's synthetic six-period production, inventory and setup
model. Its returned optimum agrees with the retained application demonstration.

### Convex dispatch QP

```sh
/tmp/solveforge-readme-build/solver_cli 02-software/solver/examples/dispatch.qplib --json
```

```json
{
  "status": "optimal",
  "algorithm": "diagonal_qp_dual_newton",
  "threads": 1,
  "optimality_verified": true,
  "iterations": 3,
  "rows": 1,
  "columns": 2,
  "objective": 966.6666666660267,
  "primal_residual": 2.9849864978905856e-13,
  "stationarity_residual": 0,
  "complementarity_residual": 6.613652481721589e-13,
  "dual_bound_minimization_sense": 966.6666666666666,
  "relative_gap": 6.613260863266275e-13
}
```

### Planted 10,000-variable box QP

```sh
/tmp/solveforge-readme-build/solver_scale 10000 cpu 1 30
```

```json
{
  "status": "optimal",
  "passed": true,
  "backend": "cpu",
  "columns": 10000,
  "rows": 0,
  "hessian_nonzeros_lower": 19999,
  "threads": 1,
  "iterations": 1700,
  "objective": -947.1248894454208,
  "known_objective": -947.1248894454992,
  "relative_objective_error": 8.27358493603012e-14,
  "max_solution_error": 5.334931687750455e-6,
  "stationarity_residual": 7.093582859349654e-8,
  "synthetic": true
}
```

The scale driver checks the generated sparse tridiagonal convex box QP against
its planted optimum. Its acceptance contract is relative objective error at
most `1e-8`, maximum solution error below `1e-4`, and verified numerical
optimality. The observed solve time was 0.092971833 seconds for this one smoke
run; it is not a repeated performance measurement.

## CTest result

The complete current [CMake test registration](../02-software/solver/CMakeLists.txt)
contains 29 groups. This run completed in **50.98 seconds**, with 27 passes and
these two failures:

| CTest group | Observed control statuses | Failing assertion |
|---|---|---|
| `sparse_basis_accuracy` | `cold_control=optimal warm_control=numerical_error` | `Retained cold failure no longer reproduced` |
| `selective_basis_accuracy` | `cold_control=optimal warm_control=numerical_error` | `Retained cold failure no longer reproduced` |

Both groups execute [test_sparse_accuracy.cpp](../02-software/solver/tests/test_sparse_accuracy.cpp),
with the latter supplying `--checks`. The test intentionally requires the
unrefined cold solve of its retained fixture to return `numerical_error`
before running the refinement assertions. On this Apple Clang build, that cold
solve returns `optimal`; the test therefore stops at the historical expectation.
This observation does not claim that the remaining assertions in either group
ran, and no fixture or acceptance threshold was edited to change the result.

The 27 passing groups include LP/MPS/MILP/QP correctness, primal-ratio stability,
sparse numerical regressions, exact-binary and meet-in-the-middle checks,
cover-cut and Gomory validity, resource/work accounting, frontier handling,
heuristic repair, pump guidance, private reoptimization and bounded simplex.
Two examples of actual passing output:

```text
bounded_simplex_regressions:
trials 3000 compared 2175 infeasible_agreed 631 unverified 0 warm 1746 cutoff 542 row_warm 1633 bounds 2175 farkas_rejected 0 verification_rejected 0 failures 194 cleanups 7531

gomory_cut_validity:
trials 3000 solved 2673 with_cuts 1767 cuts 2706 strictly_violated 2706 integer_points 64430 bound_checks 1491 feasible_models 1491
mixed_models 226 mixed_cuts 293 assignments 2689 feasible_completions 1059
```

These are the test executables' own counters. In particular, the bounded LP
`failures` diagnostic counter is not a count of failed CTest groups; that group
passed its checks and reports `unverified 0`.

## Evidence scope

This record covers a fresh CPU build, the current C++ regression suite and four
small reproducibility examples on this Mac. The CLI smoke cases use the core's
native numerical checks; external reference solvers were not rerun in this
smoke check. The retained [full MIPLIB campaign](../02-software/solver/reports/miplib2017-benchmark/REPORT.md)
and [repeated T4 GPU box-QP experiment](../02-software/solver/reports/kaggle-gpu-03/REPORT.md)
remain separately identified measurements with their original machines,
profiles and acceptance checks. No CUDA execution or cloud benchmark rerun is
attributed to this Mac verification.
