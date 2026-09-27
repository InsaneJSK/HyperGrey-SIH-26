# MILP iteration23 — guarded private basis handoff

**Outcome: no additional models handled. Keep the new option off by default.**
Both profiles return 24 independently checked feasible solutions and one
cross-checked infeasible status in the 27-model wave. Misc07/lotsize remain
unresolved. Control has 10 completions; candidate has 9. The complete
[ledger](MODEL_LEDGER.md) separates feasible answers from completed proofs.

## Change and boundaries

New optional `--pump-distance-reopt` retains a separately typed private basis
at the exact event where the pump selects a better, checked fractional point.
It offers that basis to the private distance dive, with the existing exact
canonical-structure and current primal/dual-feasibility checks. Incompatible
or neither-feasible offers use the existing fallback. A failed primary branch
does not overwrite the parent basis needed by the alternate branch.

The public seed remains point-only; private objectives, bounds, certificates,
auxiliaries and bases never enter global tree proof state. Original-model
candidate validation is unchanged. No solver-library dependency was added to
the C++ core. The new flag requires the prior guided/distance/pump-reopt flags
and defaults off. No GPU, extra time slice, looser tolerance, model-name rule,
reference-point injection or reference-bound injection is used.

## Protocol

Predeclared `PLAN.md`, `SCREEN.json`, `WAVE.json`. Same Release executable for
control and candidate; candidate adds only the new flag. 30 seconds/model/profile,
250000 nodes, 1e-6 gap, alternating profile order. Ten screen models with two
repeats/profile, then all 27 existing development models with one repeat/profile.
Own solves are serial; 5-second reference solves run after each own batch.
Those reference solves validate answers, not a fair equal-budget speed contest.
All outcomes are retained. No post-screen code or profile tuning.

Shared-desktop clock cutoffs can change search paths, incumbent quality and
node counts, even on cases where the new path does not execute. Do not credit
such variation to this mechanism. No best-of-profiles or best-of-repeats union
is counted as one 30-second solver result. All 27 models are reused development
data, not unseen tests or coverage of every public MILP.

## Correctness and repeated screen

- 23 CTest groups and 170 Python test methods passed.
- 320 generated binary/mixed regression runs and 100 retained exhaustive cases passed.
- 28 MPS marker/domain contracts and four independently checked LP fixture points passed.
- 16 frozen22/inactive-option parity runs (eight comparisons) and eight actual
  MIN/MAX/domain integration runs passed. The inherited frozen16 parity also passed.
- New 24 transformed handoff/bound/alternate/invalid-basis/budget cases passed;
  changed auxiliary count/identity, free/equality cases and 48 empty-integer-domain
  combinations passed. Existing primal-reoptimization guards also passed.

The 40-run screen has zero validation failures. Both profiles return 16 checked
points in 20 runs: 14 open-gap feasible points and two p0201 numerical completions.
Misc07 and lotsize remain without integer points in both repeats/profiles.
Danoint 69.5, eil33-2 1204.099899, rout 1293.19, blend2 8.788661, p0201 7615,
mas74 13588.56430256 and gt2 35673 are retained in both profiles/repeats.
Pk1 is 20 versus 35 in the first candidate/control pair, but both are 35 in the
second pair. The handoff executes zero calls on pk1, so that difference is not
evidence of a handoff improvement. Mas74 does not recover iteration22's older
non-reopt profile objective 12914.4386906; retaining the reopt result is not a fix.

The screen directly reproduces lotsize's critical rejection: its retained
distance 0.189355520349557 seed has a structurally compatible basis, but neither
primal nor dual feasibility remains after retargeting and the first bound
tightening. The guard correctly falls back; the private solve still fails to
return a verified point within its slice. Misc07 accepts its initial seed basis
but still finds no integer solution. Blend2 rejects its incompatible seed basis
and later retains its checked final solution. These are mechanism observations,
not claims of general speed or coverage gains.

## Full wave, private replay, disposition

| Outcome | Control: prior reopt profile | Candidate: add handoff |
|---|---:|---:|
| Checked feasible solutions | 24 | 24 |
| Restricted exact completions | 2 | 2 |
| Numerical/tolerance completions | 8 | 7 |
| Feasible but open gap | 14 | 15 |
| Cross-checked infeasible | 1 | 1 |
| No solution within budget | 2 | 2 |

All paired final objectives match in this wave. Mod008 is the completion loss:
both return 307, but control completes while candidate stops at a relative gap
of 0.0032467532467534313. Candidate retains three pump seed bases but executes
zero private handoff LP calls on mod008. Preserve the measured outcome, but do
not attribute its cause to the private LP restart; wall-clock-triggered search
and small retention overhead can affect time-limited outcomes. No causal speed
claim follows from this single wave. Candidate does not recover the older
mas74 profile's better solution, either.

All **94 paired records pass validation**, including 80 final solution-vector
checks. No fresh public model is introduced. The candidate's 25/27 useful or
corroborated outcomes are NOT 25 optimality proofs: only nine complete in this
wave (two restricted exact and seven numerical/tolerance completions).

The screen offers 10 seed bases: six structurally compatible and four verified
restarts. The wave offers nine: six compatible and five verified restarts.
Ten retained LPs (five models, two repeats) are replayed cold, dual-only and
adaptive; all 30 resulting points pass independent absolute-feasibility and
objective checks. These diagnostic LPs use a 10-second limit outside the
measured MILP runs, not the original two-second shared dive slice.

| Retained private LP | Cold pivots | Dual-only pivots | Adaptive pivots |
|---|---:|---:|---:|
| misc07 | 784 | 9 | 9 |
| lotsize | 2670 | 2670 | 2670 |
| eil33-2 | 317 | 44 | 44 |
| blend2 | 410 | 410 | 410 |
| gt2 | 72 | 72 | 72 |

Each row's counts repeat for both retained fixtures; they are not ten different
models. Misc07/eil33-2 establish specific LP work savings, not better end-to-end
coverage. Lotsize's neither-feasible basis falls back. Blend2/gt2 reject
incompatible offered structures. All diagnostic outcomes are retained.

Do not promote this flag or present the pass as a coverage improvement. The
[next bounded hypothesis](NEXT_STEP.md) separates objective retargeting from
bound tightening within the same existing budget. Misc07's later search
difficulty remains a separate problem. Five planning slots remain, not five
guaranteed steps to 27/27 or a prediction of competition rank.

## Reproduction and archive

See `../../docs/V2_REPRODUCE.md` and `../../docs/PUMP_DISTANCE_REOPT.md`.
Use fresh build/output paths; do not rerun report-local assembly helpers over
a frozen archive. Raw per-run commands, models' hashes, source snapshots,
references, checks and failure traces are retained. The measured/final CLI
SHA-256 is `31789d84bb10e2d0a1b99d5d421d91f0bc28b2f008385241f90e29f3441b7dfa`.
The low-level sparse LP implementation is byte-identical to frozen22; this
iteration changes private handoff/integration, telemetry and tests.
`FINAL_STATE.json` and `SNAPSHOT_MANIFEST.json` record the completed archive and
preservation checks. Frozen22 is preserved. No Kaggle artifact was changed and
no GPU was used; no user upload is needed.
