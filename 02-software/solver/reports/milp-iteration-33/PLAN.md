# Iteration 33 plan — what an open node costs

Declared 18 September 2026, before any timed comparison or holdout solve, and
after the MIPLIB 2017 sweep changed the priority order.

## Why this and not more cuts

Iteration 32 ended expecting the cover/Gomory ordering fix to be next. The
public benchmark says otherwise. Across the first 120 MIPLIB 2017 benchmark
instances at 300 s ([batch 1](../kaggle-miplib2017-02/REPORT.md),
[batch 2](../kaggle-miplib2017-03/REPORT.md)), **17 instances stop on our own
open-node memory guard**, and the sizes rule out a tuning explanation:

| Instance | Size | Nodes at stop | Distance from optimum |
|---|---|---:|---|
| `markshare2` | **7 × 74** | 664,509 | far |
| `mas76` | **12 × 151** | 356,977 | 1.8% |
| `mas74` | **13 × 151** | 350,259 | 7.5% |
| `gen-ip054` | **27 × 30** | 1,142,795 | 0.58% |
| `irp` | 39 × 20315 | 6,499 | **2.4e-09** |

A seven-row model cannot legitimately need a gigabyte of frontier. `irp` is the
sharpest: it had the optimum to nine digits and was stopped before it could
prove it.

## Diagnosis

`struct Node` stores complete `lower` and `upper` vectors. Every open node
therefore costs `16n` bytes plus its record, so the frontier grows with
**nodes × columns** rather than with the branching decisions that actually
distinguish one node from another. Two siblings differ from their parent in
exactly one variable's one bound and each keeps a full copy of everything else.

## Mechanism

A queued node keeps a pointer into a shared trail instead of dense vectors.

```
struct BoundTrail {
    std::shared_ptr<BoundTrail> parent;
    std::vector<Change> changes;   // {column, lower, upper}, infinite where unset
};
```

- **Branching** creates one trail record per child holding that child's single
  bound change, with the parent's record shared between the two siblings.
- **Popping** materializes `p.lower`/`p.upper` and walks the trail to the root,
  applying `lo[j] = max(lo[j], change.lower)` and `up[j] = min(up[j],
  change.upper)`. Bounds only tighten down a branch, so the result does not
  depend on the order of application.
- **After propagation succeeds at a popped node**, the propagated differences
  are appended to that node's own trail record, so its children inherit
  propagated bounds exactly as they do today. This memoization matters because
  `propagate` runs at most ten passes rather than to a fixpoint: re-deriving
  bounds from branch decisions alone could reach a weaker result and change
  search behaviour. If the propagated delta exceeds `n/2` entries the
  memoization is skipped and children re-propagate, so a pathological node
  cannot reintroduce dense storage.
- The open-node estimate behind `--open-node-memory-mib` is re-derived from the
  new representation rather than from `16n`.

Defaults unchanged in the sense that no flag changes meaning; this is a
representation change that applies whenever the tree runs.

## Risks, stated in advance

1. **Search behaviour may change.** Memoization is intended to keep propagated
   bounds identical, but the `n/2` cap means some nodes will re-propagate from
   looser bounds and may get weaker bounds and different branching. This is the
   main thing the screen must detect.
2. **Pop cost rises** by one trail walk and one bound materialization per node.
   On models with very deep trees this is O(depth) per pop.
3. Nothing about cut validity, certificates or the LP engine changes.

## Correctness gate, before any timed comparison

- CTest, all 29 tests including `gomory_cut_validity`.
- `sparse_accuracy_gate.py` with the full flag set including `--gomory-cuts`.
- A dedicated equivalence check: with the memoization cap raised so that it
  never triggers, running the same models at a fixed node limit and
  `--no-heuristics` must give **identical** node counts, bounds and objectives
  to the current build. A representation change must be invisible at fixed work.

## Profiles

- Control: iteration 32's promoted profile on the iteration 32 executable.
- Candidate: the same flags on the iteration 33 executable.

Serial runs, rotating profile order, 30 s, gap 1e-6, node limit 100,000,000,
45 s watchdog, 1536 MiB sampled commit threshold.

## Model sets

1. Development: the 27 reused models, two repeats per profile.
2. **A memory-bound set**, declared here because the development suite does not
   exercise the defect: `gen-ip054`, `mas74`, `mas76` and `markshare2` from the
   sweep evidence, plus `markshare1` and `swath` from the iteration 32 holdout.
   These are already development data and cannot support a generalization
   claim; they are the direct test of the mechanism.
3. Fresh holdout: declared separately in `HOLDOUT_SELECTION.md` before download.

## Decision rule

Promote only if, against the control:

- zero validation failures in every set, and no objective disagreeing with an
  independently proven HiGHS optimum;
- the fixed-work equivalence check passes;
- peak open-node memory falls on the memory-bound set;
- no memory-guard stop appears that the control did not have;
- development completions and checked-point coverage do not fall;
- nodes explored per second do not fall by more than 10 percent on the
  development set, measured at fixed time.

Report every regression, including any model made slower by the trail walk.
