# Iteration 12 — guarded objective-lattice bounds (predeclared)

CPU only. Preserve iteration11 and use a separate build-milp-iter12.
The candidate is opt-in; the control uses the same binary without that flag.
No reference objectives, names or solutions enter the solver.

1. Detect an objective lattice from exactly represented integral objective
   coefficients on integer variables. Permit continuous objective variables only
   through checked unit-coefficient defining equalities whose other variables
   are integer. Check every integer accumulation/product for overflow.
2. Support checked dyadic offsets, negative/zero coefficients and both senses.
   Unsupported structures retain the previous numerical bound. Never round
   unchecked LP outcomes, heuristic fixing objectives or incumbent values.
3. Round only existing validated, safety-adjusted minimization lower bounds,
   with an additional outward arithmetic margin and downward publication.
   This is numerical bound strengthening, NOT an exact rational LP certificate.
4. Test structural guards, near-grid arithmetic, generated exhaustive min/max
   cases, partial outcomes and independent original-model point checks first.
5. Screen mod008 and misc03 at 30 seconds. Then retain all 17 wave1 models in
   matched 30-second control/candidate runs; alternate profile order. Repeat
   the two targets three times separately. Run references only after timings.
6. Independently check recorded substitutions and rounding events using Python
   rational arithmetic and the HiGHS model reader. Keep all limits, regressions
   and validation failures. Freeze binary/source/checkers and report evidence.

Success is valid general-purpose strengthening and measurable proof closure,
not an all-public-MILP or top-percentile claim. Broader holdouts and remaining
search/LP weaknesses remain separate next work after this bounded experiment.
