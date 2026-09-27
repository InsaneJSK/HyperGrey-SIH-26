# Current-source LP and convex-QP validation

17 September 2026. The iteration 29 executable completes all 12 retained
Netlib LPs in both tested profiles and three of four additional LPs in each.
All three default QPs pass the declared independent relative KKT checks.
The additional `bandm` LP exposes a retained default-path numerical failure;
QP 9002 still has a material absolute residual. This is checked coverage on
a small public set, not submission readiness or a matched-accuracy speed ranking.

## Protocol and identity

[PLAN.md](PLAN.md) declares the model sets, profiles and budgets before their
outcomes. The binary SHA-256 is
`b0f2c51eba65cd9a4ff8ad3817dfe289eae90823a7bb8f749185bbb7249df2dc`.
Each own solve has 30 seconds, a 45-second external watchdog and a sampled
1536 MiB process-commit threshold. LPs retain the 10000-pivot cap. Configurations
run serially; independent references run afterward and never feed search.

LP validation uses original rows and bounds, objective reconstruction,
native optimality verification and a separate HiGHS optimum. The acceptance
checks use scaled feasibility at 1e-8 and objective agreement at 1e-6 relative
scale; own LP tolerance remains 1e-9. QP checks use original QPLIB coefficients,
independent KKT checks at 1e-7 and the applicable diagonal dual certificate.
OSQP runs on original QP data with its separately documented 30-second protocol.
These different accuracy contracts do not support a fair speed ranking.

## LP results

| Cohort | Default checked completions | Refined checked completions |
|---|---:|---:|
| 12 retained Netlib LPs | 12/12 | 12/12 |
| Four additional LPs | 3/4 | 3/4 |

The additional models are `agg`, `bandm`, `israel` and `scagr7`, selected before
their solves from the [official Netlib archive](https://netlib.org/lp/data/readme).
They are reported separately from retained development inputs. This small
addition does not establish broad unseen industrial coverage.

Both default and refined `bandm` calls return `numerical_error` after 200
pivots, with no point or objective. HiGHS independently completes at
-158.62801845012078. The solver does not falsely claim an optimum. A subsequent
[bounded representation study](../lp-bandm-01/REPORT.md) finds an existing
compact-equality profile that completes all 16 LPs. That later profile score
does not replace the default failures or repair their source-level cause.

## QP results and accuracy limits

| QPLIB/profile | Native status | Maximum absolute violation | Scaled violation | Independent KKT pass | Completed reference comparison |
|---|---|---:|---:|---|---|
| 8792/default | optimal | 1.11e-16 | 4.71e-17 | Yes | Yes |
| 8991/default | optimal | 0 | 0 | Yes | Yes |
| 9002/default | optimal | 2.38102249 | 8.57e-8 | Yes | No: OSQP time limit |
| 9002/tolerance 1e-10 | time_limit | 0.22181812 | 3.81e-6 | No | No |
| 9002/tolerance 1e-12 | time_limit | 0.22173449 | 3.79e-6 | No | No |

Default 9002 has independent relative stationarity about 2.41e-16 and relative
diagonal dual gap 7.85e-11. Its relative certificate does not establish an
acceptable absolute violation in unspecified operational units. Both tighter
tolerance probes reduce the maximum absolute violation but worsen scaled
feasibility and stationarity (about 3e-5). Both hit the time limit and fail the
independent KKT/diagonal acceptance check; a small dual gap alone is insufficient.
Neither probe is selected as an improved accuracy profile.

The 9002 original-data OSQP run again reaches its 30-second limit. Its partial
objective is not an optimum or a finite speedup denominator. The two probes
explicitly reuse this same-model reference status, with provenance, and receive
fresh per-point original-model KKT checks. The audit retains the 92 Hessian
discrepancies in the official LP export; original QPLIB data remain authoritative.

## Evidence and retained setup failures

[MODEL_LEDGER.md](MODEL_LEDGER.md) covers all 37 observations. Raw commands,
vectors, stdout/stderr, reference/KKT records, source identity, input snapshots,
dependency versions and resource observations are under [results](results/SUMMARY.json).
No native completion fails its declared independent check. The four honest
noncompletions are two `bandm` numerical failures and two 9002 tolerance limits.
Peak sampled working set is 15.668 MiB and peak commit is 12.203 MiB for this
small study; these are observations, not general capacity guarantees.

The first EMPS decoder check failed because checkout CRLF bytes differed from
the retained source hash. A separate LF copy matches the original hash; its
source, compiler log and raw/decoded data hashes are retained. A restricted
network attempt then failed; the approved download succeeded. Initial logs and
the first script remain available. QPLIB snapshots restore original manifest
LF bytes without modifying working input files or weakening hash checks.

## Next numerical work

Keep the default `bandm` fixture for tracing the standard equality formulation's
numerical rejection, and evaluate the compact profile on broader LPs before
changing defaults. For 9002, trace the specialized-method accuracy floor and
its fallback behavior before another tolerance policy experiment. Broader QP
structures, domain tolerances, equal-accuracy comparisons and actual GPU
measurements remain open. No LP/MILP GPU claim follows from these CPU results.
