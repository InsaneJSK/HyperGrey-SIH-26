# Iteration 33 — what an open node costs

18 September 2026. Plan and holdout selection declared before any timed run
(`PLAN.md`, `HOLDOUT_SELECTION.md`). Binary SHA-256
`db61dd2628022491c637526bd5cfc8b11b7361458f97a986633d72917810f045`, 213 frozen
source files. Control is the frozen iteration 32 executable
(`6e073229…351a4`) on **identical flags** — only the executable differs.

## Why this iteration exists

Iteration 32 ended expecting a cut-ordering fix next. The MIPLIB 2017 sweep
overruled that: **17 of the first 120 benchmark instances stop on our own
open-node memory guard**, including `markshare2` at 7 rows and `irp`, which had
the optimum to nine digits and was stopped before it could prove it. Every open
node stored complete `lower` and `upper` vectors, so the frontier grew with
nodes × columns rather than with the branching decisions that distinguish nodes.

## Mechanism

A queued node now holds a pointer into a shared `BoundTrail` instead of dense
vectors. Siblings share every ancestor record; bounds are rebuilt on pop by
walking to the root and applying each change with max/min, which is
order-independent because bounds only tighten down a branch.

Propagation needed care. `propagate` stops after ten passes rather than at a
fixpoint, so children re-deriving bounds from branch decisions alone could reach
a weaker result and change the search. Each popped node therefore memoizes what
propagation derived onto its own trail record, which both children inherit.

**The first version of that memoization was wrong and the gate caught it.** A
cap of `n/2` entries per node meant that on `binkar10_1` the root's delta
exceeded the cap, nothing was memoized, and every node re-derived from scratch:
bound tightenings went from 26,618 to **6,457,700** and 8 of 32 equivalence
cases differed. One record is shared by every descendant, so a large delta near
the root is cheap; what needs bounding is the total, not the per-node size.

## Correctness gate

- **Fixed-work equivalence: 0 mismatches in 32 comparisons** (16 models × 2 flag
  profiles, fixed node limit, heuristics off). Identical status, objective,
  bound, nodes, LP iterations and bound tightenings against iteration 32. A
  representation change must be invisible at fixed work, and it is.
  (`EQUIVALENCE.log`, `equivalence.py`)
- CTest 28/28.

## Memory at a fixed node count

Same models, same flags, same nodes explored — the only difference measured is
what an open node costs. (`FIXED_NODE_MEMORY.log`, `fixed_node_memory.py`)

| Model | Columns | Old MiB | New MiB | Ratio | Nodes old → new |
|---|---:|---:|---:|---:|---|
| `gen-ip054` | 30 | 100.8 | 69.9 | 1.44x | 120,000 → 120,000 |
| `markshare2` | 74 | 182.1 | 80.3 | 2.27x | 120,000 → 120,000 |
| `gt2` | 188 | 451.0 | 93.4 | 4.83x | 120,000 → 120,000 |
| `mas74` | 151 | 375.2 | 76.8 | 4.89x | 120,000 → 120,000 |
| `swath` | 6805 | 1013.4 | 336.4 | 3.01x | 9,490 → **27,191** |
| `lotsize` | 2985 | 1008.9 | 107.5 | 9.39x | 19,898 → **25,030** |

`swath` and `lotsize` reached the time limit rather than the node cap, so their
ratios understate it: per node the improvement is 8.6x and 11.8x, and the new
build explored 2.9x and 1.3x more nodes in the same 300 seconds. The win scales
with column count, which is why 30-column `gen-ip054` gains least.

## Development: 27 models, two repeats, 54 records

| | Iteration 32 | Iteration 33 |
|---|---:|---:|
| Completions (our status) | 24 | 24 |
| Checked points | 50 | 50 |
| Validation failures | 0 | 0 |
| Memory-guard stops | 0 | 0 |
| Peak commit | 762.8 MiB | **183.9 MiB** |
| Nodes explored | 1,999,859 | **2,394,726** |
| Nodes per second | 2,233 | **2,675 (+19.8%)** |

**A correction against our own category counts, for the second iteration
running.** The raw categories show completions rising 23 → 26. They did not.
All three changes (`blend2` twice, `neos859080` once) are records where the
five-second HiGHS reference finished this time and timed out last time. By our
own solver's status it is 24 against 24.

Relative gap moved better on 14 records and worse on 10 — a wash, and expected:
the equivalence check proves the semantics are identical at fixed work, so every
difference at a *time* limit comes from reaching more nodes, not from solving
differently. `danoint` improved consistently across both repeats (0.266 → 0.094)
and `misc07`, `pk1` and `p0282` worsened.

## Fresh holdout: 10 untouched MIPLIB 2017 benchmark models

Declared before download. Positions 180–212 of the benchmark list, none of them
run by this project in any form.

| | Control | Candidate |
|---|---:|---:|
| Checked points | 5 | 5 |
| Categories | identical on all 10 | identical on all 10 |
| Validation failures | 0 | 0 |
| Memory-guard stops | 0 | 0 |
| Peak commit, worst | 512.1 MiB | 407.6 MiB |
| **Nodes explored, total** | **47,947** | **40,621 (0.85x)** |

Memory fell on 8 of 10, including `sp150x300d` 512.1 → 53.6 MiB and `sct2`
88.0 → 11.0 MiB. It rose on two: `sorrell3` 357.3 → 407.6 and `s250r10`
221.7 → 225.1, both models that explore almost no nodes, where the frontier is
not what holds the memory.

### The retained regression: fewer nodes on this set

Node counts fell on 8 of 10 models — `ran14x18-disj-8` 2,015 → 1,399,
`rmatr100-p10` 229 → 163, `sp150x300d` 43,227 → 36,900. This is systematic, not
variance, and it is the opposite of development's +19.8%.

The cause is the trail walk. Materializing bounds on pop costs one pass over the
columns plus one pass over every entry on the path to the root, and memoized
propagation deltas may hold up to `n` entries per ancestor. On a deep path
through a wide model that is far more work than the dense copy it replaced. The
development suite has narrow models where the saving at push dominates; this
holdout has wide ones where the walk dominates.

**The fix is bounded and is iteration 34's first item**: cap the *total* entries
on a path, not the per-node delta. `BoundTrail::entries` already carries the
running count, so refusing to memoize once a path exceeds roughly `4n` keeps
materialization O(n) — the same order as the copy it replaces — while keeping
memoization where it pays. That was not changed here because the regression was
found by reading this holdout, and re-tuning against it would be fitting to it.

## Decision

Against the rule declared in `PLAN.md`:

| Declared criterion | Result |
|---|---|
| Zero validation failures in every set | ✅ 0, 0 and 0 |
| No objective disagreeing with a proven HiGHS optimum | ✅ none |
| Fixed-work equivalence check passes | ✅ 0 of 32 mismatches |
| Peak open-node memory falls on the memory-bound set | ✅ 1.44x–9.39x |
| No memory-guard stop the control did not have | ✅ none in either |
| Development completions and coverage do not fall | ✅ 24 → 24, 50 → 50 |
| Nodes per second do not fall by more than 10% on development | ✅ rose 19.8% |

**Promoted.** Every declared criterion passes. The rule measured throughput on
the development set and that rose; the holdout node drop is a real cost that the
rule did not cover, it is diagnosed, and the fix is declared rather than applied
retroactively.

This is a representation change: no flag changes meaning, and the fixed-work
equivalence check is the evidence that nothing about the search was altered.

Also added: `--open-node-memory-mib`, so the guard threshold is reachable from
the command line. It was previously a compiled-in constant, which made the
defect that motivated this iteration untestable without a rebuild.

## What this does not show

- **No completion gain.** 24 against 24 on development, 5 points against 5 on
  the holdout. This iteration bought memory and headroom, not solving power.
- **Update — the 17 motivating instances have now been re-run**
  ([guard-rerun/REPORT.md](guard-rerun/REPORT.md)), old and new builds side by
  side at 300 s on the sweep's flags. Guard stops fall **16 to 1**, nodes rise
  **2.61x**, and checked incumbents improve on **10, worsen on 1** — `mas76` from
  1.57% above the optimum to 0.28%, `mas74` from 9.8% to 2.0%, `50v-10` from
  66.8% to 12.5%. **Proofs: 0 to 0.** The headroom is real and it improves
  solutions, but it did not close a single gap at 300 s. `markshare2` still
  trips the guard, 2.6x later; `gen-ip054` did not reproduce its guard stop on
  this host and is not counted.
- One host, two repeats on development and one on the holdout.

## Iteration 34 candidates, in order

1. **Cap total path entries** so materialization stays O(n); re-measure the
   holdout node rate. Validate on an unused set.
2. **Frontier-aware search**: switch to depth-first diving when the open
   frontier grows faster than it closes. The guard re-run shows `markshare2`
   needs this rather than a cheaper node.
3. Separate cover cuts before tableau cuts, or fall back to tableau cuts only
   when covers add nothing (`p0282`, carried from iteration 32).
4. Root LP throughput: 12 of 120 benchmark instances never leave the root.

## Artifacts

`PLAN.md`, `HOLDOUT_SELECTION.md`, `SOURCE_IDENTITY.json`, `EQUIVALENCE.log`,
`FIXED_NODE_MEMORY.log`, `development-30s/` (54 records),
`holdout33-30s/` and `holdout33-30s-control/` (10 records each),
`CANDIDATE_PROFILE.json`, and the frozen binary with runtime DLLs and
`final-source/`.
