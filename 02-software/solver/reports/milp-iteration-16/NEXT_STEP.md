# Next bounded work — fix sparse LP reliability before more cut tuning

The new guard protects first-feasible cut allocation, but both Binkar screen
pairs and the full-wave pair have worse final gaps than their five-round controls. Keep it
optional and stop treating fewer cut LPs as a general performance improvement.
Fresh holdouts and repeated whole-solve evidence are needed before promotion.

## Priority: the retained mas74 relaxation

Use `mas74-diagnosis/captured-relaxation.mps` as a permanent numerical fixture,
with its source-result and model hashes. Frozen15 sparse cold solving returns
numerical_error with about 9.77e-5 absolute violation; dense recovery matches
the independent objective with about 4.37e-11 violation. Both report 130 LP
iterations. The sparse primal/dual relative gap fails its existing threshold.

Instrument the sparse basis solve and original-model residuals to locate the
loss of accuracy. Investigate guarded residual-based refinement and fresh
factorization before increasing pivot or fallback budgets. A 1e12 finite upper
bound and small objective coefficients make cancellation plausible, but the
exact arithmetic cause is not yet established. Do not remove valid bounds,
loosen tolerances or accept the failing sparse point to obtain a green status.

The next candidate must preserve the full node domain and validate primal/dual
certificates after repair. Test the retained fixture, min/max and scaled/
translated equivalents, singular/degenerate bases, infeasible and unbounded
cases, bounded interruption and resource rejection, then all development models.
Keep a frozen control, generated regression tests and genuinely new holdouts.
Any rejected correction falls back to the previous honest numerical outcome.

## Separate allocation follow-up

Mas74's six-second global recovery allowance is exhausted before the half-time
restart. Its restarted root's two children are deferred; the active queue is
empty, so the solver returns unresolved_relaxations while preserving bounds.
The same happens without late LP transformations. Disabling the restart uses
the full 30s but leaves thousands of unresolved nodes. This is diagnostic
evidence, not a sufficient general restart policy.

Only after LP accuracy work, test a separate recovery-aware restart/deferred
retry policy with an unchanged total resource allowance. Never discard
unresolved nodes, silently reset spent budgets or certify completion from
exhausted heuristics. Keep allocation and numerical changes in separate
experiments so improvements and regressions remain attributable.

CPU-only work remains local. No Kaggle upload is needed. Real domain validation,
the final reproducible demo and repeated GPU-specific evidence remain separate
submission requirements; all-public-MILP coverage is not established.
