# Iteration24 complete 27-model ledger

Same binary,30 seconds/model/profile; all models are reused development data.
Control: iteration23 handoff profile. Candidate: add --pump-distance-stage.
Independent checks validate points/statuses;5-second reference runs are not a fair speed comparison.

| Model | Control category | Objective | Gap | Stage category | Objective | Gap |
|---|---|---:|---:|---|---:|---:|
| p0033 | exact_proof_checked | 3089 | 0 | exact_proof_checked | 3089 | 0 |
| enigma | numerical_completion_checked | 0 | 4.940656458e-324 | numerical_completion_checked | 0 | 4.940656458e-324 |
| flugpl | numerical_completion_checked | 1201500 | 1.000110807e-07 | numerical_completion_checked | 1201500 | 1.000110807e-07 |
| stein27 | numerical_completion_checked | 18 | 1.869849305e-16 | numerical_completion_checked | 18 | 1.869849305e-16 |
| markshare_4_0 | exact_proof_checked | 1 | 0 | exact_proof_checked | 1 | 0 |
| blend2 | feasible_limit | 8.788661 | 0.13663244 | feasible_limit | 8.788661 | 0.1370371745 |
| binkar10_1 | feasible_limit | 6787.820026 | 0.01623664738 | feasible_limit | 6790.910033 | 0.01657949869 |
| egout | numerical_completion_checked | 568.1007 | 0 | numerical_completion_checked | 568.1007 | 0 |
| gt2 | feasible_limit | 35673 | 0.6091831586 | feasible_limit | 35673 | 0.6091831586 |
| lseu | numerical_completion_checked | 1120 | 2.02831111e-16 | numerical_completion_checked | 1120 | 2.02831111e-16 |
| mod008 | numerical_completion_checked | 307 | 1.845565547e-16 | numerical_completion_checked | 307 | 1.845565547e-16 |
| p0201 | numerical_completion_checked | 7615 | 1.194189472e-16 | numerical_completion_checked | 7615 | 1.194189472e-16 |
| p0282 | feasible_limit | 266462 | 0.03535950582 | feasible_limit | 266462 | 0.03496920773 |
| misc03 | feasible_limit | 3360 | 0.03124070217 | feasible_limit | 3360 | 0.03421600714 |
| misc07 | no_incumbent_limit | none | none | feasible_limit | 3970 | 0.6094182825 |
| pk1 | feasible_limit | 36 | 0.9729729757 | feasible_limit | 31 | 0.9687500031 |
| rgn | numerical_completion_checked | 82.19999923 | 1.02283651e-07 | numerical_completion_checked | 82.19999923 | 1.02283651e-07 |
| gen-ip002 | feasible_limit | -4681.758266 | 0.02903151433 | feasible_limit | -4681.758266 | 0.02903707321 |
| assign1-5-8 | feasible_limit | 220.9999998 | 0.1518006218 | feasible_limit | 220.9999998 | 0.1518369255 |
| lotsize | no_incumbent_limit | none | none | no_incumbent_limit | none | none |
| eil33-2 | feasible_limit | 1204.099899 | 0.3162012761 | feasible_limit | 1204.099899 | 0.3161874205 |
| mas74 | feasible_limit | 13588.5643 | 0.1974912307 | feasible_limit | 13588.5643 | 0.1974773788 |
| gen-ip054 | feasible_limit | 6911.531524 | 0.01835103787 | feasible_limit | 6911.531524 | 0.01837247695 |
| neos859080 | terminal_status_crosschecked | none | none | terminal_status_crosschecked | none | none |
| danoint | feasible_limit | 69.5 | 0.09664425953 | feasible_limit | 69.5 | 0.09716580665 |
| rout | feasible_limit | 1293.19 | 0.2279414152 | feasible_limit | 1293.19 | 0.227920775 |
| mas76 | feasible_limit | 41519.99574 | 0.05277353733 | feasible_limit | 41519.99574 | 0.05248776766 |

`feasible_limit` means a checked point with an open proof gap, not optimality.
`terminal_status_crosschecked` is independently corroborated infeasibility, not a feasible point.
`exact_proof_checked` is the restricted binary proof path; numerical completion is not an exact rational proof.
