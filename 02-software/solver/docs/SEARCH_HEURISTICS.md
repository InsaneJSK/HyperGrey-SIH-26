# Tree dives and fix-and-propagate

Two optional primal heuristics added in iteration 31, once relaxations became
fast enough that incumbent quality, not bound strength, limited most models.
Neither creates a node, tightens a bound, or exports anything to the proof: they
only offer points, and every point must pass the same `accept()` checks as any
other (integrality within tolerance and original-model feasibility).

## `--tree-dives`

Before iteration 31 the dive block ran only at the root, or every 100 nodes
while no incumbent existed. With an incumbent present the search relied on
integral node relaxations and the neighborhood search, which rarely reach good
leaves in a best-bound tree.

With the flag, the same dive block also runs during the search:

- spacing: 32 nodes initially, halved after a dive that improves the incumbent
  and doubled after one that does not, clamped to 16–1024 nodes;
- total budget: dives stop once they have used about a tenth of elapsed time;
- per-call budget: at most 1 s or 5% of the remaining time, and 256 steps;
- a third mode: pick the fractional coordinate closest to the incumbent and
  round toward the incumbent's value, rather than by fractionality or cost.

Dive relaxations carry the node cutoff, so a dive branch whose bound reaches the
incumbent stops immediately instead of solving to optimality.

## `--fix-propagate`

A first-point search for models where the pump and dives fail. It fixes integer
columns one at a time and propagates after each fixing:

- order: nearest-integral LP values first (policy 0), or by bound (policies 1
  and 2, toward lower and upper bounds); the root tries all three.
- value: the rounded LP value, then the other side; for bound policies, the
  bound then its neighbor.
- backtracking: the last 16 fixings keep their untried value and the bounds
  before they were applied. A dead end restores the most recent frame with an
  untried value; at most 32 backtracks per call.
- finish: when every integer column is fixed, solve the LP over the remaining
  continuous columns and offer the point to `accept()`.
- scheduling: at the root, and while no incumbent exists every 100 nodes with
  geometric backoff to 6400 nodes after failures.

Propagation itself is unchanged apart from reusing one scratch buffer instead of
allocating per row and pass, which is why node throughput rose sharply on models
with many rows (gt2: about 148,000 to about 390,000 nodes in 30 s).

## Measured effect (iteration 31)

Two development repeats: incumbents improve on gt2, rout, misc07, p0282, mas74,
mas76, gen-ip002, gen-ip054 and pk1; `eil33-2` and `assign1-5-8` regress
marginally; `danoint` varies between runs in every profile. On 12 unseen MIPLIB
3 models the promoted profile returns 10 checked points against the control's 8,
including `mod011`, which no other profile solved.

## Limits

- `lotsize`, `mitre` and `p2756` still get no point: fix-and-propagate reaches
  thousands of fixings without completing an assignment on those structures.
- Dives spend budget that the tree would otherwise use; on models where the
  tree was already productive this costs a little quality.
- Bounded backtracking is chronological, not conflict-driven, so a dead end far
  above the last 16 frames ends the attempt.
- Both heuristics are off by default and are part of the recommended evaluation
  profile only; see `reports/milp-iteration-31/CANDIDATE_PROFILE.json`.
