# SIH26119 implementation worklog

## 16 September 2026 — MILP iteration24, objective-only private stage

Added optional --pump-distance-stage with an immutable selected parent model,
strict unchanged-domain prefilter, verified absolute-feasibility boundary,
separate parent/child telemetry and bounded exact LP snapshots. It shares the
existing dive slice and never exports private proof state. Flag remains off.

Screen: candidate 18 checked points versus control 17 in 22 runs each, four
completions each. Misc07 gains both points, danoint loses one control success,
and lotsize remains unresolved. Wave: candidate 25 points versus control 24,
ten completions each, one separately cross-checked infeasible case each.
Misc07's 3970 point repeats; lotsize is the remaining no-point candidate model.
Danoint returns 69.5 in both wave runs, without staging executing there.
Binkar quality worsens; pk1's better candidate objective has no stage calls.

All 98 public records and 84 final vectors pass validation. Gates pass 24 CTest
groups, 176 Python tests, 320 generated runs and 100 retained cases, plus 16 parity
runs and 10 actual MIN/MAX/domain integrations. Sixteen exact private LPs replay
in three modes with 48 independently checked points. Lotsize parent 2670->1 and
child 2670->4 pivots show the intended mechanism; its MILP remains unsolved.
Misc07 parent 900->0 but child 641->2541 exposes a warm-work regression, alongside
tiny-coordinate/near-tie trajectory sensitivity leading to its feasible gain.

Same measured/final binary and unchanged measured source/checkers; frozen23
preserved. Next test stable private-dive near-tie selection, then later expensive
branch fallback as a separate same-budget hypothesis. Four planning slots remain,
not a guarantee of 27/27. All work was CPU-local; Kaggle artifacts are unchanged.

## 16 September 2026 — MILP iteration23, guarded private basis handoff

Added optional --pump-distance-reopt. A separate tagged basis follows the exact
selected fractional seed; incompatible structures and neither-feasible bases
fall back. Private objectives, bounds, proof state and basis remain outside the
global tree. Budgets and acceptance tolerances are unchanged; flag stays off.

Screen: both profiles return 16 checked points in 20 runs. Full wave: both have
24 checked points plus one corroborated infeasible status; misc07/lotsize remain
unresolved. Control completes ten, candidate nine. Mod008 retains objective 307
but misses completion; it makes no private LP call, so no causal claim is made.
Mas74's older-profile quality advantage remains unrecovered. Pk1's one-off
screen objective difference also occurs without the new LP path and does not repeat.

All 94 paired records pass validation, with 80 final vectors checked. Gates:
23 CTest groups, 170 Python tests, 320 generated runs, 100 retained cases,
16 parity runs and eight actual MIN/MAX/domain runs. Ten private LP replays
pass 30 independent point checks. Misc07 pivots fall 784 to 9 and eil33-2 317
to 44, but lotsize falls back to 2670 and no additional model is handled.
Same measured/final binary; frozen22 preserved. Next hypothesis: stage target
and bound changes under the same time slice. CPU-local, no Kaggle changes.

## 16 September 2026 — MILP iteration22, guarded pump primal reoptimization

Added optional --pump-primal-reopt only for the pump's private projection LPs.
Exact canonical structure/mapping/equality checks and current primal/dual
feasibility select a guarded restart; invalid or incompatible bases retain
cold fallback. No private basis/bound enters tree or distance-dive proof state.
Existing budgets and tolerances remain unchanged; new option defaults off.

Repeated screen: candidate 14 checked points versus control 12 in 18 runs each.
Wave: candidate 24 versus control 23, ten completions each, one cross-checked
infeasible case. Danoint's 69.5 point and rout's improvement to 1293.19 repeat
3/3. Misc07/lotsize remain unresolved; mas74 regresses to 13588.56 from control
12914.44. Keep that loss visible and retain prior profiles.

All 90 paired records pass validation. Gates: 22 CTest groups, 166 Python tests,
320 generated runs, 100 reused exhaustive cases; 16 parity runs, six actual
MIN/MAX/domain runs, twelve supplemental refinement/scale/sense combinations.
Fourteen actual private-LP replays pass 42 independent point checks; e.g.
lotsize 1860->60 pivots and rout 519->4 for the retained LPs. These are specific
LP-work reductions, not end-to-end or universal speedups. The same binary is
used for timings and final artifact; frozen21 stays intact. Next tackle the
initial cold distance LP with compatible private-state reuse, protecting
mas74 quality and the new feasible points. CPU-local; no Kaggle needed.

## 16 September 2026 — MILP iteration21, private distance dive and domain guard

Added optional --pump-distance-diving, requiring pump guidance. The first
eligible dive uses a private L1 objective with correctly bounded auxiliaries
and private cold/warm bases. Its outputs are explicitly point-only; unchanged
original-model acceptance recomputes the objective. Time, step, repair, cut
and restart envelopes remain unchanged, and the second dive is preserved.

The repeated eight-model screen has 12 candidate checked points versus 8
controls across 16 runs each, retaining both p0201 completions per profile.
Eil33-2/rout gains repeat in the 27-model wave, but misc07 loses a control point.
Wave: 23 candidate solutions versus 22 guided controls, 10 completions each,
one independently cross-checked infeasible model. Candidate misc07/lotsize/
danoint remain no-point limits. No blanket promotion or historical breadth
guarantee follows; both flags stay off by default.

All 86 saved comparisons, 65 final vectors, 40 fractional seeds and 213 retained
distance metrics pass the re-audit, including four restricted exact certificates.
The gate passes 21 CTest groups, 162 Python tests, 320 generated runs and 100
retained exhaustive cases. Frozen20 remains intact.

A source-review edge case was separately reproduced after timed own solves:
presolve-off empty integer bounds could throw in the private builder. A narrow
eligibility guard now leaves that decision to the existing original-model tree.
The final build reruns the full gate, 16 parity runs, 32 internal domain/option
combinations, ten CLI domain replays and four actual MIN/MAX private-dive runs.
The two p0201 metamorphic points pass independent checks. Benchmark and final
binaries/source identities are explicitly distinct; the 86 timings were not
rerun on the patched artifact. The first CLI replay harness's exit-code
expectation was corrected, and its original output retained.

See [iteration21](../reports/milp-iteration-21/REPORT.md), its full ledger and
three-iteration checkpoint. Next isolate private LP reoptimization work while
protecting misc07 and the repeated gains; proof-gap closure remains separate.
No GPU or user upload was required.

## 16 September 2026 — MILP iteration20, pump-guided diving experiment

Implemented opt-in --pump-guided-diving after diagnosing discarded pump
fractional progress. Only checked, strictly closer projections may seed the
first existing dive mode; subsequent directions favor their clipped nearest
integer target. Original objective/basis, second mode, proof accounting,
original-model acceptance and resource allowances are retained. Added bounded
seed telemetry and an independent fractional-point checker, without treating
fractional seeds as integer feasible solutions.

The full gate passes 20 CTest groups, 152 Python tests, 28 MPS-domain cases,
320 generated integrations, 100 retained exhaustive cases and the retained
numerical repair/transformed LP checks. Twelve fixed-node runs retain four
three-way frozen19/new-off/traced-off parity comparisons. Four additional
no-pump/no-heuristics suppression runs pass. Four public root-only mechanism
runs exercise actual guided dives on blend2/danoint; none returns an integer
point at that node cap.

The repeated six-model screen retains all 24 outcomes, all eight final point
checks and zero validation failures. Both profiles have two p0201 completions,
two open blend2 points and eight no-point limits. The target cases do not gain
first feasibility. Lotsize remains highly fractional after 64 steps; danoint
spends much of its budget in LP work and has only two guided steps in the first
pair. This is not a demonstrated breadth improvement. See the
[complete iteration20 report](../reports/milp-iteration-20/REPORT.md) for full
wave outcomes, the decision and archived evidence. New guidance is off by
default; frozen19 is preserved. No GPU or user upload is involved.

The full wave checks all 44 returned points and has zero validation failures:
control 21 points versus guided 23, nine completions each. Two initial
neos859080 reference timeouts remain in the raw records; one separate 30-second
reference confirms Infeasible in 14.91s and cross-checks both saved statuses.
Guided misc07/rout gain points in this pair but rout fails both screen repeats.
Gt2 improves 42649 -> 35673, repeated in two additional post-selected pairs;
all four follow-up points and their full re-audit pass. Pk1 regresses about
20 -> 30 and all three targeted no-point cases remain. Keep guidance off by
default. The scalar-path diagnosis shows the first original-objective LP
discarding much of the improved integer-distance geometry, including danoint's
0.03501 -> 5.6678 jump; this motivates a separate next experiment, not a claimed
solution to the remaining models.

Final main re-audit passes 78 records, 52 integer solution vectors and 20
retained fractional seeds, with four exact-subset certificates recomputed.
The separate four-run gt2 repeat audit passes four more final points. Main
guidance counters show 24 dives/702 steps; ten numerical repair attempts
accept ten valid points. Original reference timeouts remain explicit and the
longer status cross-check is separately hashed. No observed validation failure
or pending final integer point remains. These are bounded numerical/structural
checks, not exact general-MILP proof or 27/27 completion.

## 16 September 2026 — MILP iteration19, repair missed dive candidates

Added bounded optional pump/dive tracing and separate diagnostic builds. Initial
five-model diagnostics retain all outcomes and expose several mechanisms: pump
target rejection, expensive projection LPs, many fractional variables and a
near-integer blend2 dive point rejected on original rows. Priority capture
retains that point within the same 100000-vector-value limit after the initial
trace had lost its vector. The captured raw/rounded violations are 2.01e-6 /
2.129e-6, so rejection at 1e-7 was correct. Frozen18 cold fixing replay fails
sparse LP checks but dense LP returns 8.788661, independently checked with
4.55e-13 original-model violation and zero integrality error.

Implemented optional `--repair-heuristic-candidates`, requiring
`--repair-candidates`, for rejected near-integer dive points. It uses exact
integer fixings on the original model, sparse polishing then dense recovery,
the existing dive slice and shared repair allowance, and at most 16 unique
assignments. Only checked points reach the incumbent; no fixing bound/status
can certify the global node. Tolerances, cut/restart rules and LP iteration/fill
allowances remain unchanged. Pump-seed handoff is not mixed into this change.

The gate passes 19 CTest groups, 140 Python tests, 28 MPS-domain cases,
320 generated runs, 100 reused exhaustive cases, the retained sparse cold/warm
repairs and 24 transformed LP checks. Four public fixed-node cases have
three-way semantic parity across frozen18, new repair-off and new traced-off.
The repeated screen passes all 20 records and 18 returned points: both blend2
controls find none while both repair runs find 8.788661 in about 3.4–3.6s,
with about 13.6% open gaps. Other sentinels retain points/completions, with mixed
gap/objective differences. The full 54-run wave returns 23 checked points with
repair versus 21 for control, with 9 optimality/tolerance completions in each.
Blend2 repeats the direct point gain; rout's additional point has zero repair
attempts and is not attributed to the new mechanism. Lotsize, eil33-2 and
danoint remain no-point limits. The repair reference for neos859080 times out;
a separate check confirms status agreement against the paired reference's
Infeasible result on the identical hashed model, preserving the original
timeout. Both profiles leave mod008 open, unlike prior iteration18 timings.
Final re-audit passes all 74 paired records and 62 final points, with no pending
final point or observed validation failure. Seven repair attempts accept seven
valid points; that counter does not require incumbent improvement. Four exact
subset proofs are recomputed. The limited traces and numerical infeasibility
cross-check do not constitute exact general-MILP proof coverage.
See the [full iteration19 report](../reports/milp-iteration-19/REPORT.md)
for the complete 27-model comparison and final archive identities.

## 16 September 2026 — MILP iteration18, selective correction and measured work

Separated instrumentation-only Stage A from the final selective algorithm.
Six fixed-node cases have identical frozen17/untraced/traced semantic results;
24 diagnostic runs and their exact source/binary are retained separately.
Optional `--capture-refinement` attributes calls, residual scans, visited
entries, corrections and nested time to every MILP LP phase, including fallback
work. Added ledger, cancellation, disabled-mode and accounting regressions.

Added optional `--refine-basis --refine-at-checks` for selected simplex terminal/
rejection boundaries. Re-evaluate the corrected same basis once, preserving
cycle accounting, budgets and final numerical certificates. Tolerances, shared
LU, dense recovery, cuts/restarts and global recovery allowance are unchanged.
Captured cold/warm repairs each use 3 attempts / 2 accepted corrections versus
always-check 99/72 cold and 18/12 warm. Independent point checks pass at about
2.91e-11 violation. The full gate passes 17 CTest groups, 126 Python tests,
28 MPS-domain cases, 320 generated runs, 100 reused exhaustive models,
four disabled-option parity cases and 24 transformed LP checks across both modes.

The two-pair p0201/eil33-2/mas74 screen and 24-model development wave preserve
all outcomes. P0201 completes in all six current runs. Selective mas74 avoids
all recovery/deferred nodes in its three runs, but keeps about 15.5–15.6% gaps.
Wave completions are 10/24 in both profiles (2 restricted exact, 8 numerical),
with checked points on 19 control versus 20 selective models. Misc07 gains a
point; Binkar's objective/gap worsen. Eil33-2 has points in all four screen runs
but neither wave run, so first-feasible reliability remains unresolved. Three
predeclared new instances add no completions: danoint/rout have no point under
either profile, while mas76 improves from 7.50% to 5.24% gap in one pair with
checked points. Mas76 is related to mas74, not an unseen-family result. See
[the full report](../reports/milp-iteration-18/REPORT.md) for final audit identities.
The final re-audit passes all 66 public records and 53 returned points, with
zero pending points. It recomputes four restricted exact proofs and checks
52 covers, 82,308 saved lattice events (19 capped traces), 80 cut rounds and
four source incumbents. All three batches retain matching code/binary hashes.
Neither refinement mode is promoted to default.
Frozen17 remains preserved; CPU work stays local and no Kaggle upload is needed.

## 16 September 2026 — MILP iteration17, sparse basis-value correction

Diagnosed the retained mas74 basis residuals and preserved a frozen arithmetic
control. One residual correction repairs the final basis; fresh factorization
alone does not. Added opt-in `--refine-basis` for guarded basic primal/dual
correction against the actual basis, with at most two attempts per RHS and
strict improvement required. Shared LU, dense simplex, tolerances, valid bounds,
pivot/fill limits, cuts, restart policy and global recovery allowance remain
unchanged. Corrections use the current LP clock. Final certificate checks remain.

Cold (130-pivot) and original warm (5-pivot, warm_started) replays pass, with
independent absolute violations about 2.91e-11. Added 12 transformed min/max LP
checks and correction/certificate/resource guard tests. The final gate passes
15 CTest groups, 115 Python units, 28 domain cases, 320 generated MILP runs,
100 reused exhaustive cases and four disabled-option fixed-node parity cases.

Two mas74 screen pairs and the 24-case wave give 52 public runs. All three
refined mas74 runs have zero recovery attempts and zero unresolved/deferred
nodes. Screen gaps improve, but the wave control has a better objective/gap.
Wave completions are 9 control versus 8 refined (2 restricted exact in each),
with 20 models returning points under each profile. The misc07 point gain is
offset by an eil33-2 point loss; p0201 loses completion. Keep the repair optional,
retain all failures and test selective refinement and genuinely new holdouts.
Re-audit passes all 52 public records and 44 points, recomputing 4 restricted
exact proofs and checking 64 covers, 63,548 saved lattice events (14 truncated
traces), 70 cut rounds and 7 cut-source incumbents. Previous16 is preserved.
No Kaggle work, tolerance relaxation or universal-public-MILP claim.

## 15–16 September 2026 — MILP iteration16, incumbent-gated cuts and mas74 diagnosis

Added optional `--cut-after-incumbent`, requiring `--adaptive-cut-rounds`.
Before an original-model-accepted point exists, the ordinary cut schedule is
retained. Afterward the unchanged iteration15 rule may stop. Defaults remain
five rounds and both options off. Version2 cut traces record the source
incumbent objective; an independent checker validates its retained original-MPS
vector. Missing source capture is explicit, never silently counted as checked.

Two screen pairs on each of Binkar/p0282/mod008 plus a 24-case wave give
60 public candidate runs. All returned points pass independent checks. Binkar
preserves a point in all three guarded runs but has a worse gap than all three
controls. The feature is not promoted. Both wave profiles have 2 restricted
exact proofs, 8 numerical completions, 10 checked feasible limits, 1 unresolved
checked point, 2 no-point limits and 1 cross-checked infeasible termination.
No new untouched cases or general completion-rate improvement is claimed.

Final gate passes 14 CTest groups, 115 Python units, 28 MPS-domain cases, seven
four-way fixed-node parity comparisons, 320 generated runs on 80 cases and
100 reused exhaustive MPS cases. Expanded C++ policy tests cover 120 min/max
models, 1080 full solves, 2160 partial/zero checks, 408 cut rounds and 672
restarts. Separate C++ analytic tests run 12 solves; independent CLI integrations
run 12 solves on four analytic MIN/MAX models, checking eight stops and six
source incumbents. Generated regression runs alone have zero cut rounds, so
they are not claimed as production stop-branch coverage.

Separate frozen15 mas74 diagnostics reproduce early unresolved termination
with and without late LP transforms. Recovery uses its six-second allowance
before restart; the new root's two children are deferred and empty the active
queue while preserving bounds. Disabling the clock restart reaches 30s but
leaves 5141 unresolved nodes. The latter frontier trace is explicitly truncated.
Cold replay of the captured first failed LP remains a sparse numerical_error
after 130 iterations, with 9.77e-5 absolute violation. Dense recovery uses 130
iterations and matches the independent optimum with 4.37e-11 violation. The
sparse relative primal/dual gap fails its existing verification threshold.
No tolerance or recovery change is made. This is a reproduced numerical
fixture and exit diagnosis, not a fixed mas74 solve or warm-pivot replay.

Final re-audit passes all 60 public records: 54 final-point checks, four
restricted exact-proof recomputations, 135 retained lifted covers, 98798 saved
lattice events (24 explicitly truncated traces), 142 cut rounds, six stops and
12 independently checked cut-source incumbents. No reference point is pending.
The diagnostic output/reference hash chains are also checked; the failing
sparse replay remains a documented failure, not a successful solve. Final
regression work overlaps references only after candidate timings finish.

Build `build-milp-iter16`, SHA256
`9fcd999d6226c9464513c22554680e78e90e586a521f6a1d0001a34283841502`.
See [iteration16 evidence](../reports/milp-iteration-16/REPORT.md) and
[next numerical work](../reports/milp-iteration-16/NEXT_STEP.md). Earlier archives
remain preserved. CPU work stays local; no Kaggle upload is required.

## 15 September 2026 — MILP iteration15, selective cut continuation

Added optional `--adaptive-cut-rounds` and `--capture-cut-rounds`, with fixed
two-round preference, a 256-LP-iteration cheap-work floor and a marginal bound
gain/work rule. The existing five-round default and all proof/tolerance logic
remain unchanged. Independent Python replay checks every recorded allocation
decision and its phase accounting; this is not a general exact LP certificate.

The fixed policy is tested in 66 public runs on 24 distinct models, including
three predeclared fresh cases. It is NOT promoted: Binkar has no point in all
four adaptive runs, while every paired control has a checked point. In the
screen, cut LP time drops from 9.81s to 4.81s, but pump/diving time grows and
feasibility is lost. A small dual gain does not measure a cut's effect on the
next heuristic starting point. P0282 avoids the prior one-round regression but
shows no clear improvement. Clock-driven restarts still cause work variability.

The 21-case wave completes 10 cases in both profiles (2 restricted exact and
8 numerical). Baseline has 9 further feasible limits and 2 no-point limits;
adaptive has 8 and 3. Fresh gen-ip054 retains a checked point with about 1.83%
gap; mas74 returns checked points with unresolved relaxations at about 15s
under a 30s limit; neos859080's infeasible status agrees with HiGHS, without
an exact infeasibility certificate. All failures and open gaps are retained.

Final gate passes 13 CTest groups, 100 Python units, 28 MPS marker-domain cases,
seven frozen14/current-off/current-capture semantic parity triples, 320 generated
regression runs on 80 models and 100 reused exhaustive MPS cases. The new C++
group covers 120 exhaustive mixed min/max models, 720 full solves, 1440 partial/
zero checks, 272 traced rounds and 448 restarts. Four extra analytic MIN/MAX
integrations actually exercise the production early-stop threshold: baseline
completes, adaptive returns honest partial node-limit bounds without a point.

The reference helper now caches sparse binding arrays while preserving exact
accumulation order. Its vector-validation fields equal frozen14 on all 21 old
public models. The 66 new public runs have no pending point checks; historical
iteration14 watchdog failures and their separately checked retries are unchanged.
This is validation-throughput work, not a core solver-speed claim.

Final saved-result re-audit passes all 66 public records: 56 checked points,
4 exact-proof recomputations on 2 models, 208 retained cuts, 115194 saved
lattice events (28 explicitly truncated traces), and 176 cut-round decisions
including 12 adaptive stops. No validation failure or pending reference point
is observed. Fresh holdouts generate zero cut rounds; their partial differences
are not evidence of adaptive-policy benefit. Earlier archives remain preserved.

Build `build-milp-iter15`, SHA256
`57ce59edcc13d7717e0a8fd3f964dd8960d79cb86f9acb0dde9ee7d78003d159`.
See [iteration15 report](../reports/milp-iteration-15/REPORT.md) and
[next bounded work](../reports/milp-iteration-15/NEXT_STEP.md). Protecting
first-feasible search through incumbent-gated allocation is proposed, not
implemented here. CPU work stays local; no Kaggle notebook or upload is needed.

## 15 September 2026 — MILP iteration14, measured root-cut work allocation

Added optional exclusive wall-time/LP-work attribution, a 0-through-5 root
cut-round allowance, and a separate counter-only restart trigger. Defaults
remain capture off, five rounds and the existing time trigger. These are
observability and round controls, not new hard pivot/memory limits. Proof,
feasibility/gap tolerances and heuristic algorithms are unchanged.

Five diagnostics identify different bottlenecks: Binkar spends 13.80s in cut
LPs, while other no-point cases spend heavily in tree LPs, pump projections or
dives. One cut round is then predeclared and tested against five. The screen's
Binkar gain comes with a p0282 regression, which repeats in the broader wave.
The candidate is retained for measurement but NOT promoted or tuned afterward.

The full 21-model 30s comparison completes 10 versus 9 cases (baseline/candidate):
2 restricted exact proofs each, plus 8 versus 7 numerical completions. After
separate reference retries, baseline has 9 further checked feasible limits and
2 no-point limits; candidate has 10 and 2. Candidate misses mod008's completion
and worsens p0282's gap from 3.51% to 28.40%. All 21 models are development data,
including the previous iteration's holdouts. No new untouched cases are claimed.

Three new Binkar pairs favor candidate in two gaps but not the third. Median
gap is 1.5551% versus 1.4165%; median cut-LP time is 9.94s versus 2.53s, and
median tree nodes 793 versus 1444. Candidate bounds are weaker in all repeats;
the best baseline run beats all candidate repeats. Shared-desktop timings and
clock-driven search are not controlled comparisons with old archived versions.

Both eil33-2 reference processes initially hit their 25s external watchdog.
The original pending records are preserved. Repeating only those checks with
the unchanged checker, the same configured 5s HiGHS solve limit and a 150s
process watchdog validates both vectors with zero reported violations. Both
reference optimizations still time out. No own solver run or input is changed.
The final auditor counts actual point checks, including linked retries, rather
than merely counting nonempty vectors.

Final gate: 12 CTest groups, 88 Python units, 360 solves on 120 new exhaustive
C++ models, 720 partial/zero-time checks, 237 counter restarts, 28 MPS-domain
checks, 240 generated runs on 80 cases, 100 reused exhaustive MPS cases, four
default/capture parity triples, three invalid CLI cases and two public restart
integrations pass. The lattice reader's sparse-array caching is checked equal
to frozen13 on all 21 public models; this is checker speed work, not solver speed.

The saved audit passes 59 experiment records with 51 independently checked
final points, 4 exact-proof recomputations on 2 models, 202 retained lifted-cover
checks and 82258 saved lattice events. Twenty lattice traces are explicitly
truncated at 4096 events. General LP/MILP certificates remain numerical.

Build `build-milp-iter14`, SHA256
`f31c1181bc6b775f197a47aee543c9f997955df4a9ff9cb7da61a9820a69df69`.
Read [iteration14 evidence](../reports/milp-iteration-14/REPORT.md) and
[next experiment](../reports/milp-iteration-14/NEXT_STEP.md). Earlier archives
remain preserved. No GPU, new notebook or user upload is needed.

## 15 September 2026 — MILP iteration13, independent frontier accounting

Implemented opt-in `--raw-lp-priority` and `--capture-frontier`, preserving
objective-lattice proof strengthening, old defaults and all earlier archives.
A ranking heap and separate scalar proof-bound index keep node selection
independent of the global minimum. Gap checks, full-domain restart inheritance
and final bounds include all queued/deferred nodes. New independent event replay
checks saved queue selection, counts, deferral and restarts, not raw LP validity
or every branching domain. General proof bounds remain numerical.

The 24-run fixed-node screen (4 models x 3 profiles x 2 repeats) passes all
checks; all 12 paired semantic traces repeat exactly. No model completes at
2048 nodes with heuristics/cuts disabled. The matched 17-model 30s wave completes
7 in both policies: 2 restricted exact proofs and 5 numerical completions;
7 more have checked points with open gaps, and 3 have no point. Raw ordering
improves the gt2/p0282 wave incumbents but worsens other gaps. It is not promoted.

Three target repeats per profile restore gt2 objective 42649 in all raw runs,
matching control and improving on lattice ordering's 92866. All remain open.
All nine mod008 runs find 307 but time out; lattice/raw gaps are 0.6494% versus
the control's median 0.8441%. These loaded-desktop results do not replace the
earlier repeated completion. Identical egout work counts took 2.46s in12 versus
7.22s in13; background CPU activity and two diagnostic overlaps are documented.
No clean cross-version speed claim is made.

Four predeclared untouched MIPLIB2017 benchmark members are retained unchanged:
gen-ip002 and assign1-5-8 have checked points with about 3% and 18% gaps;
lotsize and eil33-2 have no point at30s. No holdout completes, none is replaced,
and there is no post-holdout tuning. All four are ineligible for lattice
strengthening, so their original numerical bound path remains necessary.

The final regression gate passes 11 CTest groups, 79 Python unit tests, 100000
queue operations, 720 solves on240 new exhaustive C++ models, 1440 partial/
zero-time checks, 93 forced restarts, LP/deferred guards, 28 marker-domain
checks, 240 generated runs on80 cases, and100 reused exhaustive MPS cases with
fresh references and full frontier replay. Three short public integrations
replay late resets and a generated interrupted-LP case retains deferral.

The final re-audit passes84 experiment records on21 distinct public models,
with56 saved final-point checks,186648 frontier events,173428 SAVED lattice
events,22 retained cuts and4 exact-proof recomputations on2 models. Frontier
capture covers24 fixed-node runs; timed runs omit it. No captured public
frontier trace is truncated, but26 lattice traces reach their4096-event cap.
Zero observed validation failures is not general exact LP/MILP certification.

Build `build-milp-iter13`, binary SHA256
`bdfdb8fc7a21d411d47557f093e728e018e86960c359f86573393711b5b4757e`.
See [iteration13 evidence](../reports/milp-iteration-13/REPORT.md), final audit
and frozen state. Next: phase/work attribution, better budget-controlled
feasibility progress, then stronger relaxations and larger guarded waves.
CPU only; no Kaggle notebook or user upload is required.

## 15 September 2026 — MILP iteration12, guarded objective-lattice bounds

Implemented opt-in `--objective-lattice` in a new build, retaining iteration11's
MPS correction and all historical archives. The method derives integral
effective objectives, including strict unit-equality continuous definitions,
and safely rounds only validated, safety-adjusted main-tree bounds. Checked
integer arithmetic, finite/range guards, dyadic offsets and downward publication
prevent unsupported structure/arithmetic from creating a new bound. General
LP certificates remain numerical; the restricted exact engine is unchanged.

All 17 retained public cases were run in a matched 30s control/candidate pair.
Completion moves from 2 restricted exact + 7 numerical to 2 exact + 8 numerical.
mod008 closes at objective307 in 13.58s; the matched control is still open at30s.
A separate three-pair experiment repeats mod008 completion at13.94/14.23/14.36s
(median14.23s), versus 0/3 completed controls. misc03's valid step-5 derivation
does NOT close its proof gap; candidate median gap3.1241% is worse than control
2.3059%. gt2's wave incumbent regresses42649 to92866. Lattice bounds can affect
queue order and short-budget search; the option stays OFF by default.

Safety evidence: 300 exhaustive C++ models, 600 partial/zero-time outcomes,
10005 near-grid checks and supplemental structure/terminal/default-domain guards;
100 fresh MPS models checked by625-point enumeration and independent completed
HiGHS references (34 direct/66 derived lattices,742 audited rounding events).
Final gate passes10 CTest groups,65 Python checker tests,28 marker-domain checks
and160 generated regression runs (80 cases in both profiles).

The final audit passes50 public records across the screen/wave/repeats:
48 saved final-point checks,65710 SAVED lattice events,64 retained cuts and4
recomputed exact proofs on2 distinct models. Sixteen traces are explicitly
truncated at4096 events. This is not exact validation of every raw LP bound.
No core or timed checker changed after public timing began; supplemental C++
tests were added and passed afterwards. Build `build-milp-iter12`, SHA256
`3d29e6a0d5f0ed3bfb6c35e0a3ccee0bc158dda987b619242ed201aff3235a7d`.

Seven candidate wave models remain unfinished. Next isolate proof accounting
from search ranking under deterministic node budgets, then strengthen mixed
proof/search and predeclare untouched holdouts. See iteration12 REPORT/NEXT_STEP
and docs/OBJECTIVE_LATTICE.md. CPU only; no Kaggle handoff or upload is pending.

## 15 September 2026 — MILP iteration11, breadth and input correctness

User requests broad public-MILP proof/robustness coverage. Predeclared 17 cases
(7 existing, 10 new historical MIPLIB3 originals) with one fixed 30s profile,
followed by separate 5s HiGHS references. Both old and corrected binaries give
2 independently recomputed restricted exact proofs, 7 numerical completions,
7 checked feasible limits and 1 no-incumbent limit. All public validation checks
pass; unfinished cases remain on the ledger. These are not 17 modern benchmark
instances, nor a complete library or performance-repeatability claim.

Found and reproduced a separate correctness defect: marked integers with no
explicit bound record were parsed [0,+inf] rather than [0,1]. Old build says
optimal -7 where the independent intended-model optimum is -1. Four of 28
domain cases fail before the fix; all 28 pass afterwards. The C++ reader and
independent literal checker now use per-column bound presence, preserving
explicit LO-only +inf uppers and continuous defaults. Nine CTest groups, 52
Python checker/classifier tests and 80 generated MILPs pass. General numerical
LP/MILP/QP algorithms and heuristics are unchanged; only src/mps.cpp differs
among core source/header files versus iteration10. No performance improvement
is attributed to wall-clock-driven search variation between these full sweeps.

Build `build-milp-iter11`, SHA256
`867191540898cb1ea7a4bb91a85949734d476b900ca94039025ae818f4ece0cf`.
The final classifier additionally respects the requested gap-limit accuracy
when comparing completed references; all 34 public classifications remain
unchanged and the timed runner versions are archived. See iteration11's report,
audit and final state. CPU only, prior evidence preserved, no Kaggle handoff.
Next investigate guarded objective-lattice bounds and broader proof strength,
starting with the retained mod008/misc03 open-gap results and new holdouts.

## 15 September 2026 — completed local MILP iteration10

Implemented optional guarded reduced-bound LPs, with full-node primal gates,
full-LP fallback and delayed activation preserving search budgets. Final build
`build-milp-iter10`, SHA256 `3cac5f39d5f2546006cb3bd5788ff0e44245ceaab282e86b8a4caf5062295eeb`.
Three Binkar root pairs preserve bound 6645.940875 and remove 2128 rows; median
time 6.7029 to 2.4653s. Fresh 180s full pair retains incumbent 6747.310015 and
improves bound 6683.003921 to 6685.681835 (gap 0.95292% to 0.91324%). It still
times out. Blend2 reaches 7.598985/gap_limit in 144.04s versus control timeout
at 8.015188. This does not beat every earlier protocol or prove general speedup.

CTest 8/8 (including 200 new mixed-MILP comparisons), checker tests 33/33,
independent HiGHS mixed cases 80/80 and generated profile runs 240/240 pass.
The audit rechecks 49 retained cuts and 24 saved public vectors. All four
application examples pass both profiles against completed HiGHS references;
these are teaching/synthetic models. Eighty control outputs match iteration09.
Markshare's original-literal exact-proof sentinel remains valid. Source identity
checks cover 83 files for the full pair and 84 for later root repeats; the
application-check script was added between their metadata captures.

Defaults, prior builds and historical evidence are preserved. No numerical
changes after timing, no CPU-only Kaggle handoff. The current report and honest
submission assessment are in `reports/milp-iteration-10/REPORT.md` and
`docs/SUBMISSION_ASSESSMENT.md`. Next prioritize repeated broader hard-MILP
coverage, domain validation and the final reproducible demo.

This continues the supplied V1 conversation and evidence. The user's current
instruction is to build a strong, working submission covering the PS, with tests,
phase reports, and explicit limitations. Existing V1 reports are historical.

## Delivery contract

- Initial classes: LP, MILP, and continuous convex QP. The PS asks for an
  architecture extensible to MIQP/NLP/MINLP; it does not require all of these
  extensions to be implemented initially. Nonconvex-QP scope is unresolved.
- All optimization and numerical algorithms in the core are our implementation.
  External solver packages are permitted only as isolated validation references.
- Keep unsuccessful benchmark runs. Optimal status requires numerical checks.
- GPU performance must be measured on available hardware, never inferred from
  a CPU run or a kernel-only timing.

## Current machine (2026-09-14)

Intel Core i5-10210U, 4 physical cores / 8 logical processors,
42,523,881,472 bytes physical RAM, Intel UHD Graphics. GCC 14.2.0 and CMake
3.30.4 are available. NVIDIA hardware is not detected. The user confirmed
30 September 2026 as the deadline and Kaggle as the GPU execution environment.

## Implementation and verification sequence

1. Preserve V1; establish a modern-compiler baseline.
2. Add sparse LP computation, reusable basis solves, and numerical certificates.
3. Add MILP presolve, incumbent heuristics, improved search and reusable LP state.
4. Strengthen constrained convex QP, scaling, PSD checks and stopping evidence.
5. Add multicore operations and an optional GPU backend with device detection.
6. Exercise analytical, generated, old-failure and broader public datasets;
   record source/input/binary hashes, hardware, timing, memory and reference checks.
7. Add literature-grounded industrial cases and submission documentation,
   including API/CLI usage, architecture, provenance, results and unresolved gaps.

This list records intended work, not implemented capabilities. Completed phases
and final evidence will be recorded below as they are verified.

## Implemented and assessed

- Preserved V1 source and executable in `reports/v2-baseline/`.
- Added sparse primal/dual revised simplex, own LU/eta basis algebra and warm
  starts; all 120 generated LP tests and the 12-instance Netlib subset passed.
- Added propagation, root cover cuts, diving and integer-candidate polishing;
  all 40 binary and 40 mixed/general-integer regressions passed. All four
  historical MIPLIB cases completed to the stated tolerance in the V2 run.
- Added scaled ADMM/PCG, bounded active-set polishing, broader sparse PSD tests,
  and a small structured diagonal-QP dual-Newton path. Generated QP checks pass;
  QPLIB 9002 remains incomplete.
- Added OpenMP and optional resident CUDA box-QP code. Repeated CPU scale tests
  through one million variables passed; the later P100 return also passed all
  three selected CUDA scale cases (see the GPU return entry below).
- Added three MIPLIB 2017 stress cases, four industrial/literature models,
  a consolidated evidence runner, and a separate self-contained Kaggle notebook.
- Added current requirements, architecture, limitation and handoff documents.

The deadline is now confirmed as 30 September 2026. See `V2_REMAINING.md` for
the exact Kaggle return bundle and outside information still needed.

## Kaggle usability revision

After the user reported a notebook error and requested a simpler iteration,
the delivery was reduced to two code cells. It uses the current Kaggle Python,
standard pip/subprocess, explicit working paths, a single timing repetition,
and a results ZIP on normal installation/build/check errors. Missing GPU/CUDA
is labeled CPU-only. The numerical solver was not changed. The original
traceback was not supplied, so its exact cause is not asserted.

The user subsequently reported a notebook/kernel size limit of less than 1 MB.
The source/data payload was moved out of the notebook into a required companion
ZIP, attached as a private Kaggle input dataset. The notebook automatically
loads zipped or unpacked inputs and verifies their hashes before running.
No numerical solver or benchmark scope changes were needed for this packaging fix.

## First Kaggle GPU return, 14 September 2026

Imported Downloads/sih26119_kaggle_results.zip and preserved it unchanged in
reports/kaggle-gpu-01/ with the submitted source/notebook. Audited 115 source
files, 59 runtime-source hashes, original benchmark checks and all counts.
The P100 run passed 230 generated cases, 12/12 Netlib, 4/4 historical MIPLIB,
2/3 QPLIB, 0/3 additional MIPLIB, 4/4 application cases and 9/9 scale checks.
The one-million-variable box QP took 2.9818 s GPU vs 16.7640 s CPU1 (5.62x,
single pass only). GPU was slower at 1,000 variables. The same four hard cases
remain incomplete. The reporting fix for HiGHS native output worked.

All GPU-memory fields were null; old exceptions were suppressed. Added a tested
diagnostic sampler for the next snapshot, keeping whole-device memory distinct
from process-attributed memory. No numerical core changes or rerun of the
unchanged Kaggle notebook are needed for this evidence import.

## MILP iteration 01, 14 September 2026

User authorized starting the next targeted engineering iteration. Preserved
the original executable (SHA 9740e7ee...) at build-v2 and as an explicit
reports/milp-iteration-01 baseline copy; the original Kaggle delivery and return
remain untouched. New build: build-milp-iter1. The first candidate SHA was
859060f9...; the retained post-budget-fix candidate SHA is 696b8518....

Implemented our own bounded L1 feasibility pump, deterministic perturbation,
general-integer absolute-distance auxiliaries and fixed-integer polishing.
Added --no-pump, counters/first-incumbent time, finite-coordinate guard and
correct heuristic sub-LP time allocation. Acceptance tolerances and proof-bound
semantics are unchanged. Added analytical tests for these contracts.

Paired exploratory checks: binkar10_1 now has a checked incumbent 7297.320029;
the baseline and no-pump control had none. The first candidate's full CPU run reproduces
that candidate at 19.61 seconds, final reported gap 8.7881%, independently
zero original constraint/integrality violation. It is NOT proven optimal.
blend2 still has no incumbent; markshare_4_0 still has the old approximate-33
incumbent and a large gap. Deeper-backtracking and broader-pump experiments
did not fix blend2 and were discarded; exact exploratory sources/results are
retained in experiment-01/02/03.

First candidate full CPU gate: 230/230 generated, 3/3 CTest, 12/12 Netlib,
4/4 historical MILP, 2/3 QPLIB, 0/3 completed modern MILP, 4/4 application
models, 6/6 CPU scale checks through one million variables. Full evidence:
reports/milp-iteration-01/final-cpu. No LP/QP/CUDA numerical changes this cycle;
QPLIB 9002 remains a separate next work item. No new GPU performance claim.

A further repeat of that first candidate missed its incumbent; preserved in
final-ablation/. The shrinking pump allowance after root cuts was too fragile.
An early-pump/capped-cut experiment also failed twice (experiment-04, retained
as unsuccessful evidence). The retained fix instead reserves up to five
seconds for a post-cut pump, with safe rollback of incomplete cut attempts.
Two exact-binary repeats in experiment-05 independently verified objective
7297.320029, first incumbents 21.7381 and 20.7504 seconds, gaps about 8.79%.
Current exact-binary full evidence is validated-cpu/, not the older final-cpu/.
That full gate reproduced the candidate at 19.7005 seconds with 8.8121% final
gap and zero independently measured feasibility/integrality violation.

Specific next MILP performance investigation: new cut rows currently force a
cold LP solve. Safely extending the old basis across added rows may reduce
root overhead; it requires independent primal/dual checks and a dedicated
iteration, not a guessed basis transfer. blend2 is a search failure, not a
claim that the original model is infeasible.

Kaggle packaging can now select matching CPU evidence and refuses stale core
hashes. The next separate delivery is kaggle_delivery/milp_iteration_01;
same small two-cell notebook / companion private-input ZIP workflow. Request
the NEW results ZIP to validate this snapshot on Linux/P100 and capture the
previously added GPU-memory diagnostics. The old P100 baseline stays historical.

## Second Kaggle return, 14 September 2026

User returned Downloads/sih26119_kaggle_results (1).zip. Audited/preserved as
reports/kaggle-gpu-02; exact source f9b8a366... matches MILP iteration 01.
128 source files and 63 runtime hashes verified. Completed CUDA/P100 run:
230/230 generated, 12/12 Netlib, 4/4 historical MILP, 4/4 application cases,
2/3 QPLIB, 0/3 completed modern MILP, 9/9 scale (including 3/3 CUDA).

binkar10_1 improvement confirmed on Kaggle: feasible 7297.320029 at 13.7940 s,
549 nodes at 30 s, bound 6658.583810, gap 8.7518%. Kaggle and fresh local
independent readers both measure zero original feasibility/integrality
violation. Not an optimality proof; the other three hard cases remain open.
P100 million-variable synthetic box QP: 2.96186 s vs CPU1 15.94096 s (5.38x),
single pass. GPU still loses at 1,000 variables. No QP/CUDA core changes.

Memory diagnostics now show NVML successful but no matching solver PID,
despite one visible GPU process. Whole-device peaks are available; solver-only
VRAM is not. Cause of PID mismatch is not established. Do not relabel device
memory as process memory. Current snapshot now has its own GPU evidence.

No new notebook or rerun needed for this import. Next numerical priority remains
constrained QPLIB 9002. See reports/kaggle-gpu-02/REPORT.md and AUDIT.json.

## QP iteration 01, 14 September 2026

User authorized starting the constrained-QP cycle. Preserved the MILP build and
both returned Kaggle snapshots. New build is build-qp-iter1, CLI SHA-256
4786604e43e70efdaf92c93c9294df1fa12fc71aa97358c2ebfc89ca509c8a2c.

9002 is strictly positive diagonal with 1,649 equality rows and 2,890 columns;
curvature spans about 11 orders and some bounds are around 1e11. Removing the
old 512-variable specialist cap alone stalled above tolerance. Magnitude
normalization after curvature whitening, with correctly rescaled duals, solves
it. Added structure-based bounded dispatch and exact separable numerical dual
bounds; strict-diagonal acceptance now also requires relative gap <= tolerance.
No tolerance relaxation, name-based routing, coefficient dropping or external
solver use in the core. LP/MILP/CUDA numerical sources are unchanged.

Retained-source full gate: CTest 3/3, 251/251 generated (21 new equality cases),
7/7 adversarial certificate checks, 12/12 Netlib, 4/4 historical MILP, 4/4
application examples and 6/6 CPU scales through one million variables. Original
QPLIB candidate KKT checks now pass 3/3; completed-reference comparisons stay
2/3 because the unchanged OSQP 9002 reference protocol still times out.

Final 9002 repeats: 4.2754, 4.1924, 4.8112 seconds, all 180 iterations. Independent
objective 5698097498.566484, numerical lower bound 5698097498.119152, relative
feasibility 8.5718e-8, stationarity 2.4132e-16, complementarity 4.1248e-11,
relative gap 7.8506e-11. Maximum absolute violation is 2.3810; do not confuse
relative acceptance on huge values with exact/absolute feasibility.

binkar10_1's feasible 7297.320029 incumbent is retained; modern MILP completed
score remains 0/3. All unsuccessful experiments and harness setup/scoring
errors are preserved with explanations. Current evidence: reports/qp-iteration-01
validated-cpu and final-repeats. See REPORT.md and docs/DIAGONAL_QP_METHOD.md.

Separate next delivery: kaggle_delivery/qp_iteration_01, same small two-cell
notebook and matching external private-input source ZIP. It requires a NEW
Kaggle return; old P100 evidence must not be attributed to this snapshot.
No MIQP/NLP/MINLP/nonconvex scope expansion in this iteration. Remaining work:
modern MILP gap/feasibility progress, broader QP tests, industrial inputs, repeated
equal-accuracy measurements, organizer clarification and submission material.

## MILP iteration 02 — focused Kaggle experiment

User wants faster hard-MILP iteration without waiting for the QP Kaggle return.
Added opt-in --branching reliability; existing fractionality remains default.
Pseudocost learning and bounded trial LPs only select variables, never manufacture
proof bounds or prune nodes. Original candidate checks remain unchanged. Added
branching counters, trial time and incumbent_trace to JSON. New build is
build-milp-iter2; build-qp-iter1 and earlier deliveries remain preserved.

Local smoke: 160 generated checks across BOTH strategies, CTest 3/3. Six hard
runs at equal 15-second / 250,000-node budgets, all time-limited. markshare_4_0
incumbent improves from about 21 (control) to 13 (reliability); binkar10_1 both
7127.780038; blend2 neither finds a candidate. All four incumbents independently
verified. Zero-second references were candidate checks, not optimum comparisons.

Dedicated delivery kaggle_delivery/milp_iteration_02: 180 seconds and 250,000
nodes per model/strategy, 3 models x 2 strategies, 160 generated checks and
30-second independent references. CPU only, no GPU quota needed. Notebook
remains below 1 MB with matching external ZIP as private input. Expected return
is sih26119_milp_results.zip, not the previous generic Kaggle filename. It does
not run the QP/GPU sweep; reliability is not yet promoted to default. See
reports/milp-iteration-02/REPORT.md and local-smoke for exact evidence.

## Focused MILP Kaggle return, 14 September 2026

Imported Downloads/sih26119_milp_results.zip as reports/kaggle-milp-01.
Returned hash f70ee00fcd9df87da3c9e9ef759c8558747d2b350de431ddf2a98261fbe497e8;
source a200a445... matches the delivered MILP iteration 02 exactly. Verified
140 packaged / 71 runtime hashes, CMake CPU-only, CTest 3/3 and generated160/160.
Fresh local original-MPS checks verify all four hard-case incumbents.

At equal 180 s / 250k-node caps: markshare control reaches objective about5
(node limit,164.17s), reliability about7 (time limit,180.04s). The longer run
reverses the short local ranking; do NOT promote reliability to default.
binkar both7297.320029, control gap8.6587%, reliability8.5743%; neither improves
its first incumbent at~14.3s. Local15s7127 incumbent is not reproduced: local
15cuts/1rollback/2pump projections versus Kaggle18cuts/0rollback/1projection.

blend2 neither has an incumbent; both stop EARLY with iteration_limit at41.27s
and53.92s. Source confirms default10,000-iteration cap per LP relaxation, then
MILP abort/requeue on unresolved LP. This is not the250-step trial-probe cap.
Exact cause of the difficult LP remains unmeasured; capture failing node/basis
and implement bounded recovery before simply raising limits. Stronger branching
alone does not solve this termination issue.

Zero hard optimum completions. Reference solves blend2 at7.598985 but times out
on markshare/incumbent3 and binkar/incumbent6746.760023. Keep those latter values
as reference incumbents, not optimal values. No core/default changed on import.
No rerun of unchanged notebook needed. Next bounded work: tree-LP recovery and
post-incumbent improvement, preserving all proof/candidate validation rules.

## MILP iteration 03 — recovery and incumbent improvement

Implemented opt-in LP cold/dense recovery, proof-preserving deferred nodes,
LP-guided restricted neighbourhood search, and first-failed-LP model/input-basis
capture. Default branching stays fractionality; new options remain opt-in.
Final build build-milp-iter3 SHA-256
ae6d294de68e932ae3c48ea784a34651a040cc530f1e91540eab0ad96e88e19f.
Earlier builds/deliveries/returns are preserved, plus the initial iteration-03
binary and changed MILP source before the final repair-handling fix.

Final-source CTest3/3 and generated240/240 pass. Six equal15s hard smoke runs
yield four independently checked candidates: markshare both~21, blend2 none,
binkar control7297.320029 vs new6810.690026 (gap8.8011% vs2.2929%). Initial
60s experiment reached binkar6789.670035 vs7297.320029; those distinct-source
results are retained with a failed blend2 gate, not relabeled as final evidence.

The initial blend2 cold recovery succeeded, then a nearly integral candidate
failed strict absolute feasibility and its exact-fixing repair failed. Final
handling retains that node/bound unresolved and continues the other tree work.
The final equal90s blend2 comparison: control stops33.49s/3762nodes at LP cap;
new mode reaches90.03s/8170nodes, recovers3/3 LPs, retains2 unresolved nodes,
and improves lower bound7.468466152 to7.564874474. Still no valid incumbent.

Captured failing node4615/depth19 reaches10000 warm pivots; cold sparse513
and dense546 pivots both solve to7.7347385328076, agreeing with independent
HiGHS. This supports recovery but does not prove the exact warm-stall cause.
The first cold-diagnostic reference invocation missed a required candidate
argument; its error is retained, the helper is fixed, and the rerun passes.

Separate delivery kaggle_delivery/milp_iteration_03: two-cell sub-1MB notebook,
matching private input ZIP, CPU-only, six180s/250k hard runs and240 generated
checks. Return sih26119_milp_results.zip. New Kaggle execution remains pending.
No general speedup, hard optimum completion, new GPU evidence or submission
ranking is claimed. See reports/milp-iteration-03/REPORT.md for exact evidence.

## Kaggle MILP iteration03 return and Downloads cleanup — 15 September 2026

Imported Downloads/sih26119_milp_results (1).zip to reports/kaggle-milp-02.
Return SHA711867e10aba5bc0cb0192faed038a0a86e20c94b03826c1473123b24eabb7fa;
source1ba3309e... matches delivered iteration03 exactly. Verified176 source and
74 runtime hashes, CPU-only CMake, CTest3/3 and generated240/240. All four
incumbents pass fresh original-MPS feasibility/integrality checks locally.

Equal180s/250k-node pairs: binkar control7297.320029 vs new6747.310015,
gap8.6623% vs1.2257%, five post-first incumbent improvements by77.60s. The new
bound is slightly weaker, so this is incumbent improvement, not proof speedup.
Reference times out with6746.760023; do not call it an optimum. markshareboth~5,
83.33% gap, node limit. blend2control stops45.18s/3762nodes; newmode runs180s/
10285nodes, recovery5/5 in0.409s, bound7.591048200, two unresolved nodes, NO
incumbent. Reference proves7.598985. Zero hard optimum completions.

First failed blend2 model/input basis is exactly the already-diagnosed local
snapshot; no need to repeat identical cold solves. Rejected near-integer points
are not in this return, so exact fixing/repair cause remains unknown. Next move:
capture those points and repair outcomes, distinguish genuinely infeasible
integer assignments from continuous numerical repair failure, then test checked
repair or branching without loosening1e-7 original feasibility/integrality gates.
Keep current combined mode as next comparison baseline; no default promotion
or core change during this audit. Unchanged notebook does not need another run.

User authorized removing redundant Downloads results. Verified SHA256 and length
against preserved project copies, then recycled exactly four resultZIPs: generic
Kaggle returns original/(1), and focusedMILP returns original/(1). Rehashed saved
copies afterward. Backups remain in kaggle-gpu-01/02 and kaggle-milp-01/02; removed
copies are also recoverable in Recycle Bin. No unrelated downloads were touched.
See reports/kaggle-milp-02/DOWNLOADS_CLEANUP.json for exact filenames/hashes.

## MILP iteration04 — checked candidate repair, 15 September 2026

User authorized the next repair iteration. Preserved iteration03 binary/source
and created diagnostic-only build plus build-milp-iter4. Captured blend2 node10612:
rounded violation2.000999984e-6, scaled sparse exact-fixing numerical_error.
Own dense and unscaled sparse solves find8.015188, matching independent HiGHS;
dense point has2.27e-13 violation. Added opt-in --repair-candidates bounded dense
fallback (2s per call,20% remaining, totalmin15s/10%); original1e-7 acceptance
and dense memory guard remain unchanged. No external optimizer enters the core.

Found a separate correctness defect: an almost-integer LP point repaired to one
integer assignment could close the whole node. Saved asymmetric-V example:
old binary incorrectly reports optimal80; new code without fallback flag branches
and finds true0.99999992. Proof-safe tiny-fraction branching/deferred bounds now
apply to successful repairs in BOTH modes; experimental fallback is separate.
Counterexample, exact CLI comparisons and regression tests are retained.

Final CLI SHA17ba159a72eaf04e34f6754795ac0013c8bc6c0a75b7bca9d1ce46318139a679.
CTest3/3 and generated240/240 pass, including new proof/repair/maximization/budget
regressions. Equal90s blend2 pair: baseline no incumbent; new8.015188 at58.43s,
independent violation2.2737e-13/integer0, reportedgap5.0051%. Both bounds7.563968067
and8055nodes. One dense repair0.382s; one tiny-fraction branch. Baseline2unresolved
versusnew0deferred atdeadline, but active proof tree unfinished. Reference proves
7.598985. Neighbourhood search does not improve the first new incumbent by90s.

Final15s six-run gate: both markshare~21, both binkar6810.690026, blend2none at
shortlimit. Four independently checked candidates, no unsafe/error run. Existing
LP/QP/CUDA numerical sources unchanged; no long QP/GPU sweep repeated.
Separate milp_iteration_04 notebook compares current combined baseline+shared
proof fix against optional repair at180s/250knodes. Still two cells,sub1MB,current
Python,CPU-only; return sih26119_milp_results.zip. New Kaggle execution pending.
No hard optimum/industrial completeness/ranking claimed. See iteration04 report.

## Execution-policy change — 15 September 2026

User explicitly requests local execution and assistant-led iteration for all
CPU-only work. Use Kaggle if and only if an experiment needs NVIDIA GPU/CUDA.
The iteration04 CPU notebook is no longer a requested user run. Preserve it,
but run the180s paired repair comparison locally and use its saved evidence.
Future CPU solver cycles must not be blocked on notebook upload/download.
See docs/EXECUTION_POLICY.md. CUDA evidence remains a separate GPU workflow.

## Completed local MILP comparison — 15 September 2026

Executed the full iteration04 repair comparison locally: same final CLI SHA17ba159a...,
six sequential180s/250k runs, alternating order, references afterward. No core
change or new CPU-only Kaggle handoff. CTest3/3 and generated240/240 pass.

Blend2 repair reaches7.598985 in114.5299s, matching independently solved HiGHS
optimum, gap_limit/reportedgap1e-7. Baseline has no incumbent after180s and four
unresolved nodes. Both final lower bounds7.5989841401015. Two dense fixes take
0.5833s total; accepted sequence8.015188 then7.598985, with proof-safe branching.
Both binkar runs retain6747.310015, about1.22% reportedgap; last improvement at
62.88/64.80s. Both markshare runs stop at250k nodes with~5 and83.33% gap.
References time out on binkar and markshare with6746.760023 and3, respectively;
neither reference incumbent is called a proven optimum.

All five final incumbents pass original-MPS checks. New audit_local_milp.py
also rechecks the two captured accepted dense repairs:7/7 vector checks pass,
maxabsoluteviolation about6e-9, integer0. Blend2finalviolation4.5475e-13.
Raw generated counts, source/model/binary/cache identity, budgets, aggregates,
rounding, traces and gap arithmetic pass. No unsafe/error run; one completed
reference comparison. Capture limits and uncaptured objective-only history
remain explicit. Full evidence: reports/milp-iteration-04/LOCAL_VALIDATION.md.

Retain optional repair without default promotion from one timing pass. Next
local CPU experiment should target binkar neighbourhood selection/budget use
and plateaued search, retaining markshare stress coverage and blend2/proof
regressions. No GPU required; no user result ZIP is pending.

## MILP iteration05 — local neighbourhood experiments, 15 September2026

Preserved iteration04 source/binary before edits. Added guided/diversified
selection, bounded per-call diagnostics and captured last-improved vectors.
First two-stall probe (CLIe0f8e2d4...) regresses binkar at90s:6789.67 versus
6757.19 guided. CTest3/3, generated240/240 and7 fresh vector checks pass, but
the performance regression is retained and not promoted.

Four-stall revision (CLI855c3413...) keeps the same cumulative allowance while
allowing4s/128-node triggered calls. Full180s/250k paired run: both markshare~5,
both blend27.598985 atgap_limit, both binkar6747.310015 at time_limit/~1.22% gap.
Six final incumbents and28 total captured/final points pass original-MPS audits.
No unsafe/error run. Markshare's diversified call improves early73 to61, but
the final objective is unchanged. Binkar's one late alternative gets only0.2022s
of allowance and explores one node. Trigger delay alone does not reserve budget.

Diagnostics reveal markshare spends16 calls before1s around73, while the tree
does not reach~5 until76s. Added separate opt-in --pace-neighborhood with
min(5s,2% total budget) start-time spacing, keeping guided selection unchanged.
Final CLIef1856d074862aa754a81e5bff7bfc44c350c02eae4f0a6b43a309c4f4e53cd6.
Single-strategy180s screen: markshare~5/node_limit, blend27.598985/gap_limit,
binkar6747.310015/time_limit. Calls now span54s on markshare but still do not
improve the final result. This is not a fresh paired/repeated timing comparison.
Three final candidates and12 available vectors pass independent checks.

Final CTest3/3, generated240/240, diagnostic checker11/11 pass. Eighty current
guided generated outputs exactly match prior status/objective/primal/bounds/
gap/nodes/LP iterations (timings/new fields excluded). Captures/checks include
integer-index sets, timing/aggregate consistency, max/min objective sense and
proof-safe local bounds. LP/QP/CUDA numerical modules remain unchanged.

No final-objective improvement is established, and neither new option becomes
a default. Preserve all failed/neutral experiments. Next CPU work must reserve
useful late-search budget and improve restricted domains or global bounds; the
three-instance score does not establish industrial readiness or a ranking.
See reports/milp-iteration-05/REPORT.md and FINAL_STATE.json. No GPU/Kaggle work
or user result file is requested.

## MILP iteration06 — local structural gain, 15 September2026

Reserved-search binary8bcdf69b... adds material-progress scheduling, late-call
and time reservations and private binary Hamming neighborhoods. Full six-run
comparison: both markshare~5; blend2 reserved7.598985/gap_limit versus fresh
guided8.015188/time_limit; binkar reserved6810.69 versus fresh guided no incumbent.
Five final candidates and28 available points pass independent checks. Other
application CPU activity and baseline variation are documented; no speedup or
default promotion is claimed. Prior stronger binkar6747.31 evidence is preserved.

Inspecting model structure motivated a separately versioned small-binary
meet-in-the-middle incumbent heuristic. Prototype finds objective1 with zero
original violation in0.206s. Final binary65686ab5... integrates --binary-meet
as an opt-in root helper, never a proof engine. Eligibility is structural, not
instance-specific: <=36 binaries, <=8 rows, optional single-row continuous
recourse. Actual blend2/binkar inputs are declined without enumeration.

Fresh markshare180s/250k pair: guided~5/118.95s versus new~1/103.88s, both
node_limit. New exact1 point appears at0.2411s; later tiny objective decrease
to0.999999998 has2e-9 violation, not meaningful progress below1. Bound remains
-1e-7 and reported gap~50%. HiGHS30s reference times out with3. Seven points
pass fresh audit. Three root-only repetitions return the exact1 point at
0.1969–0.1982s; all six final/root-vector checks pass. Not full timing repeats.

CTest4/4, including180 exhaustive structural cases; generated240/240; diagnostic
tests15/15 and parser3/3. Eighty guided generated outputs exactly match prior
default numerical results. Tests retain proof-bound separation and max/min,
zero budget/nodes, no-heuristics and unsupported-domain controls. Previous
core/binary archives and failed experiments remain intact. LP/QP/CUDA numerical
modules unchanged; no QP/GPU sweep or new Kaggle artifact. See iteration06 report,
method docs, final snapshot and FINAL_STATE.json. Next: safe proof-gap closure,
broader structural models, and general binkar numerical/root-search robustness.

## MILP iteration07 — independent exact proof closure, 15 September 2026

Added separate opt-in --binary-proof with checked int64 arithmetic, strict
structural/integer eligibility, complete bounded enumeration and exact original-
model witness verification. The old floating meet helper is unchanged and still
never supplies a proof. The exact attempt runs before floating presolve/root LP;
incomplete, unsupported or unsafe attempts add no proof bound. MPS parsing now
tracks original integer-literal/accumulation safety without changing ordinary
floating values. Fractional literals that round to integers cannot gain proof
eligibility. Defaults remain unchanged; no-heuristics does not disable a proof
explicitly requested by the user.

Twelve sequential local runs, two models x two profiles x three repetitions,
alternating order, 30s/250k/gap1e-6; references/checkers afterward. Markshare exact:
objective=bound=1/gap0 in0.65298,0.69621,0.73051s. Old meet mode: ~1 and50% gap
at30s in all repeats. Independent integer zero-objective equality hash joins
exclude every better point; all exact original witnesses have zero violation.
HiGHS30s still times out with3 and is NOT the source of markshare's proof.
P0033 exact:3089/gap0 in0.45823–0.47680s, independently recomputed with Python
unbounded-integer range joins. Existing mode is faster at0.08345–0.08602s;
this remains opt-in. HiGHS independently solves p0033 to numerical3089.

CTest5/5 includes600 new exhaustive proof cases plus180 existing heuristic
cases. Generated240/240,40 generated independent proofs,6 public independent
proofs,12 final candidate checks, diagnostic15/15, parser3/3, checker9/9 pass.
All40 unsupported mixed models safely fall back with proof verified=false.
Guided and old-meet outputs match iteration06 on160 generated runs, excluding
timing/new diagnostics. An additional post-timing -ftrapv probe passes98 checked
arithmetic boundary tests. Audit verifies67 timing-source identities and all
public result/model/checker links. CLI SHA256:
3e623c0cec0a943d042a1310be84f0962dbeaec021de7220f705dd1c6f8f7a90.

Separate final-source/binary and evidence in reports/milp-iteration-07. LP/QP/
CUDA numerical modules are unchanged; no new QP/GPU sweep, Kaggle artifact or
user upload. Markshare proof closure is now a submission result, not a promise
of general exact MILP support. Next target is binkar's open general proof gap
and numerical/search progress, followed by broader public/industrial validation.

## MILP iteration08 — checked cuts and delayed restart, 15 September2026

Binkar's saved guided run had no failed/recovered/deferred global LPs; inspection
found ten17-binary capacity rows. Added opt-in --lifted-covers with exact dyadic
conversion of parsed coefficients, exhaustive feasible-assignment separation,
sequential up-lifting and full cut-activity verification before export. Existing
cut-LP gates/rollback and candidate tolerance remain unchanged. Domain/arithmetic
guards decline unsupported rows. New C++400-row suite checks391 generated cuts.

Root prototype improves Binkar bound6645.94 to6662.93;29 cuts independently
verified. Direct resource-guarded build043cd987... then regresses Binkar in180s:
guided6747.31/bound6665.03/gap1.219%, direct6775.20/bound6681.85/gap1.378%.
P0033 remains3089 but slows0.118s to1.710s. CTest6/6,generated240/240,47 public
cuts and16 intermediate/final vectors pass. This failed performance attempt is
saved in direct-source/, direct_solver_cli.exe, local-180s/ and direct-audit/.

Final buildbea877af... adds separate --late-lifted-covers: one half-time restart
over the entire original domain, carrying only the valid global minimum bound
and same-run original-checked incumbent. Time/node/heuristic budgets stay spent.
Deterministic min/max tests verify incumbent retention/full-domain optimality,
node accounting, zero limits and no-cuts controls. No reference vector is seeded.

Fresh final180s pair, reversed Binkar order: delayed6747.310015, bound6682.719904,
gap0.95713%,180.239s; guided6747.310015, bound6665.353567,gap1.21447%,181.177s.
Remaining reported gap decreases21.19%; this is not a speedup or optimality.
Restart90.017s/node2117 carries6747.31 and global bound6662.370749. New retained
cuts25; additional independent audit confirms15 final/intermediate/restart
vectors and74 timing-source identities. P0033 solves3089 before any restart.
HiGHS30s Binkar times out with6746.760023; not called optimal. Markshare's
independent original-literal exact proof remains valid at1/gap0.

Final CTest6/6, generated240/240, diagnostic15/parser3/exact-checker9/cut-checker6
pass. Guided80 generated numerical outputs match iteration07; LP/QP/CUDA and
the binary-proof numerical implementations remain unchanged. Current build
build-milp-iter8c; final archive/report/state in reports/milp-iteration-08.
Defaults unchanged; next repeat the delayed schedule across budgets and public
models, then improve the remaining Binkar gap. No GPU/Kaggle or user upload.

## MILP iteration09 — compact equations and an incomplete proof attempt, 15 September 2026

Added optional compact equality representation to the sparse simplex engine.
Equality identity columns are Phase-I artificials, excluded from Phase II and
warm bases. Equality dual multipliers are unrestricted; rays must satisfy both
directions. A failed compact attempt can fall back cold within the remaining
wall-clock allowance. Original feasibility and numerical tolerances stay unchanged.

Initial build d65d6327... reduces Binkar's root screen from 10.710s to 7.192s,
same lower bound and 1016 fewer canonical rows. But a fresh 180s full pair
regresses the immediate compact incumbent to 6772.83 and gap to 1.340%, versus
6747.31 and 0.963% for the control. Preserved under direct-source/binary,
paired-180s and direct-audit; 48 cuts and 15 saved vectors pass independent checks.

Final build 3335c4cc... (`build-milp-iter9b`) adds delayed compact activation at
the existing half-time full-domain cut restart. No time/node/heuristic budgets
are reset, and the same-run incumbent/global bound are retained. Deterministic
min/max tests check activation, early completion, no-cuts and zero-time guards.
Fresh reversed-order 180s pair: control 6747.31/bound 6682.700412/gap 0.95742%;
delayed compact 6747.31/bound 6682.903189/gap 0.95441%. That is marginal evidence,
not an established speedup. P0033 remains 3089/optimal before activation.

A separate 600s attempt processes 20431 nodes, 565762 LP iterations, and reaches
bound 6686.056417/gap 0.90769% with the same 6747.31 incumbent. It stops at
time_limit after 604.303s; Binkar is NOT proved optimal. Restart at 300.032s/node
9959 carries global bound 6667.065617. No compact fallback or unresolved LP node
is recorded, but the live MILP tree remains incomplete.

Final CTest 7/7 includes 300 new LP and 80 mixed MILP comparisons plus analytical
and delayed-activation guards. Generated MILP 240/240; 90 additional independent
HiGHS equality-LP checks cover 60 optimal, 15 infeasible and 15 unbounded cases.
Fifteen dependent-row fallbacks are exercised. Final pair audit: 48 cuts,
16 saved vectors, 77 timing-source identities. Long-run audit: 23 cuts,
7 saved vectors, 78 identities. The extra reference test was added after the
paired timing protocol was captured and is included in the long-run identity.
Post-timing diagnostic/parser/checker tests pass 33/33. Control outputs match
iteration08 on all 80 generated cases compared. Markshare's independent exact
proof sentinel remains valid at 1/gap zero. No new QP/GPU or Blend2 long run.

Source, binary, failed experiment, audits and final state are versioned in
reports/milp-iteration-09. Defaults remain unchanged. Next investigate redundant
propagation-derived continuous bound rows with explicit safety gates, then
stronger general search/bounds. CPU only; no Kaggle artifact or upload needed.
