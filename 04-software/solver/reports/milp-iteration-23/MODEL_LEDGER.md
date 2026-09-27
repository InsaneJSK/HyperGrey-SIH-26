# Iteration23 complete 27-model ledger

Same binary,30 seconds/model/profile; all models are reused development data.
Control: iteration22 reopt profile. Candidate: add --pump-distance-reopt.
Independent checks validate points/statuses;5-second reference runs are not a fair speed comparison.

| Model | Control category | Objective | Gap | Handoff category | Objective | Gap |
|---|---|---:|---:|---|---:|---:|
| p0033 | exact_proof_checked | 3089 | 0 | exact_proof_checked | 3089 | 0 |
| enigma | numerical_completion_checked | 0 | 4.940656458e-324 | numerical_completion_checked | 0 | 4.940656458e-324 |
| flugpl | numerical_completion_checked | 1201500 | 1.000110807e-07 | numerical_completion_checked | 1201500 | 1.000110807e-07 |
| stein27 | numerical_completion_checked | 18 | 1.869849305e-16 | numerical_completion_checked | 18 | 1.869849305e-16 |
| markshare_4_0 | exact_proof_checked | 1 | 0 | exact_proof_checked | 1 | 0 |
| blend2 | feasible_limit | 8.788661 | 0.137570399 | feasible_limit | 8.788661 | 0.1379319394 |
| binkar10_1 | feasible_limit | 6810.690026 | 0.01961464166 | feasible_limit | 6810.690026 | 0.01959925058 |
| egout | numerical_completion_checked | 568.1007 | 0 | numerical_completion_checked | 568.1007 | 0 |
| gt2 | feasible_limit | 35673 | 0.6092672535 | feasible_limit | 35673 | 0.6092672535 |
| lseu | numerical_completion_checked | 1120 | 2.02831111e-16 | numerical_completion_checked | 1120 | 2.02831111e-16 |
| mod008 | numerical_completion_checked | 307 | 1.845565547e-16 | feasible_limit | 307 | 0.003246753247 |
| p0201 | numerical_completion_checked | 7615 | 1.194189472e-16 | numerical_completion_checked | 7615 | 1.194189472e-16 |
| p0282 | feasible_limit | 266462 | 0.03553213767 | feasible_limit | 266462 | 0.03544206888 |
| misc03 | feasible_limit | 3360 | 0.05355548944 | feasible_limit | 3360 | 0.05355548944 |
| misc07 | no_incumbent_limit | none | none | no_incumbent_limit | none | none |
| pk1 | feasible_limit | 34.99999996 | 0.972222225 | feasible_limit | 34.99999996 | 0.972222225 |
| rgn | numerical_completion_checked | 82.19999923 | 1.02283651e-07 | numerical_completion_checked | 82.19999923 | 1.02283651e-07 |
| gen-ip002 | feasible_limit | -4681.758266 | 0.02912829644 | feasible_limit | -4681.758266 | 0.02911786375 |
| assign1-5-8 | feasible_limit | 220.9999998 | 0.1519989577 | feasible_limit | 220.9999998 | 0.1519989577 |
| lotsize | no_incumbent_limit | none | none | no_incumbent_limit | none | none |
| eil33-2 | feasible_limit | 1204.099899 | 0.3162407638 | feasible_limit | 1204.099899 | 0.3162012761 |
| mas74 | feasible_limit | 13588.5643 | 0.197940213 | feasible_limit | 13588.5643 | 0.1978937613 |
| gen-ip054 | feasible_limit | 6911.531524 | 0.0183853241 | feasible_limit | 6911.531524 | 0.01839438628 |
| neos859080 | terminal_status_crosschecked | none | none | terminal_status_crosschecked | none | none |
| danoint | feasible_limit | 69.5 | 0.09695656044 | feasible_limit | 69.5 | 0.09695656044 |
| rout | feasible_limit | 1293.19 | 0.2279088132 | feasible_limit | 1293.19 | 0.2279097421 |
| mas76 | feasible_limit | 41519.99574 | 0.05254206147 | feasible_limit | 41519.99574 | 0.05258987729 |

`feasible_limit` means a checked point with an open proof gap, not optimality.
`terminal_status_crosschecked` is independently corroborated infeasibility, not a feasible point.
`exact_proof_checked` is the restricted binary proof path; numerical completion is not an exact rational proof.
