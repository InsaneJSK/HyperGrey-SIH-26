# Iteration05 experiment log

All experiments are local CPU runs. Existing iteration04 binaries/source ZIPs
and evidence remain unchanged. Nothing is requested from Kaggle.

## Preserved starting point

`baseline-source/` and `baseline_solver_cli.exe` preserve the files before this
iteration. CLI SHA256:
`17ba159a72eaf04e34f6754795ac0013c8bc6c0a75b7bca9d1ce46318139a679`.
The prior checked180s outcomes are blend2=7.598985 with gap completion,
binkar=6747.310015 with an open1.22% gap, and markshare~5 with an open83.33% gap.

## Probe A: two-stall diversification — rejected as a replacement

Source: `probe-source/`; executable: `probe_solver_cli.exe`.
CLI SHA256:
`e0f8e2d4b98b6202172d47a2336183a8f737f482154650564daa773c3ce71ce7`.
Two equal90s/250k-node binkar runs; separate reference workers use zero solve
time only to check candidates, not establish optima. CTest3/3, generated240/240.

| Mode | Objective | Reported gap | Status |
| --- | ---: | ---: | --- |
| Guided | 6757.190021084338 | 1.412943% | time_limit |
| Two-stall diversified | 6789.670034824617 | 1.885821% | time_limit |

The early trigger replaces the sixth guided neighbourhood, which improves the
baseline from6789.67 to6757.19. The corresponding diversified/expanded calls do
not improve6789.67. Wall-clock conditions also vary, so this is an observed
regression under the paired protocol, not an isolated timing-independent cause.
The candidate is NOT promoted. Preserve the unsuccessful run, not just later
successful evidence.

Both final candidates and the last improved vector from each successful
neighbourhood call pass an additional independent original-MPS audit:7/7
points. Source/model identity, traces, released-integer sets and counters also
pass. See `probe-90s/` and `probe-90s-audit/AUDIT.json`.

## Probe B: four-stall trigger and deeper late attempts

CLI SHA256:
`855c3413c056c7ede4e180774991801413549b561f8cca4c6305b9f1d293f6ca`.
The trigger now waits for four consecutive unsuccessful neighbourhood calls.
Triggered calls can use4s/128 local nodes rather than2s/64, but the same
min(30s,15% of total time) cumulative allowance and16-call cap apply.
Global proof accounting and original candidate tolerances are unchanged.

The full equal180s/250k-node comparison is complete in `local-180s/`.
Both modes finish markshare at4.999999994 (node_limit), blend2 at7.598985
(gap_limit), and binkar at6747.310014559364 (time_limit, about1.22% gap).
Six final incumbents and28 total captured/final vectors pass independent
original-MPS checks. Both blend2 runs match the independently solved optimum.
There are no unsafe/error runs. This is not a final-objective improvement,
so diversification is not promoted to a default.

The new call-level diagnostics expose an additional scheduling issue:
markshare exhausts all16 guided neighbourhood calls by0.90 seconds, around
incumbent73. Its main tree does not reach incumbent~5 until76.19 seconds.
The diversified run uses its last call by0.87 seconds; it improves the early
incumbent to~61 but also finishes at~5. This motivates testing time spacing
separately from variable selection, not merely increasing the total budget.

These observations do not justify changing defaults or claiming either
markshare or binkar solved. Full raw results and independent checks remain the
authority for submission claims.

## Probe C: guided selection with time spacing

CLI SHA256:
`ef1856d074862aa754a81e5bff7bfc44c350c02eae4f0a6b43a309c4f4e53cd6`.
`--pace-neighborhood` enforces min(5s,2% of the global time budget) spacing
between successive neighbourhood starts. All other budgets and guided variable
selection are unchanged. This isolates pacing from diversification.

CTest3/3, generated240/240 and11 diagnostic checker tests pass. An exact check
of80 generated guided-mode results against Probe B finds no differences in
status/objective/primal/bound/gap/nodes/LP iterations/pass status; timings and
new output fields are intentionally excluded. See `DEFAULT_NONREGRESSION.json`.

The single-strategy180s screen is in `pacing-180s-screen/`, with the just-completed
guided data as a historical comparison, not a new paired/repeated timing claim.
Markshare's16 calls now span0.01 to54.03 seconds, versus ending before1 second;
its final objective is still4.999999994. Scheduling alone therefore has not
improved that final solution. The screen is complete: blend2 reaches7.598985
with gap_limit; binkar retains6747.310015 with about1.23% gap and time_limit.
All three final candidates and12 total available vectors pass fresh original-MPS
checks, including actual spacing verification. No unsafe/error run is flagged.
Neither new option is enabled by default. See `REPORT.md` and `FINAL_STATE.json`.
