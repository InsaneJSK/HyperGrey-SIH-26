# Iteration 34 — let the root LP finish

19 September 2026. Plan declared before any code change (`PLAN.md`). Binary
SHA-256 `f749c5af915b2a8a613a9fda5424a80601750040c366cc6311165de8d6a9bddb`, 213
frozen source files. Control is iteration 33's promoted profile on this same
executable; the candidate adds one flag, `--root-iteration-limit 100000000`.

## The finding that caused this iteration

Across the first 164 MIPLIB 2017 benchmark instances, 17 never left the root LP.
A diagnosis of twelve of them (`reports/root-lp-diagnosis/`) found **one cause
for all twelve**: every root relaxation stopped at exactly 10,000 simplex
iterations — the default per-LP count cap, which suits warm node LPs and which
no code path raises for the one LP that starts cold. The bounded engine had used
11 to 59 seconds of a 300-second budget when the cap stopped it; the remainder
went to fallback engines carrying the same cap. `CMS750_4` needed 11,261
iterations and was stopped 1,261 short.

## Mechanism

`--root-iteration-limit N` sets the cap for the root relaxation and its
cut-round re-solves to `max(--iteration-limit, N)`. Node and heuristic LPs keep
`--iteration-limit`. Default `N = 0` changes nothing. No LP engine changed: this
is a budget allocation, and it cannot alter any LP's answer, only whether the
root is allowed to finish.

## Correctness gate

CTest 28/28. `sparse_accuracy_gate.py` with the full flag set: `all_pass`, 14
generated profiles.

## Development: 27 models, two repeats, 108 records

| | Control | Candidate |
|---|---:|---:|
| Completions (our status) | 26 | 26 |
| Checked points | 50 | 50 |
| Validation failures | 0 | 0 |

As predicted: at 30 seconds on these models no root approaches 10,000
iterations, so nothing changes. The screen exists to catch a regression, and
there is none.

## The 12 diagnosed instances, 300 s, paired (development data)

| | Control | Candidate |
|---|---:|---:|
| **Root relaxation solved** | **0** | **8** |
| Proven optimal | 0 | **1** |
| Validated points | 0 | 1 |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

**`neos-827175` is proven optimal at 112.00152, exactly MIPLIB's published
value** — an instance that previously returned nothing at all.

Still unresolved at the root: `dano3_3`, `dano3_5`, `mzzv11`, `mzzv42z`. With
the cap lifted they reach the time limit instead, at 64 to 240 iterations per
second. That is LP throughput, the structural gap this iteration does not touch.

## Fresh holdout: 5 root-stuck instances never run with the cap lifted

Their sweep outcome (stuck at the root) is why they were chosen; their response
to this change was unknown until this run. Declared in `PLAN.md` before any.

| | Control | Candidate |
|---|---:|---:|
| **Root relaxation solved** | **0** | **3** |
| Proven optimal | 0 | 0 |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

Solved at the root: `academictimetablesmall`, `k1mushroom`,
`neos-3216931-puriri`. Still unresolved: `brazil3`, `irish-electricity`, both
too slow for the cap to matter. The mechanism generalizes to instances it was
not designed on.

## What the root bought, and what it did not

Across both sets, **11 instances now solve their root that did not before**. But
only one returned a point — the one it proved. The others spent most of the 300
seconds on a root that needs 11,000 to 42,000 iterations, then explored 1 to 213
nodes. A root bound and a started search are real progress from nothing; a
feasible point is not yet among them.

The plan asked for every instance where the uncapped root consumed the budget
and the search got less time than before. There is none in that sense: in the
control, the search got no time at all, because the root never finished.

## A defect this run exposed in iteration 32

Several instances show **root solved, then two or three nodes, then
`unresolved_relaxations`**. The split is clean:

| Tableau cuts purged after the root? | Instances | Bounded-engine fallbacks |
|---|---|---|
| Yes | `CMS750_4`, `neos-3656078-kumeu`, `neos-662469`, `neos-957323`, `academictimetablesmall`, `neos-3216931-puriri` | 1–2 in every one |
| No | `neos-827175`, `neos-933966`, `ns1208400`, `k1mushroom` | 0 in every one |

(`neos-1354092` purged cuts but explored only its root, so it has no children to
test.)

When iteration 32 purges slack tableau cuts it discards the basis entirely
(`lp.basis = LpBasis(); node.basis = LpBasis()`), so the root's children cold
start — and a cold start on a model this size needs more than the 10,000
iterations node LPs still get. They fail, fall back, and are retained as
unresolved.

Discarding the basis was needlessly conservative. Every purged row's logical is
basic, which is exactly why the row was purged; deleting a row together with its
own basic logical leaves a square, nonsingular basis (expand the determinant
along that unit column), and since the purged rows carried zero duals it is
still optimal. **Keeping the basis — dropping just those logical entries — is the
first iteration 35 item.** It was not applied here because the plan did not
declare it and it was found by reading this run.

## Decision

| Declared criterion | Result |
|---|---|
| Zero validation failures and zero rejected points in every set | ✅ |
| No objective disagreeing with a published or proven optimum | ✅ `neos-827175` matches |
| Development completions and coverage do not fall | ✅ 26 → 26, 50 → 50 |
| Root completes on more mechanism-set instances than control | ✅ 8 against 0 |
| Fresh five: root on at least as many, no new failure | ✅ 3 against 0 |

**Promoted into the recommended profile.** Executable defaults unchanged.

## Iteration 35 candidates, in order

1. **Keep the basis through the Gomory purge**, so the root's children warm
   start. Direct fix for the unresolved nodes above.
2. Cold-started node LPs on large models inherit the root's larger cap, as a
   fallback for any other path that loses the basis.
3. LP throughput on `dano3`, `mzzv`, `brazil3`, `irish-electricity`: 64–240
   iterations per second at 3,000–17,000 rows is the structural gap.
4. Carried: frontier-aware search for `markshare2`; the trail path-entry cap.

## Artifacts

`PLAN.md`, `SOURCE_IDENTITY.json`, `gate/`, `development-30s/` (108 records),
`mechanism-300s/` and `holdout34-300s/` (every monitor record, `results.json`,
`SUMMARY.json`), `paired.py`, the diagnosis in `../root-lp-diagnosis/`, and the
frozen binary with runtime DLLs and `final-source/`.
