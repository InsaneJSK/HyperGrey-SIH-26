# Iteration20 — complete 27-model ledger

One 30-second run per profile, 250000-node cap and requested gap 1e-6.
Same final binary and all common options; only --pump-guided-diving differs.
Both profiles retain iteration19's numerical heuristic repair. All 27 cases
are development data, not fresh holdouts. See [REPORT.md](REPORT.md) for all
screen, wave, exploratory repeat and audit evidence.

| Model | Control outcome | Objective | Reported gap | Guided outcome | Objective | Reported gap |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| p0033 | Exact subset | 3089 | 0% | Exact subset | 3089 | 0% |
| enigma | Tolerance completion | 0 | 4.941e-322% | Tolerance completion | 0 | 4.941e-322% |
| flugpl | Tolerance completion | 1201500 | 1.000e-5% | Tolerance completion | 1201500 | 1.000e-5% |
| stein27 | Tolerance completion | 18 | 1.870e-14% | Tolerance completion | 18 | 1.870e-14% |
| markshare_4_0 | Exact subset | 1 | 0% | Exact subset | 1 | 0% |
| blend2 | Feasible / open | 8.788661 | 13.7639% | Feasible / open | 8.788661 | 13.7519% |
| binkar10_1 | Feasible / open | 6810.690026 | 1.9596% | Feasible / open | 6810.690026 | 1.9579% |
| egout | Tolerance completion | 568.1007 | 0% | Tolerance completion | 568.1007 | 0% |
| gt2 | Feasible / open | 42649 | 67.3200% | Feasible / open | 35673 | 60.9267% |
| lseu | Tolerance completion | 1120 | 2.028e-14% | Tolerance completion | 1120 | 2.028e-14% |
| mod008 | Feasible / open | 307 | 0.3247% | Feasible / open | 307 | 0.3247% |
| p0201 | Tolerance completion | 7615 | 1.194e-14% | Tolerance completion | 7615 | 1.194e-14% |
| p0282 | Feasible / open | 266462 | 3.5461% | Feasible / open | 266462 | 3.5427% |
| misc03 | Feasible / open | 3360 | 5.9506% | Feasible / open | 3360 | 5.3555% |
| misc07 | No-point limit | — | — | Feasible / open | 3785 | 60.3539% |
| pk1 | Feasible / open | 20 | 95.2381% | Feasible / open | 30 | 96.7742% |
| rgn | Tolerance completion | 82.199999 | 1.023e-5% | Tolerance completion | 82.199999 | 1.023e-5% |
| gen-ip002 | Feasible / open | -4681.758266 | 2.9880% | Feasible / open | -4681.758266 | 2.9201% |
| assign1-5-8 | Feasible / open | 221 | 15.6996% | Feasible / open | 221 | 15.6996% |
| lotsize | No-point limit | — | — | No-point limit | — | — |
| eil33-2 | No-point limit | — | — | No-point limit | — | — |
| mas74 | Feasible / open | 12914.438691 | 15.8063% | Feasible / open | 12914.438691 | 15.7310% |
| gen-ip054 | Feasible / open | 6911.531524 | 1.8529% | Feasible / open | 6911.531524 | 1.8494% |
| neos859080 | Infeasible cross-check* | — | — | Infeasible cross-check* | — | — |
| danoint | No-point limit | — | — | No-point limit | — | — |
| rout | No-point limit | — | — | Feasible / open | 1247.32 | 20.0075% |
| mas76 | Feasible / open | 41519.99574 | 5.3037% | Feasible / open | 41519.99574 | 5.3304% |

Control: 21 checked points (2 restricted exact completions, 7 numerical
completions, 12 open feasible limits), 5 no-point limits and 1 cross-checked
infeasible model. Guided: 23 checked points (the same 2 exact / 7 numerical
completions, 14 open feasible limits), 3 no-point limits and 1 cross-checked
infeasible model. Valid points do not mean completed optimality proofs.

* Both original neos859080 references hit their five-second limit. The raw wave
and main audit retain terminal_reference_pending. A separate independent solve
with a 30-second allowance reports Infeasible after about 14.91 seconds and
cross-checks both statuses on the identical hashed model. See
[terminal reference evidence](terminal-references/SUMMARY.json). No own solver
run was repeated or given additional time, and original reference timeouts
remain unchanged. This is numerical agreement, not an exact general
infeasibility certificate or an equal-budget speed comparison against HiGHS.

Reported gap is max(0, incumbent-bound)/(1+abs(incumbent)) in minimization sense.
No-point limits have no meaningful incumbent gap and do not prove infeasibility.
Objectives are rounded here; full precision, bounds, counters and adverse
outcomes remain in [raw wave results](wave-30s/results.json).

The repeated target screen has no coverage gain. Lotsize, eil33-2 and danoint
remain no-point limits in both profiles. The wave's additional misc07/rout
points are single-pair observations: rout had no point in any of its four
screen runs, and both models had points in earlier iteration19 experiments.
Gt2 improves objective in this wave; pk1 worsens from about 20 to 30. Guidance
therefore remains optional and off by default, not a uniform improvement.

