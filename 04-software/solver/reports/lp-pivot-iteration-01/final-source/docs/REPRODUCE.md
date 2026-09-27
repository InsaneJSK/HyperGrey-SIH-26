# Reproduce the first version

All commands below run from the repository root. Use a Python 3.12 executable
for the reference wheels tested here. The core needs only a C++11 compiler.

## Build and analytical checks

```powershell
./scripts/build.ps1
```

The script stops on compiler/test failure. It builds the CLI and C++ tests with
`-std=c++11 -O2 -Wall -Wextra -pedantic`. It was run with MinGW GCC 6.3.

## Isolated reference dependencies

Set `$solverPython` to your Python executable. On the development machine it is:

```powershell
$solverPython = 'C:\Users\JSK\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $solverPython -m pip install --target tools/reference/python highspy==1.12.0 numpy==2.5.3
& $solverPython -m pip install --target tools/reference/qp osqp==1.0.5 numpy==2.5.3 scipy==1.18.1
```

These directories are ignored by Git and never linked into the core. The
reference package pins are recorded in `tools/reference-requirements.txt`.
Network access or platform wheel availability may require setup on another host.

## Dataset preparation

```powershell
& $solverPython scripts/fetch_netlib.py
& $solverPython scripts/fetch_phase23.py
```

The Netlib script uses the official EMPS data decompressor compiled separately
with `gcc`; it is not an optimization solver. Each manifest records source URL,
retrieval time and original/expanded SHA-256 hashes. Downloads and expanded
files are cached locally, not committed as source. Netlib selection is in
`datasets/netlib/selection.json`; MIPLIB/QPLIB selections are declared in the
phase 2/3 fetch script before solving.

QPLIB is attributed to its authors/maintainers and distributed by the official
site under [CC BY 4.0](https://qplib.zib.de/instances.html). Original downloaded
files are kept unchanged. Historical MIPLIB source is explicitly recorded; it
must not be described as the MIPLIB 2017 benchmark set.

## Full validation

Choose a NEW output directory so previous successes and failures are preserved:

```powershell
./scripts/validate_v1.ps1 -Python $solverPython -Output reports/my-new-run
```

This executes the build/C++ checks, 120 generated LPs, 12 Netlib cases, 40
enumerated binary MILPs, four historical MIPLIB cases, 30 planted QPs, three
QPLIB cases and the three demonstration models. Runs are sequential. Dataset
failures remain in JSON; successful harness execution does not mean all
benchmarks passed. Inspect the `passed` values in every `results.json`.

Each family can also run separately using `test_generated.py`, `benchmark_lp.py`,
`test_milp.py`, or `test_qp.py`, with `--output` pointing at a fresh directory.

## Evidence and comparison protocol

- Netlib: own result must be optimal with numerical dual checks, match HiGHS and
  the published objective to relative 1e-7, and pass independent original-MPS
  feasibility/objective reconstruction checks (scaled tolerance 1e-8).
- MILP: exhaustive enumeration provides exact objectives for tiny binary cases.
  Public cases must reach optimal/gap_limit, match HiGHS to relative 1e-6 and pass
  independent feasibility/integrality checks. A reference-matching incumbent
  without gap closure is not counted as a completed solve.
- QP: generated cases have planted KKT optima. Public cases require optimal KKT
  termination, OSQP optimal termination, objective agreement to relative 1e-6,
  and independent feasibility/objective checks. Final OSQP input comes from an
  independent Python reader of the original QPLIB file. The official LP export
  is audited, but may lose tiny coefficients in HiGHS' parser (seen on `9002`).
- Limits: LP 30 seconds; public MILP/QP 15 seconds; MIP cap 10,000 nodes. A separate
  subprocess watchdog records external_timeout if internal checks overrun.
- Source hashes/settings are stored with family reports; Netlib metadata also
  records compiler, executable hash, OS, Python, processor identifier and logical
  processors. Do not infer actual RAM/GPU from the user's target specification.
- Native short runtimes can be below timer resolution. Process timings include
  startup. Peak memory, repeated timing distributions and performance profiles
  are still missing; these runs support functional evidence, not speedup claims.
