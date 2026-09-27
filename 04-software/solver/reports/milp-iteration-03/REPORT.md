# MILP iteration 03 — LP recovery and incumbent improvement

Update 15 September 2026: the [Kaggle return is now audited](../kaggle-milp-02/REPORT.md).
The incumbent gain reproduces on binkar; blend2 recovery works but still finds no
incumbent, and markshare is unchanged. The experiment description and pre-return
local evidence below remain historical; no unchanged-notebook rerun is needed.

Implemented opt-in `--lp-recovery`, `--improve-incumbent`, and
`--capture-lp-failure`. Fractionality remains default; reliability was not
promoted. Existing LP/QP/CUDA algorithms and original absolute MILP candidate
tolerances are unchanged. See `docs/MILP_RECOVERY_METHOD.md` for budgets,
proof accounting, diagnostic limitations, and algorithm background.

## Final-source correctness and short hard-case gate

Final build: `build-milp-iter3`, CLI SHA-256
`ae6d294de68e932ae3c48ea784a34651a040cc530f1e91540eab0ad96e88e19f`.
All three CTest groups pass, including new regressions for unresolved roots,
deferred children with retained bounds, recovery success, invalid rounded
repairs, neighbourhood improvement, maximization and zero-budget/disabled modes.

`final-smoke/` passes 240/240 generated checks: 40 exhaustive binary and 40
independently checked mixed/general-integer cases each for control,
recovery-only, and the combined mode. Six equal 15-second/250,000-node hard
runs produce four independently verified incumbents and no invalid candidate
or error status. All six are time-limited, not hard optimum completions.

| Model | Control objective | Recovery + neighbourhood objective |
| --- | ---: | ---: |
| markshare_4_0 | 20.999999976 | 20.999999976 |
| blend2 | None | None |
| binkar10_1 | 7297.320029 | 6810.690026 |

binkar reported gap drops from 8.8011% to 2.2929%. The new mode records a
checked post-pump improvement; the independently measured maximum absolute
row/bound violation is 7.00000001e-9 and integrality violation is zero. The
reference processes in the 15-second solver gate only parse/check candidates; they have zero
optimization time and do not establish reference optima.

## Final-source extended blend2 check

`final-blend-90s/` repeats the generated 240/240 and CTest 3/3 gates, then runs
the control and combined mode with the same 90-second/250,000-node limits.
Control again stops early: 33.49 seconds, 3,762 nodes, `iteration_limit`, lower
bound 7.468466152. The combined mode reaches the global time limit at 90.03
seconds and 8,170 nodes, with lower bound 7.564874474. It recovers three of
three failed LPs in 0.1817 seconds of recovery work, and retains two rejected-
repair nodes as unresolved. There is no numerical-error abort in this run.

Neither mode finds a valid incumbent. The independent reference solves blend2
to 7.598985. The new bound stays below that optimum, and no finite MILP gap or
feasible solution is claimed. This demonstrates continued search and better
bound progress in this run, not completion of blend2. No unsafe/error run is
reported in the final extended gate.

## Preserved initial 60-second experiment

`local-60s/` uses the initial iteration-03 binary
`70d0172b83ded21a593d31fba43705a194c19e35f8792a70b562904cab2db789`,
preserved as `initial_solver_cli.exe`, with changed numerical source preserved
as `initial_milp_v2.cpp`. This is not silently relabeled as the final source.

| Model | Control | Initial combined mode |
| --- | --- | --- |
| markshare_4_0 | Objective ~8, gap 88.89% | Same objective/gap |
| blend2 | No incumbent; iteration limit at 32.03 s | Cold recovery succeeds, then invalid rounded repair stops at 53.61 s |
| binkar10_1 | 7297.320029, gap 8.7018% | 6789.670035, gap 1.8864% |

All four incumbents pass independent original-MPS checks. binkar's new mode
improves its incumbent twice through neighbourhood search; this is promising
but a single timing pass, not a general speedup claim. Its 10-second reference
times out with incumbent 6746.760023; that value is not a proven optimum.

The initial gate deliberately fails overall due to blend2's numerical-error
exit. Its raw files and failed summary remain intact. A near-integer LP point
failed the original absolute check by about 2e-6, and the exact-fixing repair
also failed. The final change keeps such a node unresolved with its checked
LP bound and continues other tree work. It does not accept that point, loosen
tolerances, or call an incomplete node infeasible. A dedicated regression
exercises this failure path.

## Captured LP diagnosis

The first failing blend2 relaxation is node 4615, depth 19, input basis with
353 structural columns. The warm run reaches 10,000 iterations. Fresh solves
of its captured continuous model reach objective 7.7347385328076:

- Own sparse simplex: 513 pivots, 0.0863 s.
- Own dense simplex: 546 pivots, 0.5894 s.
- Independent HiGHS: optimal objective 7.7347385328072.

This supports cold recovery, but does not identify the exact warm-pivot stall
mechanism. The stored basis is the input basis; the cold diagnostic does not
replay its pivot sequence. Full checked diagnostic is `lp-diagnostic-checked/`.
The first diagnostic attempt omitted the reference worker's required candidate
argument; its process error remains in `lp-diagnostic/`. The helper was fixed
and rerun in a new directory; this was a harness error, not a solver result.

## Kaggle handoff and remaining work

Separate delivery: `kaggle_delivery/milp_iteration_03`. Two small code cells,
matching external private-input ZIP, current Kaggle Python/pip/subprocess, no
second environment, no manual paths and no GPU quota. Six hard runs compare
control with recovery + neighbourhood at identical 180-second/250,000-node/gap
limits; generated checks include a recovery-only correctness ablation.

Return `sih26119_milp_results.zip`, even if a notebook stage fails. It contains
incumbent traces, original candidate checks, recovery counts/time, deferred
nodes/global bounds and the first failing LP model/input basis when available.
The importer recognizes this experiment separately from the old branching run.

The final 180-second Kaggle comparison has not run yet. No hard-case optimum,
repeatable overall improvement, broad industrial robustness, or top-percentile
submission ranking is claimed. No GPU/QPLIB sweep was repeated in this focused
cycle, and nonconvex QP/MIQP/NLP/MINLP remain outside implemented scope. Next:
audit the new Kaggle return, compare feasibility/gaps and traces, then decide
whether to ablate/tune either option or address the next concrete bottleneck.
