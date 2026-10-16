# Bounded repair of rejected dive candidates

Iteration19 adds experimental `--repair-heuristic-candidates` for MILP. It
requires `--repair-candidates`; both remain opt-in. This version repairs dive
candidates only, not every pump/neighborhood rejection or every LP failure.

## Why this exists

A retained blend2 dive point is within integer tolerance but fails original
rows by about 2.01e-6 (2.129e-6 after rounding). Rejecting it is correct. However,
the integer choices are feasible: the existing dense LP algorithm re-solves
the integer fixing to objective 8.788661, independently checked at about
4.55e-13 original-model violation. Previously only the main tree had a candidate
repair path; a dive could discard this opportunity. See the retained
[diagnosis](../reports/milp-iteration-19/DIAGNOSIS.md).

## Point-only repair, not a proof operation

Only finite, correctly sized vectors whose integer values are within the existing
integer tolerance are eligible. Rounded integers must respect original bounds.
The fixing LP uses the original model and exact rounded integer bounds; its
continuous variables remain free within their original bounds. The helper
first tries sparse LP at the existing tighter polishing tolerance (at most
1e-11), reserving half the local allowance for dense recovery if needed.

A recovered vector is checked against original rows/bounds, exact fixed integer
choices, and finite values, then passed through the unchanged original-MILP
acceptance function. A valid point can improve the global incumbent, even if
it lies outside the current dive's restricted domain. That is safe for an
incumbent, not for a local-domain certificate.

The helper returns a vector and diagnostics, **no optimization bound**. A fixing
LP's optimum or terminal status is not a global-node certificate. The main tree
still branches and performs its existing proof accounting using the original
relaxation; a newly checked incumbent participates only in ordinary valid
incumbent-based pruning. Tolerances and final checks are not
weakened; no published solution or model-name condition enters the algorithm.

## Spent budgets stay spent

Each attempt is limited by the remaining current dive slice, at most two seconds,
and the existing shared candidate-repair allowance `min(15s, 0.1 * total_limit)`.
The new sparse and dense work both charge that shared spent-time counter, so
later tree repairs do not receive a fresh allowance. At most 16 distinct integer
fixings are tried per MILP; repeated assignments are skipped. The two-second
dive allowance, LP iteration/fill limits, root cuts and restart policy are
unchanged. A repair can consume time that would otherwise explore another dive
step; this trade-off must be measured in complete paired solves.

These are cooperative in-process clocks and allocation rules, not a hard
operating-system resource sandbox. Standardization/allocation and scheduling
can overshoot a wall-clock boundary. Full OS time/memory containment is still
separate work.

## Diagnostics and evidence limits

`--capture-feasibility` records at most 512 pump/dive events and 100000 numeric
vector entries, with individual vectors capped at 2048 columns. It reports
integer distance/fractional count, exact repeated pump targets, propagation
rejections, LP statuses and dive progress. The first retained near-integer dive
rejection has vector priority: older vector payloads may be dropped within the
same cap, while their scalar records remain. Events beyond the cap are counted
but not stored; this is not full-history coverage. Disabled capture stores no
trace. Instrumentation can perturb clock-driven heuristic paths.

`heuristic_repair` JSON exposes attempts, accepted points, duplicate skips,
sparse/dense calls, spent seconds and the shared allowance. LP work is recorded
in the existing repair phase; acceptance time remains in the validation phase.
Do not add these nested elapsed times to the solver total.
The existing `candidate_repair_seconds` is the shared spent counter; the older
`candidate_repair_attempts/successes` still count tree dense repairs, while the
new namespace counts dive repair attempts. Do not pair the old tree-only
attempt count with the shared time as if it covered the same work.

The retained regression covers sparse failure followed by successful dense
repair in equivalent MIN/MAX formulations, fixed integer choices, invalid
inputs, zero budget and priority capture. Exhaustive/generated tests guard
proof logic. Public paired results and regressions are in the
[iteration19 report](../reports/milp-iteration-19/REPORT.md). The option is not a
guarantee of first feasibility, full-library proof or uniformly better runtime.
Full-wave detailed capture is off: every final returned point is independently
checked, but not every intermediate repair vector or internal LP certificate
is retained for independent replay. Internal original-model acceptance still
applies to every proposed incumbent.
