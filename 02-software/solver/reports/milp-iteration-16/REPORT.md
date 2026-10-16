# MILP iteration16 — first-feasible protection and separate mas74 diagnosis

Completed local iteration, 15–16 September 2026. The new guard protects the
experimental first-feasible path, but is not promoted over the five-round
baseline. Mas74's exit mechanism and a sparse numerical failure are reproduced;
the underlying numerical fix remains next work.

The optional [incumbent-gated cut rule](../../docs/INCUMBENT_GATED_CUTS.md) is
implemented without changing iteration15's thresholds, proof/tolerance logic
or recovery. The predeclared comparison is five rounds versus adaptive cuts
enabled only after an original-model-accepted incumbent exists. Both adaptive
options remain OFF by default. The old ungated experiment and archives remain.

## Preflight

All 14 CTest groups and 115 Python unit tests pass. The expanded C++ policy group
checks 120 exhaustive min/max models with 1080 full solves and 2160 partial/zero
checks, observing 408 cut rounds and 672 restarts. Separate analytic C++ tests
run 12 solves, observe 14 protected rounds and 2 stops after checked incumbents.
Both min/max first-feasible counterexamples now complete under protection;
the retained ungated policy still returns a partial no-point result there.

Seven fixed-node cases have identical semantic results under frozen15,
current defaults, current trace capture and current guarded policy. These use
no heuristics and generous time limits; they are not claims about identical
time-limited trajectories. The 28 independent MPS domain cases also pass.
CLI misuse (protection without adaptive mode) is explicitly rejected.

Candidate executable SHA256:
`9fcd999d6226c9464513c22554680e78e90e586a521f6a1d0001a34283841502`.

The public protocol and separate diagnostic ablations are fixed in [PLAN](PLAN.md).
All 24 public models here are retained development cases; no new untouched
holdout or universal MILP performance claim is made this iteration.

## Independent analytic integrations

All 12 CLI integrations on four generated MIN/MAX cases pass original-MPS,
bound-orientation, cut-policy and work checks. The 40-pair cases have a fixed
continuous chain and known optima +/-51356000; with one tree node and heuristics
off, ungated cuts stop too soon and return no point. Guarded and baseline runs
numerically complete. The 100-pair cases have known optima +/-51350000 and a
counter restart: guarded cuts wait for the solver's own first point, then stop
after two restarted rounds and numerically complete. Ungated returns a checked
point but remains open under that node limit. No point or answer is injected.

The independent source-vector checks validate six cut-root incumbents across
these modes. Eight stop decisions replay, including two in guarded runs after
known incumbents. The synthetic objective contains a large fixed contribution;
this intentionally exposes the weakness of a relative-dual-gain-only metric.
These are analytic coverage cases, not public benchmark counts or evidence of
a general speedup. See [integration summary](analytic/SUMMARY.json).

## Two paired screen repeats per target

All 12 outputs, their final vectors and their cut-source incumbents pass the
independent checks. Both modes numerically complete mod008 twice and return
checked feasible limits on Binkar and p0282. No candidate tuning follows.

| Case / repeat | Baseline objective; gap | Guarded objective; gap |
|---|---|---|
| Binkar / 0 | 6810.690026; 1.9370% | 6810.690026; 2.0421% |
| Binkar / 1 | 6810.690026; 1.9528% | 6808.850028; 2.0156% |
| p0282 / 0 | 266462; 3.5168% | 266462; 3.5071% |
| p0282 / 1 | 266462; 3.5251% | 266462; 3.5074% |
| mod008 / 0 | 307; numerical completion, 28.22s | 307; numerical completion, 28.92s |
| mod008 / 1 | 307; numerical completion, 28.33s | 307; numerical completion, 28.76s |

Binkar retains four cut LPs at the first root while there is no incumbent.
After its own checked incumbent exists, the restarted guarded loop stops at
round two: six total cut LPs versus eight. It now preserves a point in both
runs, unlike iteration15's ungated failures. However both guarded gaps are
worse than their paired baseline gaps. Preserving feasibility is not a general
full-solve improvement, and the optional policy is not promoted from this screen.

P0282 retains nine cut LPs in every run, despite one recorded adaptive stop.
The stop does not establish an avoided LP call; the control also has no further
cut to add. Its small reported-gap differences do not establish a policy gain.
Mod008 has five cut LPs and no adaptive stops in every run. All four cross the
existing half-time restart boundary, completing with 16629–16888 total nodes.
Clock-driven work and shared-desktop load prevent clean cross-version speed
claims. See [all screen records](screen-30s/results.json).

## Separate frozen15 mas74 diagnosis

These three diagnostic runs use the archived iteration15 executable, not the
new candidate. All final points and saved frontier/work checks pass. No LP
recovery algorithm, proof rule or tolerance is changed in this iteration.

| Frozen15 diagnostic | Outcome | Recovery seconds | Unresolved nodes |
|---|---|---|---|
| Existing late-transform restart | Unresolved at 15.023s; objective 14165.464078 | 6.00027 | 2 |
| Same restart without late LP transformations | Unresolved at 15.012s; same objective | 6.00048 | 2 |
| Clock restart disabled | Time limit at 30.019s; objective 14113.274425; gap 23.8060% | 6.00189 | 5141 |

The complete 7813-event trace of the first diagnostic shows 1452 queued and
285 deferred nodes before the restart. A full-domain root replaces them while
carrying the checked global minimum. Its two children both fail to resolve and
are deferred. The active queue is then empty; the existing loop terminates with
two unresolved nodes and retains their bound. The nominal time limit is still
30s: this is not an accidental 15s global limit. The global recovery allowance
of min(30s,20% of time limit), here 6s, was already spent and is correctly not
reset at restart. Disabling the transforms does not avoid the failure.

With the clock restart disabled, the old queue continues to the full budget
but accumulates 5141 unresolved nodes. That control's frontier trace truncates
at 20000 events, so its full final queue history is not independently replayed.
Avoiding the restart can preserve more useful search here; it does not repair
the underlying LP reliability issue or justify changing every model's restart.

Cold replay of the original first captured depth-one LP isolates a numerical
failure even without its saved warm basis. At the ordinary 10000-iteration
allowance and 5s limit, both sparse and dense methods use 130 iterations:

| Captured continuous relaxation | Sparse | Dense recovery |
|---|---|---|
| Status | numerical_error | optimal |
| Objective | 10515.605883733524 | 10515.606014154164 |
| Independently checked absolute violation | 9.7701e-5 | 4.3656e-11 |
| Reference optimum | 10515.606014154164 | 10515.606014154164 |

The sparse result's relative primal/dual gap is 3.3785e-8, above the existing
1e-8 verification threshold. Its scaled primal and dual residuals pass their
relative checks, but the independent absolute violation is still material.
The original model has a continuous upper bound of 1e12 and small 1e-5 costs;
cancellation/refinement is a plausible investigation target, not a demonstrated
specific arithmetic root cause. Cold replay does not reproduce the warm pivot
trajectory that first failed after five reported iterations. Loosening checks
or simply granting unlimited recovery would hide the problem, not solve it.

The demonstrated exit mechanism is exhausted recovery plus full-domain restart
into unresolved children. The underlying sparse numerical issue is reproduced
but not fixed. See [diagnostic records](mas74-diagnosis/results.json),
[cold replay](mas74-diagnosis/cold-replay.json) and [next work](NEXT_STEP.md).

## Full 24-case development wave

All 48 outcomes pass independent checks. Both profiles have the same counts:

| Outcome category | Cases per profile |
|---|---:|
| Restricted exact proof checked | 2 |
| Numerical optimal/gap completion checked | 8 |
| Checked feasible point, time limit | 10 |
| Unresolved relaxations, checked point | 1 |
| No point at the time limit | 2 |
| Infeasible status cross-checked, not exact proof | 1 |

The exact cases are p0033 and markshare_4_0. Numerical completions are enigma,
flugpl, stein27, egout, lseu, mod008, p0201 and rgn. Blend2 and lotsize still
have no point. Mas74 remains unresolved at about 15.02s in both profiles;
neos859080 agrees with the independent infeasible status in both.

Binkar's wave baseline returns 6804.410009 with 1.8480% gap; guarded returns
6810.690026 with 2.0445% gap. Across the two screen repeats and wave, guarded
preserves a checked point in all three runs but has a worse gap than every
paired control. The first-feasible protection is functioning; it is not a
demonstrated improvement over the five-round baseline.

Other partial results remain mixed. Assign1-5-8 is 224 at 16.2623% gap under
baseline versus about 228 at 17.7104% under guarded. Misc03 keeps objective 3360
with gaps 4.0167% versus 3.8679%. Both modes leave large reported gaps on gt2
(67.31%), misc07 (46.73%) and pk1 (96.88%). These are selected time-budget
outcomes and numerical bounds, not exact certificates of near optimality.

Only Binkar and p0282 record an adaptive stop in the guarded wave. P0282 still
uses nine cut LPs in both modes. Differences on models with no cut stop must
not be presented as evidence that stopping cuts improved those models. In
particular mod008 takes 27.21s / 17546 nodes under baseline versus 14.88s /
8781 nodes under guarded, but makes no adaptive stop: the first run crosses
the existing half-time restart boundary and the second finishes just before it.
Shared-desktop timing and clock-driven search explain why this is not a clean
policy speedup. See [the complete wave ledger](wave-30s/results.json).

## Final regression gate

The full gate repeats all 14 CTest groups, 115 Python units, 28 MPS-domain cases
and seven four-way fixed-node parity cases successfully. Four profiles
(baseline5, guarded0, guarded1, guarded5) pass 320 generated runs on 80 models;
100 reused exhaustive MPS models also complete and match their known objectives
with fresh references. These generated gate runs have zero cut rounds, so the
separate exhaustive C++ traces and analytic integrations supply the targeted
cut-branch coverage. See [gate summary](final-gate/SUMMARY.json).

The final gate overlaps only independent reference/validation work after all
candidate performance timings are complete. No build, reference solve or heavy
test from this task overlaps a measured candidate own solve. The unrelated
desktop load is not controlled, and reference solve limits are not equal-budget
performance comparisons. All CPU work stays local; no Kaggle upload is needed.

## Saved-result audit and decision

All 60 candidate public records pass re-audit: 54 final vectors, four restricted
exact-proof recomputations on two models, 135 retained lifted covers and 98798
saved lattice events. Twenty-four lattice traces explicitly truncate at 4096
events; these counts do not mean every internal bound update was checked.
All 142 recorded cut rounds replay, including six stop decisions. Twelve
cut-root source incumbents are independently rechecked. There are zero pending
reference point checks and zero observed candidate-output validation failures.
The intentionally failing cold sparse diagnostic is retained separately, not
counted as a successful LP solve. Diagnostic output/reference hash chains are
also verified. See [result audit](final-audit/AUDIT.json) and
[policy/source-incumbent audit](final-audit/POLICY_AUDIT.json).

Retain five rounds and both adaptive options OFF by default. The guard fixes
the reproduced first-feasible allocation regression in the tested cases, but
does not improve broad completion and worsens Binkar's gap in all three pairs.
There are no fresh holdouts this iteration. The highest-value next experiment
is the retained sparse LP numerical fixture, not further tuning of this cut
gain metric. Do not relax tolerances or silently reset recovery budgets.

The [final state](FINAL_STATE.json), [source manifest](SNAPSHOT_MANIFEST.json),
`final_solver_cli.exe` and CMake cache identify the completed archive. The
freezer verifies the candidate and every timed source/checker/test snapshot,
and rechecks frozen15's executable, source and evidence hashes. Documentation
is finalized after results and is separate from timed source selection.
Bulk datasets and historical gate dependencies remain separate; see
[reproduction instructions](../../docs/V2_REPRODUCE.md).
