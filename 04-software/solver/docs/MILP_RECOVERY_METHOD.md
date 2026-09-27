# MILP iteration 03: recovery and incumbent neighbourhoods

Both additions are opt-in. Fractionality remains the branching default, and
`--branching reliability` remains the separate earlier experiment.

## Bounded LP recovery

`--lp-recovery` responds to a tree relaxation returning `iteration_limit`,
`numerical_error`, or `numerical_stall` with a fresh sparse Phase-I/basis solve.
The per-LP iteration cap is unchanged. A cold restart gets at most two seconds;
the existing dense simplex alternative may use the remainder of a five-second
recovery allowance if the model fits the tableau memory guard. Total recovery
time is limited to min(30 seconds, 20% of the original MILP time limit), within
the global deadline. These are cooperative solver deadlines, not hard process
kill guarantees; model conversion/factorization can slightly overshoot.

Only numerically verified LP optimality or infeasibility resolves a node. If
recovery remains unsuccessful, the node and its last validated ancestor bound
are deferred, and the other active nodes can proceed. The minimum deferred
bound participates in global stopping and final gap accounting. An empty
active queue with unproved deferred nodes returns `unresolved_relaxations`,
unless the retained valid bound already meets the requested gap. It must not
be called infeasible or solved merely because no active nodes remain.

The same rule covers a near-integer LP point that fails the unchanged absolute
candidate check and cannot be repaired by an exact-integer fixing LP. Such a
point is never accepted; its checked LP bound remains attached to an unresolved
node while other nodes continue. A regression deliberately magnifies a tiny
integer rounding displacement into an unacceptable row violation.

Deferred nodes are not given unlimited further retries. The new mode avoids
one failed relaxation aborting all other work; it is not a general solution to
simplex cycling, degeneracy, numerical conditioning, or proof completion.

## Checked incumbent improvement

`--improve-incumbent` enables an LP-guided restricted neighbourhood search after
an incumbent exists. It keeps continuous variables free, fixes most integer
variables to the incumbent, and frees integers ranked by disagreement with the
current LP solution, with deterministic tie variation. The free count is bounded
by 48 and is approximately one fifth of movable integers, with a minimum of
eight when that many exist. Fixings use global model bounds, not the current
node's bounds: an incumbent need not belong to that node.

Each private depth-first search uses at most 64 local nodes and two seconds.
Calls are separated by at least 128 main-tree nodes, with at most 16 calls and
a total min(30 seconds, 15% of global time) allowance. `--no-heuristics` disables
it. Local bounds may prune the private neighbourhood only; they never enter the
global proof queue. A candidate reaches the global incumbent only through the
unchanged original-model absolute feasibility (1e-7) and integrality checks.

This is RINS-inspired, not a claim to implement the exact published RINS
selection rule. Background: [Berthold, Heuristic algorithms in global MINLP
solvers (2014)](https://www.zib.de/userpage/berthold/Berthold2014.pdf). All search
and LP code here is our C++ implementation; reference solvers are separate
validation processes and never provide a starting incumbent to this search.

## Diagnostics and comparison

`--capture-lp-failure` records the first non-heuristic iteration/numerical failure,
including its continuous model, node/depth, parent bound and **input** basis.
The stored basis is the starting basis, not the final stalled basis. The first
failure can be an optional root-cut solve, not necessarily a terminal tree
failure. Model capture is capped at 200,000 row entries and 10,000 columns;
larger failures keep their summary with `captured: false`. JSON null denotes
infinite bounds (negative infinity for lower, positive infinity for upper).

`scripts/inspect_lp_failure.py` can export the captured relaxation and compare
cold sparse/dense/reference solves after timed measurements. It normalizes to
minimization and explicitly records the omitted objective constant. It does
not replay the warm basis, so cold success alone does not identify the precise
warm-simplex failure mechanism.

The iteration also corrects LP-iteration accounting across fallback attempts:
count each initial, cold, and dense attempt once, including unsuccessful
fallback iterations. Historical LP-iteration totals are not perfectly comparable
where the old dense fallback was used. `warm_starts` retains the existing
returned-LP-result counting convention, not a full attempted-restart census.

Generated tests cover control, recovery-only, and combined modes. The focused
hard run compares control against the combined mode using identical time/node/
gap limits. This isolates the package against the current default, but does not
separate both components' hard-case effects; counters and a follow-up ablation
are needed before promoting either option. One sequential timing pass is an
iteration check, not a repeatable speedup claim.
