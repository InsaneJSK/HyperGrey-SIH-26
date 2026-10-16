# Build and verify V2

Current policy: run all CPU-only validation locally. Use Kaggle only for tests
requiring NVIDIA GPU/CUDA; see [execution policy](EXECUTION_POLICY.md).

Use the project directory containing CMakeLists.txt. The Windows local project
and the separate Kaggle delivery are independent copies of the same source
snapshot. The notebook never accesses or changes the Windows workspace.

## Local CPU build

Iteration24 tests the optional [objective-only private stage](PUMP_DISTANCE_STAGE.md).
Use new build/output directories and run these commands sequentially. Keep
source/checkers unchanged between paired measurements; do not run competing
builds or references during the timed own solves.

```powershell
cmake -S . -B build-my-stage-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-my-stage-run -j2
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-stage-run/solver_cli.exe --output reports/my-stage-gate --selective --heuristic-repair --pump-guidance --pump-distance --pump-reopt --distance-reopt --distance-stage
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-stage-run/solver_cli.exe --plan reports/milp-iteration-24/SCREEN.json --output reports/my-stage-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-stage-run/solver_cli.exe --plan reports/milp-iteration-24/WAVE.json --output reports/my-stage-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_distance_stage.py reports/my-stage-screen reports/my-stage-wave --output reports/my-stage-audit
```

The new flag defaults off. Plans compare the same executable with staging off/on,
at identical limits. Report-local parity/replay/freeze helpers bind to their
original directories and must be adapted before a new reproduction, not rerun
over the archive. Stage and child diagnostic LP replays use a separate ten-second
allowance and are not measured MILP runs. Five-second references validate saved
answers; they are not equal-budget performance competitors. All retained dataset
and historical-fixture dependencies below still apply. No Kaggle upload is needed.

Iteration23 tests [guarded private basis handoff](PUMP_DISTANCE_REOPT.md).
Use fresh output paths and run sequentially; do not overwrite the archived
experiment. The new option is off by default. The plans compare the same
binary with the new flag off/on, not two differently built solvers.

```powershell
cmake -S . -B build-my-handoff-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-my-handoff-run -j2
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-handoff-run/solver_cli.exe --output reports/my-handoff-gate --selective --heuristic-repair --pump-guidance --pump-distance --pump-reopt --distance-reopt
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-handoff-run/solver_cli.exe --plan reports/milp-iteration-23/SCREEN.json --output reports/my-handoff-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-handoff-run/solver_cli.exe --plan reports/milp-iteration-23/WAVE.json --output reports/my-handoff-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_distance_reopt.py reports/my-handoff-screen reports/my-handoff-wave --output reports/my-handoff-audit
```

The iteration23 report-local parity, replay and archive helpers bind to their
own evidence directories; adapt their paths for a separate reproduction.
They must not be rerun over the frozen archive. Reference solves validate
saved answers; their shorter time budget is not a fair performance comparison.

Iteration22: [private pump reoptimization](PUMP_PRIMAL_REOPT.md) adds optional
`--pump-primal-reopt` to the prior distance profile. Use matching source and
fresh output directories. The default flag remains off. Run these sequentially:

```powershell
cmake -S . -B build-my-reopt-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-my-reopt-run -j4
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-reopt-run/solver_cli.exe --output reports/my-reopt-gate --selective --heuristic-repair --pump-guidance --pump-distance --pump-reopt
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-reopt-run/solver_cli.exe --plan reports/milp-iteration-22/SCREEN.json --output reports/my-reopt-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-reopt-run/solver_cli.exe --plan reports/milp-iteration-22/WAVE.json --output reports/my-reopt-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_pump_reopt.py reports/my-reopt-screen reports/my-reopt-wave --output reports/my-reopt-audit
```

The report-local parity, replay, integration and archive helpers deliberately
bind to the iteration22 paths. They are evidence assembly tools, not generic
commands to rerun in place over a frozen archive. Use separate output paths
when adapting them. All earlier dataset/reference dependencies remain required.

Iteration21: [private distance diving](PUMP_DISTANCE_DIVING.md) compares the
previous guided profile with the additional `--pump-distance-diving` option.
Use matching source and new output directories; keep measured solves serial:

```powershell
cmake -S . -B build-my-distance-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-distance-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-distance-run/solver_cli.exe --output reports/my-distance-gate --selective --heuristic-repair --pump-guidance --pump-distance
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-distance-run/solver_cli.exe --plan reports/milp-iteration-21/MECHANISM.json --output reports/my-distance-mechanism
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-distance-run/solver_cli.exe --plan reports/milp-iteration-21/SCREEN.json --output reports/my-distance-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-distance-run/solver_cli.exe --plan reports/milp-iteration-21/WAVE.json --output reports/my-distance-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_pump_distance.py reports/my-distance-screen reports/my-distance-wave --output reports/my-distance-audit
```

The original measurements use binary `fcc2817f...`; the final domain-guard
artifact uses `16a77b3d...`. Per-run `source` snapshots match the former;
`final-source` matches the latter. Restore the chosen snapshot within a full
project containing the retained data/dependencies before rebuilding. The above
commands on current source create a NEW final-build experiment, not an exact
rerun of the earlier binary's measurements.

The post-measurement stage is documented in iteration21's EDGE_CASE_PLAN.md.
Its report-local `check_final_parity.py`, `check_domain_guard.py`,
`check_max_distance.py` and `freeze_with_domain_guard.py` use fixed original
paths and refuse overwrite. The earlier root `freeze_pump_distance.py` is the
pre-guard single-binary freezer, not the final dual-identity archive workflow.
These are not generic commands to rerun over archived evidence.
All retained dependencies below still apply. Do not change root source,
checkers or test scripts during timings. Private-distance metrics are not
MILP certificates; final points are independently checked on the original MPS.
Read the experiment report before selecting either optional profile.

Historical iteration20 (use its matching archived source):
Iteration20: [pump-guided diving](PUMP_GUIDED_DIVING.md) is a separate optional
experiment. Both comparison profiles retain iteration19's heuristic repair;
only `--pump-guided-diving` differs. Use matching source and NEW directories,
running the following sequentially:

```powershell
cmake -S . -B build-my-guidance-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-guidance-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-guidance-run/solver_cli.exe --output reports/my-guidance-gate --selective --heuristic-repair --pump-guidance
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-guidance-run/solver_cli.exe --plan reports/milp-iteration-20/MECHANISM.json --output reports/my-guidance-mechanism
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-guidance-run/solver_cli.exe --plan reports/milp-iteration-20/SCREEN.json --output reports/my-guidance-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-guidance-run/solver_cli.exe --plan reports/milp-iteration-20/WAVE.json --output reports/my-guidance-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_pump_guidance.py reports/my-guidance-screen reports/my-guidance-wave --output reports/my-guidance-audit
```

Keep source/checkers unchanged during measured batches and audit. Do not run
competing builds/reference solves during measured own solves. All old retained
dependencies below still apply. The new bounded fractional-seed checker is not
an integrality certificate; final MILP solutions are checked separately.
The root-only mechanism plan is an integration check, not a performance result.
Fixed-path `pump_guidance_parity.py` and `freeze_pump_guidance.py` preserve the
original experiment and refuse overwrite; do not use them to overwrite an
existing archive. Frozen19 remains intact. Read the report before selecting an
experimental profile; no default promotion follows merely from passing tests.

Historical iteration19 (use its matching archived source):
Iteration19: [rejected dive-candidate repair](HEURISTIC_CANDIDATE_REPAIR.md)
is experimental and requires `--repair-candidates --repair-heuristic-candidates`.
The two profiles retain selective basis refinement; only heuristic repair differs.
Keep the retained blend2 input in `datasets/miplib2017/blend2.mps`: the new C++
fixture test uses that original MPS with `tests/heuristic_rejected_point.txt`.
Use matching source and NEW directories, running these commands sequentially:

```powershell
cmake -S . -B build-my-heuristic-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-heuristic-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-heuristic-run/solver_cli.exe --output reports/my-heuristic-gate --selective --heuristic-repair
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-heuristic-run/solver_cli.exe --plan reports/milp-iteration-19/SCREEN.json --output reports/my-heuristic-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-heuristic-run/solver_cli.exe --plan reports/milp-iteration-19/WAVE.json --output reports/my-heuristic-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_heuristic_repair.py reports/my-heuristic-screen reports/my-heuristic-wave --output reports/my-heuristic-audit
```

Do not rebuild or edit source/checkers during the measured batches. References
run after all own solves in each batch. As before, the gate needs frozen16,
iteration12's reused exhaustive cases, and the public audit needs iteration14's
reader equivalence plus all dataset manifests in the plans. Keep those retained
dependencies with the project. The additional frozen18 parity and diagnostic
scripts target fixed original archive directories and refuse overwrite; they
are not generic rerun commands. Use saved plans/new paths for a new experiment.

The instrumentation-only and priority-capture binaries/source snapshots are
separate from the final repair candidate. Replaying the captured integer fixing
uses the original model plus our rejected point, never a published/reference
solution as an input. Full-wave tracing is disabled in both profiles; the
repeated screen enables its bounded diagnostic capture in both.

Historical iteration18 (use its matching archived source):
Iteration18: [selective basis refinement](SELECTIVE_BASIS_REFINEMENT.md) keeps
both accuracy modes optional. The candidate adds `--refine-basis --refine-at-checks`;
both timed profiles use `--capture-refinement` for nested work measurement.
Use the matching source, existing retained inputs and NEW output directories.
Run these commands sequentially, without concurrent task builds/reference
solves during the measured own-solver batches:

```powershell
cmake -S . -B build-my-selective-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-selective-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-selective-run/solver_cli.exe --output reports/my-selective-gate --selective
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-selective-run/solver_cli.exe --plan reports/milp-iteration-18/SCREEN.json --output reports/my-selective-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-selective-run/solver_cli.exe --plan reports/milp-iteration-18/WAVE.json --output reports/my-selective-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-selective-run/solver_cli.exe --plan reports/milp-iteration-18/HOLDOUT.json --output reports/my-selective-holdout
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_selective_accuracy.py reports/my-selective-screen reports/my-selective-wave reports/my-selective-holdout --output reports/my-selective-audit
```

Keep the source/checkers unchanged through these timed batches and their audit.
The gate uses frozen16 for disabled-mode parity and iteration12's exhaustive
inputs; public validation also requires iteration14's saved reader-equivalence
evidence and the dataset manifests named in the plans. Keep all those retained
dependencies. Warm replay is in the C++ test, not the cold-only CLI. The new
holdout inputs are retained in `datasets/milp-accuracy-holdout`; their provenance
plan predates candidate runs. They are development cases after this experiment,
not fresh holdouts for later tuning.

`profile_refinement.py` targets the separately archived Stage A, before selective
logic existed. Its archived source/binary are the correct reproduction inputs;
do not rebuild it from the final candidate and call it instrumentation-only.
The setup/freezer scripts intentionally target fixed original archive paths
and refuse overwrite. They are not commands for rerunning against old evidence.
Use new build/result directories and saved plans for a new experiment.

Historical iteration17 (use its matching archived source):
[sparse basis refinement](SPARSE_BASIS_REFINEMENT.md) is experimental
and opt-in. These commands use fresh output directories; do not rerun a setup
or freezer against an existing archive. Run each command sequentially.

```powershell
cmake -S . -B build-my-accuracy-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-accuracy-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/sparse_accuracy_gate.py --binary build-my-accuracy-run/solver_cli.exe --output reports/my-accuracy-gate
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-accuracy-run/solver_cli.exe --plan reports/milp-iteration-17/SCREEN.json --output reports/my-accuracy-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-accuracy-run/solver_cli.exe --plan reports/milp-iteration-17/WAVE.json --output reports/my-accuracy-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_sparse_accuracy.py reports/my-accuracy-screen reports/my-accuracy-wave --output reports/my-accuracy-audit
```

Both timed profiles use the same executable and unchanged resource budgets;
only the candidate has `--refine-basis`. The gate also checks disabled-option
parity against the frozen iteration16 executable. The saved warm-basis replay
is part of `solver_sparse_accuracy_tests`, not the cold-only MPS CLI interface.
The full gate also uses iteration12's retained exhaustive MPS cases; the public
audit uses iteration14's lattice-reader equivalence and the three dataset
manifests named in `WAVE.json`. Keep those dependencies alongside the archive.

Iteration16: [incumbent-gated cuts](INCUMBENT_GATED_CUTS.md) preserve first-feasible
cut allocation. Protection requires `--adaptive-cut-rounds --cut-after-incumbent`;
neither option is a default. Use matching source, retained inputs and new output
directories. The predeclared screen repeats each pair twice; the wave contains
all24 retained development models and is not an untouched holdout experiment.

```powershell
cmake -S . -B build-my-incumbent-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-incumbent-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/incumbent_cut_gate.py --binary build-my-incumbent-run/solver_cli.exe --output reports/my-incumbent-preflight --quick
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/incumbent_cut_integration.py --binary build-my-incumbent-run/solver_cli.exe --output reports/my-incumbent-analytic
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-incumbent-run/solver_cli.exe --plan reports/milp-iteration-16/SCREEN.json --output reports/my-incumbent-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-incumbent-run/solver_cli.exe --plan reports/milp-iteration-16/WAVE.json --output reports/my-incumbent-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/incumbent_cut_gate.py --binary build-my-incumbent-run/solver_cli.exe --output reports/my-incumbent-gate
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_incumbent_cuts.py reports/my-incumbent-screen reports/my-incumbent-wave --output reports/my-incumbent-audit
```

Run sequentially, with no competing task builds/tests/reference work during
own-solver timings. References run afterward. Keep the current file hashes
unchanged through all timings and their final audit; documentation may be
updated afterward. Gate dependencies include frozen15, iteration12's100 reused
MPS cases, iteration14's lattice-reader equivalence, and all three public dataset
manifests. A new build has a new binary identity; do not rebuild old archives.

`diagnose_mas74.py` deliberately uses the separately frozen15 executable and
its source manifest, not the current candidate. It writes a fixed fresh archive
directory and refuses overwrite. Its saved ablations/cold replays are diagnostic
evidence; cold LP solves do not replay the captured warm pivot sequence. Setup
and freezer scripts also target the original evidence layout, not generic
commands to overwrite an archive. Use the saved plans and fresh directories
for a new candidate run instead of rerunning setup against existing files.

Historical iteration15 reproduction (use its matching archived source):
Iteration15: [selective root-cut continuation](ADAPTIVE_CUT_ROUNDS.md) is
experimental and off by default. Its first Binkar screen/repeats regress, so
the preserved five-round default is retained. Use the matching source, a NEW
build/output directory, and the already retained plans and datasets:

```powershell
cmake -S . -B build-my-cut-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-cut-run -j3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/cut_policy_gate.py --binary build-my-cut-run/solver_cli.exe --output reports/my-cut-preflight --quick
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-cut-run/solver_cli.exe --plan reports/milp-iteration-15/SCREEN.json --output reports/my-cut-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-cut-run/solver_cli.exe --plan reports/milp-iteration-15/REPEATS.json --output reports/my-cut-repeats
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-cut-run/solver_cli.exe --plan reports/milp-iteration-15/WAVE.json --output reports/my-cut-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-cut-run/solver_cli.exe --plan reports/milp-iteration-15/HOLDOUT.json --output reports/my-cut-holdout
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/cut_policy_gate.py --binary build-my-cut-run/solver_cli.exe --output reports/my-cut-gate
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_cut_stop_integration.py --binary build-my-cut-run/solver_cli.exe --output reports/my-cut-analytic-stop
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_cut_policy.py reports/my-cut-screen reports/my-cut-repeats reports/my-cut-wave reports/my-cut-holdout --output reports/my-cut-audit
```

Run sequentially; no builds, other solver experiments or reference checks
during measured own solves. All own runs precede reference work within each
batch. Preserve errors, timeouts, source/plan/input hashes and captured round
decisions. Never edit hashed source/checkers/tests during a run or rebuild an
archived build directory. A rebuild has its own binary identity.

Dependencies include the two prior public dataset manifests, the three models
in `datasets/milp-cut-policy-holdout`, frozen iteration14's executable, the 100
iteration12 exhaustive MPS models/results, and the saved iteration15 reference
equivalence and iteration14 lattice-reader equivalence summaries. The source
archive excludes bulk datasets. Copy matching evidence inputs when reproducing
elsewhere and adjust Python/compiler paths. Setup/freezer scripts refuse to
overwrite their original archive directories; they are not cleanup commands.
Reference limits are configured at 5s with a 150s process watchdog to include
parsing and point checks. These are not equal-budget reference speed benchmarks.

Historical iteration14 reproduction (use its matching archived source):
Iteration14 adds optional [exclusive work attribution and root cut-round
control](MILP_WORK_BUDGETS.md). The default is still five rounds; the tested
one-round policy has a serious p0282 regression and is not promoted. Build
from the matching source in a NEW directory, with the local reference Python
environment and retained datasets available:

```powershell
cmake -S . -B build-my-work-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-work-run -j4
ctest --test-dir build-my-work-run --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-work-run/solver_cli.exe --plan reports/milp-iteration-14/SCREEN.json --output reports/my-work-screen
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-work-run/solver_cli.exe --plan reports/milp-iteration-14/WAVE.json --output reports/my-work-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/run_milp_work.py --binary build-my-work-run/solver_cli.exe --plan reports/milp-iteration-14/REPEATS.json --output reports/my-work-repeats
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/work_final_gate.py --binary build-my-work-run/solver_cli.exe --output reports/my-work-gate
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_milp_work.py reports/my-work-screen reports/my-work-wave reports/my-work-repeats --output reports/my-work-audit
```

Run sequentially. Do not run builds, tests or references during the own-solver
timings. Each harness completes all own timings before independent reference
checks and saves the plan, inputs' hashes, binary identity, and source/checker
copies. Existing hashed files must not change during a run. Output directories
must be new; a failed experiment is retained, not overwritten.

The diagnostic build and its preflight are separate historical artifacts.
Do not rebuild `build-milp-iter14-diag` against candidate sources. The audit
uses `reports/milp-iteration-14/reader-equivalence/SUMMARY.json` and verifies the
current checker hash; retain that evidence alongside the 21 dataset inputs.
The final gate also needs the frozen iteration13 binary and the 100 exhaustive
MPS models/results under iteration12. The source-only archive intentionally
excludes these bulk evidence inputs. On another machine, preserve these relative
paths and use its Python/compiler paths; a rebuild has a new binary identity.
The freezer is for the original completed evidence layout, not a generic
command to overwrite that archive with a new run.

The recorded iteration14 wave also has two retained `eil33-2` independent
reference-process timeouts. Its saved `supplemental-references` directory retries
only those checks with the SAME five-second configured HiGHS solve limit and
unchanged checker, but a 150-second external process watchdog instead of 25.
The checker can spend substantial time checking a large saved vector after
optimization. A configured solver time limit is not a hard process wall limit.
The own-solver outputs and original pending categories are never overwritten.
To include those saved supplemental checks when re-auditing the ORIGINAL run
directories, pass `--supplemental reports/milp-iteration-14/supplemental-references`
to the auditor with a fresh output directory. Those records cannot be applied
to a different run: input/result hashes must match. New runs retain their own
pending checks until separately validated; the auditor does not count an
unvalidated vector as an independently checked point.

Historical iteration13 reproduction (use its matching archived source):
optional [separate frontier ranking](MILP_FRONTIER.md),
`--objective-lattice --raw-lp-priority`. Neither setting is enabled by default.
The checked source and binary are frozen separately in
`reports/milp-iteration-13/FINAL_STATE.json`. Use a NEW build/output directory;
never rebuild historical directories against current sources. From the matching
project source root, with the existing local reference environment and datasets:

```powershell
cmake -S . -B build-my-frontier-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-frontier-run -j4
ctest --test-dir build-my-frontier-run --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_frontier.py --binary build-my-frontier-run/solver_cli.exe --output reports/my-frontier-nodes --node-screen --models gt2 lseu mod008 misc03 --profiles control lattice raw --repeats 2
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_frontier.py --binary build-my-frontier-run/solver_cli.exe --output reports/my-frontier-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_frontier.py --binary build-my-frontier-run/solver_cli.exe --output reports/my-frontier-repeats --models mod008 gt2 --profiles control lattice raw --repeats 3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_frontier.py --binary build-my-frontier-run/solver_cli.exe --manifest datasets/milp-frontier-holdout/manifest.json --output reports/my-frontier-holdout
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/frontier_final_gate.py --binary build-my-frontier-run/solver_cli.exe --output reports/my-frontier-gate
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_milp_frontier.py reports/my-frontier-nodes reports/my-frontier-wave reports/my-frontier-repeats reports/my-frontier-holdout --output reports/my-frontier-audit
```

Run sequentially, with no reference work or builds during own timed solves.
The four holdouts were downloaded with `scripts/fetch_frontier_holdout.py`,
which refuses to overwrite the existing manifest/models. Retain failures and
download provenance. The final gate also uses the 100 frozen iteration12
generated MPS inputs. On a clean machine, copy those matching datasets/evidence
inputs; the source-only archive intentionally excludes bulk benchmark files.
Hashes reject source/checker/model drift. A rebuilt binary has a new identity.
The current shared-desktop timings are not clean speed comparisons against
earlier versions; see the iteration13 timing caveat and result ledger.

Historical iteration12 reproduction (use its matching archived source):
guarded [objective-lattice bounds](OBJECTIVE_LATTICE.md),
opt-in via `--objective-lattice`. It retains iteration11's corrected reader.
Use a NEW build directory; never rebuild a preserved historical directory
against current sources. The frozen binary/source identity is recorded in
`reports/milp-iteration-12/FINAL_STATE.json`. From the current project root:

```powershell
cmake -S . -B build-my-lattice-run -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-my-lattice-run -j4
ctest --test-dir build-my-lattice-run --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_objective_lattice_generated.py --binary build-my-lattice-run/solver_cli.exe --output reports/my-lattice-generated
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_objective_lattice.py --binary build-my-lattice-run/solver_cli.exe --output reports/my-lattice-wave
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_objective_lattice.py --binary build-my-lattice-run/solver_cli.exe --output reports/my-lattice-repeats --models mod008 misc03 --repeats 3
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_objective_lattice_runs.py reports/my-lattice-wave reports/my-lattice-repeats --output reports/my-lattice-audit
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/objective_lattice_final_gate.py --binary build-my-lattice-run/solver_cli.exe --output reports/my-lattice-final-gate
```

These scripts require the already downloaded wave1 manifest/models and the
existing local reference Python packages. Run commands sequentially. Timed
own solves precede reference work; timeouts stay on the ledger. Each harness
hashes the current core source, binary and relevant checkers and rejects
changed evidence. Do not pass an old binary with unrelated current source.
The audit must run against the same unchanged source/checkers as the timing.

Historical iteration11 reproduction (use its matching archived source):

Latest corrected input reader: `build-milp-iter11`. Follow the
[robustness program](MILP_ROBUSTNESS.md) and [MPS domain contract](MPS_DOMAIN_CONTRACT.md).
Build with the same CMake configuration below using `build-milp-iter11` as the
build directory. For the already downloaded first wave, run from the project root:

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/milp_robustness.py --binary build-milp-iter11/solver_cli.exe --source . --output reports/my-new-breadth-run --limit 30 --reference-limit 5
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/check_mps_marker_contract.py --binary build-milp-iter11/solver_cli.exe --output reports/my-new-marker-run --require-pass
```

The `--source` directory must correspond to the supplied binary. The ledger
hashes both; it does not itself build the executable. Use fresh output paths.
The manifest is `datasets/milp-robustness-wave1/manifest.json`; the fetcher only
creates a new wave directory and refuses to overwrite an existing download.
All own timings precede reference checks. Reference timeouts remain explicit;
the reference worker is not an equal-budget performance comparison. Older
reproduction recipes below retain their original input-reader limitations.

Preserved iteration10 candidate: `build-milp-iter10`. Its archived source and
binary are identified by `reports/milp-iteration-10/FINAL_STATE.json`. From the
project root, with the existing local reference Python environment:

```powershell
cmake -S . -B build-milp-iter10 -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-milp-iter10 -j4
ctest --test-dir build-milp-iter10 --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_reduced_bound_lp.py --output reports/my-new-reduced-pair --limit 180 --models p0033 binkar10_1 blend2 --generated
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_reduced_bound_run.py reports/my-new-reduced-pair --binary build-milp-iter10/solver_cli.exe --output reports/my-new-reduced-audit
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_reduced_bound_reference.py --binary build-milp-iter10/solver_cli.exe --output reports/my-new-mixed-reference
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/check_application_reduction.py --binary build-milp-iter10/solver_cli.exe --output reports/my-new-application-checks
```

Use fresh output paths; never overwrite preserved evidence. Complete timings
before independent/reference work. Add `--repeats 3` for repeated full pairs,
or `--root-only --nodes 1 --models binkar10_1 --repeats 3` to the validation
command for the root-only protocol. Both `--reduced-bound-lp` and
`--late-reduced-bound-lp` are opt-in MILP options; see
[method and safeguards](REDUCED_BOUND_LP.md). Earlier build examples below
remain historical reproduction recipes, not instructions to replace the latest archive.

```powershell
cmake -S . -B build-current-local -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-current-local -j 4
ctest --test-dir build-current-local --output-on-failure
./build-current-local/solver_cli.exe examples/blending.lpmini --json
./build-current-local/solver_cli.exe examples/production.mps --milp --json
./build-current-local/solver_cli.exe examples/dispatch.qplib --json
./build-current-local/solver_cli.exe datasets/qplib/9002.qplib --json --time-limit 30
```

On Linux omit the generator argument and `.exe` suffix. The core needs a C++11
compiler and CMake; OpenMP is detected optionally. GPU builds additionally need
NVIDIA hardware and CUDA, using `-DSOVEREIGN_ENABLE_CUDA=ON`.

## CLI controls

`--json`, `--time-limit SECONDS`, `--iteration-limit N`, `--tolerance VALUE`,
`--lp-method sparse|dense`, `--milp`, `--node-limit N`, `--gap VALUE`,
`--no-presolve`, `--no-heuristics`, `--no-pump`, `--no-cuts`, `--no-scaling`,
`--threads N`, `--backend cpu|cuda`.

MILP experiments also support `--branching fractionality|reliability`,
`--lp-recovery`, `--improve-incumbent`, `--repair-candidates`,
`--capture-lp-failure` and `--capture-rejected-candidates`. Experimental dense
repair is opt-in; the repaired-node proof-safety fix applies to both modes.
Iteration05 also adds `--neighborhood guided|diversified`, `--pace-neighborhood`
and `--capture-neighborhood`. See [method and budgets](MILP_NEIGHBORHOOD_METHOD.md).
Selection and pacing remain opt-in; neither enables `--improve-incumbent` by itself.
Iteration06 adds `--neighborhood reserved`: a budget-reserved coupled binary
search, also opt-in. See [schedule, method and proof boundary](MILP_RESERVED_SEARCH.md).
Use a fresh build/output directory rather than rebuilding any archived iteration.
`--binary-meet` separately enables a bounded root incumbent search for small
binary models with separable continuous variables. Unsupported structures fall
back to the general solver. See [scope and verification](MILP_BINARY_MEET.md).
Iteration07 adds the distinct `--binary-proof` and `--binary-proof-work N`
controls. Only a guarded, completed integer search can certify its strict
small-model subset. See [exact scope, budgets and independent checker](MILP_BINARY_PROOF.md).
Iteration08 adds opt-in `--lifted-covers` for small binary capacity rows. It is
disabled by `--no-cuts`; see [validity checks, limits and comparison runner](MILP_LIFTED_COVERS.md).
`--late-lifted-covers` instead delays them until a single half-time full-domain
restart, preserving the same-run incumbent and consumed budgets. These are
separate experiments, neither enabled by default.

Iteration12/13 add `--objective-lattice`, `--raw-lp-priority` and
`--capture-frontier`. The first strengthens supported numerical proof bounds;
the second changes queue ranking with separate proof-minimum accounting; the
third enables bounded diagnostic replay. They are independent opt-in flags.
The raw experiment combines the first two, not capture, in performance runs.
See [frontier scope and trace limits](MILP_FRONTIER.md).

## Local focused MILP comparison

Use the project's existing Python/reference dependencies. On this machine the
interpreter is `C:/Users/Admin/anaconda3/python.exe`; the separate reference
worker supports the pinned wheels in `tools/reference/python`.

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_focus.py --build build-current-local --output reports/my-new-local-milp-run --limit 180 --nodes 250000 --reference-limit 30 --experiment reserved
```

The output directory must not exist. This runs CTest and240 generated checks,
then six sequential hard runs with equal limits, followed by independent
references/candidate checks. Optional `--models blend2` narrows a diagnostic
iteration; full comparisons retain all three hard cases. Read the saved
`summary.json`, `results.json`, raw candidates/references and incumbent traces.
Time limits are incomplete outcomes, not evidence of infeasibility.

After all timed runs finish, audit final incumbents and captured accepted repairs
again against the original MPS files, also verifying run identity and traces:

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_local_milp.py reports/my-new-local-milp-run --binary build-current-local/solver_cli.exe --output reports/my-new-local-milp-audit
```

This output directory must also be new. Captures include only the first four
rejections per run; objective-only uncaptured history is not a full vector audit.
Captured neighbourhood calls also retain their last improved vector on models
up to10000 variables. Use `--experiment neighborhood` for the selection-only
comparison or `--experiment repair` for the earlier repair comparison. A
`--strategies paced` screen is not a replacement for paired/repeated evidence.
Preserve older build directories; do not rebuild historical binaries in place.

LP/MILP execution is sequential; `--threads` applies to sparse QP computation.
CUDA is supported for box QPs only. Thread count is a requested configuration;
very small CPU kernels intentionally remain serial to avoid launch overhead.

For a C++ application, include `sparse_lp.hpp`, `milp.hpp` or `qp.hpp` and link
the CMake `solver` target. `solve_sparse_lp(problem, options, &previous.basis)`
requests basis reuse. `solve_milp` and `solve_qp_admm` accept their corresponding
option structures. `accelerated_qp.hpp` exposes the CPU/CUDA box path.

## Full evidence run

### Local compact-equality experiment

The preserved iteration09 CPU build is `build-milp-iter9b`. Use
`--compact-equalities` for immediate sparse-LP activation, or MILP-only
`--late-compact-equalities` to activate at the full-domain half-time cut
restart. The latter includes delayed lifted cuts. Both remain optional.

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_compact_equalities.py --build build-milp-iter9b --output reports/my-new-delayed-equality-run --late-compact --limit 180 --models p0033 binkar10_1 --generated
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_compact_run.py reports/my-new-delayed-equality-run --binary build-milp-iter9b/solver_cli.exe --output reports/my-new-delayed-equality-audit
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_compact_reference.py --binary build-milp-iter9b/solver_cli.exe --output reports/my-new-independent-equality-checks
```

Every output path must be new. Run independent checks after timed comparisons.
Use `--profiles compact --limit 600` for a separate, longer attempt; its larger
budget must not be compared with 180s as evidence of speedup. See
[method and limitations](COMPACT_EQUALITY_LP.md) and the
[versioned results](../reports/milp-iteration-09/REPORT.md).

### Broader LP/MILP/QP validation

Reference environments need HiGHS, OSQP, NumPy, SciPy and psutil. Existing local
reference wheels are supported. The simplified Kaggle notebook uses its current
Python interpreter and installs reference packages there with standard pip.

```powershell
python scripts/industrial_cases.py
python scripts/fetch_v2.py
python scripts/validate_v2.py --build build-current-local --output reports/my-new-v2-run --limit 30 --sizes 10000 100000 1000000 --repeats 3
```

The output directory must be new. The runner preserves every public failure and
records all scale repetitions. It emits `summary.json`, `benchmarks.json`,
`scale.json`, `metadata.json`, `REPORT.md`, CTest logs, candidate solutions,
reference results and generated regression inputs. The preserved V1 generators
use an executable alias at `build/solver_cli.exe`, including on Linux.

The numerical library references are isolated from the C++ core. Do not compare
raw process times as kernel times: process times include startup/imports, whereas
the reported solve interval includes solver setup, transfers and solution checks.
RSS sampling every 20 milliseconds is an observed lower bound on peak memory.

## Separate Kaggle notebook — GPU experiments only

For an actual CUDA/QP experiment, package only after its CPU validation succeeds.
The following preserved QP-iteration example describes the GPU workflow, not a
request to send CPU-only work to Kaggle:

```powershell
python scripts/check_v2_evidence.py reports/qp-iteration-01/validated-cpu --build build-qp-iter1
python scripts/package_kaggle.py --evidence reports/qp-iteration-01/validated-cpu --output ../kaggle_delivery/qp_iteration_01
python scripts/check_kaggle_package.py ../kaggle_delivery/qp_iteration_01
```

This keeps the original V2 delivery unchanged. Its `.ipynb` stays below 1 MB. Upload the
companion `SIH26119_V2_source.zip` as a private Kaggle dataset and attach it
using Add Input. The source and cached public inputs are loaded from that
dataset automatically, whether zipped or unpacked. Internet is needed to install
the reference packages. Select an NVIDIA GPU before running it. There is no
second virtual environment and no manual path editing.

The notebook has two code cells: unpack, then install/build/run/export. It runs
the same CPU regressions and public cases, with CPU/multicore/GPU planted scale
checks at 1,000, 100,000 and 1,000,000 variables. This quick iteration uses one
timing repetition; repeated speedup measurements and additional public GPU
cross-checks can follow. Without a GPU/compiler it produces clearly labeled
CPU-only results. Installation/build/check failures also produce a diagnostic
`sih26119_kaggle_results.zip`. Return that ZIP to guide the next iteration.

The million-variable scale family is a synthetic tridiagonal convex box QP with
a planted optimum. It is useful for memory and accelerator measurements, but
does not demonstrate million-variable LP, MILP or general industrial QP support.
