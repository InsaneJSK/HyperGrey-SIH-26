# Untouched-model selection, declared before download or solve

17 September 2026. Select six public historical MIPLIB models: `vpm1`, `vpm2`,
`bell3a`, `bell5`, `gesa2`, `noswot`. None is in the 27-model development suite
or present among local MPS files. A search of retained report JSON/Markdown
(excluding copied source/gates/manifests) found only a prior attempted `gesa2`
metadata lookup; iteration18 explicitly says it was not downloaded or solved.
No solve outcome for these six was inspected to select this set.

Download original MPS archives from the same public historical MIPLIB index
already retained in `datasets/miplib/index.html`. Keep download failures in the
ledger, verify bounded size, preserve archives and record exact hashes. Inspect
structure/scaling after selection without changing the set based on outcomes.
Related pairs vpm1/vpm2 and bell3a/bell5 are not four independent families.

Select the retained release profile from development evidence before running
these models. Fixed source/binary, one initial 30-second run per model, 250000
nodes, 1e-6 relative MILP gap. Run serially. Use separate 30-second, one-thread
HiGHS references at the declared tighter validation accuracy; report accuracy
and budget differences explicitly, avoiding speedup claims from limits.

This moderate historical set is not evidence for arbitrary industrial scale.
Supplement with bounded transformed correctness fixtures for degeneracy,
scaling/ill-conditioning and weak relaxations; report these as artificial
stress tests, separately from the untouched public score. Once any result
influences tuning, the affected public cases become development data.

The final development-suite recheck and release/resource decision are separate
from this holdout score. No automatic promotion at iteration28.
