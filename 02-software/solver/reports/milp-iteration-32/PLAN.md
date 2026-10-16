# Iteration 32 plan — tableau cuts for the bound

Declared 18 September 2026, before any timed comparison or holdout solve.

## Hypothesis

Iterations 30 and 31 fixed relaxation speed and first points. What now limits
completion is bound strength: the engine separates cover and lifted-cover cuts
only, so models whose LP relaxation is weak for reasons other than knapsack
structure get no help at all, and the search has to close the gap by branching
alone. HiGHS proves 13 of the 15 iteration-30 holdout models inside 30 s where
we prove 5, and its advantage is concentrated in cut families we do not have.

The bounded dual simplex of iteration 30 keeps a factorized basis, so a Gomory
mixed-integer cut can be read directly off a tableau row of any fractional
basic integer variable. Adding those cuts at the root should raise the root
bound and reduce the tree, at the cost of larger node relaxations.

## Mechanism

`--gomory-cuts` (requires `--bounded-lp`; rejected with `--no-cuts`). In each
root cut round, before any row is appended, the separator rebuilds the basis
from the relaxation just solved and, for each basic integer variable with
fractional value:

1. BTRANs a unit vector to get the tableau row, and prices every nonbasic
   column against it;
2. shifts each nonbasic column to its active bound, so every term is a
   variable that is nonnegative at ANY feasible point, and skips the row if a
   free nonbasic column appears in it;
3. applies the standard GMI formula, treating a nonbasic integer column as
   integral only when its active bound is integral;
4. substitutes rows back into structural variables and unscales exactly (the
   scale factors are powers of two);
5. relaxes the cut by the largest contribution any dropped small term could
   have made, so dropping can only weaken it;
6. rebuilds the cut in original space and requires it to reproduce its own
   unit violation there, rejecting it otherwise;
7. rejects the cut outright if a known incumbent violates it.

Per round the separator returns at most `min(16, max(4, rows/8))` cuts, drops
cuts nearly parallel to one already selected, and enforces support, dynamism
and efficacy limits. After the last round, any tableau cut whose logical is
basic in the final root relaxation is removed: it is not binding there, its
dual is zero, so the point and the bound are unchanged and the tree stops
paying for the row.

Defaults are unchanged. Nothing runs in the tree; this is a root separator.

## Why the cuts are believed valid

A wrong cut removes the optimum and returns a confident wrong answer, so
validity is gated before any benchmark:

- `tests/test_gomory_cuts.cpp`, run by CTest as `gomory_cut_validity`:
  3,000 random all-integer models with small explicit boxes, where every
  integer point is enumerated and every returned cut checked against all of
  them; the strengthened relaxation is re-solved and must not pass the
  enumerated integer optimum; and 400 mixed models where each cut is
  *maximized* over the continuous variables with the integers fixed, one LP
  per assignment, which is an exact test over the whole mixed region.
- The derivation is floating point and is not claimed to be certified. The
  runtime checks above (unit-violation rebuild, incumbent rejection) and the
  independent HiGHS objective comparison on every benchmark record are what
  stand behind the answers.

## Profiles

- Control: the iteration 31 promoted profile
  (`reports/milp-iteration-31/CANDIDATE_PROFILE.json` `recommended_flags`).
- Candidate: control plus `--gomory-cuts`, a single-flag ablation.

Serial runs, rotating profile order, 30 s, gap 1e-6, node limit 100,000,000,
45 s watchdog, 1536 MiB sampled commit threshold, same executable for both.

## Model sets

1. Development: the 27 reused models, two repeats per profile. Two repeats
   because iteration 31 showed single-repeat differences on `danoint` that
   were run-to-run variation, and this host's node counts vary by 40 percent
   between identical runs.
2. Fresh holdout: 10 public MIPLIB 3 models never downloaded or solved by this
   project, declared in `HOLDOUT_SELECTION.md` before download. This set is
   deliberately hard and may return few completions in either profile; it is a
   generalization and safety check, not the primary discriminator.

## Validation

Every record is checked against HiGHS 1.12.0 on the original model (5 s
development references, 30 s holdout references), with the existing
work/frontier/cut/pump/bounded/search-heuristic checks and a new
`check_gomory_cuts.py` accounting check. The local correctness gate (CTest,
28 tests including the new enumeration test, plus the sparse accuracy gate)
runs and passes before any timed comparison.

## Decision rule

Promote the candidate only if, against the control:

- zero validation failures in either set, and no record where our objective
  disagrees with an independently proven HiGHS optimum;
- development completions do not fall across the two repeats;
- development checked-point coverage does not fall;
- the root bound improves on more models than it worsens;
- the holdout shows no new failure, crash, memory-guard stop or rejected
  point.

Any model that differs between the two repeats is named as variable rather
than counted as an improvement or a regression. Executable defaults stay
unchanged whatever the outcome. Report every regression, including models
where cuts consumed budget and produced nothing.
