# Tableau Gomory mixed-integer cuts

An optional root separator added in iteration 32, once iterations 30 and 31 had
made relaxations fast and first points reliable, leaving bound strength as the
limit on completion. Before this, the engine separated cover and lifted-cover
cuts only, so a model whose relaxation is weak for any reason other than
knapsack structure got no help and had to close its gap by branching alone.

`--gomory-cuts` requires `--bounded-lp` and is rejected together with
`--no-cuts`. Defaults are unchanged; nothing runs in the tree.

## Where the cuts come from

The bounded dual simplex keeps a factorized basis, so a tableau row is one
BTRAN away. In each root cut round, before any row is appended to the model, the
separator rebuilds the basis from the relaxation that was just solved and, for
each basic integer variable whose value is fractional:

1. BTRANs a unit vector to get the row of `B^-1`, and prices every nonbasic
   column against it;
2. shifts each nonbasic column to its active bound, so every term becomes a
   variable `t = X - L` or `t = U - X` that is nonnegative **at any feasible
   point, not just this one**. A row containing a free nonbasic column cannot be
   shifted and is skipped;
3. applies the standard GMI formula, treating a nonbasic integer column as
   integral only when its active bound is integral — otherwise `t` need not be
   an integer and the stronger coefficient would be wrong;
4. substitutes the row logicals back into structural variables and unscales.
   Scale factors are powers of two, so this is exact;
5. relaxes the cut by the largest contribution any dropped small term could have
   made, which is why dropping can only ever weaken it;
6. rebuilds the cut in original space and requires it to reproduce its own unit
   violation there;
7. rejects the cut outright if a known incumbent violates it.

Fixed columns and equality-row logicals drop out exactly: their shifted variable
is identically zero.

## Why validity does not depend on the current point

Two facts carry it. The tableau equality holds at every point satisfying the
rows, and every shifted variable is nonnegative at every feasible point. The LP
solution is used only to choose which rows are worth cutting and to measure
violation. A cut derived from a poor or repaired basis is still valid; it is
just weaker.

## Selection and lifetime

- At most `min(16, max(4, rows/8))` cuts per round. A handful of cuts on a
  fifteen-row model is a rewrite of the model, and `pk1` showed exactly that:
  an unscaled limit produced 78 rows on a 15-row model and cut node throughput
  by a factor of four.
- Cuts nearly parallel to one already selected in the round are dropped. A
  tableau produces plenty of them and they add rows without adding information.
- Support, dynamism and efficacy limits apply; a cut must still remove the
  current point after its safety relaxation.
- **After the last round, any tableau cut whose logical is basic in the final
  root relaxation is removed.** It is not binding there, so its dual is zero,
  the point and the bound are both unchanged, and every node below stops paying
  for the row. Only rows this separator added are considered; cover cuts are
  left alone.

## What is and is not claimed

The derivation is floating point. These are not certified cuts in the
directed-rounding sense, and the document does not claim they are. What stands
behind the answers is the checking:

- `tests/test_gomory_cuts.cpp` (CTest: `gomory_cut_validity`) builds 3,000
  random all-integer models with small explicit boxes, **enumerates every
  integer point**, and checks every returned cut against all of them. It then
  re-solves the strengthened relaxation and requires that it not pass the
  enumerated integer optimum. A further 400 mixed models *maximize* each cut
  over the continuous variables with the integers fixed, one LP per assignment,
  which is an exact test over the whole mixed feasible region.
- At runtime, each cut must reproduce its unit violation after being rebuilt in
  original space, and is rejected if it would remove a known incumbent.
- Every benchmark record is compared against HiGHS 1.12.0 reading the original
  file.

## Telemetry

The `gomory_cuts` JSON object reports `calls`, `candidates`, `attempts`,
`generated`, `applied`, `purged`, `rounds`, `best_efficacy`, `seconds`, and one
counter per rejection reason (`skipped_free`, `skipped_drop`,
`skipped_consistency`, `skipped_dynamism`, `skipped_support`,
`skipped_efficacy`, `skipped_parallel`, `rejected_incumbent`,
`basis_rejected`). `scripts/check_gomory_cuts.py` verifies that the outcomes of
every attempt add up to the attempts made, that a disabled separator did no
work, and that retained rows never exceed the reported cut total.
