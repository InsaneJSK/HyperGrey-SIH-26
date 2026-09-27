# QP iteration 01 — independently checked 9002 improvement

14 September 2026. The retained CPU solver now solves original QPLIB 9002 to
the existing relative feasibility/KKT tolerance, with an additional numerical
dual-gap check. Final exact-binary repeats took 4.2754, 4.1924 and 4.8112 seconds
(median 4.2754 s), all at 180 Newton iterations. The full regression run also
passed it in 4.1875 s. This is a local CPU result; this new snapshot has not yet
run on Kaggle/CUDA.

## What changed and why

9002 has 2,890 variables, 1,649 equality rows and 9,690 linear nonzeros. Its
positive diagonal Hessian ranges from 9.288328e-12 to 2, while some bounds
are around 1e11. The existing specialist was limited to 512 variables. Simply
bypassing that cap did not solve it: the preserved unmodified dual-Newton
probe stopped at its 500-iteration cap with relative feasibility 7.38e-6.

The retained change normalizes magnitudes after curvature whitening and
correctly reconstructs original row multipliers. Eligibility is now based on
mathematical structure, with a bounded specialist budget and ADMM fallback.
There is no instance-name branch, imported solution, dropped tiny coefficient,
new numerical library, or relaxed acceptance tolerance.

The checker also computes the separable diagonal Lagrangian lower bound and
requires its relative gap to meet tolerance. This prevents tiny curvature from
making a misleadingly small projected gradient sufficient for acceptance.
Malformed/nonfinite candidates cannot retain a previous verification flag.
See [the derivation and scope](../../docs/DIAGONAL_QP_METHOD.md).

## Independent evidence on the original model

All three final repeats produced the same candidate and independent values:

| Quantity | Result |
| --- | ---: |
| Recomputed objective | 5,698,097,498.566484 |
| Numerical dual lower bound | 5,698,097,498.119152 |
| Relative primal feasibility | 8.5718305e-8 |
| Projected stationarity | 2.4131729e-16 |
| Relative complementarity | 4.1247946e-11 |
| Relative primal/dual gap | 7.8505568e-11 |
| Maximum absolute constraint violation | 2.3810225 |

The absolute violation is intentionally visible: tolerance is relative to
original row/bound magnitudes, not an absolute operational tolerance. These
are floating-point numerical certificates, not exact arithmetic proofs.
For maximization, the reported dual bound is in normalized minimization sense.

The preserved baseline CLI timed out at 30 seconds in all three paired
experiment-03 repeats. Its relative feasibility stayed around 3.74e-6 to
4.25e-6 and it failed independent KKT checks despite a superficially close
objective. No finite speedup ratio to convergence is inferred from a timeout.

The unchanged OSQP 1.0.5 reference protocol still times out on original 9002.
The official LP export audit detects 92 changed Hessian entries; all candidate
certificates instead use the independently parsed original `.qplib` coefficients.
Thus the old reference-comparison score remains **2/3 QPLIB**, while the
separately labeled original-model independent KKT score is **3/3**. The 9002
diagonal-bound certificate passes as well. No reference timeout was hidden or
reclassified as a successful comparison.

## Complete retained-source gate

`validated-cpu/` contains the raw candidates, independent reference outputs,
hardware/source metadata and incomplete cases. `final-repeats/` adds full
source snapshots and exact-binary repeat results.

| Check | Passed / total |
| --- | ---: |
| CTest groups | 3 / 3 |
| Previous generated cases | 230 / 230 |
| New diagonal-equality cases | 21 / 21 |
| Independent certificate adversarial tests | 7 / 7 |
| Selected Netlib LPs | 12 / 12 |
| Historical MILPs | 4 / 4 |
| Application examples | 4 / 4 |
| Public QP independent KKT | 3 / 3 |
| Public QP completed reference comparisons | 2 / 3 |
| Modern MILPs completed | 0 / 3 |
| CPU scale checks through 1,000,000 variables | 6 / 6 |

The unchanged MILP implementation retains binkar10_1's independently feasible
7297.320029 incumbent (zero original feasibility/integrality violation). This
run finds it at 11.5645 s, with final gap 8.7455%; variable machine load means
this is not evidence of a new MILP speed improvement. blend2 still has no
incumbent; markshare_4_0 still has an approximately 33 incumbent and a large gap.

The scale family is synthetic convex box QP, not general million-variable
LP/MILP/constrained-QP capability. LP/MILP/CUDA numerical sources are unchanged;
the shared QP verification routine did change, so fresh Kaggle evidence is needed.

## Reproducibility and preserved attempts

Retained CLI (`build-qp-iter1/solver_cli.exe`, also copied here):
`4786604e43e70efdaf92c93c9294df1fa12fc71aa97358c2ebfc89ca509c8a2c`.

Baseline CLI (`build-milp-iter1/solver_cli.exe`, also copied here):
`696b8518fdec9325fb75231bbe21e02b08e37b3722bcb60e0ac4e4b428e0d22b`.

Only `src/qp_admm.cpp`, `src/qp_dual_newton.cpp` and `tests/test_v2.cpp` changed
within the 22-file numerical core inventory. New Python validation and
documentation files are separate from that core.

- `experiment-01/`: preserved probe compilation setup failure (missing header).
- `baseline-probe/`: unmodified diagonal specialist, unsuccessful.
- `experiment-02/`: first magnitude-scaled probe, independently successful.
- `experiment-03/`: three sequential baseline/new pairs, exploratory binary.
- `generated-equalities-01/`: rejected malformed generated QPLIB trailer.
- `generated-equalities-02/`: harness field-name scoring error; full candidates retained.
- `generated-equalities-03/`: corrected harness, all 21 passed, no solver retuning.
- `validated-cpu/` and `final-repeats/`: final retained-source evidence.

Reproduce using [V2_REPRODUCE.md](../../docs/V2_REPRODUCE.md). The earlier builds,
notebooks, source ZIPs, and both P100 returns remain unchanged.

## Next handoff and submission position

Use the separate `kaggle_delivery/qp_iteration_01` notebook and matching source
ZIP, not an old notebook with the new ZIP. Attach the ZIP as a private Kaggle
input, enable GPU and Internet, Run All, and return `sih26119_kaggle_results.zip`.
The kernel remains below 1 MB; source/data stay in the external input archive.

Next decisions depend on that exact-snapshot return: Linux numerical agreement,
251 generated checks, original 9002 feasibility/gap, and CPU/GPU scale regressions.
The next algorithmic priority remains modern-MILP incumbent/bound progress,
including safer basis reuse after cuts. Broader QP coverage, domain data,
repeated equal-accuracy measurements, organizer scope clarification and final
submission material remain open. This is a stronger candidate, not evidence of
industrial completeness or a guaranteed competition percentile.
