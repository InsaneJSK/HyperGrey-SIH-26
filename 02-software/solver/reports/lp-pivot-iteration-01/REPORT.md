# Opt-in stable primal ratio: retained LP failure resolved under the new profile

17 September 2026. `--stable-primal-ratio` completes all 16 public LPs, both
alone and with refinement, with independent original-model checks. It resolves
the retained standard-form bandm failure under these explicit profiles.
Defaults remain unchanged; default/refined bandm still return numerical error.
The safeguard is experimental and has no measured broad MILP performance claim.

## Change and evidence-selected scope

The [preceding diagnosis](../numerical-diagnosis-01/REPORT.md) captures an
exactly singular basis following an inaccurate small pivot. Refreshing the
basis alone fails later. A two-pass ratio rule succeeds; applying it only when
the original selected pivot is weak preserves other tested LP pivot counts.
The integrated change uses that selective rule and no other numerical policy.

The option retains ordinary ratio choices unless the pivot is at most
1e-7 times one plus the direction infinity norm. It then favors a larger
pivot within the step allowance defined by the existing feasibility tolerance.
Bland's cycle fallback and all final original-model checks remain unchanged.
See [the method and limitations](../../docs/PRIMAL_RATIO_STABILITY.md).

The exact final CLI SHA-256 is
`070878750efa73d39aa2815075132212c70f1cbbafd9528f8c2875db3b15cb68`.
No reference solver is linked into the numerical core or supplies search
points/bounds. The LP options can reach MILP sparse relaxations, but a public
MILP search study is deferred; do not silently add this option to the older
frozen staged profile or reuse its 26/27 score as a new-binary result.

## Final executable checks

| Profile/cohort | Checked completions | Outcome |
|---|---:|---|
| Stable ratio alone, 16 LPs | 16/16 | All original-model checks pass |
| Stable ratio plus refinement, 16 LPs | 16/16 | All original-model checks pass |
| bandm default/refined controls | 0/2 | Retained numerical errors at 200 pivots |
| bandm compact/refined control | 1/1 | 1279 pivots; checked optimum |
| Three unchanged default QPs | 3/3 | Relative KKT/applicable diagonal checks pass |

Both standard-form stable bandm calls take 3254 pivots. Objectives are
-158.62801845012092 and -158.62801845012072, agreeing with the independent
reference. Maximum absolute violations are about 8.00e-13 and 1.42e-13;
scaled violations are about 2.11e-15 and 2.57e-16. Compact equality remains a
successful separate profile; the new option is not claimed fastest or best
for every input.

All 38 observations are in [MODEL_LEDGER.md](MODEL_LEDGER.md). The 36 completed
points pass the reviewed acceptance checks; the two retained no-point controls
remain numerical errors. Each own solve uses 30 seconds, the LP 10000-pivot
cap, a 45-second watchdog and sampled 1536 MiB commit threshold. Configurations
run serially, with independent LP references afterward. This is correctness
and numerical-robustness evidence, not a matched-accuracy speed ranking.
Peak sampled working set is 19.414 MiB and peak commit is 16.266 MiB for this
small validation set, not a general capacity guarantee.

QP numerical sources are byte-identical to frozen 29. Fresh original-model
checks reproduce all three default KKT results; 9002 still has about 2.381
maximum absolute violation and only the declared relative acceptance contract.
No new external QP solve or GPU execution was performed. Prior OSQP timeouts
and the diagnostic tight-tolerance failures remain applicable historical
evidence, not new completed head-to-head comparisons.

## Correctness gate and retained harness corrections

- 27 CTest groups pass, including selection edge cases, 512 generated
  step-feasibility checks and four retained LP modes with zero budgets.
- 176 Python gate tests, 400 generated MILP runs across five profiles and
  100 retained exhaustive cases pass.
- Four feature-off fixed-work comparisons match the frozen control semantics.
- The new stable-only generated profile and three refined profiles enable the
  safeguard; the baseline remains off. Output option markers are checked.

The first build emits a test-only narrowing warning. Changing an integer
literal to a double literal removes it without changing test values or the CLI
binary; the rebuilt focused CTest passes. Original build and gate logs remain.

The initial validation runner incorrectly required a diagonal certificate on
8792 and 8991, where that optional checker does not apply. Their independent
KKT checks already passed. `review_qp_applicability.py` verifies each original
Hessian's structure and recomputes the identical KKT checks at the same
tolerance. The reviewed ledger requires the diagonal bound only when it is
applicable. Original vectors, checker results, initial ledger/summary and
the executed `validate.initial.py` remain; `validate.py` is corrected for future
runs. Use [REVIEWED_SUMMARY.json](validation/REVIEWED_SUMMARY.json) for the final
classification. No solver rerun, tolerance relaxation or changed point was used
to repair this reporting error.

## Decision and next work

Retain the new safeguard as an explicit opt-in LP profile. Freeze this binary,
source, dependencies, commands, inputs and reports. Broader LP structures,
transformations and a declared MILP performance comparison are needed before
default/profile promotion. The older compact LP and staged MILP profiles remain
separately labeled; no best-of-profile union is reported.

Next diagnose QP 9002's line-search and active-set oscillation using objective
differences and directional derivatives, before changing its algorithm. Advance
industrial what-if, CLI/API demonstration and the CPU-validated GPU-only package
as separate submission tracks. Domain tolerances and organizer deliverables
remain external inputs. Overall submission readiness is still incomplete.
