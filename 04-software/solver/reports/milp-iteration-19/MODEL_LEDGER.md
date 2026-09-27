# Iteration19 — complete 27-model ledger

One 30-second run per profile, 250000-node cap and requested gap 1e-6.
Both profiles use the same candidate executable; only optional heuristic repair differs.
All 27 are development cases, not fresh holdouts. See [REPORT.md](REPORT.md)
for repeated comparisons, gates, assumptions and limitations.

| Model | Control outcome | Objective | Reported gap | Repair outcome | Objective | Reported gap |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| p0033 | Exact subset | 3089 | 0% | Exact subset | 3089 | 0% |
| enigma | Tolerance completion | 0 | 4.941e-322% | Tolerance completion | 0 | 4.941e-322% |
| flugpl | Tolerance completion | 1201500 | 1.000e-5% | Tolerance completion | 1201500 | 1.000e-5% |
| stein27 | Tolerance completion | 18 | 1.870e-14% | Tolerance completion | 18 | 1.870e-14% |
| markshare_4_0 | Exact subset | 1 | 0% | Exact subset | 1 | 0% |
| blend2 | No-point limit | — | — | Feasible / open | 8.788661 | 13.6224% |
| binkar10_1 | Feasible / open | 6810.690026 | 1.9327% | Feasible / open | 6787.820026 | 1.6205% |
| egout | Tolerance completion | 568.1007 | 0% | Tolerance completion | 568.1007 | 0% |
| gt2 | Feasible / open | 42649 | 67.3271% | Feasible / open | 42649 | 67.3482% |
| lseu | Tolerance completion | 1120 | 2.028e-14% | Tolerance completion | 1120 | 2.028e-14% |
| mod008 | Feasible / open | 307 | 0.3247% | Feasible / open | 307 | 0.3247% |
| p0201 | Tolerance completion | 7615 | 1.194e-14% | Tolerance completion | 7615 | 1.194e-14% |
| p0282 | Feasible / open | 266462 | 3.5874% | Feasible / open | 266462 | 3.5318% |
| misc03 | Feasible / open | 3360 | 5.5043% | Feasible / open | 3360 | 5.5043% |
| misc07 | Feasible / open | 2810 | 45.3575% | Feasible / open | 2810 | 46.0690% |
| pk1 | Feasible / open | 32 | 96.9697% | Feasible / open | 31 | 96.8750% |
| rgn | Tolerance completion | 82.199999 | 1.023e-5% | Tolerance completion | 82.199999 | 1.023e-5% |
| gen-ip002 | Feasible / open | -4681.758266 | 2.9292% | Feasible / open | -4681.758266 | 2.9101% |
| assign1-5-8 | Feasible / open | 221 | 15.1999% | Feasible / open | 221 | 15.2073% |
| lotsize | No-point limit | — | — | No-point limit | — | — |
| eil33-2 | No-point limit | — | — | No-point limit | — | — |
| mas74 | Feasible / open | 12914.438691 | 15.6579% | Feasible / open | 12914.438691 | 15.7055% |
| gen-ip054 | Feasible / open | 6911.531524 | 1.8482% | Feasible / open | 6911.531524 | 1.8386% |
| neos859080 | Infeasible cross-check | — | — | Infeasible cross-check* | — | — |
| danoint | No-point limit | — | — | No-point limit | — | — |
| rout | No-point limit | — | — | Feasible / open | 2102.73 | 52.5523% |
| mas76 | Feasible / open | 41519.99574 | 5.2943% | Feasible / open | 41519.99574 | 5.2571% |

Control: 21 checked points, comprising 2 restricted exact completions, 7 numerical
completions and 12 open feasible limits; 5 no-point limits and 1 cross-checked
infeasible model. Repair: 23 checked points, comprising the same 2 restricted
exact completions and 7 numerical completions plus 14 open feasible limits;
3 no-point limits and 1 cross-checked infeasible model after the supplemental check.
These outcomes do not mean 23 or 24 optimality proofs.

* The original repair reference on neos859080 stopped at its 5-second limit.
The original raw category remains terminal_reference_pending. The paired control
reference reported Infeasible on the identical SHA-256 model. The separate
[terminal pair cross-check](terminal-pair-crosscheck/SUMMARY.json) verifies the
repair status against that saved reference, without rerunning either solver or
altering the raw records. This is numerical status agreement, not an exact
general infeasibility certificate.

An exact-subset completion uses the restricted independently recomputed binary
certificate. Tolerance completion is numerical, not an exact general-MILP proof.
Feasible / open means the point passed independent original-row, bound,
integrality and objective checks but its optimality gap remains open.
No-point limit is neither proof of infeasibility nor a completed solution.
Gap is max(0, incumbent - bound) / (1 + abs(incumbent)) in minimization sense.
Objectives are rounded for display; raw values and bounds remain in
[wave results](wave-30s/results.json).

Only blend2 has a repeated, direct first-feasible gain from this repair:
3/3 repair runs versus 0/3 controls across screen and wave. Rout's extra point
in this wave had zero repair attempts, so it is not credited as a repair gain.
Eil33-2 returned points in all four screen runs but neither wave run. Mod008
completed in iteration18's earlier timings but neither profile completes here.
All these outcomes remain visible rather than being replaced by better runs.

