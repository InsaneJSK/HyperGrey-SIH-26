# SIH26119: first audited Kaggle GPU run

Run date: 14 September 2026. The returned notebook run completed successfully
on a Tesla P100-PCIE-16GB. CUDA box-QP execution is now demonstrated on the
selected synthetic family. This is one timing pass, not a repeatability study
or a claim of general industrial-scale performance.

## Evidence audit

The original Downloads ZIP was left untouched. Its exact bytes, submitted
notebook/source ZIP and extracted results are preserved in `kaggle-gpu-01/`.
The audit checked archive integrity, all 115 source/data hashes, 59 runtime
source hashes, CMake/cache identity, benchmark input hashes, raw reference
acceptance checks, generated pass counts and CPU/GPU objective agreement.
It independently regenerated the planted scale-family objectives in Python.
Full scale primal vectors are not exported, so their maximum-error fields
remain solver-reported checks, not an independent full-vector recheck.

Returned ZIP SHA-256:
`307152f3596dd9d17127b31257b540fb07adb8bb0d4fd90ad8f46d22f906c9f8`.
Source ZIP SHA-256:
`6df478b347011bddb81af6950fbfec1a7c2557954c2fc4ccc0cea42a18f2bb6b`.

See the [machine-readable audit](kaggle-gpu-01/AUDIT.json),
[raw summary](kaggle-gpu-01/raw/reports/kaggle_validation/summary.json),
[build log](kaggle-gpu-01/raw/run_logs/build.log), and
[original returned ZIP](kaggle-gpu-01/returned_results.zip).
The Linux binaries are identified by recorded hashes, but were not included
in the returned bundle; this is evidence consistency checking, not remote
execution attestation or an independent rerun of the GPU binary.

## Correctness and public coverage

| Family | Passed / attempted |
| --- | ---: |
| Generated LP / MILP / QP / mixed-integer | 230 / 230 |
| CTest targets | 3 / 3 |
| Selected Netlib | 12 / 12 |
| Historical MIPLIB | 4 / 4 |
| QPLIB | 2 / 3 |
| Additional MIPLIB 2017 | 0 / 3 |
| Application models | 4 / 4 |
| CPU / 2-thread CPU / CUDA scale checks | 9 / 9 |

All three CUDA cases passed at 1,000, 100,000 and 1,000,000 variables.
Their objectives agree with the CPU results. These are sparse tridiagonal
convex box QPs with planted optima. Public QPLIB results in this run use CPU,
not CUDA; general constrained-QP, LP and MILP GPU support is not claimed.

## Single-pass timing observations

| Variables | CPU 1 thread | CPU 2 threads | P100 GPU | CPU 1 / GPU |
| ---: | ---: | ---: | ---: | ---: |
| 1,000 | 0.0153 s | 0.0151 s | 0.1270 s | 0.12x (GPU slower) |
| 100,000 | 1.2127 s | 0.7504 s | 0.3687 s | 3.29x |
| 1,000,000 | 16.7640 s | 9.8766 s | 2.9818 s | 5.62x |

For the million-variable case the GPU was 3.31x faster than the two-thread
CPU in this pass. Including process startup and input generation, one-thread
CPU/GPU process times were 16.9497/3.2016 seconds (5.29x).

Solve timing includes solver setup, transfers, iterations and final checks;
it is not kernel-only time. There is no variance estimate from one repetition.
Do not describe 5.62x as a repeatable or general solver speedup. Small inputs
were slower on GPU, so GPU should not be the default for every problem size.

Environment: Linux, two physical/four logical CPU cores, approximately 31.3 GiB
RAM, Python 3.12.13, GCC 11.4.0, CUDA compiler 12.8.93, NVIDIA driver 580.159.04.
The driver's displayed CUDA compatibility version is not the compiler version.

## Remaining failures and next priorities

- QPLIB **9002**: time limit after 90,350 iterations. Primal residual
  3.70e-6 and stationarity residual 4.74e-4 did not establish optimality;
  no usable dual bound was returned. OSQP also timed out. Improve constrained
  QP conditioning/linear solves; do not loosen acceptance to call this solved.
- **markshare_4_0**: 10,000-node limit, incumbent about 33 and gap about 0.971.
  HiGHS had incumbent 3 but also timed out. Branching/bounds and incumbent
  improvement remain necessary; the comparison is not against a proven optimum.
- **blend2**: timed out without an incumbent. HiGHS solved to 7.598985.
  The previous reference-output parser fix worked in the returned run.
- **binkar10_1**: timed out without an incumbent; HiGHS returned an incumbent
  but also timed out. Feasibility heuristics are a priority for both no-incumbent cases.

## Memory reporting correction implemented after this run

All returned per-process GPU-memory values were null. The old sampler suppressed
NVML errors, so the exact cause cannot be recovered from this bundle. Container
PID visibility, unsupported queries and unavailable values are possibilities,
not established diagnoses. Sampled host RSS is not GPU VRAM.

The next-run sampler now records missing-data reasons and query errors, requires
a matching PID for process attribution, and separately reports device-wide
baseline/peak observations. Device-wide increases can include other processes
and driver allocations; they are not substituted for solver memory. This
distinction follows the [NVIDIA NVML query definitions](https://docs.nvidia.com/deploy/nvml-api/api/group__nvmlDeviceQueries.html).
Six mocked-NVML regression tests and a real CPU subprocess integration check
passed. Actual Kaggle sampling still needs a future run to validate the change.

The solver core and already-tested small Kaggle delivery were left unchanged
while importing these results. The next code snapshot will include the sampler
correction. No repeat run of the unchanged notebook is needed just to ingest
this evidence. Before final submission, run repeated equal-accuracy GPU timings,
add public box-QP GPU comparisons and address the four CPU algorithm gaps.
