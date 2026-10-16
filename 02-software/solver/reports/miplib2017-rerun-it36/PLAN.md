# MIPLIB 2017 re-run on the current engine — what is being measured

Declared 20 September 2026, before any result is read.

## Why

The [complete benchmark](../miplib2017-benchmark/REPORT.md) ran all 240
instances on the engine as it stood before iterations 33 to 36. Every one of
those iterations fixed a failure category that the benchmark itself exposed:

| Iteration | Fixed | Benchmark instances affected |
|---|---|---:|
| 33 | Open nodes stored full bound vectors | 31 memory-guard stops |
| 34 | The root LP was capped at 10,000 simplex iterations | 27 unresolved roots |
| 35 | The cut purge discarded the basis, so children cold started | — |
| 36 | A factorization limit aborted the whole solve | 2 exits, `neos8` |

Each was measured on its own paired set. None has been measured on the public
benchmark. This run answers the only question that matters for the submission:
**does the public result move.**

## What is run

- All 240 MIPLIB 2017 benchmark instances, 300 seconds each, node limit
  100,000,000, gap 1e-6 — identical budget to the original run.
- Engine: the **frozen iteration 36 source**, uploaded as the Kaggle dataset
  `sih26119-solver-source-it36` and compiled inside each session. The frozen
  binary's SHA-256 is `e379b12c…1dad`; each session records the SHA of the
  binary it builds.
- Flags: the **iteration 36 recommended profile**, verbatim.
- Four Kaggle CPU sessions in parallel, 60 instances each, two at a time within
  a session — the same contention as the original run.

## The comparison is engine *and* profile, and that is deliberate

The original run used the older recommended flag list (`--late-*` cut flags, no
`--gomory-cuts`, no `--root-iteration-limit`). This run uses the current one.
So the difference between the two tables is **the engine and its recommended
configuration together**, not an isolated engine change.

That is the honest framing of the question being asked — "is the thing we would
ship better than the thing we shipped before" — but it means no single code
change can be credited from this table alone. The per-iteration paired runs are
where individual mechanisms were isolated.

## Checking, unchanged from the original run

Every returned point is checked for feasibility and integrality against the
original file by an independent HiGHS 1.12.0 reader; every objective is compared
with MIPLIB's published solution file. No reference value is fed back into the
engine. **No timing claim**: two instances share four cloud vCPUs.

## What will be reported

The same table for all 240 instances, and a direct comparison against the
original: proven optimal, proven infeasible, validated points, rejected points,
answers disagreeing with MIPLIB, memory-guard stops, unresolved roots and
resource-limit exits — including **every instance that got worse**, which is the
outcome this run is most at risk of hiding.
