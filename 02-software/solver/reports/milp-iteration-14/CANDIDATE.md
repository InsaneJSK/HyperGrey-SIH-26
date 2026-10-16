# Predeclared candidate after phase diagnostics

Only the root-cut round allowance changes: candidate1 versus legacy5 per root
(including the one existing full-domain restart). This is a call/round cap,
NOT a hard cap on LP pivots, factorization work, elapsed time or total memory.
Keep pump, dives, neighborhoods, feasibility/gap tolerances and proof rules.
Add CLI counter-only restart control for reproducibility tests, not the timed
candidate profile. Both options preserve defaults when not specified.

Reason: the Binkar diagnostic spends13.80s in5 cut LPs, versus4.28s in215 tree
LPs. It returns6810.690026 with2.2682% reported gap at30s. The four other no-point
diagnostics have different bottlenecks; this candidate is NOT expected to fix
all of them. No completion or improvement is assumed from the diagnosis.

Protocols, run sequentially with independent work after own timings:

1. 30s target pair on binkar10_1, mod008, p0282. Baseline5 versus candidate1.
2. If correctness passes, retain the same candidate in a30s pair on all21 saved
   public cases. No tuning from this wave and no rebranding old holdouts.
3. Three new rotated30s pairs on Binkar to test whether the hypothesized benefit
   repeats. Keep no-point and worse-gap runs. Both profiles capture phase totals;
   these are instrumented comparisons, not clean uninstrumented speed claims.
4. Final12-group C++ gate, Python checkers,80 generated MILPs across rounds0/1/5,
   reused100 exact-enumerated MPS cases, parser and frontier checks. Compare
   capture on/off and legacy13 under deterministic node limits.

No external incumbents, named-model solver rules, GPU, or accuracy relaxation.
No general cut-strength or arbitrary MILP proof claim is added this iteration.
