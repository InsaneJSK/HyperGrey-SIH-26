# Iteration19 — recover valid points from rejected dive candidates

Completed local CPU experiment: implementation, regression gates, 74 paired
public runs, independent point checks and final re-audit. The optional repair
repeats a direct first-feasible gain on blend2; broad completion remains open.

## Implemented change

Optional `--repair-heuristic-candidates` extends bounded numerical candidate
repair to dives, requiring `--repair-candidates`. It does not change pump seed
handoff, branching, root cuts, restart policy, LP tolerances, or proof bounds.
The repair uses exact integer fixings on the original model and unchanged
original-model point acceptance. Sparse polishing precedes dense recovery;
the helper exports points only, never a node proof or global objective bound.

At most 16 unique integer fixings are attempted. Both sparse and dense work
charge the existing shared repair allowance, bounded also by the remaining dive
slice. Duplicate fixings are skipped; no spent recovery/time budget is reset.
See [algorithm and limits](../../docs/HEURISTIC_CANDIDATE_REPAIR.md).

## Diagnosis, kept separate from candidate timings

Stage A adds bounded `--capture-feasibility` and passes 18 CTest groups,
including 80 trace-on/off solves on 40 small min/max exhaustive models. Its
five public diagnostic outputs are independently checked: blend2, lotsize and
danoint have no point; eil33-2 and rout have checked points. Those latter
outcomes are baseline variability, not gains from the new repair.

The blend2 trace exposes an integer-close point rejected on original rows.
Because the first trace's vector budget was exhausted, a separately compiled
capture gives that rejection priority within the same 100000-value cap. The
repeated candidate is saved at node 185, call 3, step 28. Its raw violation is
2.01e-6 and its rounded violation 2.129e-6, both independently checked and
above the unchanged 1e-7 threshold.

Frozen18 cold replay of the same integer fixing fails in sparse LP but succeeds
in dense LP: objective 8.788661, about 0.32s, original-model violation
4.55e-13 and zero integrality error. This independently validates a feasible
fixing at the stated tolerance, not full-MILP optimality or equivalence of
cold/warm pivot paths. No reference
incumbent is supplied to the core. Full artifacts are in `rejection-replay` and
[the diagnosis](DIAGNOSIS.md); both diagnostic builds are retained separately.
The replay runner initially failed a preflight model lookup before doing any
LP solve; it was corrected to use the saved manifest path. No solver outcome
was discarded or replaced by that path correction.

Other mechanisms remain: lotsize has hundreds of fractional variables and slow
projections; danoint has expensive LPs; repeated targets are perturbed but still
can be infeasible. Pump fractional progress alone is not proof that a fixing is
feasible. That is why this candidate addresses the reproduced numerical
rejection instead of combining it with a pump/diving redesign.

## Correctness and controls

The candidate passes 19 CTest groups, 140 Python tests, 28 MPS-domain cases,
320 generated MILP runs and 100 retained exhaustive MPS cases. Both sparse
refinement modes retain their cold/warm tests and 24 transformed LP equivalents;
four saved LP points are independently checked. The new fixing regression
exercises dense recovery in equivalent MIN/MAX formulations, fixed assignments,
input/budget guards and priority rejection capture.

Four no-heuristic disabled-option cases retain parity with frozen16. Separately,
12 fixed-node runs on p0201/mas74/lseu/enigma compare frozen18, new repair-off and
new repair-off with tracing: all four three-way semantic comparisons pass.
These parity runs are not equal-time performance evidence. The generated
tests guard correctness; actual repair-branch effectiveness must be judged on
the captured regression and full public integrations, not their test count.

## Public protocol

Both profiles use the same final binary and existing selective basis refinement.
Only `--repair-heuristic-candidates` differs. `SCREEN.json` repeats two alternating
pairs for blend2, p0201, eil33-2, binkar10_1 and mas74 (20 runs), with the detailed
feasibility trace in both profiles. `WAVE.json` covers all 27 development models
once per profile (54 runs), without detailed feasibility capture. No fresh
holdouts are claimed: all inputs have already informed development.

Each own run uses 30s, 250000 nodes and gap1e-6. Own runs are sequential and
finish before references, with no competing task builds or reference solves.
Independent references have a 5s solve allowance and 150s external watchdog;
this is not an equal-budget performance contest against HiGHS. Shared-desktop
timing can change pump/dive/restart paths. All limits, unresolved outcomes and
regressions remain in the record. Six earlier diagnostic public runs and twelve
fixed-node parity runs are separate from these 74 candidate comparison runs.
All gap percentages here use the solver's unchanged normalization
`max(0, incumbent - bound) / (1 + abs(incumbent))` in minimization sense. They
are reported gaps, not assumed identical to another solver's `mip_gap` field.
No-point runs have no meaningful incumbent gap and remain a separate category.

## Repeated five-model screen

All 20 records and all 18 returned points pass their checks. Both profiles have
two numerical completions (the repeated p0201 case). Control additionally has
six feasible limits and two no-point limits; repair has eight feasible limits.

The central gain repeats: neither blend2 control finds a point, while both repair
runs return independently checked objective 8.788661. First points arrive at
3.568s and 3.436s. Each uses one sparse attempt and one dense recovery, taking
0.363s / 0.387s from the shared 3s repair allowance. Final gaps are 13.5792% /
13.6010%; these are feasible limits, not full-MILP completions.

| Model | Control repeats | Repair repeats | Interpretation |
| --- | --- | --- | --- |
| blend2 | No point in either | Checked point 8.788661 in both | Repeated first-feasible gain; about 13.6% still open |
| p0201 | Both complete at 7615 | Both complete at 7615 | No observed completion regression |
| eil33-2 | Points 1204.099899 / 1207.176291 | Point 1204.099899 in both | All remain open; no repair attempts on this model |
| binkar10_1 | Points 6810.690026 / 6787.820026 | Points 6787.820026 / 6810.690026 | One paired gain, one regression; no actual repair attempts |
| mas74 | Point 12914.438691 in both | Same point in both | Open gaps about 15.5–15.6%; not a completion |

P0201 also has zero heuristic repair attempts. Mas74 has one accepted repair
per candidate run, costing about 0.0008s / 0.0014s, but final objective is
unchanged and paired gaps are mixed. All four mas74 runs have zero LP recovery
attempts and zero unresolved nodes. A repair's `successes` counter means a
valid point was accepted; it does not necessarily mean the current incumbent
improved. Clock-driven trajectory differences on models with no repair attempts
are retained as observed outcomes, not credited as direct algorithmic gains.

## Full 27-model development comparison

| Outcome at the 30-second budget | Control | Repair |
| --- | ---: | ---: |
| Restricted exact-subset completion | 2 | 2 |
| Independently checked numerical completion | 7 | 7 |
| Checked feasible point, optimality still open | 12 | 14 |
| No point at limit | 5 | 3 |
| Cross-checked infeasible | 1 | 1* |
| Total models | 27 | 27 |

Thus control returns 21 checked points versus repair's 23; only nine in each
profile have an optimality/tolerance completion. See the
[complete model ledger](MODEL_LEDGER.md) for every objective and gap. Neither
23 checked points nor 24 models with a point/infeasibility outcome means 24
optimality proofs or reliably handling arbitrary models.

* The original neos859080 repair reference stopped at its five-second limit,
so the raw wave and main audit correctly retain `terminal_reference_pending`.
The paired control reference reported Infeasible on the identical hashed MPS.
The separate [terminal pair cross-check](terminal-pair-crosscheck/SUMMARY.json)
validates the repair status against that saved independent reference, without
rerunning either solver or overwriting the timeout. This is numerical
infeasibility-status agreement, not an exact infeasibility certificate. Its
post-measurement runner is retained as `check_terminal_pair.py` in this report
directory; no timed source, binary or checker was edited for this check.

Blend2 again returns 8.788661 with repair and no point with control, this time
without detailed feasibility capture. Across the repeated screen and this
wave, that is three repair-profile points versus no control points. The third
first point arrives at 3.378s, with about 0.385s of repair work. This is the
directly reproduced mechanism gain, not a claim that every better timed result
was caused by a repair.

Both mod008 runs stop with objective 307 and a 0.3247% reported gap, rather than
completing as in iteration18's earlier timings. Both lseu and p0201 still
complete but cross different clock/restart boundaries from the screen. For
example, lseu control restarts at node 23605 and finishes in about 21.81s. These
are shared-desktop runs, not a clean speed comparison against a prior archive.

Other partial outcomes remain mixed: p0282 and gen-ip002 have slightly better
candidate gaps; misc03 is unchanged; misc07 and mas74 have worse candidate gaps.
Binkar's candidate point is better in the wave but its screen pairs split one
gain/one regression. Pk1's candidate objective improves from 32 to 31 while
both gaps remain near 97%. Gt2 stays near 67%. These cases are far from proved.

Lotsize and eil33-2 still have no point in either profile. Eil33-2's four screen
points followed by two wave failures must remain visible; the new repair does
not guarantee its first feasibility. Its different time-limited path does not
by itself establish a root cause or demonstrate that a longer budget will fix
all failures.
Danoint also has no point in either profile. Rout returns 2102.730000 only in
the repair profile, at about 20.85s and a 52.55% reported gap, but it records
zero heuristic repair attempts. The diagnostic baseline had previously found
a different rout point. Therefore this is retained as variable search/clock
behavior, not evidence that the new repair caused that improvement. Mas76
returns 41519.995740 in both profiles, still with gaps above 5%.

## Final audit

All 74 paired records pass the saved-result re-audit. All 62 returned final
points have independent original-model checks; no final point is pending.
The separate terminal-status timeout and cross-check above are not hidden by
that zero-pending-points count. No observed validation failures occurred.

The audit recomputes four restricted exact proof records, checks 81,718 saved
objective-lattice events, 174 retained cuts, 126 cut-policy rounds and 12 saved
cut-source incumbent vectors. Eighteen lattice traces are truncated at their
declared cap; these counts do not imply full exact proof coverage of all nodes.
Bounded pump/dive trace metrics, source identities, option identity, exclusive
work accounting and refinement/repair counters pass their respective checks.
Detailed feasibility vectors are captured in the screen, not the full wave;
the audit does not independently replay every intermediate heuristic point.

There are seven heuristic repair attempts and seven accepted valid points
across these 74 runs: four in the screen and three in the wave. Accepted points
need not improve an existing incumbent. The single retained rejected-point
regression, independent integer-fixing replay, repeated full blend2 runs and
negative-input/budget tests support the repair mechanism; the public attempt
count is small and does not establish universal reliability.

Evidence: [main audit](final-audit/AUDIT.json),
[repair audit](final-audit/HEURISTIC_AUDIT.json),
[full regression gate](final-gate/SUMMARY.json), and
[disabled-option parity](control-parity/SUMMARY.json).
Screen results SHA-256:
`49b751bb4ec906f1da535cf05be7be6e58c0801483fb355c966c189785d07eb8`.
Wave results SHA-256:
`9a272cf3d8d37691a0ac1b84cddfb431d22cc2a8fe4f159c5fc5b0e4fc32f1d7`.

## Decision and next work

Keep heuristic candidate repair **optional**, along with the existing selective
accuracy options. It addresses a reproducible missed-point mechanism without
weakening original-model checks. It is not a redesigned feasibility pump,
stronger global relaxation, general LP numerical fix or universal first-point
guarantee. The captured sparse integer-fixing LP still needs dense recovery.

The next priority is candidate generation on the remaining no-point cases,
separately from tighter valid bounds for models with incumbents but large gaps.
See [the bounded next experiment](NEXT_STEP.md). The ten-iteration planning
budget is a checkpoint, not a prediction that every case will be resolved in
30 seconds. Full-library/industrial robustness, hard resource containment,
real refinery/domain validation and final GPU-specific evidence remain open.
No Kaggle upload or new user input is needed for the next CPU experiment.

## Reproduction and archive layout

Use the [local reproduction instructions](../../docs/V2_REPRODUCE.md) and the
saved plans. Keep the original datasets and old gate dependencies; the C++
repair fixture uses the retained blend2 MPS and `tests/heuristic_rejected_point.txt`.
The core is the project's own C++ solver. HiGHS is an independent checker/model
reader, not the optimization backend and not a source of incumbent vectors.

Final candidate executable identity: 803,842 bytes, SHA-256
`bb14f6adeb88e869a618a185c0fd48d5666134812534d8c350d08166f6642b35`.
The instrumentation-only binary has SHA-256
`901f2ef4b831c60a4712467b8e18ca224c12b63ab60d552ab1c797c7328103d2`;
the separate priority-capture binary has SHA-256
`ace1344b8e693e692748e6b1042bc1f53a4740082061fa28204f5a75b18e1dab`.
The preserved frozen18 control has SHA-256
`8ff22dd62eabc5a8f41ea1c58a94ec79c9f8b0a99aeb47881fe099c2da665341`.

The final archive contains `final_solver_cli.exe`, `final-source`,
`SNAPSHOT_MANIFEST.json` and `FINAL_STATE.json`, alongside raw comparisons,
their source snapshots and final audits. Diagnostic source/binaries remain
separate so their results cannot be mislabeled as final-algorithm measurements.
