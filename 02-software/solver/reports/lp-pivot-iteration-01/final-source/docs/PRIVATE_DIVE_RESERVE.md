# Private dive diagnostic and alternate reserve

`--capture-private-dive` saves at most two exact private LP fixtures: the first
child needing at least256 total pivots, and the first distinct unsuccessful
child. Captures include model/bounds, objective/auxiliaries, tagged basis,
branch/step, allocated/elapsed time and LP statistics. Caps are200000 matrix
entries,10000 columns and20000 rows. Enable only for diagnostics; copying and
JSON output can affect timing. Never import replay answers into a measured solve.

`--pump-distance-alternate-reserve` requires `--pump-distance-diving`. Each
primary private child receives half the remaining shared dive slice, leaving
time for its alternate. It does not add time to the total dive deadline or
change original-model acceptance and proof checks. The parent basis advances
only after a verified optimal child; a failed primary leaves parent state for
the alternate. It is off by default.

Iteration26 rejected promotion: all three lotsize runs per profile remained
without a point; both profiles returned69.5 on danoint in all three repetitions.
The candidate cap executed47 times on lotsize, without useful coverage gain.
All twelve exact LP replays corroborated local infeasibility. Danoint's earlier
miss was a separate pump-fixing deadline, before this policy could execute.

See [the report](../reports/milp-iteration-26/REPORT.md) and exact fixture ledgers.
These are explained experiments, not a claim of reliable arbitrary MILP solving.
