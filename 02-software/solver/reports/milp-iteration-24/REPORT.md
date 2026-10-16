# MILP iteration24 — objective-only staging before private branch tightening

**Outcome: one additional feasible model in the full wave, but keep the new
option experimental.** Staging returns 25 checked feasible solutions plus one
cross-checked infeasible status: 26/27 useful outcomes under the fixed budget,
not 26 proofs. Both profiles complete ten models. Lotsize remains without a
solution; danoint's screen failures and solution-quality trade-offs remain.
See the complete [27-model ledger](MODEL_LEDGER.md).

## Change and safety boundary

The optional `--pump-distance-stage` retains an immutable parent model at the
same event as the selected checked fractional seed and its tagged private basis.
Only an exact unchanged parent domain is eligible. It first retargets the private
objective; after a verified and absolutely feasible result, the existing dive
changes a branch bound. Failed staging leaves the selected seed intact; failed
children retain the parent basis for their alternate branch.

The sparse LP engine is unchanged from frozen23. It still verifies exact
canonical identity and current primal/dual feasibility before a restart.
The two stages share the existing at-most-two-second dive allowance; no extra
time, relaxed tolerance, model-name rule or reference solution/bound is used.
Only a checked point can become an original-model incumbent. Private objectives,
dual bounds, infeasibility and certificates never become global proof state.
See [implementation scope](../../docs/PUMP_DISTANCE_STAGE.md).

Snapshot retention adds model-sized storage. Time checks are cooperative, not
hard process containment. Staging can change the fractional point and later
branch choices; it is not merely a performance-neutral cache optimization.

## Predeclared protocol

`PLAN.md`, `SCREEN.json`, `WAVE.json`: one Release executable, control `handoff`
(iteration23 profile), candidate `stage` (add only the new flag). Limits:
30 seconds/model/profile, 250000 nodes, gap 1e-6. Eleven screen models with two
repeats/profile (44 runs), then 27 reused public models with one repeat/profile
(54 runs). Alternating profile order, serial own solves, independent five-second
references afterward. Those references validate answers, not a fair speed contest.
Screen retains bounded feasibility/private-LP captures; wave disables those
captures. No source, checker or profile changes between screen and wave.

All 27 are reused development models, not unseen holdouts or all public MILPs.
Every adverse outcome is retained. Results from different profiles or historical
iterations are not unioned into a fictional single-run coverage count. Shared
desktop clock limits can affect trajectories, including when the new path is
inactive; observed differences do not by themselves establish causation.

## Correctness before timings

- 24 CTest groups and 176 Python test methods passed.
- 320 generated binary/mixed runs and 100 retained exhaustive cases passed.
- 28 MPS marker/domain contracts and four independent LP fixture checks passed.
- Frozen23/inactive-option parity: 16 runs, eight comparisons; inherited frozen16
  disabled-option parity also passed.
- Ten actual MIN/MAX/domain integrations passed, including eligible stages on
  original public models, independent point checks, and empty integer domains.
- New 24 transformed parent-stage/child/alternate/basis/resource cases passed,
  plus general-integer auxiliary RHS/layout and free-variable guard cases.
  The extended empty-domain matrix covers 64 combinations.

## Results and disposition

The repeated screen has **zero validation failures in 44 runs**. Control returns
17 checked feasible points in 22 runs; staging returns 18. Both have four
numerical/tolerance completions (p0201 and mod008, twice each). This is mixed
evidence, not uniform improvement:

- Misc07: both controls have no incumbent; both staged runs reach objective
  3970, with a still-open gap of about 62.2%. The retained accepted point comes
  from the private dive, not candidate-repair fallback.
- Danoint: one of two controls reaches 69.5; neither staged run has an incumbent.
  Earlier iteration23's repeated success is not reliable in this new screen.
- Lotsize: neither profile returns an integer point. Staging gets beyond the
  initial LP bottleneck, but later private work still exhausts its slice.
- Eil33-2, rout, blend2, p0201, mas74 and gt2 retain their paired objectives.
  Mod008 completes in all four runs at 307. Mas74 does not recover the older
  non-reopt profile's better objective.
- Pk1 returns about 20 under staging versus about 35/31 in the controls, but
  there are zero stage attempts there. This is not demonstrated staging benefit.

The two misc07 screen traces reveal a sensitivity worth addressing next. The
stage takes zero pivots and changes integer coordinates by at most
7.36e-16 (all coordinates by at most 4.55e-13). Both points have integer-distance
4.5, but the strict largest-fractionality choice changes from column 218
(score 0.2500000000000002) to column 12 (score 0.25). Ten columns are within 1e-12
of the largest score in each point. The resulting dive reaches an accepted
integer vector at step 16, with original-model violation about 8.77e-13.
This is a measured trajectory change, not proof that faster LP work alone
caused the gain or that the gain will be robust to all small perturbations.
`TRACE_DIAGNOSIS.json` is read-only evidence from saved traces, not another
benchmark or a solver-fed answer. Bounded/truncated traces remain identified.

### Full wave and disposition

| Outcome | Control: handoff | Candidate: add stage |
|---|---:|---:|
| Checked feasible solutions | 24 | 25 |
| Restricted exact completions | 2 | 2 |
| Numerical/tolerance completions | 8 | 8 |
| Feasible with open gap | 14 | 15 |
| Cross-checked infeasible | 1 | 1 |
| No solution within budget | 2 | 1 |

Misc07 repeats its 3970 point in the wave (about 60.94% gap), while its control
again has no point. That is three observed candidate successes versus three
control misses, not an unseen-model result or a robustness guarantee. Danoint
returns 69.5 in both wave runs; neither invokes the stage there. Its two staged
screen failures remain visible and are not erased by this later success.
Mod008 and p0201 complete in all six runs per model in this iteration.

Binkar10_1 worsens from control 6787.820026 to candidate 6790.910033. Pk1 instead
improves from 36 to about 31, not its screen objective of about 20. Both have
zero stage attempts, so these clock-dependent differences are not demonstrated
stage-mechanism gains or losses. Other paired final objectives are retained;
open proof gaps and node counts still differ. Mas74's older-profile quality
advantage remains unrecovered. No new optimality/tolerance completion is gained
over the same-binary control.

All **98 paired public records pass validation**, including **84 final solution
vectors** and four restricted exact proof records. All terminal references are
resolved. The screen has eight attempted/verified parent stages and six verified
first-child warm restarts; the wave has six stages and five such child restarts.
No parent stage itself supplies an integer incumbent; misc07's point is produced
later in the private dive. Global proof state and acceptance checks are unchanged.

### Actual private-LP replay

Sixteen exact saved LPs (parent and first child for four models, two repeats)
are replayed cold, dual-only and adaptive. All **48** resulting points pass
independent absolute-feasibility and objective checks. The ten-second diagnostic
limit is outside the measured MILP solve, not an extension of its shared dive
slice. No diagnostic result is fed back into the solver.

| Saved model/repeat | Parent pivots: cold to adaptive | Child pivots: cold to adaptive |
|---|---:|---:|
| misc07, both | 900 to 0 | 641 to 2541 |
| lotsize, both | 2670 to 1 | 2670 to 4 |
| danoint, both | 5442 to 0 | 5184 to 124 |
| eil33-2, repeat0 | 352 to 0 | 371 to 75 |
| eil33-2, repeat1 | 306 to 0 | 317 to 44 |

Lotsize establishes the intended objective-first mechanism: dual-only still
uses 2670 parent pivots, while adaptive primal reoptimization uses one; its
bound-only child takes four pivots with either warm mode. However, its later
root dive still spends work on an infeasible primary/alternate and reaches
the slice deadline without an integer point. The original bottleneck moved;
the MILP is not solved.

Misc07's saved child is WORSE with warm reoptimization (2541 versus 641 cold
pivots). Its observed feasible gain must not be sold as uniformly faster LP
work. The two eil33-2 repeats save different private LPs; their separate counts
are retained rather than averaged into an allegedly identical fixture.

Keep the flag off by default. Next test [private-dive near-tie stability](NEXT_STEP.md)
and preserve the exact later lotsize bottleneck for a separate bounded change.
Four planning slots remain from the earlier ten-slot budget, not a guaranteed
number to 27/27. Fresh holdouts, domain/GPU evidence and submission hardening
remain separate requirements; this pass is not a competition-percentile claim.

## Archive and reproduction

See [reproduction](../../docs/V2_REPRODUCE.md). Use fresh output directories;
report-local helpers bind to their own paths and must not overwrite this archive.
Per-run model/source/executable hashes, raw commands/results, reference checks,
traces and failures are retained. Diagnostic stage/child replays use a separate
ten-second limit outside measurements and never feed the solver.

Measured CLI SHA-256:
`00b57cdcddf68fd4cd0746703fbc23ec119436ddcbd642cdd450c1007c609a2a`.
`FINAL_STATE.json` and `SNAPSHOT_MANIFEST.json` record the completed archive,
unchanged measured source/checkers, matching measured/final executable and
preservation of frozen23. The sparse LP implementation is byte-identical to
frozen23; the integration, bookkeeping, telemetry and tests change here.
No GPU or Kaggle work is required for this CPU-only iteration.
