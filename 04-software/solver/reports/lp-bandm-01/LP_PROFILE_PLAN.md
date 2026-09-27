# One LP profile across all sixteen cases

Declared after the six bandm diagnostics pass four compact configurations.
Evaluate one explicit profile, `--compact-equalities --refine-basis
--refine-at-checks`, on all12 retained and four additional LPs, in the existing
manifest order. Use the unchanged iteration29 executable,30-second native
budget,45-second watchdog and1536MiB sampled process-commit threshold. Run
own solves serially, then references. This is a correctness/coverage check,
not a matched timing comparison to earlier measurements.

Require independently checked original points, objective reconstruction,
reference objective agreement and native numerical verification for every
completed result. Save each failure and fallback. If all pass, document this
as an explicit LP evaluation profile; leave defaults unchanged. Do not claim
the default bandm defect is repaired or construct a union of per-model flags.
