# Repeated objective coefficients: explicit input convention

The current MPS reader adds repeated entries for a variable in the objective
row (`src/mps.cpp`). For example, two records `X OBJ 1` mean a cost of2 under
this reader. This behavior existed before the resumed iterations.

Iteration28's artificial transformations deliberately used repeated objective
entries. Installed HiGHS1.12.0 reads one copy of the equal entries in these
fixtures, producing half the intended objective vector. All other parsed
matrix, bounds, integrality and offset fields match. Consequently the initial
24 direct comparisons correctly report objective/reference disagreements.
Those failures are retained, not relabeled as successful raw comparisons.

The candidate answers themselves match an independent exhaustive enumeration
of the intended additive models. A separate reference-only representation
aggregates the repeated objective entries into one record. Every other parsed
field is checked unchanged, and the resulting cost vector is checked against
the exact sums. All24 unchanged candidate answers then pass independent
original-model feasibility, integrality and objective/completion checks.
No reference answer or bound enters the solver, and the solver source is unchanged.

For interoperable MPS files and cross-solver benchmarking, use one explicit
coefficient for each variable/objective pair. Do not assume all readers share
the additive convention. This finding is an input-contract limitation, not a
claim that a solver can silently choose another reader's intended objective.

Evidence: `reports/milp-iteration-28/artificial-stress/` retains the raw failures;
`artificial-stress-canonical-reference-verified/` retains field comparisons,
explicit equivalent MPS files and all rechecks.
