# Iteration 21 — complete 27-model ledger

One 30-second run per profile/model. Both use iteration19 repair and iteration20 guidance; distance adds only the private distance objective. Lower objective is better for these listed MIN models; consult the MPS for model sense. These are development cases, not fresh holdouts.

| Model | Guided objective | Guided gap | Distance objective | Distance gap | Guided / distance outcome |
|---|---:|---:|---:|---:|---|
| p0033 | 3089 | 0.0000% | 3089 | 0.0000% | exact subset / exact subset |
| enigma | 0 | 0.0000% | 0 | 0.0000% | numerical complete / numerical complete |
| flugpl | 1201500 | 0.0000% | 1201500 | 0.0000% | numerical complete / numerical complete |
| stein27 | 18 | 0.0000% | 18 | 0.0000% | numerical complete / numerical complete |
| markshare_4_0 | 1 | 0.0000% | 1 | 0.0000% | exact subset / exact subset |
| blend2 | 8.788661 | 13.9018% | 8.788661 | 13.9151% | feasible, open / feasible, open |
| binkar10_1 | 6810.690026 | 1.9679% | 6787.820026 | 1.6274% | feasible, open / feasible, open |
| egout | 568.1007 | 0.0000% | 568.1007 | 0.0000% | numerical complete / numerical complete |
| gt2 | 35673 | 60.9267% | 35673 | 60.9239% | feasible, open / feasible, open |
| lseu | 1120 | 0.0000% | 1120 | 0.0000% | numerical complete / numerical complete |
| mod008 | 307 | 0.0000% | 307 | 0.0000% | numerical complete / numerical complete |
| p0201 | 7615 | 0.0000% | 7615 | 0.0000% | numerical complete / numerical complete |
| p0282 | 266462 | 3.5378% | 266462 | 3.5213% | feasible, open / feasible, open |
| misc03 | 3360 | 4.7605% | 3360 | 4.6117% | feasible, open / feasible, open |
| misc07 | 3785 | 59.9577% | — | — | feasible, open / no point |
| pk1 | 29 | 96.6667% | 20 | 95.2381% | feasible, open / feasible, open |
| rgn | 82.19999923 | 0.0000% | 82.19999923 | 0.0000% | numerical complete / numerical complete |
| gen-ip002 | -4681.758266 | 2.9074% | -4681.758266 | 2.9061% | feasible, open / feasible, open |
| assign1-5-8 | 220.9999998 | 15.1999% | 220.9999998 | 15.1999% | feasible, open / feasible, open |
| lotsize | — | — | — | — | no point / no point |
| eil33-2 | — | — | 1204.099899 | 31.6241% | no point / feasible, open |
| mas74 | 12914.43869 | 15.6216% | 12914.43869 | 15.6219% | feasible, open / feasible, open |
| gen-ip054 | 6911.531524 | 1.8397% | 6911.531524 | 1.8409% | feasible, open / feasible, open |
| neos859080 | — | — | — | — | infeasible cross-check / infeasible cross-check |
| danoint | — | — | — | — | no point / no point |
| rout | — | — | 1703.47 | 41.3785% | no point / feasible, open |
| mas76 | 41519.99574 | 5.2586% | 41519.99574 | 5.2618% | feasible, open / feasible, open |

A returned point is independently checked against the original MPS. Numerical completion is not an exact general MILP proof. Exact certificates apply only to the restricted binary subset. Gap uses the solver’s documented denominator `1 + abs(incumbent)`.

Both infeasibility statuses passed the original wave references; no longer supplemental reference was needed.
