# Iteration 30 — bounded dual-simplex relaxations: promoted evaluation profile

17 September 2026. A new, independently written LP engine for MILP
relaxations (`--bounded-lp`) passes the full correctness gate and every
declared comparison with **zero validation failures**. At the same 30-second
budget on the same executable and host it raises development completions from
17 to 23 records, fresh untouched-holdout completions from 1 to 5, and checked
LP completions from 15/16 to 16/16. The candidate becomes the recommended MILP
evaluation profile. The executable default is unchanged, as declared.

| Set (serial, 30 s, same executable) | Control completions | Candidate completions | Control checked points | Candidate checked points | Validation failures |
|---|---:|---:|---:|---:|---:|
| Development, 27 reused models × 2 repeats | 17 | **23** | 46/54 | **48/54** | 0 |
| Iteration 28 holdout, 6 models | 0 | 0 | 5/6 | 5/6 | 0 |
| Fresh untouched holdout, 15 models | 1 | **5** | 10/15 | **14/15** | 0 |

| LP track, 16 public LPs | Default method | Bounded method |
|---|---:|---:|
| Checked completions (HiGHS comparison) | 15/16 | **16/16** |
| False optimal claims | 0 | 0 |

Completions are records whose status is independently checked: numerical
completions, exact proofs, and corroborated terminal statuses. The 5-second
development reference timed out on `neos859080` in three of four records, so
the harness keeps those infeasibility claims as `terminal_reference_pending`;
a separately labeled 60-second HiGHS run confirms infeasibility
(`supplementary-reference/`). Counting that corroboration, development
completions are 19 (control) and 24 (candidate).

## What changed

Two separately reported changes, one executable
(`final_solver_cli.exe`, SHA-256 `2bc720db…9d10`, `SOURCE_IDENTITY.json`):

1. **Relaxation engine (`--bounded-lp`).** `src/bounded_simplex.cpp` replaces
   the sparse simplex for root, cut, tree, dive, neighborhood and
   strong-branching relaxations. Rows are ranged logicals and bounds stay on
   variables, so a child reuses its parent's basis without new rows.
   Gilbert-Peierls sparse LU with product-form updates, dual steepest-edge
   pricing, a Harris bound-flipping ratio test, per-variable tolerances derived
   from original-space targets, and a primal cleanup phase. Infeasible nodes
   end only with a Farkas ray re-checked on the original rows and bounds; nodes
   stop early only when an extended-precision Lagrangian bound reaches the
   incumbent margin; optimal results pass the same original-model checks as
   the old engine. Anything unverified is solved by the old engine. Method and
   limits: [`docs/BOUNDED_SIMPLEX.md`](../../docs/BOUNDED_SIMPLEX.md). An
   open-node memory guard is active only with the flag; it never triggered.
2. **MPS reader conformance.** The first fresh-holdout launch stopped at input
   rejections in both profiles (retained in `fresh-30s-attempt1-reader`). The
   C++ reader and the independent Python exact checker now drop later `N` rows
   with their entries, ignore text after `ENDATA`, and ignore an optional
   numeric value on `BV/MI/PL/FR` bounds. Parsed dimensions match HiGHS on the
   affected models; see the plan amendment and limitation L-10.

Private pump/distance LPs, candidate repair and all acceptance and proof rules
are unchanged. With the flag off, the executable reproduces frozen 16 on the
disabled-parity models.

## Correctness gate (before timed runs)

`sparse_accuracy_gate.py --bounded-lp` on the frozen executable (`gate/`):

- 27/27 CTest groups, including `bounded_simplex_regressions`: 3,000 random
  bounded LPs against the old engine with 2,175 matching optimal objectives,
  631 agreeing infeasibility claims, 1,746 warm/cold and 1,633 added-row
  comparisons, 542 verified cutoffs and zero unexplained unverified outcomes.
  The extended MPS contract test covers 32 marker models plus free-row,
  trailing-text, optional-bound-value and duplicate-name cases.
- 180 Python tests, including the new `check_bounded_lp.py` tests.
- Disabled parity against frozen 16 on gt2, lseu, mod008 and misc03.
- 400 generated binary/mixed runs over five profiles, including a
  bounded-engine profile, all matching exhaustive enumeration.
- The 100 retained lattice cases under both engines (200 runs), all numerical
  completions at their expected objectives with independent references.

The first frozen executable (strict reader) passed the same gate and is
retained in `superseded-strict-reader/`.

## Development set

The candidate keeps every control completion and adds `mod008` and `misc03`
in both repeats and `p0201` in the repeat the control missed.
[`COMPARISON.md`](COMPARISON.md) has every record; highlights:

| Model | Control (two repeats) | Candidate (two repeats) | Published optimum |
|---|---|---|---:|
| misc07 | no point; 3970, gap 62.2% | **2810**, gaps 17.4% / 17.1% | 2810 |
| assign1-5-8 | 220 / 221, gaps 14.8% / 15.3% | **212**, gap 10.2% | 212 |
| mas74 | 13588.56, gap 19.9% | **12590.37**, gap 12.6% | 11801.19 |
| pk1 | 30 / 28, gaps 96.8% / 96.6% | **17**, gaps 59.1% / 59.4% | 11 |
| eil33-2 | 1207.18; no point | **989.39**, gap 11.6% | 934.01 |
| blend2 | 8.788661, gaps 13.9% / 14.1% | 7.971 / 8.082, gaps 4.2% / 5.3% | 7.598985 |
| binkar10_1 | 7127.78 / 6810.69 | **6759.38**, gap 1.1% | 6742.20 |
| gt2 | **35673**, gap 60.9% | 50894, gap 72.6% | 21166 |
| rout | 1293.19 / **1136.17** | 1238.12 / 1305.77 | 1077.56 |

Nodes explored in the first repeat rise from 390 to 126,931 on pk1, 37 to
13,990 on misc07, 52 to 2,721 on eil33-2, 3 to 240 on danoint, 348 to 11,466
on assign1-5-8 and 28,083 to 303,087 on gt2. These are fixed-budget counts,
not speedup ratios.

**Regressions and unresolved cases, retained:**

- gt2's incumbent is worse in both repeats (50894 vs 35673) although its bound
  is slightly stronger (13959 vs 13931/13935); the faster tree follows a different trajectory and
  finds fewer good leaves. Incumbent quality, not bounds, now limits it.
- rout is mixed: one control repeat found 1136.17, better than either
  candidate repeat.
- lotsize and danoint have no incumbent in either profile on this host.
  Iteration 28 found a danoint point on a different machine; timings here are
  not comparable across hosts.
- The control completed mod008 and p0201 on the iteration 28 host but here
  misses mod008 in both repeats and p0201 in one; all comparisons in this
  report are same-host.

## Holdouts

**Fresh untouched set** (declared in [`HOLDOUT_SELECTION.md`](HOLDOUT_SELECTION.md)
before download; never solved by this project before). A complete post-run
text search of the project, outer planning files and delivery folder,
excluding only this iteration's folders, found none of the 15 names except the
English word "fiber" in the bell3a/bell5 header comments ("fiber optic network
design") and two third-party Python files.

- Candidate completes dcmulti (188182), dsbmip (−305.198), khb05250
  (106940226), misc06 (12850.86) and mod010 (6548); the control completes only
  misc06. All five candidate values equal the published optima.
- The control ends with unresolved LP relaxations on dsbmip and gesa3 at the
  root and on stein45 after 10 nodes (`unresolved_relaxations`). The candidate finds gesa3's published optimal
  objective with a 0.20% remaining bound gap, and stein45 at 32 (optimum 30)
  with a 15.2% gap; the control's stein45 point is also 32.
- Candidate points are better on fixnet6 (4977 vs 10904; optimum 3983), fiber
  (2273923 vs 3222528), l152lav (4741 vs 4998), modglob and qiu.
- Worse on pp08a (8990 vs 8760) and set1ch (86647 vs 81695). Neither profile
  finds a p0548 point. Two candidate LPs fell back to the old engine.

**Iteration 28 holdout:** no completions in either profile, five checked
points each. The candidate improves vpm2 (14.25 vs 17.5) and the vpm1/bell3a
gaps, and is worse on bell5 (9083879 vs 9001766) and noswot (−40 vs −41).
Neither finds a gesa2 point on this host.

## LP track

`lp-track/` runs the 16 LPs of the current-source LP study with the default
and bounded methods on the frozen executable, with HiGHS references. The
bounded method completes all 16 with default settings, including `bandm`
(833 pivots), where the default method still returns `numerical_error`.
`degen2` needs 919 pivots instead of 2,949. No method makes a false optimal
claim.

## Resources

Peak sampled commit is 594 MiB (gt2, candidate) against the 1,536 MiB
threshold; the control's peak is 146 MiB. No watchdog stop, process failure
or memory-guard stop occurred in any timed set. Faster nodes grow the frontier;
this is the main resource cost of the change.

## Decision

The declared promotion rule holds: zero validation failures in every set;
candidate completions at least the control's in the development set and the
fresh holdout; no lost control completion; checked-point coverage does not
fall. The candidate profile (`CANDIDATE_PROFILE.json`: iteration 28 flags plus
`--bounded-lp`, node limit 100,000,000) is the recommended MILP evaluation
profile, and `--lp-method bounded` the recommended LP method. Executable
defaults are unchanged in this iteration; making them default is a separate,
explicit decision.

This is a moderate public benchmark improvement, not industrial-scale
evidence: the largest models here have a few thousand columns, lotsize and
p0548 still lack points, and incumbent quality now limits several models.

## Next

1. Search for the fast engine: periodic incumbent-phase dives and an
   incumbent-guided mode; fix-and-propagate first-point search for lotsize,
   p0548 and gesa2-type models; test removing the half-time restart that
   discards the faster tree.
2. Stronger bounds: Gomory mixed-integer cuts from bounded tableau rows, and
   reliability branching now that strong-branching probes are cheap.
3. Larger LP/MILP instances (Mittelmann scale), a refinery case study, and a
   decision on changing the executable defaults.
