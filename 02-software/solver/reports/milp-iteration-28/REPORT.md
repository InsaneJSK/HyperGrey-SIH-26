# MILP iteration28 — evaluation frozen; no default/release promotion

17 September 2026. Retain the explicit staged CPU profile for reproducible
evaluation. Stable ranking, alternate reserve and deferred restart remain
rejected. Defaults are unchanged. The development score is retained and six
untouched models yield checked points, but lotsize, first-feasible reliability,
open gaps and wider submission work prevent a general release-readiness claim.

| Suite | Checked points | Corroborated infeasible | Optimization completions | Unresolved without point |
|---|---:|---:|---:|---:|
| Development,27 reused models | 25 | 1 | 10:2 restricted exact,8 numerical | 1 |
| Untouched public holdout,6 models | 6 | 0 | 0 | 0 |
| Default profile,6 reused models | 6 | 0 | 6 numerical | 0 |

All39 public/default records and37 final vectors pass the saved-run audit and
independent checks. There are no validation failures in these suites.
The holdout and default subsets are separate from the27-case development
score. [The full ledger](MODEL_LEDGER.md) records every status, objective,
bound, gap, first-point time, total time, nodes, pivots and process peak memory.
`FACTS.json` retains phase work and reference outcomes.

## Development result and remaining limitations

The retained profile again has26/27 useful outcomes, not26 solved optima.
Lotsize has no point;15 returned points have open gaps. Misc07 returns3970
with a61.32% gap. Danoint returns69.5 with a9.664% gap, but this single fresh
wave does not erase earlier missed points. P0201 and mod008 complete at7615
and307. Binkar returns6787.230021; mas74 remains13588.564303 and has not recovered
the older better incumbent. These are this wave's observations, not a union
of historical best runs or controlled cross-batch speed gains.

Both restricted exact-proof cases remain p0033 and markshare_4_0. Neos859080's
infeasibility is independently corroborated. Its terminal result is counted
separately from the ten optimization completions for consistency with24.

## Untouched public models

The six historical MIPLIB models were declared before download or solve.
The profile was selected from development evidence before their outcomes.
No tuning follows these results. Related vpm and bell pairs reduce family
diversity; this is a small historical set, not arbitrary industrial coverage.

| Model | Our objective | Our remaining gap | Independent reference objective/status |
|---|---:|---:|---|
| vpm1 | 20 | 14.286% | 20, optimal |
| vpm2 | 16.75 | 31.383% | 13.75, optimal |
| bell3a | 879000.592 | 0.303% | 878430.316, optimal |
| bell5 | 9001765.680200 | 4.122% | 8966406.491520, optimal |
| gesa2 | 26678223.287875 | 4.230% | 25779856.371698, optimal |
| noswot | -41 | 4.762% | -41, time limit |

All six own runs end at the30-second limit. Matching the reference objective
on vpm1 does not close our bound; noswot's reference also remains incomplete.
Reference failure/limit information is preserved. The holdout references use
30 seconds, one thread and stricter1e-9 gap/1e-8 feasibility settings; development
and default references use five seconds for validation. Our target is1e-6
relative gap with independent absolute feasibility/integrality checks at1e-7.
Accuracy contracts differ, so no matched-accuracy speed ranking or finite
timeout-derived speedup is claimed. A fair external performance study remains
separate work.

## Correctness, artificial stress and input interoperability

The executable is unchanged from26. Its complete25-group CTest,176 Python,
320 generated and100 retained exhaustive gate is reused by exact binary hash.
It includes LP fixtures, MIN/MAX, offsets, row/domain/parser, empty-domain,
frontier, cut/proof and failed-primary/alternate checks. Default runs separately
complete p0033, enigma, flugpl, lseu, p0201 and mod008; this is not a full27-case
default score.

Twenty-four artificial transformations cover MIN/MAX, offsets, column reversal,
negative/general-integer/free domains, a weak relaxation, duplicate/near-parallel
rows and row scales from1e-6 to1e6. All answers match exhaustive enumeration.
The initial direct HiGHS comparisons fail on all24 because our MPS reader sums
repeated objective entries while installed HiGHS retains one equal entry.
This is a real interoperability limitation, retained explicitly in the raw
ledger. No candidate answer or source is changed to hide it.

A separately labeled reference-only representation aggregates duplicate
objective entries. Every other parsed matrix, bound, integrality and offset
field is identical, and costs equal the exact intended sums. All24 unchanged
answers pass independent checks on that representation. See
[the input contract](../../docs/MPS_DUPLICATE_OBJECTIVES.md) and the canonical
reference evidence. These are related artificial fixtures, not24 new public
models or comprehensive ill-conditioning coverage. The first diagnostic JSON
export also rejected infinite bounds; that attempt is retained and corrected
by explicitly representing infinity in diagnostic metadata.

## Resources and reproduction

Fifteen status/resource checks pass: ordinary solve, zero time/node/pivots,
recovery-mode unresolved relaxation, infeasible/unbounded, malformed input,
unsupported MIQP, an actual retained numerical-error fixture, external timeout,
cancellation, memory pressure and two process/JSON consistency fault injections.
Forced termination overrides a printed optimal status. All child processes
terminate cleanly. The first test incorrectly reused recovery-mode status
expectations for the default profile; its failure remains and both contracts
are now checked separately.

All39 model runs also record per-process memory through the wrapper. Maximum
observed peak working set is166.969 MiB (gt2); the holdout maximum is106.703 MiB
(vpm2). The1536 MiB sampled threshold and45-second external watchdog do not
terminate any of these model runs. Internal limits remain cooperative.
The separate32 MiB pressure test kills its bounded synthetic process after
observing about39.19 MiB commit: sampling can overshoot. This wrapper is for
known single-process executables, not arbitrary process-tree containment or
hard real-time/allocation guarantees. Shared desktop load and different batch
start times remain timing limitations.

The isolated-folder smoke initially exposes a missing `libdl.dll` dependency
of this OpenMP runtime. The corrected snapshot includes it with the other four
runtime DLLs. The exact candidate then solves the production example correctly
from a fresh folder with PATH restricted to Windows System32 plus the copied
runtime; an independent reference checks the answer. This is a same-host smoke,
not a fresh OS or full clean-build/submission package. Earlier frozen reports
are unchanged and still document their toolchain environment.

The frozen archive includes source, executable, selected profile, five runtime
DLLs, all33 distinct final public-model inputs and provenance, dependency hashes,
raw successes/failures, checks and limitations. See `DATASET_SNAPSHOT.json`,
`DEPENDENCIES.json`, `SNAPSHOT_MANIFEST.json` and `FINAL_STATE.json`.
CLI SHA256:
`f74d9fe31411ec2c94452eb302b1967ad8bf85be44df3d6d4d177e93a162cf2c`.

## Decision and next work

Freeze an experimental evaluation candidate; do not promote defaults or call
the SIH submission ready. Use [the run guide](../../docs/RESUMED_RUN_GUIDE.md)
and the saved profile instead of guessing among experimental flags.

The next evidence-selected private-LP hypothesis is to verify a dual-row local
infeasibility certificate before restarting full phase one, with the existing
fallback retained when verification fails. Instrument the precise rejection
first; faster LP work must still earn a repeated MILP coverage gain. See
[the bounded hypothesis](../../docs/NEXT_PRIVATE_LP_HYPOTHESIS.md).
Danoint's separate fixing deadline also remains a reliability issue.

Final LP/QP breadth, actual final-source GPU evidence, industrial/domain
validation, matched-accuracy performance study and submission/demo preparation
remain in the outer objective.md. CPU work stayed local; no GPU run, upload,
external message or submission occurred.
