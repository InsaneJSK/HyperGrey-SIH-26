# Next bounded work — retain the repair, reduce its cost and test generalization

The captured mas74 cold and original warm failures are now repaired with the
unchanged numerical thresholds. Keep this regression permanently. The paired
full mas74 runs no longer consume recovery or defer nodes, but still have
about15.7% gaps. This is reliability progress, not a full MILP proof.

Do not promote universal refinement on the strength of that one model. The
development wave shows runtime/search trade-offs; p0201 completes in the
control pair but retains a0.197% gap with refinement. A fixed-time pair does
not isolate arithmetic overhead from changed pivots, heuristic timing or the
half-time restart. Preserve the current opt-in candidate and frozen control.
Eil33-2 also loses its returned point in the refined wave run while its control
finds one. First-feasible regressions must be addressed, not hidden by mas74's
gain or by a lower LP residual.

## Separate the next experiments

1. Attribute correction work without changing it: count residual scans,
   correction attempts/acceptance, LP phases and time across the MILP tree.
   Check ledger identities and disabled instrumentation parity. Do not change
   the arithmetic, cut allocation, restart or recovery budgets in that step.
2. On p0201 and the slower completed development cases, compare fixed-node
   and counter-driven-restart profiles to separate path changes from CPU cost.
   Use repeated alternating full solves as the decision endpoint, not isolated
   LP timing or a single favourable pair.
3. Only then test a general, mathematically motivated selective schedule for
   residual checks/refinement. Do not hard-code model names, known objectives
   or omit large finite bounds. Keep final certificate checks mandatory and
   preserve the captured cold/warm repair, transformed equivalents and all
   no-false-proof regressions. Resource limits and tolerances remain unchanged.
4. Before default promotion, predeclare genuinely untouched public models
   covering ill-conditioning, equality/degeneracy, general integers and weak
   relaxations. The current24 are development data. Expand actual benchmark
   coverage, retaining no-point, numerical, unresolved and resource failures.

## Broader solver and submission work

No-point models still need a feasibility diagnosis; very large remaining gaps
need stronger bounds/search. Do not combine those algorithm changes into the
accuracy experiment. Generic recovery-aware deferred retry remains relevant
only when unresolved nodes still occur; never reset the global spent allowance
or drop deferred domains to manufacture completion.

Real MRPL/domain-expert case validation, the final reproducible CLI/API demo,
and repeated GPU-specific evidence remain separate submission requirements.
Existing synthetic GPU QP results are not evidence for GPU MILP acceleration.
CPU tests continue locally. Kaggle is needed only for an actual GPU experiment;
no upload or new user input is needed for the next local work.
