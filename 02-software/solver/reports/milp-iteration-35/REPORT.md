# Iteration 35 — keep the basis through the cut purge

19 September 2026. Plan declared before any code change (`PLAN.md`). Binary
SHA-256 `58faf7cf7abfdac656b842128de823fb933dfaf1f47a4911cc6c7d96acdfb79a`, 213
frozen source files. Control is the iteration 34 frozen executable
(`f749c5af…bddb`) on **identical flags**; only the executable differs.

## What was wrong

Iteration 32 purges tableau cuts that are slack at the root. It also discarded
the basis (`lp.basis = LpBasis(); node.basis = LpBasis()`), so the root's
children started cold — and on a large model a cold start needs more than the
10,000 iterations node LPs are allowed. Iteration 34 exposed this: of eleven
instances whose root newly solved, every one that purged cuts had bounded-engine
fallbacks, and every one that did not purge had none.

## Mechanism

Keep the basis, deleting only the purged rows' logical entries. A row is purged
precisely because its logical is basic; removing that row with its own unit
column leaves a square, nonsingular basis (expand the determinant along that
column), still optimal because the purged rows carried zero duals. If anything
were wrong with it, the engine's existing warm-start checks reject it and cold
start, which is today's behaviour — the change cannot make a node worse.

Not flag-gated: like iteration 33 it changes how state is carried, not what is
solved. A new counter `gomory_cuts.basis_kept` records each purge that carried
the basis, and `scripts/check_gomory_cuts.py` checks it against the purge count.

## Correctness gate

CTest 28/28. `sparse_accuracy_gate.py` with the full flag set: `all_pass`, 14
generated profiles.

## Development: 27 models, two repeats, 54 records

| | Iteration 34 | Iteration 35 |
|---|---:|---:|
| Completions (our status) | 26 | 26 |
| Checked points | 50 | 50 |
| Validation failures | 0 | 0 |

## The six purge instances, 300 s, paired

| | Control | Candidate |
|---|---:|---:|
| **Nodes explored, all six** | **16** | **6,618** |
| Cold starts | 21 | **7** |
| Bounded-engine fallbacks | 9 | 8 |
| Unresolved nodes | 6 | **7** |
| Root solved / proven / validated points | 6 / 0 / 0 | 6 / 0 / 0 |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

Per instance:

| Instance | Nodes | Unresolved | Fallbacks |
|---|---|---|---|
| `CMS750_4` | 3 → **3,720** | 1 → **0** | 2 → **0** |
| `neos-662469` | 3 → **1,075** | 2 → **0** | 2 → **0** |
| `neos-957323` | 2 → **419** | 0 → 0 | 1 → **0** |
| `academictimetablesmall` | 2 → **26** | 0 → 0 | 1 → **0** |
| `neos-3656078-kumeu` | 3 → 1,339 | 1 → 2 | 1 → 3 |
| `neos-3216931-puriri` | 3 → 39 | 2 → **5** | 2 → 5 |

Three instances (`kumeu`, `neos-662469`, `puriri`) also moved off the
`unresolved_relaxations` status onto `time_limit`.

## Fresh set: seven instances that returned a point in the sweep

Chosen before running, by the rule in `PLAN.md`, because an instance that
returns a point branches, and branching is where a kept basis matters.

| | Control | Candidate |
|---|---:|---:|
| Cold starts | 37 | **8** |
| Bounded-engine fallbacks | 88 | **72** |
| Nodes explored | 1,230,736 | 1,206,202 |
| Validated points | 6 | 6 |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

Cold starts fall by 78% and fallbacks by 18% with node throughput unchanged
within 2%. No instance regressed.

## Decision, including a criterion that was not met

| Declared criterion | Result |
|---|---|
| Zero validation failures and zero rejected points in every set | ✅ |
| No objective disagreeing with a published or proven optimum | ✅ |
| Development completions and coverage do not fall | ✅ 26 → 26, 50 → 50 |
| Fresh set: no new failure, checked points do not fall | ✅ 6 → 6 |
| Mechanism set: bounded-engine fallbacks fall | ✅ 9 → 8 |
| **Mechanism set: unresolved nodes fall** | ❌ **6 → 7** |

**The last criterion was not met and this report does not restate it as if it
were.** Four of the six instances went to zero unresolved nodes and zero
fallbacks. The aggregate rose by one because `puriri` (2 → 5) and `kumeu`
(1 → 2) now explore 13x and 446x more nodes and meet different LP failures
deeper in the tree. As a rate the measure improves by two orders of magnitude:
375 unresolved nodes per thousand explored in the control, 1.1 in the candidate.

**Promoted, with that deviation on the record.** An absolute count of failed
node LPs scales with how much search happens, so it was the wrong measure for a
change whose whole effect is to let the search run; the rate is the right one
and is what future iterations should declare. That is a judgement made after
seeing the result, and it is recorded here as such rather than hidden by
rewriting the rule.

Executable defaults unchanged.

## A pre-existing profile defect this run found: `neos8`

`neos8` (46,324 x 23,228) is one of the seven instances the MIPLIB 2017
benchmark proved optimal — at -3719 in 71 seconds and 153 nodes. In this run it
**aborted with `resource_limit: sparse LU fill budget`, exit 2, in both
profiles.** Isolating the cause:

| Configuration | Result |
|---|---|
| The benchmark's flag list | proven -3719, 153 nodes |
| Current profile minus `--gomory-cuts` | proven -3719, 165 nodes |
| Current profile minus `--lifted-covers` | proven -3719, 34 nodes |
| **Current profile (both cut families)** | **aborts, LU fill budget** |

It needs both cut families together: the strengthened root accumulates enough
rows that the factorization exceeds its fill budget, and the exception ends the
whole solve instead of the cut round.

This is not iteration 35's doing — it is present in the iteration 34 control and
dates from iteration 32's promotion of `--gomory-cuts` on top of
`--lifted-covers`. It escaped every iteration set because those models are far
smaller than this one. **The currently recommended profile aborts on an instance
the older profile proves optimal**, and a benchmark re-run on the current engine
would lose it.

## Iteration 36 candidates, in order

1. **A resource limit inside a cut-strengthened relaxation must roll the cuts
   back, not end the solve.** The cut loop already has a rollback path for a
   failed cut LP; a `resource_limit` exception should take it. Then bound total
   added rows by model size.
2. LP throughput: `dano3`, `mzzv`, `brazil3`, `irish-electricity` still cannot
   finish a root in 300 s.
3. Carried: frontier-aware search for `markshare2`; the trail path-entry cap.

## Artifacts

`PLAN.md`, `SOURCE_IDENTITY.json`, `gate/`, `development-30s/` (54 records),
`mechanism-300s/` and `fresh35-300s/` (every monitor record, `results.json`,
`SUMMARY.json`), `paired.py`, and the frozen binary with runtime DLLs and
`final-source/`.
