# SIH26119: V2 candidate with CPU and Kaggle GPU evidence

Local verification date: 14 September 2026 (India). Submission deadline:
30 September 2026. This is a substantially expanded, tested solver candidate,
not a claim that the entire industrial-scale problem statement is solved.
The first Kaggle run is now audited: all three synthetic CUDA box-QP checks
passed on a P100, including one million variables. See the
[Kaggle GPU report](KAGGLE_GPU_REPORT.md) for the 5.62x single-pass CPU1/GPU
observation, scope, missing VRAM data and remaining failures. The CPU evidence
below is preserved; repeated GPU performance is not yet established.

## Delivered implementation

- Own sparse revised primal/dual simplex and LU/eta basis algebra, with scaling,
  warm starts and checked LP numerical optimality/recession evidence.
- Own MILP branch-and-cut baseline: bound propagation, binary cover cuts,
  incumbent diving, basis reuse, best-bound search and integer polishing.
- Continuous convex QP: sparse scaled ADMM/PCG, bounded active-set polishing,
  a small structured diagonal-QP Newton path, and CPU/OpenMP box-QP FISTA.
- Optional resident CUDA box-QP kernels; CLI/C++ APIs and JSON diagnostics.
- Reproducible reference comparisons, source/input/binary hashes, repeated
  timing/memory capture, literature application models and a separate notebook.

HiGHS and OSQP are independent validation references, not the solver core.
The active CMake target links no external optimization solver. See the
[architecture](../docs/V2_ARCHITECTURE.md) for algorithm details and provenance.

## Final CPU results

The run used a 30-second public-case solver limit and a 10,000-node MILP limit.
The generated correctness gates and synthetic scale checks passed. Public
completion requires objective agreement, original-model feasibility and the
applicable numerical optimality/gap checks; these are floating-point checks,
not exact certificates. These are selected subsets, not complete libraries.

| Test family | Passed / attempted | Interpretation |
| --- | ---: | --- |
| Generated LP | 120 / 120 | Analytical/generated correctness |
| Generated binary MILP | 40 / 40 | Independent enumeration |
| Generated mixed/general-integer MILP | 40 / 40 | HiGHS and original-model checks |
| Generated convex QP | 30 / 30 | Analytical/reference checks |
| Netlib LP | 12 / 12 | Selected public models |
| Historical MIPLIB | 4 / 4 | Optimal or numerical gap-limit completion |
| QPLIB | 2 / 3 | Constrained case 9002 remains incomplete |
| Additional MIPLIB 2017 | 0 / 3 | All three stress cases remain incomplete |
| Application models | 4 / 4 | Two refinery variants, transport, synthetic production |
| Repeated synthetic scale runs | 18 / 18 | Three sizes, two CPU configurations, three repetitions |
| CTest targets | 3 / 3 | C++ numerical regressions and a planted scale case |

Historical MILP results: p0033 = 3089 (277 nodes), enigma = 0 (4908 nodes),
flugpl = 1,201,500 (577 nodes), stein27 = 18 (9975 nodes). The last three
returned `gap_limit`; they are not relabeled as exact optimal certificates.
V1 completed only one of these four selected cases. Different builds and run
conditions prevent treating the V1/V2 wall times as a controlled speedup study.

### All incomplete public cases

| Instance | Our final CPU status | Reference context |
| --- | --- | --- |
| QPLIB 9002 | time_limit | OSQP also reached its time limit; neither objective is a certified comparison optimum |
| markshare_4_0 | node_limit | HiGHS reached its time limit; incumbent quality and our large gap remain concerns |
| blend2 | time_limit; no incumbent | HiGHS printed an optimal objective of 7.598985 with extra native diagnostics; raw runner recorded process_error |
| binkar10_1 | time_limit; no incumbent | HiGHS reached its time limit with an incumbent |

The blend2 reference-output parsing issue was corrected after the CPU run.
The original evidence is retained unchanged; a separate parser audit recovers
the reference JSON and preserves the extra text. No failed solver case becomes
a pass from this reporting correction. The Kaggle snapshot contains the fix.

## Million-variable experiment

Machine: Intel Core i5-10210U, 4 physical / 8 logical cores, approximately
39.6 GiB RAM, Windows 11, GCC 14.2.0. No NVIDIA GPU is present locally.
Each instance is a synthetic sparse tridiagonal positive-definite box QP with
an independently planted optimum. All 18 repetitions passed objective,
solution-error and numerical optimality checks.

| Variables | CPU 1-thread median | CPU 4-thread median | Largest sampled RSS across both configurations |
| ---: | ---: | ---: | ---: |
| 10,000 | 0.173 s | 0.389 s | 7.3 MiB |
| 100,000 | 1.915 s | 1.788 s | 31.5 MiB |
| 1,000,000 | 22.986 s | 18.409 s | 264.0 MiB |

Three sequential repetitions per configuration. The million-variable 1-thread
range was 21.215-31.996 seconds; the 4-thread range was 17.963-18.428 seconds.
The approximately 1.25x median ratio is a local observation, not a generalized
speedup claim. Four threads were slower on the smallest case. Timing includes
solver setup, iterations and final checks; process timing also includes startup
and model generation. RSS is sampled every 20 ms and can miss peaks.

This establishes one structured synthetic QP experiment only. It does not
establish million-variable LP, MILP, generally constrained QP or refinery scale.

## Application evidence

The [MARCO refinery literature model](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html)
and its tighter-sulfur variant were independently assembled into MPS models.
The base case has 57 variables and 40 rows and minimizes costs minus revenue:
objective -6.588421476680065, matching HiGHS. The sulfur variant returns zero:
the model has no minimum-demand constraints and can shut down. It is not a
claim that real refinery operations can simply be stopped.

The [Dantzig transportation example](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html)
returns 153.675. Our synthetic six-period production/inventory/setup MILP
returns 762. Both match HiGHS. The latter is synthetic, not industrial data.
See [model equations and provenance](../docs/INDUSTRIAL_CASES.md). Reference
agreement validates the emitted mathematics, not the business assumptions.

## Reproduction and preserved evidence

- [Final summary](v2-final-cpu/summary.json), [public results](v2-final-cpu/benchmarks.json),
  [all scale repetitions](v2-final-cpu/scale.json), [metadata and hashes](v2-final-cpu/metadata.json),
  [source/binary audit](v2-final-cpu/evidence_check.json), [CTest log](v2-final-cpu/ctest.log).
- Full candidate/reference outputs and generated cases remain in `v2-final-cpu/`
  in the local project. The notebook snapshot includes compact historical
  summaries; its new execution produces a separate full Kaggle evidence bundle.
- V1 source and executable remain in `v2-baseline/`; the
  [V1 report](V1_REPORT.md) is historical. Development attempts are retained.
- [Build, CLI/API and notebook instructions](../docs/V2_REPRODUCE.md).

The final CPU binary SHA-256 is
`9740e7ee673fd65062dde2769895d0d7be55b7bf35ef74d839147a12fd8b3aab`.
The numerical source, tests and CMake definition were checked against that
run. Subsequent reporting/parser/package edits do not alter that numerical
binary; the separate snapshot records their new hashes.

## What is needed to finalize V2

1. The first Kaggle return bundle has been received and audited. A later
   iteration needs repeated GPU timings, public box-QP GPU comparisons and
   the corrected memory diagnostics, not another copy of the same first run.
2. Provide any shareable MRPL/refinery/scheduling model or domain-expert feedback.
3. Obtain organizer clarification on convex versus nonconvex QP scope and
   permitted general GPU/numerical infrastructure.

Our remaining engineering work is to diagnose the four incomplete public
cases, extend CUDA test coverage, repeat equal-accuracy GPU measurements,
and then update the submission claims. MIQP, NLP, MINLP and global nonconvex QP
are not implemented. Full benchmark-library/Mittelmann coverage and production
industrial robustness remain unproven. See the
[requirement matrix](../docs/V2_REQUIREMENTS.md) and
[remaining-work list](../docs/V2_REMAINING.md).
