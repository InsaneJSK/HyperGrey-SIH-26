# Experimental pump-guided diving

Iteration20 adds `--pump-guided-diving`, off by default. It is independent of
`--repair-heuristic-candidates`; the paired experiment enables iteration19's
repair in both profiles. `--no-pump` / `--no-heuristics` make the guidance inert.

The existing feasibility pump optimizes integer L1 distance. Previously its
fractional progress was discarded before diving resumed from the original LP
point. The experiment stores a single best projected point with strictly lower
integer distance. It requires a verified projection, finite original-size
vector, unchanged 1e-7 original/current-model row and bound checks, and the
current node's bounds. It stores neither a projection objective nor a basis.

If the immediately following dive still lacks an incumbent, mode zero starts
from this hint. Its subsequent branch directions favor the saved point's nearest
integer values, clipped to the current dive bounds. Fractionality still chooses
the branching variable. Mode one keeps its original root point and cost-driven
direction. All dive LPs retain the original objective/current rows and root
basis; auxiliary projection columns and bases are never reused here. A hint is
local to one processed node and discarded afterward, including across restarts.
Current dive scheduling is unchanged, so a restarted root need not get a dive.

This cannot certify that the rounded target is feasible. A failed fixing does
not prune or certify the global tree. Only unchanged original-model integer
point acceptance may update the incumbent. The parent LP proof bound, frontier,
cuts, restart rules and arithmetic tolerances are unchanged. A valid incumbent
can legitimately affect ordinary bound pruning; the heuristic does not export
a replacement proof bound.

The existing five-second pump slice, two-second dive slice, two dive modes,
64 steps per mode, global time/node limit and shared candidate-repair allowance
remain in force. Selecting/checking a seed consumes the current pump/global
clock. Retaining its bounded telemetry also consumes the global clock. These
are cooperative limits, not hard operating-system time/memory isolation.

## Telemetry and checks

`pump_guidance` counts calls, candidate projections, rejected projections,
strict improvements, guided dives and guided steps. There are at most eight
scalar samples. With `--capture-feasibility`, initial/selected vectors are saved
only together, <=10000 columns each and <=20000 total values. Missing vectors
are explicitly unverified by the independent vector checker. The older
512-event/100000-value feasibility trace remains independently bounded.

The new checker validates accounting, metric reductions and retained fractional
points against independently read original rows/bounds. It does not mistake
fractional seeds for integer feasible solutions, nor independently certify
unsaved intermediate LP optima, cut rows or node domains. Final MILP points are
checked separately for integrality, original rows/bounds and objective.

Small exhaustive tests may finish in the pump without using the guided dive.
Separate root-only public integrations therefore require actual guidance use;
repeated equal-budget public comparisons assess effectiveness. Source snapshots,
old-version parity, raw results and adverse outcomes are retained. All current
27 public cases are development data, not untouched holdouts. The feature stays
experimental unless repeatable gains justify promotion.

See [iteration20](../reports/milp-iteration-20/REPORT.md) for the actual decision
and every measured outcome. No GPU work is involved.
