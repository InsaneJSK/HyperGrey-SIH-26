# Iteration 21 — private distance-objective diving

## Decision and full-wave outcome

Keep distance diving optional and off by default. The 27-model paired wave
returns 23 checked solutions for distance versus 22 for guided control, with
10 completions each. Distance gains eil33-2 and rout but loses misc07. Both
profiles report neos859080 infeasible; the original independent references
confirm it in 3.93 / 4.15 seconds, without an extended supplemental run.
The candidate's three no-point models are misc07, lotsize and danoint. This is
a mixed feasibility tradeoff, not 27/27 handled or proved, and not a net breadth
improvement over the historical iteration20 candidate's 23 checked solutions.

Eil33-2 and rout succeed in all three candidate observations (two screen
repeats plus one wave), versus no point in all three corresponding controls.
Eil33-2's wave objective is 1204.099899 (31.624% gap); rout retains approximately
1703.47 (41.378% gap). These are repeated observations on tuned development
models, not reliability guarantees or fresh holdouts.

Misc07's control returns 3785, first at 6.363 seconds, after 26 guided steps.
The distance candidate finishes just one private projection in two attempted
steps and never returns a solution within 30 seconds. Losing an existing
first-feasible path prevents blanket promotion of the new objective.

Both retain gt2 at 35673. Binkar10_1 improves 6810.6900 -> 6787.8200 and pk1
approximately 29 -> 20 in the wave, but neither executes a distance dive;
those differences are not attributed to this mechanism. Minor gap regressions
and all other rows remain visible in `MODEL_LEDGER.md`. Mod008 completes in
both profiles, unlike iteration20's timing; that is not a distance-feature gain.

The 10 completions comprise two restricted exact-subset certificates and eight
numerical/tolerance completions. The infeasible-model cross-check is separate.
Checked feasible solutions, completions, and terminal-status agreement must not
be added or described interchangeably. Combining best outcomes across multiple
runs is not a single 30-second solver result.

The final saved-run audit passes all 86 records and 65 final solution vectors,
with no pending point checks or validation failures. It also checks 40 retained
fractional seeds, 213 retained distance metrics, 57 saved cuts, 98310 lattice
events (22 traces are explicitly truncated), and recomputes four exact-subset
certificates. The main experiment exercises 27 private distance dives, 511
private LP calls, and 489 numerically verified private-LP points; these are
not 489 integer solutions. All 10 numerical-repair attempts return accepted
points, not necessarily objective improvements.

## What changed

Optional `--pump-distance-diving` (requires `--pump-guided-diving`) minimizes
L1 distance to the rounded retained pump seed in the first eligible dive mode.
Both flags remain off by default. General-integer interior targets use private
auxiliary columns; endpoint targets use a linear contribution with the correct
constant offset. Continuous variables stay in the original/node domain.

The private model starts cold and subsequently reuses only its own bases.
The failed primary branch cannot overwrite the parent's private basis used by
the alternate. Auxiliaries, objectives, dual bounds, rays, infeasibility flags
and bases are stripped before returning a point to the existing candidate path.
The original objective is recomputed at acceptance; original absolute row/bound
and integrality checks remain at 1e-7. No distance bound enters the proof queue.

No new model-name rules, reference incumbents, tolerance changes, batch fixing,
cut/restart policy or time/step increases. Construction and solves are inside
the existing per-call shared dive slice (at most two seconds for both modes,
64 steps per mode); the second dive remains original-objective. Pump and
numerical-repair scheduling/allowances are unchanged. Multiple scheduled calls
can consume more than two seconds in aggregate, as before.

## Predeclared repeated screen

Eight development models, two alternating pairs each, 30 seconds per solve.
Both profiles include iteration19 repair and iteration20 guidance. The sole
candidate flag is distance diving; detailed capture is enabled in both.
All 32 runs are retained. Independent checks pass all 20 final integer points,
with zero validation failures. The guided profile has 8 checked points (2
completions, 6 open) and 8 no-point runs; distance has 12 checked points (2
completions, 10 open) and 4 no-point runs. These are run counts, not unique models.

| Case | Guided control, both repeats | Distance candidate, both repeats |
|---|---|---|
| lotsize | No point | No point |
| eil33-2 | No point | 1207.176291; about 31.92% gap |
| danoint | No point | No point |
| blend2 | 8.788661, open | 8.788661, open |
| p0201 | Complete at 7615 | Complete at 7615 |
| rout | No point | 1703.469999923, about 41.4% gap |
| gt2 | 35673, about 60.92% gap | 35673, about 60.92% gap |
| pk1 | Approximately 20 / 29 | Approximately 20 / 25 |

Eil33-2's first incumbent arrives at 6.103 / 6.586 seconds, with a trace of
three private LP steps ending integer. Both final points have zero independently
measured original-model and integrality violation. This recovers a case missing
from recent waves, not a first-ever solution of the public model: older
development iterations have also found points on it. It remains far from proven.

Rout's trace shows the unchanged second (original-objective) dive producing the
integer candidate after the new first dive terminates. Credit the observed
pipeline outcome, not a direct integer solution from the distance LP. The final
point's independent maximum violation is about 7.67e-8, within the unchanged
1e-7 limit; integrality violation is zero. No numerical-repair attempt occurs.

Blend2 retains one successful sparse-then-dense candidate repair in each run.
Pk1 has zero guided/distance dives in every screen run; its varying objectives
are not direct evidence for or against the new objective. Shared-desktop timing
and time-triggered search behavior matter. References are validation/status
checks with a different allowance, not an equal-time speed contest.

## Mechanism and limitations

Four root-only integration runs exercise two actual distance dives, including
blend2's auxiliary column. No root-only run returns an integer solution. The
danoint distance run retains 0.03501 -> 0.03532 after its first LP, whereas
guided screen paths jump 0.03501 -> 5.66781. This supports the diagnosed drift
mechanism, but not enough useful progress inside the unchanged slice.

Both lotsize distance screen runs exhaust the first private LP without a
verified projection. One danoint repeat does likewise; the other completes
one projection and remains fractional. Cold/reoptimization work is a concrete
remaining bottleneck, not a reason to hide extra time in the heuristic.
Blend2's initially closer first point ultimately moves away as the fixed-target
domain is restricted. Nearest-integer distance need not decrease monotonically.

Bounded telemetry retains at most eight distance samples. Existing trace limits
still apply (512 events, 100000 vector values, 2048 columns per trace point);
the 4516-column eil33-2 dive has scalar trace metrics but no full intermediate
point payloads. Its final point and separately retained pump seed are checked,
not every unsaved intermediate vector. These checks are not exact LP certificates.

## Correctness, preservation and reproducibility

Full gate: 21 CTest groups, 162 Python tests, 28 MPS-domain cases, 320 generated
binary/mixed runs and 100 retained exhaustive models. Includes 108 L1
objective-identity examples, negative/unit/general/unbounded domains, private
cold/warm/alternate solves, zero-budget and option-prerequisite checks. Existing
numerical-repair and transformed MIN/MAX LP regressions pass. Four independent
cold/warm retained-fixture points pass original-model checks.

Six frozen20/new-disabled fixed-node comparisons cover guidance on/off across
three cases; two additional no-pump/no-heuristics comparisons prove inertness
on the checked case (16 runs total). Four older frozen16/no-heuristics parity
cases also pass. Generated tests alone do not guarantee an actual guided dive;
the separate public root integration explicitly requires it.

Measured binary: `fcc2817f7e6f24dfafbbffb05350c0d2e95d17e2fa9a8e28dceaa7223f4a197c`,
822804 bytes. Source/checkers are held fixed across timed batches; independent
references run after each batch's sequential own solves. CPU local throughout;
no Kaggle upload or GPU evidence is involved. Prior archives are preserved.

## Post-measurement correctness guard

The additional `EDGE_CASE_PLAN.md` preserves a reproduced presolve-off failure:
the interval 0.2 <= integer X <= 0.8 contains no integer, yet a fractional pump
seed could reach the private model builder and raise an error instead of letting
the existing tree conclude infeasibility. The retained original binary's error
and input are saved in `domain-before`.

The final artifact adds only a presolve-off eligibility guard for this case:
skip the private heuristic on an empty integer interval and let the unchanged
original-model tree decide the status. It does not prune the global node or
change presolve-on algorithm behavior. An explicit standard-header dependency
is added, with 32 MIN/MAX, positive/negative domain, presolve, heuristic and
option combinations in the C++ regression test.

Ten CLI replay runs reproduce the old error in MIN/MAX and verify the repaired
and unchanged paths, with both models independently confirmed infeasible. The
initial replay harness incorrectly expected exit 0 for infeasibility; its output
is preserved in `domain-guard-harness-initial`. The corrected harness respects
the CLI's established exit 1 for an infeasible result versus exit 2 for an error.

The final binary is `16a77b3da88e724a39794734b3ce942ce6e3ef7bdfe9488d61fc580374f73c42`
(823828 bytes). Its full gate and 16 parity runs are separate from the original
measured build. `benchmark_solver_cli.exe` and per-run source snapshots retain
the measured build; `final_solver_cli.exe` and `final-source` include the guard.
The 86 public timings were **not rerun on the patched binary**. Do not merge the
two identities or claim byte-for-byte final-artifact performance evidence.

Four supplemental root-only MIN/MAX runs on the final artifact exercise actual
private dives on p0201 and blend2, including an auxiliary-column case. Objective
negation preserves the feasible set, recovered points and oppositely signed
original-model bounds. The two returned p0201 points are independently checked;
blend2 returns no root-only integer point. These are metamorphic correctness
checks, not new held-out models or performance claims.

See `PLAN.md`, `SCREEN.json`, `WAVE.json`, raw results, `DISTANCE_DIAGNOSIS.json`,
the complete `MODEL_LEDGER.md`, final audit, and `NEXT_STEP.md`. All 27 models
are development data. No general exact-proof, full-library, industrial-readiness
or competition-percentile claim follows from passing this experiment.
