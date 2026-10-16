# Separate MILP search ranking and proof accounting

Iteration13 adds optional `--raw-lp-priority`. Combine with
`--objective-lattice` to retain the previous lattice proof strengthening while
ranking the queue by the unrounded, safety-adjusted LP lower bound.

Every Node has a monotone `search_bound` and a separate valid numerical `bound`.
The default policy still orders by `bound`, then deeper nodes, then increasing
node ID. The new policy changes only the first key to `search_bound`. It does
not weaken pruning thresholds, loosen feasibility/gap tolerances or import
reference solutions. Heuristic subproblem bounds are not global proof bounds.

## Minimum-bound invariant

When ranking and proof differ, a multiset indexes `(proof bound, node ID)` for
every queued node. Insertions/removals keep the queue and proof index together.
Clear/restart retains the selected priority policy and clears both indexes.
NaN keys fail explicitly. The minimum is compared independently with all
deferred-node bounds and the incumbent for:

- global-gap termination;
- lower-bound inheritance at a full-original-domain restart;
- final partial-result reporting.

The selected node's proof bound is NEVER substituted for this global minimum.
For example, a node ranked first may have proof bound10 while another queued
node has bound1. An incumbent5 cannot justify termination in that state.
This adversarial case is a direct regression test even if monotone lattice
rounding often makes the two minima equal on practical inputs.

A restarted root inherits only the valid global proof bound. Its search key
resets to negative infinity and is rebuilt from the new root LP. Children
inherit both keys; only optimality-verified main-tree LP results strengthen
them. The legacy policy avoids allocation of the second index. Both features
remain optional; separate bookkeeping is not itself a speedup guarantee.

## Audit and limits

`--capture-frontier` emits up to20000 push/pop/defer/reset/checkpoint events.
Infinity is represented explicitly as strings. Truncation is reported.
The independent Python checker replays queue membership, selected priorities,
deferred nodes, reset inheritance and global-minimum checkpoints. It compares
the final checkpoint with the reported bound when available. Mutation tests
reject use of the search top as a global minimum, missing nodes, changed
priority policies, wrong restart bounds and false truncation metadata.

This is NOT a complete MILP proof certificate: it does not independently
certify each LP dual bound, incumbent feasibility, all branching domains or
unsaved events. Those require separate numerical/original-model checks or
future exact certificate machinery. The iteration12 lattice arithmetic and
restricted binary exact-proof limitations remain unchanged.

See [iteration13 plan/results](../reports/milp-iteration-13/REPORT.md), including
fixed-node repeatability, same-budget comparisons and shared-desktop timing
caveats. Existing archives and old default behavior are preserved.
