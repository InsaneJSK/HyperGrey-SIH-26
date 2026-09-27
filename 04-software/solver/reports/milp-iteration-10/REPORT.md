# MILP iteration10 — guarded reduced-bound LPs

15 September 2026. Separate CPU build `build-milp-iter10`, SHA256
`3cac5f39d5f2546006cb3bd5788ff0e44245ceaab282e86b8a4caf5062295eeb`.
Completed local CPU experiment. The new opt-in mode improves Binkar's numerical
bound and completes Blend2 to its gap tolerance in the fresh paired protocol.
Three repeated Binkar root pairs reproduce the reduction in rows and time.
Binkar is still NOT proved optimal, and the full-solve comparison has one
repetition per profile, not a broad or statistically established speedup.

## Change and safety contract

The main MILP LP helper can omit propagation-introduced upper-bound rows for
originally upper-unbounded continuous variables. Original finite domains,
integer branch decisions, lower bounds and every model row are retained.
The smaller model is treated as a relaxation, not assumed equivalent without
checks: a returned optimal point must pass all FULL-node rows and bounds, in
addition to the existing numerical primal/dual/gap checks. Its dual extends
with zero multipliers on omitted bounds. An infeasible relaxation implies an
empty full node, but a relaxed unbounded ray does not certify the full node.
Failed full-node checks and unbounded/numerically failed reduced attempts
retry the full LP within the remaining time.

`--late-reduced-bound-lp` preserves the established early search and activates
at the existing half-time full-domain cut restart, with compact equations.
Incumbent, valid global bound and spent time/node/search budgets are retained.
Private heuristic/fixing/strong-branch paths remain on their established LP
formulations. Both immediate and delayed modes stay opt-in. The prior exact
proof engine and standalone LP/QP numerical routines are unchanged.

See [method, counters and reproduction](../../docs/REDUCED_BOUND_LP.md).

## Root screen

One node, no heuristics, compact equations in both profiles, same binary and
60s limit. These are not full solves and have no integer incumbent.

| Binkar mode | Canonical rows after root cuts | Bound | Seconds |
|---|---:|---:|---:|
| Compact control | 3342 | 6645.940875 | 6.5962 |
| Compact plus guarded bound reduction | 1214 | 6645.940875 | 2.4600 |

2128 upper-bound rows are omitted; all five root LP attempts are accepted by
the full-node gates, with no fallback. P0033 has no eligible continuous bounds
and retains its root bound and 72 canonical rows.

A separate [three-pair repeat](root-repeats/results.json), with alternating
order, gives control times 6.6474, 6.7052, 6.7029s and reduced times 2.4653,
2.7217, 2.4622s. Median time drops 6.7029 to 2.4653s (2.72x ratio). All six
have the same bound and respective row counts, and reduced attempts have no
fallback. This is repeated ROOT-screen evidence, not full-MILP acceleration.

## Full solves — fresh equal-budget comparison

Both profiles use delayed lifted covers and compact equations; only the
candidate adds `--late-reduced-bound-lp`. Same binary, 180s budget, 250000-node
cap and requested gap 1e-6. Runs are sequential, alternate profile order by
model, and use no external incumbent. Reference checks run after all timings.
The solver's reported gap is `(incumbent - bound)/(1 + abs(incumbent))` for
these minimization models; it is not necessarily another solver's convention.

| Model / profile | Objective | Lower bound | Reported gap | Seconds | Status |
|---|---:|---:|---:|---:|---|
| P0033 control | 3089 | 3089 | 0 | 0.0878 | optimal |
| P0033 reduced | 3089 | 3089 | 0 | 0.0798 | optimal |
| Binkar control | 6747.310015 | 6683.003921 | 0.95292% | 180.4697 | time_limit |
| Binkar reduced | 6747.310015 | 6685.681835 | 0.91324% | 181.0222 | time_limit |
| Blend2 control | 8.015188 | 7.593468 | 4.67789% | 180.0273 | time_limit |
| Blend2 reduced | 7.598985 | 7.598984 | 0.000010% | 144.0356 | gap_limit |

Binkar processes 10705 nodes versus 6061, retains the same incumbent, and
accepts 8444 reduced LP attempts without fallback. Its better numerical bound
is useful, not proof of optimality. The prior iteration09 600s run still has a
slightly better bound (6686.056417); unequal budgets are not a speedup comparison.

Blend2 accepts 12073 reduced attempts and safely retries the full LP three
times. Its final original-model violation is about 4.55e-13. Objective 7.598985
matches the independently established iteration04 reference; the current
post-timing audit independently checks the point but does not rerun a full
public reference optimization. Iteration04's different protocol took 114.53s,
so this is a win against today's matched control, NOT a new fastest-ever
Blend2 result. P0033 completes before delayed activation and is a nonregression
sentinel, not evidence that reduction accelerates pure binary models.

Time limits are cooperative: actual wall time can exceed the nominal budget
slightly. Unfinished live search on Binkar/control Blend2 is reported as a
limit, not falsely closed.

## Correctness gates

- CTest 8/8, including 200 new generated MILP comparisons, full-node/domain
  safeguards, false relaxed unboundedness, genuine full-node rays, empty
  relaxations, warm-mode crossing and delayed min/max activation.
- Independent HiGHS mixed-model checks 80/80, with 127 accepted reduced LPs
  and no fallback. These generated cases actually have continuous columns
  without original finite upper bounds. Both minimization and maximization
  are covered. They are not public industrial cases.
- The retained 240 generated profile checks pass: 80 models under three
  profiles, not 240 distinct public benchmarks. Many have finite original
  bounds and primarily check nonregression rather than the new reduction.
- Markshare's independent original-literal exact-proof sentinel passes after
  the root screen, full pair and root repeats. It does not establish Binkar optimality.
- Fresh [public-run audit](paired-audit/AUDIT.json): 49 retained lifted cuts
  rechecked using Python integer arithmetic on parsed binary64 data; 24 saved
  final/restart/neighborhood/repair vectors pass independent original-model
  bounds, rows, integrality and available objective checks. All 83 recorded
  timing-source hashes and the binary identity match. This audit does not
  independently certify every internal LP dual bound or unsaved intermediate point.
- [Application checks](application-checks/SUMMARY.json): all four preserved
  application models pass in both profiles, including completed HiGHS objective
  comparisons, original-row checks and the tighter-sulfur scenario ordering.
  The MARCO cases omit 46 rows each, transport 6, lot sizing 0. LP examples
  intentionally use the MILP facade to exercise this helper. These are literature
  teaching/synthetic models, NOT MRPL production or domain-expert validation.
- [Control nonregression](CONTROL_NONREGRESSION.json): all 80 generated models
  match iteration09's delayed-compact profile on status, objective, primal,
  bound, gap, nodes and LP iterations. Timings/new diagnostics are excluded.
- Final CTest 8/8 and checker/parser unit tests 33/33 pass. The new C++ group
  exercises 412 accepted reduced LPs across its 200 mixed-MILP comparisons.

## Decision and next work

Keep the method available as an opt-in candidate; do not change defaults based
on a small public subset. The implementation retains explicit safety gates and
versioned fallbacks. The most useful next CPU cycle is a predeclared broader
hard-MILP suite with repeated equal-budget comparisons, including both wins
and timeouts, followed by profiling the persistent Binkar proof gap. Domain
validation and a final reproducible submission demo remain separate priorities.

## Evidence and submission meaning

[Root protocol/results](root-screen/results.json),
[independent mixed checks](independent-mixed/SUMMARY.json),
[full comparison protocol](paired-180s/metadata.json),
[raw full results](paired-180s/results.json).
The [submission assessment](../../docs/SUBMISSION_ASSESSMENT.md) separates
demonstrated engineering/correctness from industrial readiness and ranking.

No external incumbent or published answer enters the algorithm. General
LP/MILP bounds are numerical, not exact rational proofs. This is local CPU work;
no GPU/Kaggle run, notebook or user upload is needed. Earlier binaries and
evidence are preserved unchanged. The [final state](FINAL_STATE.json) and
[snapshot manifest](SNAPSHOT_MANIFEST.json) identify the archived binary/source.
