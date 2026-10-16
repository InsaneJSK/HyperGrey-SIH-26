# Refresh eta-based directions before a numerically small pivot

Declared after the logging-only diagnosis and before this candidate is run.
The rejected 610-column bandm basis has exactly opposite rows 500 and 501,
with zero RHS. Checking their captured binary64 coefficients gives an exact
row dependence; this is stronger than the accompanying numerical SVD rank 609.
At pivot 194 the eta-based direction reported 2.7228116161127502e-8 for the
last independent slack of that row pair. The factorization at pivot 200 then
correctly rejects the singular basis. Refining primal/dual RHS values alone
does not correct that entering-column direction.

Candidate: when a selected pivot is at most 1e-7 times (1 + the direction
infinity norm), and eta updates are present, refactor the CURRENT basis and
recompute values, pricing, direction and ratio selection before any mutation.
There is at most one such refresh on a given iteration because the fresh LU
has no eta updates. This threshold requests more accurate arithmetic; it does
not discard coefficients or relax feasibility, integrality, pivot eligibility
or final optimality checks. It is a numerical heuristic, not a condition-number
proof. Refactor failure or an expired budget retains an honest failure/limit.

First test a separate diagnostic candidate on bandm default/refined/compact,
then all 16 retained/additional LPs with the same candidate source. Protect
genuine small pivots, failed refactors, cycling bookkeeping, warm/alternate
ownership and resource budgets. Any working-engine change requires dedicated
regressions and the full correctness gate, followed by a declared broader
validation on the final binary. Preserve failed attempts and do not promote
solely on bandm or claim a MILP gain from this LP fixture.
