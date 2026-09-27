# Sovereign optimization solver

## V2 candidate — current development version

Latest continuous checkpoint: the [weak-pivot safeguard](reports/lp-pivot-iteration-01/REPORT.md)
adds opt-in `--stable-primal-ratio`. Both stable-only and stable/refined profiles
complete all 16 checked LPs, resolving standard-form bandm under those profiles.
Defaults remain unchanged. The full gate passes 27 CTest groups, 176 Python
tests, 400 generated MILPs, 100 exhaustive cases and four feature-off parity
checks. The [numerical diagnosis](reports/numerical-diagnosis-01/REPORT.md)
preserves the exact singular-basis witness, failed refresh attempt and QP 9002
trace. Its relative/absolute accuracy limitation remains unresolved.

Previous MILP checkpoint: [iteration 29](reports/milp-iteration-29/REPORT.md) adds an
experimental verified private dual certificate. It avoids repeated phase one
in saved lotsize LPs but gains no integer coverage or completions in the
repeated screen: both profiles have 22/24 checked points and four completions.
The feature stays off. The current-source [LP/QP check](reports/cpu-validation-2026-09-17/REPORT.md)
and [compact LP profile](reports/lp-bandm-01/REPORT.md) give 16/16 checked LP
completions with one explicit profile, versus 15/16 by default. Three default
QPs pass relative KKT checks, but 9002's absolute violation remains about 2.381;
tighter probes do not resolve it. Defaults remain unchanged.

Earlier broader MILP evaluation: [iteration28](reports/milp-iteration-28/REPORT.md), after
resuming the objective's four MILP slots. The retained staged profile has
**26/27 useful development outcomes and ten optimization completions**.
Six untouched public models all return checked feasible points, with **zero
completions** in30 seconds. Lotsize and reliability/quality gaps remain.
The six-case default-profile check also passes; defaults are unchanged.

Stable ranking ([25](reports/milp-iteration-25/REPORT.md)), alternate reserve
([26](reports/milp-iteration-26/REPORT.md)) and deferred restart
([27](reports/milp-iteration-27/REPORT.md)) were tested and rejected for promotion.
The final39 public/default records and37 vectors pass validation;24 artificial
answers pass enumeration and an explicitly canonicalized reference after a
[duplicate-objective input mismatch](docs/MPS_DUPLICATE_OBJECTIVES.md).
Fifteen resource/status checks and an isolated-folder runtime smoke pass.

See the [codebase review](docs/CODEBASE_REVIEW_2026_09_17.md),
[full ledger](reports/milp-iteration-28/MODEL_LEDGER.md),
[reproduction guide](docs/RESUMED_RUN_GUIDE.md) and
[tested private-LP hypothesis](docs/NEXT_PRIVATE_LP_HYPOTHESIS.md).
This is a frozen experimental evaluation profile, not submission readiness.

Development priority is now [broad MILP robustness](docs/MILP_ROBUSTNESS.md).
Historical [iteration24](reports/milp-iteration-24/REPORT.md) tests an optional
[objective-only private stage](docs/PUMP_DISTANCE_STAGE.md) before branch tightening.
The wave returns **25 checked solutions plus one cross-checked infeasible case**:
26/27 useful outcomes, but only ten completions (two restricted exact, eight
numerical/tolerance). Lotsize remains unresolved. Misc07 gains a valid solution
in all three paired observations, with a large open gap. Danoint fails both
staged screen runs despite succeeding in the wave; Binkar's wave quality worsens.
The new option remains off by default, and no universal robustness claim follows.

All 98 public records and 84 final vectors pass validation. Gates pass 24 CTest
groups, 176 Python tests, 320 generated runs, 100 retained cases, parity and
MIN/MAX/domain integration. Sixteen saved LPs pass 48 independent replay-point
checks. Lotsize's parent/child LP pivot savings do not solve its MILP; misc07's
gain also exposes near-tie branch sensitivity. See the
[complete ledger](reports/milp-iteration-24/MODEL_LEDGER.md) and
[next bounded work](reports/milp-iteration-24/NEXT_STEP.md). CPU-local, no upload needed.

Previous [iteration23](reports/milp-iteration-23/REPORT.md) tests optional
[private pump-to-distance basis handoff](docs/PUMP_DISTANCE_REOPT.md).
**No coverage gain:** both profiles return 24 checked feasible solutions plus
one cross-checked infeasible status; misc07/lotsize remain unresolved. Control
has ten completions, candidate nine (mod008 misses completion at the same
objective). The private LP path does not execute on mod008, so the measured
loss does not establish mechanism causation. Keep the new flag off by default.
All 94 paired records pass validation; ten private LP replays pass 30 independent
point checks. Specific LP pivot savings do not imply better MILP coverage.
The gate passes 23 CTest groups, 170 Python tests, 320 generated runs and 100
retained exhaustive cases, plus parity and MIN/MAX/domain integration.
See the [complete ledger](reports/milp-iteration-23/MODEL_LEDGER.md) and
[next hypothesis](reports/milp-iteration-23/NEXT_STEP.md). CPU-local; no upload needed.

Previous [iteration22](reports/milp-iteration-22/REPORT.md) adds optional
[guarded primal reoptimization inside the pump](docs/PUMP_PRIMAL_REOPT.md).
The 27-model wave returns 24 checked feasible solutions plus one cross-checked
infeasible status; misc07/lotsize remain unresolved. Ten models complete, not
25 optimality proofs. Danoint gains a checked solution in all three comparisons,
and rout's objective improves from 1703.47 to 1293.19. Mas74 regresses, so the
new option remains off by default. No best-of-profile union is reported.

All 90 paired records pass validation. The gate passes 22 CTest groups, 166
Python tests, 320 generated runs and 100 reused exhaustive cases. Fourteen
actual private-LP replays pass 42 independent point checks; frozen21/inactive
parity and actual MIN/MAX/domain integration also pass. Same measured/final
binary; frozen21 is preserved. See the [27-model ledger](reports/milp-iteration-22/MODEL_LEDGER.md)
and [next-step diagnosis](reports/milp-iteration-22/NEXT_STEP.md).
CPU work remains local; no Kaggle upload is needed.

Previous [iteration21](reports/milp-iteration-21/REPORT.md) tests optional
[private distance-objective diving](docs/PUMP_DISTANCE_DIVING.md). Eil33-2 and
rout return checked solutions in all three candidate observations versus none
in their paired controls. The wider wave also loses misc07: candidate 23 checked
solutions versus guided control 22, with 10 completions each and one separately
cross-checked infeasible model. Lotsize/danoint remain without points. This is
mixed progress, not 27/27 handled or proved; the option remains off by default.

All 86 paired records and 65 returned vectors pass the final audit. The final
build additionally fixes a reproduced presolve-off empty-integer-domain error,
and passes 21 CTest groups, 162 Python tests, generated/exhaustive gates, parity
and actual MIN/MAX private-dive checks. The report explicitly separates the
measured binary from that final guard; earlier timings were not rerun on it.
Frozen20 is preserved. See the [complete ledger](reports/milp-iteration-21/MODEL_LEDGER.md)
and [three-iteration checkpoint](reports/milp-iteration-21/NEXT_STEP.md).
CPU work stays local; no Kaggle upload is needed.

Prior [iteration20](reports/milp-iteration-20/REPORT.md) tests optional
[pump-guided diving](docs/PUMP_GUIDED_DIVING.md), keeping a checked fractional
pump point as guidance for one existing dive mode. It changes neither proof
bounds nor resource allowances. The repeated six-model screen shows no new
first-feasible coverage: lotsize, eil33-2, danoint and rout still have no point;
blend2's repair and p0201's completion survive. The gate passes 20 CTest groups,
152 Python tests, 320 generated runs and 100 retained exhaustive cases. See the
full report for the complete paired wave and decision; the new feature remains
off by default. Frozen19 is preserved, and CPU work stays local.

The wave returns 23 checked points versus control's 21, but both complete only
9 models and the same three targets remain without points. Gt2's feasible
objective improves from 42649 to 35673 in three paired observations; pk1
regresses from about 20 to 30. Misc07/rout wave gains are not repeatable
first-feasibility guarantees. See the
[27-model ledger](reports/milp-iteration-20/MODEL_LEDGER.md). This remains mixed
performance, not a new default or 27/27 optimality proof.

Prior [iteration19](reports/milp-iteration-19/REPORT.md) adds optional
[repair of rejected near-integer dive candidates](docs/HEURISTIC_CANDIDATE_REPAIR.md).
The retained blend2 point is correctly rejected because it violates original
rows, but its integer choices admit a checked continuous solution. The new
`--repair-candidates --repair-heuristic-candidates` path repairs that point inside
the existing dive/shared repair budget. It exports no proof bound and does not
loosen tolerances. Disabled behavior retains fixed-node parity with frozen18.

The gate passes 19 CTest groups, 140 Python tests, 320 generated MILP runs and
100 retained exhaustive cases. The 27-model wave returns 23 checked points with
repair versus 21 for control; both have 9 optimality/tolerance completions.
Repair leaves lotsize, eil33-2 and danoint without a point. Neos859080 is
cross-checked infeasible, including a separate same-model reference check for
the repair record. Blend2's direct first-feasible gain repeats 3/3; rout's
extra point had zero repairs and is not credited as an algorithmic gain.
See the [complete ledger](reports/milp-iteration-19/MODEL_LEDGER.md) and full
report for all failures and open gaps. The option stays
experimental and off by default. Use `build-milp-iter19`, the
[reproduction instructions](docs/V2_REPRODUCE.md), and
[next work](reports/milp-iteration-19/NEXT_STEP.md). CPU work remains local;
no Kaggle upload is needed. Frozen18 and both diagnostic builds are preserved.

Prior [iteration18](reports/milp-iteration-18/REPORT.md) adds optional
[selective basis checks and correction-work measurement](docs/SELECTIVE_BASIS_REFINEMENT.md).
Use `--refine-basis --refine-at-checks` for selective checking, or the original
`--refine-basis` alone for always checking. Neither is promoted to default.
The captured cold/warm mas74 LP repair survives with 3 attempts / 2 accepted
corrections in either replay, with unchanged tolerances and independent checks.
The full gate passes 17 CTest groups, 126 Python tests, 320 generated MILP runs,
100 reused exhaustive cases and 24 transformed LP checks across both modes.

The public experiment retains all 24 development models and adds three
predeclared new instances. Both profiles complete 10/24 development models;
selective returns checked points on 20 versus 19 for control. Eil33-2 returns
points in the repeated screen but in neither wave run, so its first-feasible
problem remains. Binkar's selective point/gap also regress. See the report for
paired completions, first-point
outcomes, gaps and regressions; numerical repair alone is not a universal
performance gain or proof of every public MILP. Use `build-milp-iter18` and
the [reproduction commands](docs/V2_REPRODUCE.md). The separately archived
instrumentation-only control and frozen17 remain preserved. CPU work stays
local; no Kaggle upload is needed. See [next work](reports/milp-iteration-18/NEXT_STEP.md).

Prior [iteration17](reports/milp-iteration-17/REPORT.md) adds opt-in
[sparse basis refinement](docs/SPARSE_BASIS_REFINEMENT.md), enabled by
`--refine-basis`. It repairs the retained mas74 cold and original warm-basis
LP failures at unchanged tolerances; both points pass independent checks at
about 2.91e-11 absolute violation. All three refined full mas74 runs avoid LP
recovery and unresolved nodes, but retain about 15.7% gaps. This is a numerical
reliability gain, not a proof of full mas74 or consistently better objectives.

The 24-case paired wave completes 9 control cases versus 8 refined cases
(both include 2 restricted exact proofs). Refinement gains a point on misc07
but loses one on eil33-2; p0201 retains a small gap instead of completing.
The option is **not promoted to default**. All 52 public experiment records
pass re-audit, including 44 returned points. The gate passes 15 CTest groups, 115 Python units,
320 generated runs, 100 reused exhaustive cases, 12 transformed LP equivalents
and four disabled-option parity comparisons. All public cases remain
development data, not fresh holdouts or a competition-percentile claim.
Use `build-milp-iter17`; see [next work](reports/milp-iteration-17/NEXT_STEP.md).
CPU work stays local, with no Kaggle upload required.

Prior [iteration16](reports/milp-iteration-16/REPORT.md) adds optional
[first-feasible protection for adaptive cuts](docs/INCUMBENT_GATED_CUTS.md).
The two Binkar screen pairs retain independently checked points, but both have
worse gaps than their five-round controls. The guarded rule is not promoted;
all defaults and the rejected ungated mode remain preserved. Analytic MIN/MAX
integrations independently check both protected and post-incumbent stop paths.

Separate frozen15 diagnostics reproduce mas74's sparse LP accuracy failure:
about 9.77e-5 absolute violation versus dense recovery's 4.37e-11. Exhausted
recovery followed by restart into two unresolved children explains its early
exit; disabling the late LP transforms does not fix it. No recovery algorithm
or tolerance change is mixed into this candidate. Use `build-milp-iter16` and
see [the numerical-accuracy work next](reports/milp-iteration-16/NEXT_STEP.md).
CPU work stays local; no Kaggle upload is needed.

The 60 public experiment runs cover 24 retained development models, with no
fresh holdouts. Both wave profiles finish 10 optimal/gap cases (2 exact-subset,
8 numerical), return 10 feasible limits, 1 unresolved checked point, 2 no-point
limits and 1 cross-checked infeasible termination. There is no broad completion
gain. Validation passes 14 CTest groups, 115 Python tests, 320 generated
runs, 100 reused exhaustive MPS cases and 12 separate analytic CLI integrations.
All 60 public records pass re-audit, including 54 final points and 12 source
incumbents behind cut decisions. The diagnosed sparse numerical issue is not
fixed in this archive.

Prior [iteration15](reports/milp-iteration-15/REPORT.md) adds optional
[selective cut continuation and independently replayed decisions](docs/ADAPTIVE_CUT_ROUNDS.md).
The completed 66 public experiment runs cover 24 distinct models, including
3 fresh cases. The new policy is NOT promoted: Binkar has no adaptive point
in all four paired runs, while every control finds a checked point. In the
21-case wave both profiles complete 10; adaptive loses one additional feasible
result. Fresh cases add a cross-checked infeasible result, a feasible time limit
and an unresolved-relaxation outcome with a checked point. No universal proof
or broad performance gain is established. Five rounds remain the default.
Use `build-milp-iter15`; all CPU work remains local, with no Kaggle upload needed.
The final gate passes 13 CTest groups, 100 Python units, 320 generated runs,
100 reused exhaustive cases and four additional analytic stop integrations.
All 66 public records pass re-audit, including 56 checked final points and
176 replayed cut decisions; there are no pending reference point checks.
See [next work](reports/milp-iteration-15/NEXT_STEP.md) and the
[submission assessment](docs/SUBMISSION_ASSESSMENT.md).

Prior iteration14 adds optional [phase/work attribution and root cut-round
controls](docs/MILP_WORK_BUDGETS.md), with preserved defaults and separate source,
binary and result archives. Its matched 21-model 30s wave completes 10 cases
under the five-round baseline and 9 under the one-round candidate. After linked
independent checks, the baseline has 9 further feasible limits and 2 no-point
limits; candidate has 10 and 2. These profiles include the opt-in raw/lattice
features, not just the CLI's default settings.

Three Binkar repeat pairs reduce median gap from 1.56% to 1.42%, but candidate
loses one pair and seriously worsens p0282. The one-round policy is NOT promoted;
five rounds remain the default. All 12 CTest groups, 88 Python tests, 240 generated
regression runs and 100 reused exhaustive cases pass. The saved-result audit
covers 59 public runs on 21 distinct models, including 51 checked final points.
Two independent-check watchdog timeouts are preserved and separately resolved.
See [iteration14 evidence](reports/milp-iteration-14/REPORT.md), using
`build-milp-iter14`, and [the next bounded experiment](reports/milp-iteration-14/NEXT_STEP.md).
This improves measurement and tested controls, not universal MILP proof or
industrial readiness. All CPU work is local; no Kaggle upload is needed.

Prior iteration13 adds optional [separate search ranking and proof accounting](docs/MILP_FRONTIER.md),
with randomized, exhaustive and independent event-replay checks. Its fresh
17-model 30s wave completes 7 cases in BOTH compared policies: 2 restricted
exact proofs plus 5 numerical completions. Ten remain unfinished. This shared
desktop run was substantially slower at identical work counts than prior
timings, so it is not a clean speed comparison against iteration12. See
[iteration13 evidence](reports/milp-iteration-13/REPORT.md), using `build-milp-iter13`.
New ordering and [objective-lattice bounds](docs/OBJECTIVE_LATTICE.md) remain
opt-in; there is no general completion-rate gain established. CPU work stays
local and no Kaggle upload is needed.

Four then-untouched MIPLIB2017 benchmark holdouts add two checked feasible limits
and two no-incumbent limits per policy, with no completions. Across the combined
21-case timed wave/holdout: 7 completed, 9 checked feasible-but-open, 5 without
a point. The broader test ledger is evidence of measured scope, not universal
MILP robustness.

The preserved [iteration12 experiment](reports/milp-iteration-12/REPORT.md)
completed 10 versus 9 cases and repeated the new mod008 numerical completion.
Those historical outcomes remain valid for their recorded protocol; they are
not silently replaced by the latest, differently loaded desktop measurements.

Iteration11's [MPS integer-default correctness fix](docs/MPS_DOMAIN_CONTRACT.md)
is retained. Its [17-model baseline](reports/milp-iteration-11/REPORT.md) and
all older builds remain preserved. Older readers can misinterpret marker-only
integers without explicit bounds. Numerical completions and structurally
checked lattice rounding do not establish universal support or general exact proof.

Prior verified CPU candidate: [MILP iteration10](reports/milp-iteration-10/REPORT.md),
`build-milp-iter10`. Guarded, optional reduced-bound LPs give a 2.72x median
Binkar ROOT-screen ratio over three pairs, improve the fresh 180s Binkar gap
0.9529% to 0.9132%, and complete Blend2 to gap tolerance in 144.04s while the
matched control times out. Binkar remains unproved. All 8 CTest groups, 80
independent mixed-model checks, 240 generated profile checks, 49 retained cuts,
24 saved public vectors and 4 application models in both profiles pass their
checks. Defaults and prior versions are preserved. Read the
[honest submission assessment](docs/SUBMISSION_ASSESSMENT.md) for strength,
scope and highest-value remaining work; these results do not establish a
competition rank or industrial readiness.

Execution policy: [CPU testing and iteration run locally](docs/EXECUTION_POLICY.md).
Kaggle is reserved for experiments that actually require NVIDIA GPU/CUDA.
Previously prepared CPU notebooks do not need to be run by the user.

V2 adds sparse revised simplex, reusable LP bases, MILP bound propagation,
cover cuts and diving heuristics, a scaled constrained-QP method, multicore
operations, and an optional CUDA box-QP backend. The separate Kaggle notebook
loads its matching source snapshot as Kaggle input. The first returned P100
run is now audited: [GPU results and limitations](reports/KAGGLE_GPU_REPORT.md).

The next MILP iteration adds an independently implemented feasibility pump and
bounded heuristic sub-solves. Its evidence is separate from the original V2:
[MILP iteration 01](reports/milp-iteration-01/REPORT.md).
Its [second Kaggle return](reports/kaggle-gpu-02/REPORT.md) now confirms the
new binkar10_1 incumbent on P100-hosted Kaggle, with the proof gap still open.

The next [constrained-QP iteration](reports/qp-iteration-01/REPORT.md) adds
magnitude scaling, larger structure-based dual-Newton dispatch, and a separable
diagonal dual bound. QPLIB 9002 now passes independent original-model KKT and
gap checks locally; its OSQP comparison still times out and is kept incomplete.
Further CPU validation of this newer snapshot runs locally; it does not require
a Kaggle return.

The [MILP candidate-repair experiment](reports/milp-iteration-04/REPORT.md) is
preserved locally as `build-milp-iter4`. It adds an independently
checked blend2 incumbent locally and compares the existing recovery/neighbourhood
baseline against an optional dense repair. Both modes include a correctness fix
preventing a repaired integer fixing from incorrectly closing the whole node.
Iteration04 and later contain this proof fix; earlier binaries remain historical
evidence and have a reproduced false-optimality edge case in that repair path.
The earlier [branching experiment](reports/milp-iteration-02/REPORT.md) is
preserved; reliability remains experimental, not the default.
The [focused Kaggle return](reports/kaggle-milp-01/REPORT.md) is now audited:
it motivated blend2 recovery and post-incumbent progress. The
[iteration03 Kaggle return](reports/kaggle-milp-02/REPORT.md) now confirms the
binkar incumbent gain (7297.32 to6747.31, gap1.23%) and continued blend2 search.
That audited run still has no blend2 incumbent. The later
[local180-second comparison](reports/milp-iteration-04/LOCAL_VALIDATION.md)
reaches blend2 objective7.598985 in114.53 seconds, matching the independent
optimum at gap_limit status. CTest3/3, generated240/240 and all five final
candidate checks pass. Binkar remains at6747.31 with about1.22% gap; markshare
remains incomplete. The previously prepared CPU notebook is preserved but is
not a required user run. Repeated/broader evidence is still needed.

The latest [local MILP iteration05](reports/milp-iteration-05/REPORT.md),
`build-milp-iter5`, tests neighbourhood diversification and call spacing, with
per-call diagnostics and independently checked intermediate vectors. Three
experiments did **not** improve the final hard-case objectives, so neither
option is promoted. Current guided-mode outputs match the prior build on80
generated models; the latest gate passes240/240 and12/12 available vector checks.
No Kaggle run is needed. This is diagnostic/search work, not a claim of broader
industrial performance or solved markshare/binkar instances.

The newer [local MILP iteration06](reports/milp-iteration-06/REPORT.md),
`build-milp-iter6b`, adds an opt-in `--binary-meet` root search for small binary
models with separable continuous variables. On markshare it finds an independently
checked objective1 point in about0.24s, versus the guided run's final~5. Three
root-only repeats reproduce objective1; the main proof gap remains~50% under
the solver's reported-gap convention. CTest4/4 (including180 exhaustive structural
cases), generated240/240 and independent vector checks pass. This is a limited
structural result, not a general MILP speedup or proof of optimality. Reserved
neighborhood experiments and timing variability are preserved separately.
No GPU/Kaggle run is required; previous builds and defaults remain available.

The current [local MILP iteration07](reports/milp-iteration-07/REPORT.md),
`build-milp-iter7`, adds a separate opt-in `--binary-proof` engine with checked
integer arithmetic and strict eligibility guards. It certifies markshare's
optimum of 1 with zero gap in all three local runs (0.653–0.731s), independently
recomputed from the original MPS literals. It also certifies p0033 at 3089,
but the existing solver is faster there, so this is not a default or universal
speedup. CTest5/5, including 600 new exhaustive exact-proof cases, generated
240/240, six independent public proof checks and 12 final-point checks pass.
The previous guided/meet results match on 160 generated runs. Binkar's general
MILP proof gap remains open; only two eligible public models were tested here.
See the [exact method and limits](docs/MILP_BINARY_PROOF.md). No Kaggle run needed.

The latest [local MILP iteration08](reports/milp-iteration-08/REPORT.md),
`build-milp-iter8c`, tests checked lifted covers and a delayed full-domain restart.
Direct root cuts worsened Binkar's incumbent and are preserved as a failed
performance experiment. The delayed option `--late-lifted-covers` keeps6747.31
and reduces its reported gap from1.214% to0.957% in a fresh180s pair. Binkar is
still incomplete. All25 retained new cuts and15 captured/final vectors pass
independent checks; CTest6/6 and generated240/240 pass. Markshare's exact-proof
sentinel remains valid. The schedule stays opt-in pending repeated/broader
evidence. No CPU-only Kaggle run or user upload is required.

The newer [local MILP iteration09](reports/milp-iteration-09/REPORT.md),
`build-milp-iter9b`, adds optional compact equality LPs and delayed activation.
The faster root screen did not translate into a better immediate-mode full
solve; that failed experiment is preserved. Delayed activation retains Binkar's
6747.31 incumbent but changes the fresh 180s gap only marginally, from 0.9574%
to 0.9544%. It is not promoted as a general speedup or default. Seven CTest
groups, 240 generated MILP checks and 90 independent equality-LP checks pass.
The separate 600s attempt reaches 0.9077% gap but still times out; it does not
prove Binkar optimal. See the report for the final audit and the
[method and limits](docs/COMPACT_EQUALITY_LP.md). CPU only; no upload needed.

Start with [V2 build and reproduction](docs/V2_REPRODUCE.md),
[architecture and exact scope](docs/V2_ARCHITECTURE.md),
[industrial cases](docs/INDUSTRIAL_CASES.md), and
[remaining submission requirements](docs/V2_REMAINING.md).

The material below records V1. V1 results are historical and must not be used
as current binary hashes or GPU evidence. `build-v2` preserves the previous
baseline; the MILP iteration build is `build-milp-iter1`.
The QP iteration uses `build-qp-iter1`; the current MILP experiment uses
`build-milp-iter11`. Earlier builds and deliveries are preserved.

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
