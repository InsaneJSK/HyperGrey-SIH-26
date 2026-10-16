# Guarded sparse basis-value correction

Iteration17 adds the experimental `--refine-basis` CLI flag and
`Options::refine_basis`. It defaults to **false**. It affects sparse LP solves,
including MILP relaxations using the sparse backend. It does not change the
shared SparseLU implementation, dense simplex, cut policy, recovery allocation,
branching policy, bounds, tolerances, pivot limit or fill limit.

## Why it exists

The retained mas74 node contains 151 continuous variables and 13 original rows,
including a finite variable upper bound of 1e12. The frozen solver's cold solve
and original saved warm-basis solve both fail the existing numerical check.
The cold solve reaches 130 pivots but has about 9.77e-5 absolute violation and
3.38e-8 relative primal/dual gap (threshold 1e-8). Dense recovery is accurate.

Diagnostic basis residuals show loss of accuracy in the combined LU/eta RHS
solves. One correction on that same basis reduces original violation to about
7.71e-12 and closes its numerical gap. Fresh factorization alone does not fix
the problem. This isolates an effective arithmetic repair; it is not a proof
that every ill-conditioned basis has the same cause or that refinement always
converges. No bound is removed and no reference point is supplied to the core.

## Algorithm and safeguards

For basic primal values and basic-cost dual multipliers, compute the residual
against the actual current basis B, using long-double accumulation:
`r = rhs - B*x` or `r = rhs - transpose(B)*x`.

The trigger is `max_i(abs(r_i)/(1+abs(rhs_i))) > 64*double_epsilon`.
This is an arithmetic trigger, not a relaxed feasibility criterion. It keeps a
large-bound slack from masking errors in unrelated small equations. At most two
correction solves per RHS use the existing LU and eta updates. A trial is
accepted only when finite and its residual measure strictly improves. A bad,
stagnating, malformed or interrupted correction leaves the previous values.

Cancellation checks occur between stages and during residual accumulation.
Work is charged to the existing LP wall-clock budget; there are no additional
pivots or new factorizations in the correction routine. This does not promise
an operating-system hard memory/time sandbox. On compilers where long double
equals double, residual arithmetic has no additional mantissa precision.

The ordinary simplex decisions and final original-model primal/dual/gap checks
remain in force. Rejected refinement does not confer a certificate. MILP proof
accounting still retains unresolved relaxations. General certificates remain
floating-point numerical evidence, not exact rational proofs.

LP JSON includes `basis_refinement_enabled`, `basis_refinement_attempts` and
`basis_refinement_accepted`; the counters include compact-equality retries.
MILP JSON records the enabled flag; those per-LP counters are not aggregated
across the tree. Pivot directions and pivot-row solves are not refined by this
version. The feature is for sparse LP; the dense backend does not use it.

## Evidence and reproduction

See [iteration17](../reports/milp-iteration-17/REPORT.md) for final public results,
the unchanged control, remaining failures, hashes and promotion decision.
`tests/sparse_accuracy_fixture.mps` and `tests/sparse_accuracy_basis.txt` retain
the captured domain and original warm input. Their provenance links to the
original node result. The warm replay uses the ordinary 10000-pivot allowance,
not the previously spent five-pivot count as a new limit.

The dedicated C++ test covers cold and genuine warm replay, 12 transformed
min/max LP equivalents, numerical certificates, degeneracy/singularity,
infeasible/unbounded cases, budget rejection and correction acceptance guards.
The gate independently checks both repaired original-model points, runs the
existing suites, generated mixed-integer cases and disabled-option parity.
Public timing comparisons are sequential and all reference work follows the
own-solver runs. The 24 retained public models are development cases, not fresh
holdouts. CPU work runs locally; no Kaggle notebook is involved.
