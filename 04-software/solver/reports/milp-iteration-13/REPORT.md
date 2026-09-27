# MILP iteration13 — separate search priority and proof accounting

15 September 2026. CPU only, build `build-milp-iter13`.

## Result and scope

The candidate adds optional raw-LP queue ordering without using that queue's
top as the global proof minimum. This makes the ranking/proof boundary explicit
and independently replayable. It is not a new exact general-MILP certificate.
The 17-model paired wave has **7 completions per policy**, with mixed partial
outcomes. No general completion-rate or speed improvement is established.
Both `--objective-lattice` and `--raw-lp-priority` remain OFF by default.

Completed the predeclared experiments and correctness gates. The final audit
passes all 84 retained experiment runs across 21 distinct public models, with
zero observed validation failures. This is evidence of tested behavior, not
a universal correctness theorem or a claim that all those models were solved.

## Implementation

- `include/milp_frontier.hpp`: ranking heap plus separate `(proof bound, ID)`
  multiset in raw-priority mode. The legacy policy retains proof-bound ranking
  without allocating the extra index. Depth and ID tie-breaks are unchanged.
- Each node carries a monotone unrounded, safety-adjusted LP `search_bound`
  and a separate lattice-strengthened numerical `bound`.
- Pruning retains the strengthened bound. Global gap, restart inheritance and
  final reporting use the minimum over ALL queued/deferred proof bounds and
  the incumbent. Search-top bound is diagnostic only.
- Full-original-domain restarts clear both indexes, preserve the selected
  policy, inherit the global proof minimum and reset the raw search key.
- `--capture-frontier` records push/pop/defer/reset/checkpoint events, with
  explicit infinities and a 20000-event prefix limit. Independent replay checks
  selection, membership/counts, deferred minima and restart/global-bound logic.

No benchmark-name rules, reference incumbents or published objective targets
are used. HiGHS remains a separate read/check/reference worker, not part of the
optimization core. Earlier parser and candidate-repair correctness fixes remain.
See [method and limitations](../../docs/MILP_FRONTIER.md).

## Protocol and timing limitation

The [predeclared plan](PLAN.md) separates fixed-node, paired-wave, repeated-target
and untouched-holdout experiments. Own solves run sequentially before reference
work within each experiment. Full runs use 30s, 250000 nodes, gap tolerance
1e-6, an external 45s watchdog and the existing recovery/heuristic/late-cut
profile. References have 5s and one thread; they are validation workers, NOT an
equal-budget solver-speed comparison. No tolerances are loosened.

The desktop was not controlled/idle. On egout, iteration12 and iteration13
lattice runs have identical 3827 nodes, 15627 LP iterations, 386 heuristic
solves and 4172 warm starts, but elapsed times 2.46s and 7.22s. This establishes
a timing difference at equal recorded work, not its isolated cause. A CPU
snapshot showed substantial background activity; no user process or power plan
was changed. Two read-only diagnostics overlapped the lseu/mod008 wave portion.
All outcomes remain saved. See [timing conditions](TIMING_CONDITIONS.md).

Consequently, the earlier iteration12 10-versus-9 completion result and repeated
mod008 completion are preserved historical evidence, not a promise for every
30s run on this desktop. The present wave does not reproduce that completion
count, and we do not attribute the difference solely to code or solely to load.

## Fixed-node screen — completed

Four models, three profiles, two repeats: **24 runs**. Node cap 2048, gap 0,
no heuristics or cuts; 120s safety cap. All hit the node cap, all validation
checks pass, and all **12 model/profile pairs** have identical semantic outputs
and captured search traces across repeats. All saved frontier traces are full.
No model closes at this small node budget. Only misc03 returns an incumbent.

Frontier capture is disabled in the 60 timed experiment runs. Public frontier
replay therefore covers these 24 fixed-node traces, not every event of every
timed search. The separate short integration checks add restart/deferral coverage.

| Model | Control bound | Lattice bound | Raw-ordering bound |
|---|---:|---:|---:|
| gt2 | 13899.065101 | ~13900 | ~13900 |
| lseu | 1011.893376 | ~1012 | ~1012 |
| mod008 | 301.900568 | ~302 | ~302 |
| misc03 | 3277.499672 | ~3280 | ~3280 |

Strengthened values are published just below the displayed lattice point by
the existing outward guard. This demonstrates repeatability and retained bound
strength, not a node-budget completion gain or exact validity of raw LP bounds.
Evidence: [screen summary](node-screen/SUMMARY.json).

## All 17 paired-wave outcomes

Lattice and raw profiles differ only by `--raw-lp-priority`. Both have:
**2 restricted exact proofs, 5 checked numerical completions, 7 checked feasible
limits and 3 no-incumbent limits**. Zero observed validation failures.

| Model | Lattice policy | Raw-LP priority |
|---|---|---|
| p0033 | Exact 3089 | Exact 3089 |
| enigma | Numerical completion 0 | Numerical completion 0 |
| flugpl | Numerical completion 1201500 | Numerical completion 1201500 |
| stein27 | Numerical completion 18 | Numerical completion 18 |
| markshare_4_0 | Exact 1 | Exact 1 |
| blend2 | No point; bound 7.325419 | No point; bound 7.398656 |
| binkar10_1 | No point; bound 6645.513139 | No point; bound 6645.513139 |
| egout | Numerical completion 568.1007 | Numerical completion 568.1007 |
| gt2 | Point 92866; gap 85.0033% | Point 42649; gap 67.3458% |
| lseu | Numerical completion 1120 | Numerical completion 1120 |
| mod008 | Point 307; gap 0.6494% | Point 307; gap 0.6494% |
| p0201 | Point 7735; gap 2.3268% | Point 7735; gap 2.1975% |
| p0282 | Point 266462; gap 3.9165% | Point 264979; gap 3.3787% |
| misc03 | Point ~3360; gap 12.3475% | Point ~3360; gap 13.6864% |
| misc07 | No point; bound ~1415 | No point; bound ~1415 |
| pk1 | Point ~30; gap 96.7742% | Point 33; gap 97.0588% |
| rgn | Point ~82.2; gap 0.7212% | Point ~82.2; gap 1.6827% |

Gaps use the solver's `(incumbent-bound)/(1+abs(incumbent))` convention for these
minimization cases. Values are rounded here; raw JSON remains authoritative.
The two policies find better/worse points or bounds on different cases.
Neither dominates. A matching known objective with an open gap is NOT proof.
Evidence: [wave summary](wave1-paired-30s/SUMMARY.json) and
[all raw outcomes](wave1-paired-30s/results.json).

## Repeated targets

Three fresh 30s runs for each of control (no lattice), lattice ordering and raw
ordering on gt2 and mod008, rotating order. These are separate from the wave.
Treat every timeout as censored, never as a completed 30s solve time.

For gt2, all three raw runs and all three controls return objective 42649;
all three lattice-ordering runs return 92866. Median reported gaps are about
67.3388% raw, 67.3391% control and 85.0001% lattice. All nine runs remain open.
This supports restoring the better incumbent while retaining lattice bounds,
not an improvement over the control's incumbent or a proof-gap closure.

All nine mod008 runs return objective 307 without closing at 30s. The lattice
and raw policies finish at bound ~305, reported gap 0.6494%, in every repeat;
the control's median bound is 304.400113 and median gap 0.8441%. Thus both
strengthening profiles retain the stronger bound under these conditions but
do not repeat the earlier completion. All 18 final points and result
classifications pass the independent checks. Evidence:
[repeat summary](target-repeats-30s/SUMMARY.json).

## Untouched holdout

The [selection plan](HOLDOUT_PLAN.md) was written before solving these models.
Four members of the [official MIPLIB2017 benchmark](https://miplib.zib.de/tag_benchmark.html)
were selected by size and structure, not our solver's outcomes. Some originated
in earlier collections; this is not a representative sample of the full library.
Official compressed/MPS files, sources and hashes are retained in the
[download manifest](../../datasets/milp-frontier-holdout/manifest.json).

| Model | Lattice policy | Raw-LP priority |
|---|---|---|
| gen-ip002 | Point -4681.758266; gap 2.9661% | Same point; gap 2.9537% |
| assign1-5-8 | Point ~228; gap 18.1067% | Same point; gap 18.0658% |
| lotsize | No point; bound 371214.933914 | No point; bound 370233.022809 |
| eil33-2 | No point; bound 816.875853 | No point; bound 816.875853 |

All eight runs reach their 30s limit. Neither policy completes a case. No case
was swapped or removed. All four objective structures are ineligible for the
current lattice detector: nonintegral/out-of-range effective costs on gen-ip002
and eil33-2, and continuous objective terms without a supported unit definition
on assign1-5-8 and lotsize. They retain numerical LP bounds. Raw ranking can
still differ after a restart inherits a stronger global proof floor; short
wall-clock changes are not isolated as search-policy gains.

The largest selected model has 4516 columns, not millions. The 16M-cell guard
applies to dense fallback only, NOT total process memory. No RSS measurements
or total process-memory limit are claimed. References and validation follow
the timed solves; full outcome ledger:
[holdout results](holdout-30s/results.json).

The four saved holdout points pass independent original-model row, bound,
integrality and objective checks. All eight 5s HiGHS reference solves also
time out; none supplies a completed-reference optimality comparison. HiGHS
finds points on gen-ip002, assign1-5-8 and eil33-2, but not lotsize. On lotsize
there is therefore no saved independent feasible point against which to test
our bound. Zero observed validation failures must not be read as exact proof
of all reported bounds or a completed solve of these difficult models.

## Final correctness gate and archive

The [post-timing gate](final-gate/SUMMARY.json) passes:

- All 11 CTest groups and 79 Python checker/classifier unit tests (14 new
  frontier mutation tests).
- 100000 randomized queue operations against independent linear scans.
- 240 new exhaustive C++ models across three profiles: 720 complete solves,
  1440 partial/zero-time checks and 93 exercised restarts. Includes min/max,
  negative general-integer domains and unit-defined continuous objectives.
- LP-iteration-limit and deferred-node safety cases.
- 28 independently checked MPS integer-marker domain cases.
- 240 generated regression runs: 40 binary and 40 mixed models in each of
  control/lattice/raw profiles. These are 80 distinct models, not 240.
- The 100 retained iteration12 exhaustive MPS cases rerun with raw priority,
  independent HiGHS/original-model/expected-optimum checks and 1300 fully
  replayed frontier events. These inputs were reused, not newly invented.
- Three short public integration runs each replay one late full-domain reset;
  their traces contain 15447, 2055 and 689 events. A separate five-event
  interrupted-LP case checks retained deferral. These are correctness checks,
  not additional performance comparisons or public completions.

The [final re-audit](final-audit/AUDIT.json) verifies binary/core/helper/model/
command/result identities, recomputes saved checks and passes all 84 experiment
records. Totals: **56 saved final-point checks, 186648 frontier events replayed,
173428 SAVED lattice events, 22 retained cuts and four exact proofs recomputed
on two distinct models**. All 24 captured public frontier traces are full;
26 lattice traces are explicitly truncated at4096 improvements. Unsaved events
and raw LP bounds are not independently certified by that count. Supplemental
integration and generated-model checks are listed separately above.

Binary SHA256:
`bdfdb8fc7a21d411d47557f093e728e018e86960c359f86573393711b5b4757e`.
The [frozen state](FINAL_STATE.json) identifies the separate archived executable,
source snapshot, build cache and evidence hashes. Core and timed helpers did
not change after the first measured run; no post-holdout tuning was performed.
The archive procedure verifies the preserved iteration12 source/binary and
iteration11/10 binaries before creating a new snapshot. It refuses replacement.
See [reproduction](../../docs/V2_REPRODUCE.md); no GPU was used.

## Submission position and next step

Across the combined 17-model timed wave and four holdouts, EACH compared policy
has **7 completions (2 exact-subset, 5 numerical), 9 checked feasible-but-open
outcomes and 5 no-incumbent outcomes**. The new tests make this a more defensible
research prototype. They do not establish full MIPLIB coverage, arbitrary MILP
proof, consistent industrial-scale convergence or a top-0.1% competition rank.
The repeated gt2 incumbent restoration is real within this experiment; overall
completion and several other gaps still need substantial improvement.

The [next local cycle](NEXT_STEP.md) targets phase/work attribution and better
budget-controlled feasibility progress, followed by stronger general relaxation
bounds and resource-guarded broader waves. The four holdouts are now development
cases, so future tuning needs additional untouched inputs. Domain review,
applicable final GPU repetitions and a frozen submission demonstration remain
separate outstanding work. No CPU-only Kaggle run or user upload is needed.
