# Iteration18 — selective basis correction

Implemented and audited locally on CPU. All 66 public experiment records and
53 returned points pass their checks. Selective correction preserves the
retained numerical repair, but neither mode is promoted to default: broader
feasibility and optimality coverage remain incomplete.

## Implementation

Optional `--capture-refinement` measures RHS calls, scans, visited basis
entries, correction attempts/acceptance and time inside each existing MILP
phase. These times are included in phase time, not additive extra solver time.
All sparse call sites and compact/reduced-bound retries retain spent work.
Disabled capture does not record detailed work. It does not enable refinement.

The separately archived Stage A changes instrumentation only. Six fixed-node
cases (five models, including a counter-restart p0201 case) have identical
frozen17/refinement-telemetry-off/refinement-telemetry-on semantic results.
The stage passes 16 CTest groups and 11 new checker tests; 24 diagnostic runs
also retain an unrefined comparison. These short diagnostic timings are not
final first-feasible or robust whole-solve speedup evidence.

P0201's counter-restart sample scans 5,776 RHSs and 5.29 million entries without
a correction. Eil33-2 scans 1,004 RHSs for 27 corrections. Mas74, in contrast,
has 1,529 correction attempts over 1,200 RHSs. These observations support
testing selective checks rather than assuming correction is unnecessary.

Stage B adds `--refine-basis --refine-at-checks`. It checks at selected simplex
terminal/rejection decisions, then re-evaluates the same basis once. The
two-correction-per-RHS cap, finite strict-improvement guard, final numerical
certificates, tolerances, pivots/fill budgets, cuts, restarts and global recovery
allowance remain unchanged. No model-name or known-objective rules are added.
The original always-check mode and unrefined mode remain available.

## Retained numerical repair and regressions

Both cold (130 pivots) and original warm (5 pivots, warm_started true) captured
mas74 LPs still solve to objective 10515.606014154158. Selective correction takes
3 attempts / 2 accepted corrections in either replay, compared with 99/72
cold and 18/12 warm under always-check refinement. Independent HiGHS checks
confirm both selective points at about 2.91e-11 absolute violation, matching
the independent objective to floating-point precision. No tolerance is loosened.

The final gate passes 17 CTest groups, 126 Python tests, 28 MPS-domain cases,
four disabled-option fixed-node parity comparisons, 320 generated MILP runs
on 80 models, and 100 reused exhaustive MPS cases. Both refinement modes run
12 transformed min/max LP equivalents (24 total). Four retained cold/warm
points receive independent checks. The tests cover interruption, rejected
corrections, invalid option pairing, nested accounting and fallback work.

## Public protocol

Predeclared `SCREEN.json`: p0201/eil33-2/mas74, two alternating control/selective
pairs each. `WAVE.json`: all 24 previous development models, one pair each.
`HOLDOUT.json`: danoint/rout/mas76, one pair each, selected before new solver
runs. See [holdout provenance](HOLDOUT_PLAN.md) for primary metadata links and
limitations: mas76 is related to mas74, and these are moderate historical
instances, not the hardest industrial-scale class. Previous local dataset and
result records contain no tests on these three inputs. Published solutions are
not supplied to the core.

Every own run has 30s, 250000 nodes, gap 1e-6 and the same other flags, with only
the two selective-mode flags differing. Own runs are sequential, with no
competing task builds/tests/reference solves. References follow the own runs
with a 5s solve allowance and 150s external watchdog; this is not an equal-budget
performance comparison against HiGHS. The desktop is shared hardware; timing,
heuristics and half-time restarts can affect the search path.

## Repeated three-model screen

All 12 records pass the original-model point, saved proof/structure, phase-work
and refinement-work checks. Every run returns an independently checked point.

| Model | Control, two runs | Selective, two runs | Interpretation |
| --- | --- | --- | --- |
| p0201 | Completes at 7615 in 12.28 / 13.23s | Completes at 7615 in 12.57 / 12.68s | No completion loss in these pairs; no consistent timing win |
| eil33-2 | Checked point 1204.099899 in both, about 31.62% gap | Same checked point in both, about 31.62% gap | Earlier point loss is absent; still far from proof |
| mas74 | Unresolved exits near 15s; gaps 20.58% / 24.10% | Checked point 12914.438691 at 30s; gaps 15.54% / 15.53% | Better gaps in these pairs and no recovery/deferred nodes, but still open |

Both selective p0201 runs use 8,874 RHS checks and accept five corrections,
spending about 0.07s in refinement. They visit 4,196 nodes versus 4,194 for
controls, and neither profile restarts. First points arrive in 0.78–0.80s for
selective versus 0.82–0.85s for controls. Those small shared-desktop differences
are not a robust speed claim. The previous iteration's 29–30s p0201 comparison
crossed different clock/restart boundaries and is not a matched timing control.

Eil33-2 first points arrive in 6.92–7.02s selectively versus 6.95–7.24s for
controls; refinement costs about 0.01–0.02s. Both selective mas74 runs have
zero recovery attempts, zero unresolved nodes and zero deferred nodes, with
29,824 / 30,913 nodes visited. Controls have 576 / 607 recovery attempts and
two unresolved nodes each. Selective refinement itself takes 0.89–0.90s;
accepted corrections number 66,335 / 68,657. Arithmetic work remains material
on this model, unlike the mostly correction-free p0201 sample.

## The 24-model development wave

Both profiles complete the same ten cases within the configured tolerance:
p0033, enigma, flugpl, stein27, markshare_4_0, egout, lseu, mod008, p0201 and
rgn. P0033 and markshare_4_0 have the restricted exact-binary proof; the other
eight are numerical completions, not general exact rational certificates.
Neos859080 returns infeasible in both profiles and is counted separately.

All 48 records pass validation, with all 39 returned points independently
checked. The mutually exclusive categories are:

| Outcome, 24 models per profile | Control | Selective |
| --- | ---: | ---: |
| Restricted exact-binary proof | 2 | 2 |
| Numerical completion | 8 | 8 |
| Checked feasible limit | 8 | 10 |
| Unresolved relaxation, checked point | 1 | 0 |
| No-point limit | 4 | 3 |
| Cross-checked numerical infeasibility | 1 | 1 |

Thus completion is unchanged at 10/24; checked-point coverage is 19/24 for
control and 20/24 for selective. These are fixed experimental profiles with
several existing opt-in search/proof features, not plain CLI defaults.

P0201 completes at 7615 in 13.05s selectively versus 13.02s for the control,
again without restart. This removes the prior iteration's observed completion
loss in all three current selective runs, but is not a matched speedup against
the old always-check archive. The selective mas74 run again has zero recovery,
unresolved and deferred nodes, and improves the paired gap from 24.18% to
15.61%; full mas74 is still not solved.

Selective misc07 returns 2810 with a 44.82% gap; the control has no point.
Assign1-5-8 improves from about 228 / 17.74% gap to 220 / 14.82%; pk1 improves
from about 29 / 96.67% to 20 / 95.24%. Those large residual gaps must not be
hidden by the improved objectives. P0282 and misc03 have slightly tighter gaps.

Adverse outcomes remain: binkar10_1 worsens from 6774.140014 / 1.4153% gap to
6787.820026 / 1.6198%, with first point at 12.23s instead of 11.88s. Gen-ip002
and gen-ip054 keep the same points but have slightly worse selective bounds.
Gt2 keeps the same 67.31% gap. Blend2 and lotsize have no point in either profile.

Crucially, **eil33-2 has no point in either wave run**, despite all four screen
runs finding one. Selective wave pump projection uses 10.01s versus 5.00s in
the first screen, with different dive counts and restart locations. This
demonstrates time-limited path/feasibility variability, not a guaranteed fix of
its first-point problem. The selective wave run has no numerical recovery or
unresolved node on this input. The screen's point retention does not override
the negative broader result.

## Three predeclared new instances

All six records pass validation. Both returned points pass independent
original-model checks; the four no-point runs remain explicit limits, not
infeasibility results.

| Model | Control at 30s | Selective at 30s |
| --- | --- | --- |
| danoint | No point, 7 nodes | No point, 8 nodes |
| rout | No point, 1,265 nodes | No point, 1,120 nodes |
| mas76 | Checked objective 42498.141700, 7.5029% gap | Checked objective 41519.995740, 5.2420% gap |

None of the three is completed. Mas76 shows improved objective/gap in one
paired unseen-instance run, but is related to mas74 and does not establish
unseen-family generalization. Danoint and rout expose remaining feasibility/
LP-search limitations even on moderate historical models. These inputs now
join the 27-model development ledger; they are not fresh holdouts for future
tuning.

Combining the single development wave and these new inputs, both profiles
complete 10/27 models, plus one separately cross-checked infeasible case.
Control returns checked points on 20/27, selective on 21/27. Do not interpret
these small, nonrandom, shared-desktop samples as a full-library success rate.

## Decision and submission significance

Keep both refinement modes **optional**. Selective correction preserves the
specific numerical repair, removes many unnecessary residual checks on the
retained fixture, retains p0201 completion in all three pairs, and avoids the
observed mas74 recovery/unresolved exits. This is a real engineering improvement.
However, Binkar regresses, eil33-2's point outcome varies between batches,
several public cases have no point, and large proof gaps remain. There is no
general completion-rate increase, universal runtime win, exact general-MILP
proof or basis for a top-0.1% competition claim.

Next prioritize evidence-led first-feasible work on the retained failures,
separately from stronger valid bounds for models with large gaps. See
[the next bounded experiment](NEXT_STEP.md). Real refinery/domain validation,
hard resource/deployment testing, a final reproducible demo and final GPU-only
measurements remain separate submission requirements. This iteration uses no
GPU and requires no Kaggle upload or new user input.

## Final audit and preserved identities

The final audit rechecks all 66 records across 27 distinct public models:
12 screen + 48 development-wave + 6 new-instance runs. All 53 returned points
are independently checked against original models, with zero pending points
and zero observed validation failures. It recomputes four restricted exact
proofs on two models, checks 52 retained covers, 82,308 saved lattice events,
80 cut rounds and four source incumbents. Nineteen lattice traces are capped;
this verifies saved events, not an uncapped replay of every historical event.
Adaptive cut stopping is disabled in these profiles, so their 80 checked
rounds are not coverage of the adaptive stop branch. Dedicated gates cover
those separate features.

The same final binary and code/checker identities are used throughout all three
public batches. The archive checker verifies their saved/current hashes, the
gate identity, input/plan identities and the previous iteration's untouched
source/binary/evidence. Stage A remains separate from the final selective code.
The 24 Stage A diagnostic runs are additional fixed-node telemetry experiments,
not included in the 66 independently validated public timing records.

- Final CPU executable: `final_solver_cli.exe`, 778,794 bytes,
  SHA-256 `8ff22dd62eabc5a8f41ea1c58a94ec79c9f8b0a99aeb47881fe099c2da665341`.
- Instrumentation-only executable: `profile/solver_cli.exe`,
  SHA-256 `744e3018fc24e8af639c699c308adcaa37c39bb3c1503ada4c05d112502f90fc`.
- Preserved frozen17 executable:
  SHA-256 `a4b9f9350638f97a5230923554c5788af3c4c95bb552282686aeb408524f88c4`.
- Screen results SHA-256:
  `3293709208eb9b420018b7e9619d48eadbc360dbf816857a63b689055ae0c9a9`.
- Wave results SHA-256:
  `c8289bcd75b23fb59399ec7d0a7bf841826e131e5d874efa672a89a409aa50be`.
- New-instance results SHA-256:
  `b0b02b6147f21ffdff8bf1e1686fdd6600a6e057e19c494428ed432365a96966`.

See [final machine-readable state](FINAL_STATE.json),
[source manifest](SNAPSHOT_MANIFEST.json), and
[re-audit](final-audit/SELECTIVE_AUDIT.json). The final source snapshot is
`final-source`; raw runs and their individual source snapshots remain in
`screen-30s`, `wave-30s` and `holdout-30s`.

## Reproduction

See [algorithm and measurement](../../docs/SELECTIVE_BASIS_REFINEMENT.md) and
[local reproduction](../../docs/V2_REPRODUCE.md). Sources, binaries, raw results,
input identities and checks are archived after audit. Stage A and frozen17
remain separate controls. CPU-only: no Kaggle upload, no user input required.
