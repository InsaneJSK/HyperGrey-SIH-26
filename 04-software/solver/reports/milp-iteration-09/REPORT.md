# MILP iteration09 — compact equations, measured cautiously

15 September 2026. Separate final candidate: `build-milp-iter9b`.
The compact LP representation passes correctness checks, but its root speed
advantage does not establish a meaningful full-MILP improvement. The final
180s delayed-activation pair retains Binkar's incumbent and changes the gap
only marginally: 0.95742% to 0.95441%. Both runs remain incomplete.

The separately budgeted 600s attempt reaches lower bound 6686.056417 and gap
0.90769%, with the same incumbent 6747.310015. It stops at `time_limit` after
604.303s and **does not prove Binkar optimal**. The extra runtime produces only
modest bound progress. No new exact-optimality achievement is claimed here.

## Final equal-budget comparison

One run per profile/model, sequential, alternating order. P0033 control then
delayed compact; Binkar delayed compact then control. Both profiles use LP
recovery, guided incumbent improvement, candidate repair and delayed lifted
covers. The only strategy difference is delayed compact equality activation.
Limits: 180s, 250000 nodes, relative gap 1e-6. No external solution is seeded.

| Model | Mode | Objective | Lower bound | Reported gap | Seconds | Nodes |
|---|---|---:|---:|---:|---:|---:|
| Binkar | Ordinary LP control | 6747.310015 | 6682.700412 | 0.95742% | 180.237 | 4979 |
| Binkar | Delayed compact LP | 6747.310015 | 6682.903189 | 0.95441% | 180.469 | 5825 |
| P0033 | Ordinary LP control | 3089 | 3089 | 0 | 0.098 | 277 |
| P0033 | Delayed compact LP | 3089 | 3089 | 0 | 0.087 | 277 |

The Binkar gap change is only about 0.003 percentage points. More processed
nodes and a slightly stronger bound are not sufficient to claim a general
speedup. The P0033 timing difference is small-run variability; it solves before
either delayed mode activates. Measured time-limit overruns are preserved.

## Longer proof attempt — still incomplete

One independent 600s run of delayed compact mode, same binary, 250000-node
limit and 1e-6 gap target. It processes 20431 nodes and 565762 LP iterations.
The half-time restart occurs at 300.032s after 9959 nodes, carrying its own
6747.310015 incumbent and global lower bound 6667.065617. Its final lower bound
is 6686.056417, gap 0.90769%, with no compact fallback, global LP recovery or
unresolved-node count. The 4.303s cooperative time-limit overrun is reported,
not rounded away. Absence of unresolved LP nodes does not mean the live MILP
tree is exhausted; the status remains `time_limit`.

The [independent long-run audit](proof-attempt-audit/AUDIT.json) rechecks all
23 retained lifted cuts and 7 saved neighborhood/restart/final vectors, plus
78 timing-source identities, raw results, commands, limits and gap arithmetic.
Maximum checked vector violation is below 1e-8 under the unchanged 1e-7 gate.
The separate exact Markshare sentinel passes again.

This is a larger-budget attempt, not an equal-time comparison or evidence of
speedup. It suggests that stronger bounds/search are needed alongside cheaper
LP solves. Simply allocating more time has not closed the remaining gap.

## Implementation and failed experiment

Binkar has 1016 equality rows. The sparse LP engine previously represented
each as two inequalities. The new opt-in mode stores each equation once,
allows its dual multiplier either sign, and removes Phase-I artificial
variables before Phase II. Artificial columns cannot reenter or be warm-start
columns. Equality rays satisfy both signs. Unchanged original-model and
numerical certificate checks remain mandatory; unsupported/dependent cases
can fall back within the remaining wall-clock budget.

The [first immediate-mode experiment](DIRECT_EXPERIMENT.md) reduces a root
screen from 10.710s to 7.192s at the same bound, but regresses the 180s incumbent
to 6772.83 and gap to 1.340%. It is preserved, not promoted. The delayed variant
keeps the earlier representation for incumbent search, then activates compact
LPs at the existing half-time full-domain cut restart. It keeps the same-run
incumbent and valid global bound without resetting time, nodes or spent search
budgets. No instance names or published answers enter the algorithm.

Both modes stay optional. Details: [compact equation method](../../docs/COMPACT_EQUALITY_LP.md).

## Verification

- CTest 7/7, including analytical equality/dual/infeasibility/ray/warm/fallback
  guards, 300 generated LP comparisons, 80 mixed MILP comparisons, and
  deterministic min/max delayed activation and incumbent-retention checks.
- Generated MILP 240/240: 80 models under three profiles, not 240 distinct
  public benchmarks. Earlier exhaustive cut/proof CTest groups remain passing.
- Additional independent HiGHS checks 90/90: 60 bounded equality LPs including
  maximization and dependent rows, 15 infeasible systems, and 15 unbounded
  systems with original-equation ray checks. Fifteen dependent-row fallbacks
  occur as intended. These are numerical cross-checks, not general exact proofs.
- The final pair's [audit](delayed-audit/AUDIT.json) checks all 48 retained lifted
  cuts, 16 available final/restart/neighborhood vectors, 77 timing-source
  identities, model/binary hashes, budgets, incumbent traces and gap arithmetic.
- [Nonregression](NONREGRESSION.json): all 80 control generated outputs match
  iteration08's delayed-cut profile on status, objective, primal, bound, gap,
  node and iteration counts, excluding time and new diagnostics.
- Markshare's independent original-literal proof sentinel remains objective 1,
  bound 1, gap zero. That restricted proof engine cannot certify Binkar.
- Final post-timing CTest 7/7 and diagnostic/parser/exact-checker/cut-checker
  unit tests 33/33 pass. Logs: `FINAL_CTEST.log` and `CHECKER_TESTS.log`.

## Scope and evidence

Final candidate CLI SHA256:
`3335c4cc5a41bf5f3581a39ef10aa43f82ad40402e0294990032063b0e503ed1`.
Windows, Intel i5-10210U, GCC 14.2, CMake 3.30.4 Release, CUDA OFF.
Source/numerical binary are separate from the earlier iteration08 and from
this iteration's immediate-mode experiment.

Evidence: [paired protocol](delayed-180s/metadata.json),
[raw results](delayed-180s/results.json), [summary](delayed-180s/summary.json),
[independent LP checks](independent-lp/SUMMARY.json), and
[external benchmark context](REFERENCE_CONTEXT.md).
The final source/binary archive and hashes are in [FINAL_STATE.json](FINAL_STATE.json).
The 600s raw run is in [proof-attempt-600s/results.json](proof-attempt-600s/results.json).

General LP/MILP bounds remain numerical, not exact rational certificates.
Cut validity is exact for guarded parsed binary64 rows, not arbitrary decimal
MPS literals. Audits cover saved vectors, not all objective-only intermediate
incumbents or every internal LP dual bound. There is no new broad QP/GPU sweep,
industrial validation, million-variable MILP evidence or full-library coverage.
No GPU/Kaggle run, notebook or user result upload is needed.

## Submission position and next step

This cycle adds a tested LP representation and reproducible negative as well
as positive evidence. It does not make Binkar solved or justify an elite ranking
claim. Markshare's earlier restricted exact proof and Blend2's earlier checked
numerical optimum remain separate achievements; no new Blend2 long run was
performed in this cycle. Continue with [the bounded next investigation](NEXT_STEP.md),
then stronger general bounds and broader equal-budget validation. All of that
can begin locally without a new user artifact.
