# Reproduce the resumed CPU candidate

The earlier broadly measured configuration is the explicit staged MILP profile in
`reports/milp-iteration-28/CANDIDATE_PROFILE.json`. The executable's defaults
remain unchanged. Stable private ranking, alternate reserve and deferred
restart were tested and rejected for promotion. The evaluation profile is
experimental; its report states unresolved models and gaps.

## Run the frozen MILP profile

From the inner source-project directory, using a Python3 interpreter:

```powershell
python -B reports/milp-iteration-28/solve_candidate.py examples/production.mps --output reports/my-production-run
```

Use a fresh output prefix for every run. The launcher verifies the frozen
executable hash, applies the saved profile, and records native JSON inside
`native_result` in the output JSON, plus stdout/stderr and process memory.
It uses30 seconds,250000 nodes and1e-6 relative gap. The external timeout is
45 seconds and the sampled process-commit threshold is1536 MiB. Internal
limits are cooperative; sampled memory limits can overshoot and process
creation/termination is not a strict real-time guarantee. The wrapper is for
the solver's single process, not arbitrary process trees.

A numerical `optimal` or `gap_limit` status is distinct from an exact binary
proof. The wrapper does not perform independent solution validation; see the
reference and original-model checks in the experiment ledgers. Forced stops
override native success text. Solver exit1 can represent an honest limit or
terminal non-optimal outcome. Malformed/unsupported input currently reports
an error on stderr with exit2, which the wrapper retains as `process_error`.
This launcher is for MILP, not QP or GPU experiments.

## Build on the current Windows host

The old global MinGW is incompatible with retained x64 artifacts. A matching
project-local GCC14.2 toolchain is under `tools/local-toolchain/mingw64`;
download provenance and archive hash are in iteration25's `ENVIRONMENT.md`.
Use a fresh build directory. Historical CMake caches contain obsolete paths.

```powershell
$env:PATH = "$PWD/tools/local-toolchain/mingw64/bin;$env:PATH"
cmake -S . -B build-reproduction -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build build-reproduction -j 4
ctest --test-dir build-reproduction --output-on-failure
```

Recorded full correctness commands are in iteration26's `gate-command.json`.
Its reference environment uses Python3.12, HiGHS1.12.0 and NumPy2.5.3. References
are separate validation processes; no solution or bound is fed to the C++
engine. Preserve the manifests:27 benchmark files were restored to their exact
original hashes after checkout newline conversion. Scoped `.gitattributes`
rules retain those bytes; do not update manifests to disguise a changed model.

The isolated-folder package smoke is a same-host check with copied runtime
DLLs and a restricted PATH. It does not establish a fresh-OS installation,
a complete submission package, final LP/QP breadth or GPU readiness.

## Current iteration 29 and continuous profiles

Iteration 29 retains a separate experimental private-certificate profile in
`reports/milp-iteration-29/CANDIDATE_PROFILE.json`, with the same hash-checked
launcher interface. It passes the full correctness gate and a repeated
12-model screen but adds no integer coverage or completions. It stays off;
do not substitute its screen score for iteration 28's broader evaluation.
The frozen folder includes the five matching runtime DLLs required on this
host. See its `ENVIRONMENT.md` for retained loader failures and their resolution.

The same iteration 29 executable has a separately checked LP profile:

```powershell
reports/milp-iteration-29/final_solver_cli.exe reports/cpu-validation-2026-09-17/results/inputs/additional-lp/bandm.mps --json --time-limit 30 --compact-equalities --refine-basis --refine-at-checks
```

These flags complete all 16 tested LPs; default and refined profiles each
complete 15/16. The standard-path `bandm` failure remains recorded, and one
compact invocation uses its built-in fallback on `degen2`. This is an LP
evaluation profile, not a default change, general scale guarantee or MILP gain.
See `reports/lp-bandm-01/LP_PROFILE.json` and its complete ledger.

Three default QPLIB inputs pass current original-model relative KKT checks.
QP 9002 still has about 2.381 maximum absolute violation and a reference
timeout; tighter-tolerance probes time out and fail independent acceptance.
Use `reports/cpu-validation-2026-09-17/REPORT.md` for the precise contract and
limits. No operational accuracy or GPU evidence is implied.

## Evidence and next work

The latest standalone LP experiment is `reports/lp-pivot-iteration-01`.
Its hash-checked `solve_lp.py` launcher selects the stable-only profile by
default, or the separately validated stable/refined profile with `--refined`:

```powershell
python -B reports/lp-pivot-iteration-01/solve_lp.py tests/lp_ratio_bandm.mps --output reports/my-stable-lp-run
```

Both explicit profiles complete the 16 tested LPs, while default/refined bandm
still fail. This launcher expects continuous MPS LP input and does not select
the older MILP profile. The option is experimental; see its report and
`docs/PRIMAL_RATIO_STABILITY.md`. Use a fresh output prefix, preserve its native
and wrapper records, and independently check the original model as needed.

Use the iteration25–28 reports for decisions and the iteration28 model ledger
for the final development, holdout and default-profile results. Do not combine
historical best solutions into one claimed profile. The untouched set has six
models with related pairs; artificial transformations are reported separately.

The hypothesis in `NEXT_PRIVATE_LP_HYPOTHESIS.md` was tested in iteration 29.
Its `NEXT_STEP.md` records the remaining private-dive diagnosis. The current
LP/QP studies expose standard-path numerical robustness and QP accuracy work;
broader coverage, domain validation, final-source GPU evidence and submission
preparation remain in the outer `objective.md`.
