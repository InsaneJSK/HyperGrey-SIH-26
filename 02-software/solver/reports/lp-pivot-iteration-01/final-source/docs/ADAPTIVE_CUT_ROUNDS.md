# Selective root-cut continuation (experimental)

Iteration15 adds `--adaptive-cut-rounds` and `--capture-cut-rounds`. Both are
off by default. Adaptive mode always captures its decisions. The existing
`--root-cut-rounds N` remains an upper bound (0 through 5, default 5), not a
minimum: cuts may run out, the time reserve may be reached, or an LP may fail.

## Decision rule

Only a successfully solved, numerically verified cut LP is eligible. Keep
the first two successful rounds where the ordinary limits permit. Keep cheap
rounds below 256 reported LP iterations. Otherwise compare marginal bound
gain with the round's work relative to its own root relaxation:

```
scale  = max(1, abs(before - signed_offset), abs(after - signed_offset))
gain   = max(0, after - before) / scale
effort = max(1, round_iterations / root_iterations)
stop further cut rounds when gain <= 0.001 * effort
```

Bounds and offset here are in internal minimization sense, including for a
maximization model. These are raw numerical LP bounds used ONLY for allocation;
they are not newly published proof bounds. Root/round iterations include the
MILP-visible relaxation's reported recovery/fallback work. They do not measure
factorizations, FLOPs or interchangeable units of CPU work.

Nonfinite inputs/intermediates and zero root work retain the old continuation
behavior under the explicit round/time caps. Binary64 arithmetic is used.
Removing the objective offset reduces ordinary translation sensitivity, but
cannot undo cancellation; the scale floor of 1 breaks arbitrary small-scale
invariance. The constants are predeclared development-informed choices, not
mathematical guarantees or a fitted per-benchmark rule.

## Safety boundary

A stop keeps the current valid cut model and existing LP solution/basis. It
does not close a search node, declare infeasibility, change an incumbent, or
create a global bound. The established numerical validation, lattice handling,
frontier minimum, pruning, domain coverage and restart logic still decide those.
Failed optional cut LPs use the existing rollback; verified infeasible cut LPs
use the existing terminal handling. Heuristic-local bounds remain local.

The policy is evaluated independently at the initial root and the existing
single full-domain restart. It does not enable extra restarts or reset global
time/node/heuristic budgets. Explicit round caps 0 or 1 take precedence over
the policy's two-round preference. There is no hard pivot, process-memory or
elapsed-time guarantee added by this feature.

## Evidence fields

The JSON `cut_policy` object reports enablement, capture, stop count and each
attempted cut LP's root id, restart number, round, root/round iteration counts,
raw before/after bound, signed offset and decision. At most ten attempted LP
rounds exist under the current cap/restart rules; no silent trace truncation.

Reasons distinguish disabled policy, minimum rounds, cheap round, missing work,
invalid metrics, productive/diminishing returns, round cap, rollback and
infeasible LP. `stops` counts policy decisions, not a measured number of rounds
saved; an ordinary time or separation limit might also have stopped later work.
The independent replay checks arithmetic, sequencing, continuity, counts and
phase totals, not exact validity of the underlying LP certificates or cuts.

See [the fixed experiment plan](../reports/milp-iteration-15/PLAN.md) and the
[iteration15 results](../reports/milp-iteration-15/REPORT.md). Retain adverse
results and compare whole solves, not only saved cut time or additional nodes.
The reference checker separately caches binding-backed matrix arrays, with
validation-field equivalence to frozen14 on 21 cases. That is checker throughput,
not optimization-engine speed. CPU work stays local; no Kaggle run is required.
