# Local CPU validation — 15 September 2026

The iteration04 candidate-repair solver reaches the independently solved
`blend2` reference objective **7.598985** in **114.5299 seconds**, with
`gap_limit` status and reported relative gap approximately1e-7. The paired
baseline has no incumbent after180 seconds. This is a completed numerical
comparison on one hard instance, not an exact-arithmetic proof or evidence
of broad industrial completeness.

All work ran locally. No Kaggle upload, notebook run or result return is needed.
The existing optional notebook/source ZIP remains unchanged and separate.

## Protocol and identity

- Windows11, Intel i5-10210U,4 physical/8 logical cores, approximately40GB RAM.
- CPU-only Release build `build-milp-iter4`; CUDA disabled. MILP search is sequential.
- CLI SHA256: `17ba159a72eaf04e34f6754795ac0013c8bc6c0a75b7bca9d1ce46318139a679`.
- Each hard run:180-second budget,250,000-node cap, requested gap1e-6.
- Both modes: fractionality branching, LP recovery, incumbent neighbourhood
  search and the shared repaired-node proof correction. Only candidate repair
  enables the bounded dense fixing fallback. No acceptance tolerance changed.
- Six sequential hard runs, alternating strategy order by model. All reference
  optimization runs followed the timed runs: HiGHS1.12.0,30 seconds per model.
  References never supply solutions to our search.

## Equal-budget results

| Model | Mode | Objective | Reported gap | Seconds | Status |
| --- | --- | ---: | ---: | ---: | --- |
| markshare_4_0 | Baseline | 4.999999994 | 83.333335% | 119.258 | node_limit |
| markshare_4_0 | Candidate repair | 4.999999994 | 83.333335% | 111.345 | node_limit |
| blend2 | Baseline | No incumbent | Undefined | 180.054 | time_limit |
| blend2 | Candidate repair | 7.598985 | 0.000010% | 114.530 | gap_limit |
| binkar10_1 | Baseline | 6747.310014559 | 1.220152% | 180.877 | time_limit |
| binkar10_1 | Candidate repair | 6747.310014559 | 1.220685% | 180.856 | time_limit |

Limits are cooperative; the largest observed overshoot is0.877 seconds.
Small timing/node/bound differences are not a repeatable speedup claim.

`blend2` repairs two rejected integer fixings, both of whose primary sparse
solves returned `numerical_error`. Dense repair costs0.5833 seconds in total.
The incumbent sequence is8.015188 at52.5717 seconds, then7.598985 at114.5012
seconds. Two tiny-fraction branches preserve whole-node proof accounting.
There are no unresolved nodes in this repaired run; the baseline retains four.
Both final lower bounds are7.5989841401015. Thus the measured gain is recovering
valid incumbents that permit gap completion, not a stronger final lower bound.

No dense repairs are triggered on markshare or binkar. Both binkar runs retain
the earlier6747.310015 incumbent, with five neighbourhood-improvement calls.
Their last improvements occur at62.8775/64.8002 seconds; neighbourhood budgets
are exhausted around27 seconds of cumulative work. The remaining global proof
gap is still about1.22%. The separate30-second reference returns6746.760023
but times out; this reference incumbent is not a proven optimum. Markshare's
reference also times out, with incumbent3, versus our approximately5.

## Independent checks

- CTest3/3;240/240 generated checks (80 generated models across three modes).
- All five final incumbents independently satisfy ORIGINAL MPS constraints and
  integrality. The no-incumbent baseline is not counted as a valid solution.
- An additional fresh audit checks all five final vectors and both captured
  accepted dense-repair vectors:7/7 pass. Maximum absolute violation is about
  6e-9; all integer violations are zero. The final blend2 point's maximum
  absolute violation is4.5475e-13.
- Binary/core/test/model identity, validation-source hashes, CMake cache,
  raw/generated aggregates, equal budgets, incumbent-trace monotonicity,
  captured integer rounding and reported-gap arithmetic pass.
- No unsafe/error run is flagged. Exactly one of six hard runs completes with
  a checked candidate matching an independently proven reference optimum.

Raw data: `local-180s/`. Additional audit: `local-180s-audit/AUDIT.json`.
Only final vectors and captured repairs can be independently recomputed;
uncaptured historical incumbents have objective-only traces. Numerical bound
checks are not exact or interval certificates.

## Decision and next local iteration

Retain candidate repair as opt-in pending broader/repeated evidence. The shared
proof correction remains enabled in both modes. Do not request another CPU-only
Kaggle run or repeat the unchanged notebook.

Prioritize a separately versioned binkar experiment on neighbourhood selection
and budget use: it plateaus well before the deadline while the incumbent and
proof bound remain improvable. Compare against this exact baseline under equal
local budgets, preserving original feasibility/integrality checks and all
failures. Keep markshare as a difficult search/bound stress test, not a solved
case. Recheck blend2 completion and adversarial proof regressions whenever the
shared search changes. Broader repeated and industrial validation remain open.
