# Second Kaggle return — MILP iteration confirmed

14 September 2026. Imported `Downloads/sih26119_kaggle_results (1).zip`.
The notebook completed with CUDA enabled and matches the MILP iteration 01
source ZIP exactly. The Downloads file and previous return remain untouched.
This directory preserves the new returned ZIP, submitted source/notebook,
extracted raw results, audit and an additional local candidate check.

## What changed relative to the first Kaggle run

The first run had no `binkar10_1` incumbent after 30 seconds. This run finds
**7297.320029 in 13.7940 seconds**, using one pump projection. At the 30-second
limit it has explored 549 nodes, with bound 6658.583810 and reported gap
**8.7518%**. It is feasible, not proven optimal.

The independent Kaggle reference check and a fresh local HiGHS 1.12 reader
both measure zero original row/bound and integrality violation. The latter
recomputes the objective as 7297.320029. The local recheck uses reference time
limit zero for candidate validation only; it does not claim a new optimum.

The 30-second Kaggle HiGHS reference found a better incumbent, 6746.760023,
but also timed out. Do not present either incumbent as an exact optimum.

## Recounted validation

| Group | Passed / total |
| --- | ---: |
| Generated LP | 120/120 |
| Generated binary MILP | 40/40 |
| Generated mixed/general-integer MILP | 40/40 |
| Generated QP | 30/30 |
| Selected Netlib LP | 12/12 |
| Historical MILP | 4/4 |
| Application examples | 4/4 |
| Selected QPLIB | 2/3 |
| Completed modern MILP | 0/3 |
| Scale configurations | 9/9, including 3/3 CUDA |

CTest also passed. All four incompletes remain visible:

- `blend2`: no incumbent at 30 seconds; HiGHS reaches 7.598985 optimally.
- `markshare_4_0`: incumbent approximately 33, gap 97.0588%, 10,000-node limit.
- `binkar10_1`: improved feasibility, but the 8.7518% proof gap remains open.
- QPLIB `9002`: 30-second limit, primal residual 3.6721e-6 and stationarity
  residual 4.4447e-5; optimality is not verified and no finite dual bound is
  reported. OSQP also times out. The QP implementation did not change, so
  residual differences from the prior timed run are not a new algorithmic result.

## GPU measurements: selected synthetic box QPs only

Tesla P100-PCIE-16GB, two physical/four logical CPU cores, GCC 11.4,
Python 3.12.13, CUDA compiler 12.8.93, driver 580.159.04. CMake recorded
CUDA ON and architecture 60. The driver's displayed CUDA 13.0 is not the
compiler version.

| Variables | CPU 1 thread (s) | CPU 2 threads (s) | CUDA (s) | CPU1/CUDA |
| --- | ---: | ---: | ---: | ---: |
| 1,000 | 0.01907 | 0.01510 | 0.12561 | 0.15x |
| 100,000 | 1.20159 | 0.77580 | 0.37472 | 3.21x |
| 1,000,000 | 15.94096 | 9.43408 | 2.96186 | 5.38x |

Each configuration has one timing repetition. CUDA objectives/solutions pass
the accuracy checks against independently regenerated planted objectives.
GPU launch/setup overhead loses on the small case. These are not general
industrial LP/MILP/QP speedups; CUDA still covers convex box QPs only.
The previous and current snapshots must not be pooled into a controlled
same-version repeated timing study.

The new memory diagnostics work, but process-attributed GPU memory is still
unavailable: NVML initializes and lists a GPU process, yet the solver PID is
never matched. No NVML query errors were recorded. PID visibility/mapping is
an investigation target, not a proven cause. Whole-device sampled peak for
the million-variable run was 483,262,464 bytes (460.875 MiB), an increase of
362,938,368 bytes (346.125 MiB) over its device baseline. Those figures can
include driver/other-process allocations and are NOT solver-only memory.

## Audit identity and next step

- Source ZIP SHA-256: `f9b8a366cbdf6d0cf216c21307d9439515e6f46c52d2ad22b612b94e5e29b1d8`.
- Returned ZIP SHA-256: `fad71cb475ec23450b9e919926f06a30f2b1fac9b80e6912bf6a877c9fb95731`.
- 128 archive files and 63 runtime-source hashes verified, plus input hashes,
  CMake cache hash, status/count recounts and planted scale-objective checks.
- Linux solver binary SHA-256: `0c7896390b9caac63ba510c29b0ad48004f96fd919a5180f012885a906d19b44`.

This establishes the intended MILP improvement on Kaggle without regression
on the selected passing cases. It does not establish submission completeness.
No rerun of this unchanged notebook is needed. Next numerical priority remains
the separate constrained-QP `9002` cycle; MILP incumbent quality, cut/bound
progress and the `blend2` search failure remain explicit follow-up work.
