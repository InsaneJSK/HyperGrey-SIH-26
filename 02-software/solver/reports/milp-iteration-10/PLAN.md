# Iteration10: reduced-bound LPs and submission assessment

Keep iteration09 immutable. Test removal of propagation-introduced upper-bound
rows for originally upper-unbounded continuous variables, in main-tree LPs only.
Preserve all original finite bounds and integer branch decisions. Treat the
smaller LP as a relaxation: a returned optimum must also pass full-node primal
checks; its dual extends by zeros on omitted bounds. Retry the full LP on any
failed full-node check, relaxed unboundedness or numerical failure, using only
remaining time. Do not report a relaxed ray as full-node unboundedness.

Unit/adversarial/generated gates first, then root screens and equal-budget
local comparisons. Test delayed activation to preserve incumbent search.
Audit saved original-model points and retained cuts after timings. No new
exact MILP proof claim without a complete valid certificate. Finally assess
submission strength against the supplied PS and existing CPU/GPU evidence,
without inventing rankings or completion percentages. CPU only, no upload.
