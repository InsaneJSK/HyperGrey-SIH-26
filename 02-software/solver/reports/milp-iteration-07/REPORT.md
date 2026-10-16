# MILP iteration07 — markshare proof gap closed locally

15 September 2026. CPU-only, separate `build-milp-iter7` and preserved previous
builds. The new opt-in `--binary-proof` certifies **markshare_4_0 optimum 1 with
zero gap**, reproduced three times and independently recomputed from the
original MPS literals. P0033 is also verified, but is slower in exact mode.

## Equal-budget repeated comparison

Same current binary, same guided/recovery/repair/old-meet settings; only
`--binary-proof` differs. Twelve sequential runs, alternating profile order,
30-second / 250,000-node / gap1e-6 limits, three repetitions per row below.
Times are the CLI's total solve seconds, excluding independent validation.
All references and independent proof checks ran after the timed comparisons.

| Model | Mode | Final objective | Reported gap | Solve time range | Status in all 3 runs |
|---|---|---:|---:|---:|---|
| markshare_4_0 | Existing binary-meet | 0.999999998 | 50.000005% | 30.00120–30.00132s | time_limit |
| markshare_4_0 | New binary-proof | 1 | 0 | 0.65298–0.73051s | optimal |
| p0033 | Existing binary-meet | 3089 | 0 | 0.08345–0.08602s | optimal |
| p0033 | New binary-proof | 3089 | 0 | 0.45823–0.47680s | optimal |

The existing markshare point is about2e-9 below1 due to floating feasibility
tolerance, not a meaningful improvement below the exact optimum. Exact-mode
original witnesses have zero violation. Its bound is exactly1, not the old
safety-margin lower bound near0. The existing gap convention divides by
1+abs(incumbent), hence its roughly50% figure.

The exact mode returns at root before LP solves: one main node and zero LP
iterations, but millions of separately recorded private enumeration/query
operations. This is not a constant-work result. P0033 shows a real overhead
versus the existing path; there is no universal speedup or default promotion.

## What establishes the proof

The [new engine](../../include/binary_proof.hpp) uses a separate checked-integer
reduction, subset enumeration and range-tree join. It never uses the old
floating incumbent as an exact cutoff. It requires full completion and checks
the reconstructed witness against the original model before publishing a bound.

The [independent checker](../../scripts/exact_binary_check.py) reads original
decimal literals as exact fractions and uses unbounded Python integers and a
different variable partition/data structure. All six public checks pass:

- Markshare: a nonnegative integral objective means any value better than1 must
  be0. An independent equality hash join excludes all objective-zero points;
  an exact feasible objective-one witness supplies the matching upper bound.
  This is selected by structural conditions, not the model name or a known answer.
  Checker time0.147–0.169s, separately from solver timing.
- P0033: an independent integer range join excludes every better point and
  verifies the3089 witness. Checker time24.25–33.69s, separately from solver timing.

HiGHS checks all12 final candidates against its independently loaded original
MPS. It also solves p0033 to numerical3089. Its30s markshare reference still
times out with incumbent3; **HiGHS did not prove markshare in this protocol**.
The proof comes from independent exhaustive integer reasoning, not that timeout
or a published optimum. This checker recomputes the proof; it is not a compact
proof trace or a formally verified implementation.

## Scope and safe fallback

Eligible models have1–36 movable binaries bounded exactly[0,1],1–32 rows,
at most128 original columns, integral coefficients/costs/finite bounds/offset,
and only fixed integer variables or single-equality, unit-coefficient continuous
recourse besides the binaries. Checked envelopes are capped at2^50; actual
arithmetic uses signed64-bit integers. The MPS literal guard rejects fractional
values even if ordinary parsing rounds them to integers, and unsafe accumulated
coefficients. Ordinary floating parser values remain unchanged.

Time/work/range/resource failures cannot publish a proof bound. A partially
found, independently checked feasible point may still seed the ordinary solver.
Unsupported domains fall back. Default flags remain unchanged; explicit
`--binary-proof` still runs with `--no-heuristics` because it is not a heuristic.
At most min(5s,10% global budget, remaining budget) is reserved for the attempt;
the default work limit is50million. Fixed-size coordinates/tree storage can
approach roughly90MiB at the largest split (estimate, not a measured RSS peak).
Allocations/partitions and other operations may slightly overrun cooperative
time checks. See [method, guards and reproduction](../../docs/MILP_BINARY_PROOF.md).

## Validation and provenance

- CTest **5/5**, including600 new exhaustive small-model proof cases and180
  pre-existing meet-heuristic cases; infeasibility, maximization, offsets, recourse,
  work/deadline limits, unsafe arithmetic/input literals and fallback are covered.
- Generated **240/240** across three profiles; **40** generated exact proofs
  independently checked. All40 unsupported mixed-model exact attempts return
  verified=false and their ordinary solves still pass.
- **6/6** public independent exact proofs and **12/12** final candidate checks.
- Diagnostic tests15/15, result parser3/3, independent checker tests9/9.
- Supplementary signed-overflow-trapping (`-ftrapv`) arithmetic probe:98/98.
- **160/160** generated guided/old-meet numerical results match iteration06:
  status/objective/primal/bound/gap/nodes/LP iterations/pass flags. Timings and
  new diagnostics are excluded. See [nonregression record](NONREGRESSION.json).
- [Provenance audit](AUDIT.json) passes all67 timing-source identities,
  binary/CMake/cache identity, dataset manifest hashes, budgets, run grid,
  aggregate/raw equality and independent checker/result/model hash links.
  It also replays the40 generated proofs.

CLI SHA256:
`3e623c0cec0a943d042a1310be84f0962dbeaec021de7220f705dd1c6f8f7a90`.
Windows11, Intel i5-10210U, GCC14.2, CMake3.30.4 Release, CUDAOFF.
[Raw protocol/results](local-proof-validation/metadata.json),
[summary](local-proof-validation/summary.json),
[independent checks](local-proof-validation/exact_checks.json).
Final source/binary snapshots and their verification are recorded in
[FINAL_STATE.json](FINAL_STATE.json). The supplementary audit script, arithmetic
probe and final reporting docs were added after timing, with no core changes.
Prior binaries, snapshots, reports and Kaggle artifacts remain preserved.

## Submission position and next target

This adds a reproducible exact proof result for a difficult small structured
MILP. It does not establish an industrial general-purpose exact MILP solver:
only two eligible public models have been tested in this cycle. Binkar's prior
best6747.31/about1.22% gap remains open; blend2's earlier checked numerical
optimum remains historical evidence. Neither has a new long-run claim here.
Next CPU work should target binkar's general search/bound bottleneck and broaden
public-model validation. LP/QP/CUDA numerical modules are unchanged, and no new
QP/GPU sweep occurred. No Kaggle run or user result upload is needed now.
