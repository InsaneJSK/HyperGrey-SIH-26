# Iteration 22 — guarded primal reoptimization in the pump

The candidate returns 24 independently checked feasible solutions plus one
cross-checked infeasible model: 25/27 with a solution or corroborated terminal
status, versus control's 24/27. Only ten feasible models reach completion;
this is not 25 or 27 optimality proofs. Misc07 and lotsize remain without a
point. Danoint is the new feasibility gain; rout improves, but mas74's solution
quality regresses. Keep the new feature optional, not a blanket replacement.

All 90 paired records have zero validation errors. The final evidence re-audit
passes: 73 final solution vectors, 42 retained fractional seed points, four
restricted exact certificate records, 51 cuts and 98504 retained lattice
events are checked; no final-point references are pending. Lattice traces are
bounded (22 truncated traces), so this is not a check of every unrecorded event.
FINAL_STATE.json binds the executable, source snapshot and evidence hashes.

## What changed

Added opt-in `--pump-primal-reopt`, default off. The pump already retained its
preceding private LP basis, but previously tried only dual-simplex restarts.
An objective change can lose dual feasibility while leaving a usable primal
basis. The new path compares the exact ordered canonical matrix, variable
mapping and equality metadata, recomputes current primal/reduced-cost values,
then chooses a valid dual or primal restart. Incompatible/invalid/singular or
neither-feasible bases retain the cold fallback. Untagged root bases remain
dual-only and cannot trigger the new primal path.

Only pump projections opt into this behavior. Tree LPs, fixed-integer repair,
the following distance dive, tolerances, cuts, restarts and heuristic slices
are unchanged. Projection bases/objectives/dual bounds never enter tree proof
state. The retained dive seed stays point-only. Enabled-call accounting now
includes canonicalization inside its existing time allowance. This remains
cooperative timing, not hard resource containment.

## Declared comparisons and scope

See PLAN.md, SCREEN.json and WAVE.json, written before measurements. Same
binary, two profiles: iteration21 distance control and that profile plus the
new flag. Screen: nine models, two alternating pairs each, 36 runs. Wave: all
27 development models, one alternating pair each, 54 runs. Each has the same
30-second budget, 250000-node cap and 1e-6 requested gap. Screen captures trace
and the first bounded primal-restart replay; wave does not. Own measured solves
are serial and references follow each complete own batch. No post-screen
tuning, named-instance rules, injected reference solutions or best-of union.

The comparison is with the distance profile, not iteration21's separate guided
profile. Shared-desktop timing and time-triggered restarts vary; isolated node
counts are not controlled speedup evidence. Every raw result is retained.
All 27 inputs are development data, not new holdouts. HiGHS is a references-only
checker, not part of our solver, and its five-second solve is not an equal-time
performance competitor to the 30-second own run.

## Repeated screen (independently checked)

Control: 12 checked solutions in 18 runs, including two p0201 completions;
candidate: 14 checked solutions in 18 runs, including those two completions.
No validation errors. The two extra points are danoint's two repeats.

- danoint: candidate 69.5 in both repeats, approximately 9.70% gap; control has
  no point in either repeat. The first candidate point is found by the pump,
  after seven verified primal restarts, before any distance dive is needed.
- rout: candidate 1293.19 twice versus control 1703.4699999232714 twice; gaps
  about 22.8% versus 41.4%. The first candidate point arrives at about 0.903s
  in repeat0 through the pump, not the following distance dive.
- eil33-2: both profiles retain 1204.0998990000003 in both repeats.
- blend2: both profiles retain 8.788661; the existing repair path is preserved.
- p0201: both profiles complete at 7615 in both repeats.
- gt2: both retain 35673 with a large remaining gap (~60.93%).
- pk1: all four end near 20 with a large remaining gap (~95.24%).
- misc07 and lotsize: neither profile returns a point in either repeat.

Gt2/pk1 do not activate the new primal-restart branch in these screen runs;
do not credit their timing differences to that branch.

## Actual private-LP replay

Retained the first actual primal-restart model, exact canonical structure and
input basis in 14 candidate runs across seven models. All 14 replay records
pass; cold, dual-only and adaptive returned points pass 42 independent checks.
These diagnostic runs use their own 10-second LP allowance and are outside
the public timings. Repeats may retain identical LPs; they are not 14 new models.

| Captured model | Cold / dual-only pivots | Adaptive pivots |
|---|---:|---:|
| misc07 | 832 | 301 |
| lotsize | 1860 | 60 |
| danoint | 5442 | 611 |
| eil33-2 | 298 | 155 |
| rout | 519 | 4 |
| blend2 | 368 | 2 |
| p0201 | 234 | 9 |

Both repeats have these counts. This demonstrates reduced work for these
specific objective-change replays, not a universal or end-to-end speedup.
Lotsize nevertheless remains unresolved: its improved seed's nearest-integer
distance is about 0.18936, but the first cold distance LP returns no verified
point inside its slice in both screen runs. Misc07 makes more distance steps
without obtaining an integer point. A good distance metric is not a solution.

## Full 27-model wave

| Outcome | Distance control | Reoptimization candidate |
|---|---:|---:|
| Checked feasible solutions (includes completions below) | 23 | 24 |
| Restricted exact binary completions | 2 | 2 |
| Numerical/tolerance completions | 8 | 8 |
| Feasible solutions with open gaps | 13 | 14 |
| Cross-checked infeasible statuses | 1 | 1 |
| No-point time limits | 3 | 2 |
| Validation errors | 0 | 0 |

The ten completion cases are p0033, enigma, flugpl, stein27, markshare_4_0,
egout, lseu, mod008, p0201 and rgn. Only p0033/markshare_4_0 carry the restricted
exact certificates. Neos859080 is independently cross-checked infeasible in
both original five-second references; no longer supplemental reference or
own-solver rerun is used.

Danoint returns 69.5 with a 9.6644% gap, versus no control point. Across screen
and wave this is 3/3 candidate points versus 0/3 controls. Rout returns 1293.19
with a 22.7875% gap versus control 1703.4699999232714 with 41.3744%; its lower
objective likewise repeats in all three comparisons. Neither model is proved
optimal. Eil33-2 retains 1204.0998990000003 in both wave profiles.

The adverse case is mas74: candidate 13588.56430256 / 19.7730% gap versus
control 12914.4386906 / 15.5730%. One verified primal restart precedes the
candidate pump incumbent. Earlier feasibility is not necessarily better
integer-assignment quality, and this one wave observation is not a repeated
quality guarantee. Preserve the prior profile and add this case to the next
repeated quality guard rather than hiding it in a best-of-profile union.

Other wave solution objectives are equivalent within the unchanged numerical
tolerance; some bound/gap/timing outcomes improve, some worsen. Binkar10_1,
gt2, pk1, rgn, gen-ip002, gen-ip054 and mas76 have no new primal restart in
their candidate runs, so do not attribute their timing-driven differences to
that branch. See MODEL_LEDGER.md for every outcome, including large open gaps.

The new primal branch is exercised in 14 screen and 17 wave candidate runs:
745 primal starts total; 975 total verified compatible warm outcomes including
dual starts. These are work counters, not additional feasible solutions or
independently checked LP certificates.

## Correctness and reproducibility

- 22 CTest groups; 166 Python tests; 28 MPS marker/domain contract checks.
- 320 generated binary/mixed MILP runs and 100 reused exhaustive cases.
- Existing retained LP recovery, candidate repair and 24 transformed LP checks.
- New 24 transformed objective/bound/structure/budget combinations; free and
  upper-only variables, equality layouts, invalid bases, alternate-parent
  lifecycle and verified terminal-status checks.
- 16 frozen21/inactive-option parity runs (eight comparisons), plus the
  inherited four frozen16 no-heuristics parity comparisons.
- 12 supplemental no/always/selective-refinement MIN/MAX/scaling combinations
  and a reordered-row guard; all pass.
- Six actual MIN/MAX/domain integration runs: p0201, blend2 and the retained
  presolve-off empty-integer-domain case. Checked points and status symmetry
  pass; the new primal path is actually exercised.

The new feature remains opt-in. Numerical optimality/gap completion is distinct
from the restricted exact binary certificates; no general exact MILP proof is
claimed. No GPU or user upload is needed. See MODEL_LEDGER.md for all wave
outcomes and NEXT_STEP.md for the remaining cold-distance-LP experiment.

## Artifact identity and decision

The measured executable and final artifact use the same binary, SHA-256
`9a4d47475eca12fb68a76bf2a1fe89363f7a39f17991888e95ba153890657956`
(844556 bytes). There is no post-timing core patch in this iteration. Run-local
source snapshots bind every root CMake/src/include/scripts/tests input. The
final snapshot additionally carries the current docs; report-local diagnostic
scripts and results are bound by the evidence manifest. Frozen21's measured
and final artifacts remain separate and unchanged.

Decision: retain this as an optional, evidence-backed development profile.
It raises observed first-feasible breadth but does not close additional models
or uniformly improve quality. Next isolate compatible basis reuse at the first
distance LP, protect danoint/rout and mas74, and keep proof-gap work separate.
Six slots remain in the earlier ten-iteration plan; no fixed iteration count
guarantees 27/27, universal MILP robustness or a competition percentile.
