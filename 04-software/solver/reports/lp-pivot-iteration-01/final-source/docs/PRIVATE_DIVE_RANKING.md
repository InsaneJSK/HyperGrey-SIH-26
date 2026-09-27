# Experimental private-dive near-tie ranking

`--pump-distance-stable-ranking` requires `--pump-distance-diving`, which in
turn requires `--pump-guided-diving`. It is off by default. It affects only
the private distance dive, not original-objective dives or global branching.
The recorded full profile and its outcome belong to iteration25's report.

For a verified fractional point, compute `abs(x[j] - round(x[j]))` for integer
columns. Scores must strictly exceed the existing integer tolerance. Find the
actual maximum, then choose the first original column whose score is within
1e-12 of that maximum. Two passes anchor the tie set to one maximum; repeated
pairwise approximate comparisons could otherwise create a chain of ties.

The 1e-12 constant is a ranking tolerance only. Feasibility, integrality,
private LP verification, original-model incumbent checks and proof tolerances
are unchanged. No instance name, reference solution/bound or privileged column
number is used. The rule supplies a column index, never a bound or certificate.

The stability contract is conditional: a fixed column layout, unchanged
fractional eligibility and unchanged anchored tie-set membership preserve the
winner. No continuity is promised at a tie boundary. Permuting tied columns
can change the winner; the result must still be the first column in the new
layout's anchored tie set. Large translations can lose fractional information
in floating point; exact mathematical translation invariance is not a claim
about arbitrarily large double-precision values.

Malformed dimensions, nonfinite points and invalid integer tolerances are
rejected by the helper. Empty integer domains remain guarded before private
model construction. The existing failed-primary/alternate ownership and
shared dive deadline are unchanged. Zero/exhausted budgets invoke no ranking.

JSON `private_ranking` records enabled/calls/ties/changes. `changes` counts a
different selection from strict maximum ranking on the same point. An enabled
flag with zero calls or zero changed decisions is not evidence that the rule
caused a timed performance change. Clock-dependent cutoffs can still alter
search outcomes even when fixed-vector ranking is stable.

See `tests/test_private_dive_ranking.cpp`, the retained own-vector replay and
the complete paired ledger under `reports/milp-iteration-25/`.
