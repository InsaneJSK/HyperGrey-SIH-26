# Bandm diagnosis and a consistent compact-equality LP profile

17 September 2026. The existing options
`--compact-equalities --refine-basis --refine-at-checks` complete all 16 LPs
with independent checks on the unchanged iteration 29 executable. This is one
consistent, explicit LP evaluation profile. Defaults remain unchanged; the
standard sparse path's `bandm` numerical failure remains unresolved.

## Bounded diagnosis

The preceding [current-source check](../cpu-validation-2026-09-17/REPORT.md)
finds `bandm` failing after 200 pivots in both default and refined modes.
[PLAN.md](PLAN.md) then declares six existing-option comparisons with 30-second
solver limits, 10000 pivots, 45-second watchdogs and references afterward.
No numerical source change or reference answer enters these solves.

| Additional profile | Result | Pivots | Independent completion check |
|---|---|---:|---|
| Unscaled sparse | numerical_error | 350 | No point |
| Compact | optimal | 1279 | Pass |
| Compact, refined | optimal | 1279 | Pass |
| Compact, unscaled | optimal | 1518 | Pass |
| Compact, unscaled, refined | optimal | 1518 | Pass |
| Dense | iteration_limit | 10000 | No point |

All four compact results agree with the independent objective
-158.62801845012078, with maximum absolute violation at most 8.25e-13.
This localizes a useful representation choice, without proving the internal
cause of the default numerical failure. Dense fallback is not a demonstrated
completion remedy under the declared cap. All raw records are retained in
[results](results/SUMMARY.json).

## Full explicit-profile check

[LP_PROFILE_PLAN.md](LP_PROFILE_PLAN.md) declares the same compact/refined
flags for every one of the 12 retained and four additional LPs before this
follow-up runs. All 16 complete and pass original-model feasibility, objective
reconstruction, native verification and independent HiGHS comparison, under
the same LP acceptance contract as the preceding study. `degen2` exercises
the implementation's existing compact fallback and also passes. Its fallback
is reported, not silently substituted with a separate best-performing solve.

The binary SHA-256 is
`b0f2c51eba65cd9a4ff8ad3817dfe289eae90823a7bb8f749185bbb7249df2dc`.
Use [LP_PROFILE.json](LP_PROFILE.json) for the precise flags and
[MODEL_LEDGER.md](MODEL_LEDGER.md) for all 16 outcomes, residuals, pivots and
memory. Commands, raw output, watchdog data and reference results are in
[lp-profile](lp-profile/SUMMARY.json). The default and refined comparison
profiles each remain 15/16; the explicit compact profile is 16/16. These are
separate results, not a best-of-profile union.

From the inner project directory, after freezing iteration 29:

```powershell
reports/milp-iteration-29/final_solver_cli.exe reports/cpu-validation-2026-09-17/results/inputs/additional-lp/bandm.mps --json --time-limit 30 --compact-equalities --refine-basis --refine-at-checks
```

This small related public set does not establish general numerical robustness,
industrial scale, MILP benefit or a speed ranking. Retain the explicit profile
for reproducible LP evaluation; investigate the standard-path rejection and
add larger/difficult LPs before any default promotion. No acceptance tolerance
was relaxed and no earlier failed result was overwritten.
