# Iteration 37 — `--gomory-cuts` is removed from the recommended profile

21 September 2026. Plan and decision rule declared before the comparison
(`PLAN.md`). One flag, one frozen executable
(`e379b12cb5136cdf04ae22539d00073730dd94672b1b2075c7e8e5012bf11dad`), both sides
started together on the same host.

## Why this was asked

Iteration 32 promoted `--gomory-cuts` on a **bound** criterion: the root bound
improved on 26 of 28 changed development observations and 4 of 4 unseen. That
report said plainly that no end-to-end gain was demonstrated and the 30-second
gap was a wash. It was promoted into the recommended profile anyway, because the
declared rule was about bounds.

The MIPLIB 2017 re-run gave the evidence the development set could not: on the
60 instances of part a the current profile returned **fewer** answers than the
old one — proven 3 → 2, validated solutions 21 → 18 — even though the failure
modes iterations 33, 34 and 36 targeted were nearly gone.

## Result: 60 instances, 300 s, one flag apart

| | With `--gomory-cuts` | Without |
|---|---:|---:|
| **Proven optimal** | 2 | **3** |
| **Validated solutions** | 19 | **21** |
| Nodes explored | 5,947,089 | **7,753,820** |
| Bounded-engine fallbacks | 1,984 | **305** |
| Cold starts | 2,030 | **282** |
| Unresolved nodes | 20 | **9** |
| Roots solved | 49 | 49 |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

Four instances changed outcome:

| Instance | With cuts | Without | Nodes |
|---|---|---|---|
| `decomp2` | nothing | **proven optimal** | 8,930 → **1** |
| `b1c1s1` | nothing | **solution** | 7,726 → 16,625 |
| `cvs16r128-89` | nothing | **solution** | 479 → 981 |
| `csched008` | **solution** | nothing | 4,316 → 5,951 |

Three improve without the cuts, one worsens.

`decomp2` is the clearest: without tableau cuts it is **proven optimal at the
root, in a single node**. With them the solver explores 8,930 nodes and returns
nothing at all. Cut rounds consume the time the root proof needed.

## Why the cuts cost answers

The fallback and cold-start counts explain the node deficit. Tableau cuts add
rows that the bounded engine then fails on far more often — **1,984 fallbacks
against 305**, and **2,030 cold starts against 282**. Every fallback re-solves an
LP with a slower engine, and every cold start pays for a factorization from
scratch. The result is 30% fewer nodes explored in the same 300 seconds, and
fewer answers found.

This is the same trade iteration 32 measured as "a wash" on 27 small models at
30 seconds. On 60 public instances at 300 seconds it is not a wash; it is a
loss.

## Decision

| Declared criterion | Result |
|---|---|
| Proven optimal answers do not fall | ❌ 3 → 2 |
| Validated solutions do not fall | ❌ 21 → 19 |

**`--gomory-cuts` is removed from the recommended profile.** It remains an
opt-in flag, fully implemented, tested and documented; executable defaults are
unchanged, as they always were.

Iteration 32's evidence stands as what it measured: a real and verified
improvement in root bound, gated by enumeration over 64,430 integer points,
which does **not** convert into answers at this budget on these instances. The
error was mine, in promoting a flag into the shipped profile on a criterion that
did not measure what the profile is for.

## What this does not change

- The cut code, its validity gate and its documentation stay. The separator is
  correct; it is the default that was wrong.
- Iterations 33 to 36 are unaffected. Their mechanisms were measured separately
  and each fixed a real failure mode; the re-run confirmed those categories
  nearly vanished (memory-guard stops 8 → 1, unresolved roots 5 → 0,
  resource-limit exits 1 → 0 on part a).
- `csched008` loses a solution without the cuts and is recorded as the one
  instance that preferred them.

## Follow-up

1. **Re-run the benchmark on the corrected profile.** Part a should now be
   compared against the original table without the flag; the remaining slices
   need Kaggle quota.
2. The support cap allowing a 5,000-nonzero cut (iteration 32) remains the
   likely reason the cuts are so costly here. If tableau cuts are ever returned
   to the profile, that must be fixed and measured first.

## Artifacts

`PLAN.md`, `MODELS.txt` (the 60 instances), `ablation-300s/` with every monitor
record, `results.json` and `SUMMARY.json`, and `paired.py`.
