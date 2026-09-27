# Guarded local dual infeasibility

Iteration29 implements an experimental shortcut for compatible warm private
LPs. `--private-dual-certificate` requires `--pump-distance-reopt` and its
existing dependencies. It is off by default. It is not enabled for the MILP
root, cut relaxations, tree bounds or global infeasibility proofs.

In a dual iteration, a negative basic value with no eligible entering column
supplies a candidate row `y = B^-T e`. Absence of a pivot is not itself a
certificate. For the nonnegative canonical variables, verification requires
every true column to satisfy `A^T y >= 0`, with a strict negative `b^T y`.
Equality artificial slacks are excluded; basic columns and inequality slacks
are included. This is the opposite-sign convention of the equivalent
[Farkas certificate in the MOSEK modeling cookbook](https://docs.mosek.com/modeling-cookbook/linear.html).

The shortcut intentionally supports a narrow arithmetic domain. Multipliers,
active canonical coefficients and original row coefficients must be integers
with magnitude at most 2^26. Canonical scales must divide active multipliers
exactly. Signed coefficient sums stay within 2^52. Values outside those guards
cause rejection, not rounding into the supported domain. There is no tolerance
allowance for a negative column: a tiny negative coefficient can permit a
large feasible variable and cannot be dismissed as zero.

The verifier then reconstructs the row combination on the original private
LP coefficients, before canonical scaling and shifting. It minimizes that
combined linear expression over the original variable bounds. RHS and bound
products/sums use outward floating-point enclosures. The lower contradiction
margin must exceed the upper bound on ten times the LP tolerance times its
scale. This checks the parsed binary64 LP; it is not an exact-decimal input
proof, a MILP proof, or a new operational tolerance.

The enclosure arithmetic requires IEEE binary64, round-to-nearest and gradual
underflow, checked at runtime. Builds with fast-math or reassociated arithmetic
are outside this numerical contract. The supported Release CMake build uses
neither. Nonfinite arithmetic, overflow, uncertain coefficient signs, invalid
bases and expired deadlines preserve the existing fallback/limit behavior.
Deadline checks occur during certificate work; no extra time slice is granted.

An accepted local certificate returns no primal point or reusable basis.
The caller retains the parent basis for the alternate branch. The CLI reports
local `attempts` and `accepted` counters under `private_dual_certificate`;
these counters must never be interpreted as global pruning evidence.

The diagnostic and candidate replay source, exact independent arithmetic
checks, failure logs, correctness gate and repeated screen are retained in
`reports/milp-iteration-29/`. The saved LP work reduction alone does not justify
default promotion; use that iteration's report for the MILP decision.
