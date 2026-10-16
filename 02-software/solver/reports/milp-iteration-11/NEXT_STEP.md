# Next robustness cycle — proof closure across families

Do not remove any of the 17 first-wave cases. The domain-default bug takes
precedence over performance tuning and is corrected in iteration11.

The baseline distinguishes two needs:

- `mod008` (307) and `misc03` (~3360) already have independently checked points
  matching completed HiGHS optima, but our bounds remain open at 30s. Improve
  the general proof machinery; do not feed the reference objective into it.
- `gt2`, `p0282`, `misc07`, `pk1` and Binkar need better points and/or bounds.
  Blend2 has no incumbent under this 30s policy, even though a different 180s
  protocol previously completed it. Short-run policies need explicit testing.

First bounded candidate: guarded objective-lattice bounds. When structure and
exactly represented coefficients prove the objective lies on a known lattice,
round an already validated numerical lower bound outward to the next possible
objective value. Investigate pure/general integer objective terms first;
continuous objective terms must disable this unless a separately checked
derivation establishes the lattice. No instance-name recognition, no published
objective, no unsupported rounding of fractional coefficients. This remains
numerical MILP proof unless a fully exact global certificate is available.

Required guards: minimization/maximization, objective offsets, zero and negative
costs, mixed continuous terms, overflow/large magnitudes, bounds near a lattice
point, partial/time-limit states, and saved original-model witnesses. Compare
against complete tiny enumeration and independent references before public use.

Then repeat the SAME public budgets/profile pairs, keep regressions, and add a
predeclared holdout wave with different structures. Stronger mixed-integer cuts,
LP stability and search policies follow the observed failure map rather than
adding feature names. Full MIPLIB coverage is a target with a resource envelope,
not a claim already achieved by these 17 models.
