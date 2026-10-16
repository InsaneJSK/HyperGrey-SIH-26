# Guarded objective-lattice bounds

Iteration12 adds the optional `--objective-lattice` flag to the CPU MILP path.
It changes bound strength, not the objective, constraints, reference inputs or
incumbent values. The experiment and results are versioned separately under
`reports/milp-iteration-12`.

## Algebra and supported scope

Normalize maximization to minimization with sign -1. If the normalized objective
is `offset + sum(c[j] * x[j])`, all nonzero effective coefficients are integral,
and their variables are integer, every feasible objective lies in
`offset + gcd(abs(c)) * Z`. This can exclude the fractional interval between an
LP lower bound and the next attainable objective value.

A continuous objective variable is allowed only if an original, finite, exact
equality defines it with coefficient +1 or -1 and all other nonzero variables
in that equality are integer. Substituting that equation must produce checked
integral coefficients. Multiple independent definitions are supported; coupled
continuous equations, nonunit pivots and inequality-based arguments are not.
Neither node-local bounds nor heuristic fixings may establish this property.

For example, `y - 5*x1 + 10*x2 = 2`, integer x1/x2, and objective `y + 0.25`
give objective `2.25 + 5*x1 - 10*x2`, on the lattice `2.25 + 5*Z`.
This is a model-wide statement and remains valid after branching or adding
valid cuts. It does not require the variable y to occur in only one row.

The initial implementation deliberately rejects fractional objective costs,
fractional defining-row coefficients/RHS and constant transformed objectives.
Zero-cost continuous variables elsewhere do not invalidate a direct lattice.
Offsets must be exactly representable multiples of 2^-16; the scaled offset
and each offset accumulation have an absolute 2^50 cap. Other integer
coefficients, sums and products have a 2^40 cap. Rejection keeps the previous
numerical algorithm and records a reason; it is not a model rejection.

These are exact algebraic statements about the PARSED binary64 model. They do
not certify that arbitrary decimal input literals were represented exactly.
The separate restricted binary-proof engine retains its stronger literal-input
guards and its separate exact-proof classification.

## Numerical bound safeguards

Only the main tree's optimality-verified LP results reach the new rounder.
The existing safety subtraction `100 * LP tolerance * (1 + abs(raw bound))`
remains in place. Another conservative arithmetic margin, based on double
epsilon and bound/offset/step magnitudes, is subtracted BEFORE applying ceil.
The resulting grid value is published one double ULP downward. The rounder
never weakens the existing bound and does nothing for nonfinite or excessive
magnitudes. It does not snap the returned feasible point or objective.

Unverified LP outcomes, infeasibility/unboundedness statuses, heuristic
neighborhood objectives and repaired fixing objectives are not rounded into
tree proofs. Existing queue/deferred-node/late-restart coverage is unchanged.
The exact binary engine bypasses this numerical LP mechanism.

This strengthens a NUMERICAL bound; it does not turn a floating-point LP
certificate into an exact rational certificate. The arithmetic margin is not
a substitute for rigorous interval/exact verification of the raw LP bound.

## Independent audit

The CLI reports eligibility/rejection, normalized offset/step/effective costs,
selected defining row/column indices and bound call/improvement counts. Up to
4096 improved-bound events are saved; truncation is explicitly reported.
`scripts/check_objective_lattice.py` reads the original MPS with HiGHS, checks
its column order, and independently reconstructs each claimed substitution
using Python Fraction arithmetic. It verifies the GCD and each saved output
bound against the exact next grid value from the saved input bound.

This audit covers saved rounding events and structural algebra, not all
internal LP dual certificates or unsaved intermediate primal candidates.
Independent original-model feasibility, integrality, objective, final-bound,
lifted-cut and restricted exact-proof checks remain separate gates.

Objective integrality as a solver property is established practice; see the
[SCIP objective-integrality API documentation](https://www.scipopt.org/doc-9.2.3/html/group__GlobalProblemMethods.php).
The implementation here is independent C++11 code; SCIP is not a dependency
and no reference solver is called by the optimization core.
