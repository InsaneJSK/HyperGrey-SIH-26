# Stable primal ratio selection after the refresh-only failure

The first candidate postpones bandm's failure from 200 to 273 pivots but does
not complete it. Even immediately after a fresh factorization it chooses a
2.2347560885149775e-9 pivot whose basic value is approximately -7.83e-16.
The next basis point violates nonnegativity by about 1.045. Keep that candidate
rejected; it is insufficient as a source fix.

Test a separate candidate from the original diagnostic source, replacing only
the primal ratio selection with a two-pass stability rule. First bound the
step using (max(0, x_i) + tolerance) / d_i for the existing eligible positive
directions. Then choose the largest direction among rows whose unrelaxed step
is within that bound, breaking equal-pivot ties by basic column index. Retain
the original minimum-ratio rule once Bland's cycle fallback is active.

This uses the existing feasibility tolerance only during pivot selection;
the intermediate rejection and original-model terminal checks are unchanged.
It does not round model data or declare an infeasible point optimal. No fresh
basis-refresh policy from candidate one is included, so effects remain distinct.
Harris' two-pass ratio test is established simplex numerical practice; see
[Huangfu and Hall, section 2.2.2 and reference 12](https://www.maths.ed.ac.uk/hall/HuHa13/ERGO-14-011.pdf).
Our code is independently written from the mathematical rule.

Run the same 18 LP observations (all 16 default inputs, plus bandm refined and
compact/refined) and original-model checks. Require 18 checked completions
before pursuing production integration, then dedicated edge/degeneracy tests
and the full gate. Passing this screen alone does not justify changing MILP
defaults or claiming broad robustness/performance.
