# MIPLIB 2017 benchmark sweep, batch 2 of 4

18 September 2026. Instances 60 to 119 of the MIPLIB 2017 benchmark list,
alphabetically. Same script, same frozen binary
(`e40e849f69d273777089e3cfd21fdfd7f29803f50cf0ef4f39e26691295c866c`) and same
settings as [batch 1](../kaggle-miplib2017-02/REPORT.md): 300 seconds per
instance, two at a time on a Kaggle CPU session, 21,740 seconds total.

**No timing claim.** Two instances share four cloud vCPUs.

## Result, batch 2

| | Count |
|---|---:|
| Proven optimal, agreeing with the published value | **2** |
| Feasible points returned and independently validated | **25** |
| Points rejected by the checker | **0** |
| Objectives disagreeing with a published optimum | **0** |
| No point returned at all | 35 |

Proven: `hypothyroid-k1` (-2851, exact, 72 s) and `markshare_4_0` (1, exact,
1 s).

Two more found the optimum without being able to prove it:
`neos-2978193-inde` at a relative error of **1.2e-09** and `irp` at
**2.4e-09**. Then `neos-3083819-nubu` (0.31%), `mik-250-20-75-4` (0.80%),
`mcsched` (0.93%), `neos-3627168-kasai` (1.6%), `mas76` (1.8%).

## Running total across batches 1 and 2

**120 of 240 instances covered.**

| | Count |
|---|---:|
| Proven optimal | **5** |
| All five agreeing with the published optimum | **5 / 5** |
| Validated feasible points | **46** |
| Points rejected by the independent checker | **0** |
| Objectives disagreeing with a published optimum | **0** |
| No point at all | 74 |
| Stopped by our own open-node memory guard | **17** |
| Never got past the root LP | **12** |
| Resource-limit exit | 1 |

## The memory guard is now the clearest single defect

All nine `node_limit` results in this batch are the `Open-node memory guard`,
and the sizes make the diagnosis unavoidable:

| Instance | Size | Nodes at stop | Distance from the optimum |
|---|---|---:|---|
| `markshare2` | **7 × 74** | 664,509 | far |
| `mas76` | **12 × 151** | 356,977 | 1.8% |
| `mas74` | **13 × 151** | 350,259 | 7.5% |
| `neos-3046615-murg` | 498 × 274 | 209,124 | 8.7% |
| `neos-2657525-crna` | 342 × 524 | 154,173 | no point |
| `neos-3381206-awhea` | 479 × 2375 | 25,290 | no point |
| `irp` | 39 × 20315 | 6,499 | **2.4e-09** |
| `h80x6320d` | 6558 × 12640 | 4,759 | far |
| `neos-3004026-krka` | 12545 × 17030 | 3,499 | no point |

A seven-row model exhausting a gigabyte of open-node memory is not a tuning
problem. Every open node stores complete `lower` and `upper` vectors plus basis
state, so the frontier grows with (nodes × columns) instead of with the
branching decisions that actually distinguish one node from another. `irp` is
the sharpest case: it had already found the optimum to nine digits and was
stopped before it could prove it.

Storing each node's own branching decision and reconstructing bounds from the
parent chain on pop is the standard representation and is worth roughly two
orders of magnitude here. It is now ahead of further cut work in the queue.

## Root LP throughput remains the other structural gap

Seven instances report `unresolved_relaxations`: `irish-electricity`,
`k1mushroom`, `mzzv11`, `mzzv42z`, `neos-1354092`, `neos-3216931-puriri`,
`neos-3656078-kumeu`. With batch 1's five, that is 12 of 120 where the root
relaxation does not pass its checks within 300 seconds. No cut or heuristic work
touches this; it is LP throughput at scale.

## Artifacts

`returned/results.json` (60 records, per-instance JSON under
`returned/results/`), `returned/SUMMARY.json`, `returned/carry_over.json`
(`next_slice_start: 120`) and the session log. The submitted script is the same
one in `../kaggle-miplib2017-02/kernel/sweep.py`, with `SLICE_START` at 60.
