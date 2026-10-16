# MILP iteration04: strict candidate repair and proof-safe branching

The prior recovery/neighbourhood implementation remains the performance
baseline. The new `--repair-candidates` option adds a bounded dense fallback
after an almost-integer tree LP fails the original absolute candidate check
and the existing strict sparse exact-integer-fixing solve does not repair it.
This is a numerical candidate-repair option, not a new problem class or a
general-purpose external solver dependency.

## Evidence for the repair

A locally reproduced blend2 rejection at node10612 has rounded absolute
violation2.000999984e-6. The exact same integer assignment is feasible: the
scaled sparse fixing LP returns numerical_error, while our dense simplex and
unscaled sparse simplex both solve it to objective8.015188, matching HiGHS.
The dense candidate has independent original fixing-model violation2.27e-13.
This establishes a numerical failure for this captured assignment, not that
every rejected integer assignment is feasible or that scaling is always bad.

The implementation uses the existing own dense two-phase simplex and existing
standard-form conversion. It fixes only the proposed integers and leaves the
original continuous bounds/constraints intact. It does not feed a reference
solution, benchmark optimum or model name into our solver. Candidate acceptance
still rounds integer values only within the existing integer tolerance and
requires maximum ORIGINAL-model absolute violation<=1e-7.

The fallback gets at most2 seconds, at most20% of remaining global time, and
at most min(15 seconds,10% of total solve time) cumulatively. The existing dense
tableau allocation guard remains in force. The primary sparse fixing solve
retains its existing global deadline. These are cooperative budgets; conversion
or a factorization can cause small timing overshoots. `--no-heuristics` does not
disable correctness-related candidate repair, just as it did not disable the
existing tree fixing solve. Zero solve time performs no repair.

## Separate correctness fix, shared by both comparison modes

A near-integer LP point is not an exact integer optimality certificate. Even
when its integer fixing can be repaired, that fixing's objective can be much
worse than the original node's LP bound. Discarding the entire node after such
a repair can lose a better integer assignment.

The regression uses a convex piecewise-linear V with integer i and epigraph t:
minimize t, t>=1e9*(1.00000008-i), t>=i-1.00000008, 0<=i<=2, t>=0. The LP
minimum is at i=1.00000008. Fixing rounded i=1 costs80, but i=2 costs about1.
A successful fixing solve must not be called a proof for the entire node.

After a successful repair, both modes now branch on a remaining nonzero integer
fraction even if it is below acceptance tolerance, provided both children
strictly tighten valid integer-domain bounds. The optional repair mode can also
do this after an unsuccessful repair. Otherwise the checked node bound is kept
unresolved, not replaced by the fixing objective. Fixed/out-of-domain numerical
drift cannot create a child identical to its parent. Final gap accounting uses
the retained global bounds, including deferred nodes. A repaired feasible
incumbent can improve the global upper bound; no fixing-LP bound is exported
as a bound on other integer assignments.

This correctness fix is NOT gated behind the experimental fallback flag.
Consequently the new comparison baseline is the previous algorithm choices
plus this proof-safety correction and diagnostics, not a byte-identical old
binary. The actual previous binary/source ZIP remain preserved.

## Diagnostics

`--capture-rejected-candidates` stores at most four near-integer tree rejections
(including those ultimately repaired). It records the relaxation and rounded
points, original residuals, node bounds, exact-integer fixing model, primary
repair status/primal/verification flags, and dense fallback status/primal if
attempted. Large fixing models omit full model capture; `captured` says whether
the model is present. Null lower/upper bounds mean negative/positive infinity.
The fixing solve is cold; its stored basis is empty, not a claimed warm replay.

`scripts/probe_milp_repair.py` captures a bounded run or exports its fixing LPs
and checks them with separate sparse/dense/unscaled/reference runs. These
diagnostic reference processes do not supply incumbents to MILP search.

The focused local validation compares baseline recovery+neighbourhood against the same
solver plus dense repair, using equal time/node/gap limits. Tests also retain
the legacy fractionality mode. A verified incumbent or a single hard benchmark
does not establish general industrial robustness, repeatable speedup, global
nonconvex support, or a submission ranking.
