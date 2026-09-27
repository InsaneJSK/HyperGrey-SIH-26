# Iteration20 — pump-guided first-feasible diving

Predeclared before candidate implementation/timings, 16 September 2026.
Preserve frozen19 and all its evidence. CPU only; no Kaggle work.

## Evidence and one hypothesis

The frozen19 pump ends without a point on lotsize/eil33-2/danoint, despite
feasible fractional projection points with reduced integer L1 distance.
Distances improve 9.7737 -> 4.6966, 3.6156 -> 2.0507 and 5.8192 -> 0.03501.
The following dive instead starts from the original relaxation. The original
recorded row violations of these projections are below 1e-7. Lotsize/eil33-2
vectors exceed the older 2048-column trace cap; their scalar trace alone is
not independent verification of a complete vector. Preserve that limitation.

Test optional --pump-guided-diving: retain the best verified pump projection
with strictly improved integer distance and valid original/current-model rows
and current node bounds. In the immediately following existing root dive,
start mode zero from that point and direct subsequent branches toward its
nearest integer target, clipped to the evolving dive domain. Mode one keeps
its original root start/cost direction. Retain the ORIGINAL-objective LP model
and its root basis; never import a projection basis, distance objective/bound,
or rejected fixing certificate into the global tree. The seed is discarded
after that node, not carried across restarts/domains. It is a heuristic hint,
not evidence that its nearest integer fixing is feasible.

No changes to two-second dive/five-second pump slices, 64 steps/mode, shared
repair allowance, tolerances, root/cut/restart rules or proof accounting.
Both timed profiles retain iteration19 heuristic repair. The new option is
off by default. No model-name rules or reference incumbent input.

## Gates and evidence

Unit tests: seed eligibility/ranking, nonfinite/dimension/unverified/row/bound
rejection, integer target clipping, general integer and negative values,
small exhaustive MIN/MAX MILPs and no false terminal/proof outcomes.
Retain full iteration19 regression gates and disabled-option frozen19 parity.
Save bounded seed telemetry (8 records, 20000 total vector values, <=10000
columns per vector), independently check retained fractional seed points.
Current-model/node checks are enforced internally; independent telemetry
checks original rows/bounds and metrics, not every unsaved node domain.

Screen: lotsize, eil33-2, danoint, blend2, p0201, rout, two alternating pairs
each, 30 seconds, 250000 nodes, gap 1e-6. Detailed capture enabled in both.
Then the same 27 development models once per profile at the same budget,
capture disabled. All own solves precede references; do not run competing
builds/reference solves during measured own runs. Preserve failures and all
regressions, report first point, objective/bound/gap and actual guidance use.
Stop for correctness failures before further performance work. A negative
performance result is retained and is not grounds to retune on the same screen
silently. All 27 are development data; no fresh holdout claim in this experiment.

Do not promote the option by feature count. Judge repeatable checked-point
gains, adverse outcomes, and completion/gap tradeoffs. If it does not help,
retain frozen19 as the recommended baseline and record why before the next
separate experiment. Numerical completion is not exact general-MILP proof.
