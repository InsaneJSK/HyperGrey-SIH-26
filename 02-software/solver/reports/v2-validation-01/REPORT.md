# V2 validation evidence

Generated correctness: PASS.

| Group | Passed | Total |
| --- | ---: | ---: |
| generated_lp | 120 | 120 |
| generated_milp | 40 | 40 |
| generated_qp | 30 | 30 |
| generated_mixed | 40 | 40 |
| industrial | 4 | 4 |
| miplib | 4 | 4 |
| miplib2017 | 0 | 3 |
| netlib | 12 | 12 |
| qplib | 2 | 3 |
| scale | 18 | 18 |

All incomplete public cases remain in benchmarks.json. Scale cases are synthetic tridiagonal convex box QPs with planted solutions; they do not establish general million-variable industrial capability.

GPU status: not_run_no_cuda_requested.

Timing includes setup, transfer and solution checks inside the solver; process time also includes startup. All scale repetitions run sequentially. RSS is sampled, not an exact peak.
