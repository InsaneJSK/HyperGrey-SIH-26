# MIPLIB 2017 benchmark set — complete run

**All 240 instances** of the MIPLIB 2017 benchmark set, solved by this project's
own engine at a 300-second budget, with every answer checked independently.
The full per-instance table, failures included, is [TABLE.md](TABLE.md).

## Headline

| | Count |
|---|---:|
| Proven optimal | **7** |
| Proven infeasible | **1** |
| Instances with an independently validated feasible solution (including the 7 optima) | **69** |
| **Solutions rejected by the independent checker** | **0** |
| **Answers disagreeing with MIPLIB's published results** | **0** |
| Instances with no feasible solution at 300 seconds | 170 |

The two zeros are the result this project stands on. Across 240 public
instances, nothing this engine returned failed an independent feasibility and
integrality check, and every optimality or infeasibility claim it made agrees
with MIPLIB. When it cannot solve an instance it says so, and it does not
report a false optimum.

Every proven optimum matches the published value exactly:

| Instance | Size | Objective | Published |
|---|---|---:|---:|
| `eil33-2` | 32 × 4516 | 934.007916 | 934.007916 |
| `app1-1` | 4926 × 2480 | -3 | -3 |
| `decomp2` | 10765 × 14387 | -160 | -160 |
| `hypothyroid-k1` | 5195 × 2602 | -2851 | -2851 |
| `markshare_4_0` | 4 × 34 | 1 | 1 |
| `neos8` | 46324 × 23228 | -3719 | -3719 |
| `rmatr100-p10` | 7260 × 7359 | 423 | 423 |

`neos859080` is proven infeasible, as MIPLIB records it.

## Where it falls short

This is a hard set, curated to challenge commercial solvers, and 8 proven
answers out of 240 is far behind them. The failures are the useful part, because
each category has a cause:

| Category | Count | Cause | Status |
|---|---:|---|---|
| Stopped by the open-node memory guard | 31 | Every open node stored complete bound vectors | **Fixed in [iteration 33](../milp-iteration-33/REPORT.md)**: a paired re-run of 16 such stops removed 15 |
| Root LP never resolved | 27 | Default 10,000-iteration cap per LP, applied to the cold root | **Fixed in [iteration 34](../milp-iteration-34/REPORT.md)** for most: 11 of 17 re-tested roots now solve, one to a proven optimum |
| Resource-limit exit | 2 | LU fill budget on 155,000–166,000-row models | Honest limit, badly reported as an input error; to fix |
| No solution at 300 s | 132 | Search strength: first-point heuristics, bound quality, LP throughput | Open |

**This run used the engine as it was before iterations 33 and 34.** The two
largest failure categories have been fixed since, and each fix was measured
separately in paired runs. The table records what the benchmark run itself
produced. A full re-run on the current engine is the next measurement, and it
will be reported separately rather than merged into this one.

## Method

- **Instances**: the MIPLIB 2017 benchmark list
  (`https://miplib.zib.de/downloads/benchmark-v2.test`), all 240, downloaded
  inside each session.
- **Engine**: SHA-256 `e40e849f69d273777089e3cfd21fdfd7f29803f50cf0ef4f39e26691295c866c`,
  built from source inside each Kaggle session from the same frozen dataset.
- **Budget**: 300 seconds per instance, node limit 100,000,000, gap 1e-6.
- **Machine**: Kaggle CPU sessions, two instances at a time on four shared
  vCPUs. Outcomes are at a fixed budget under contention. **No timing claim is
  made from this run.**
- **Checking**: every returned solution was checked for feasibility and
  integrality against the original file by an independent HiGHS 1.12.0 reader,
  and every objective compared with MIPLIB's published solution file
  (`miplib2017-v32.solu`). No reference value was ever fed back into the
  engine.
- **Runs**: five sessions, [batch 1](../kaggle-miplib2017-02/REPORT.md) (0–59),
  [batch 2](../kaggle-miplib2017-03/REPORT.md) (60–119),
  [batch 3](../kaggle-miplib2017-04/REPORT.md) (120–163; the platform cancelled
  the session at 44 of 60, all 44 records recovered), and two final parts
  (164–201, 202–239) in parallel sessions. `consolidate.py` merges them and
  refuses to write unless every instance appears exactly once.

## Artifacts

[TABLE.md](TABLE.md) (all 240 rows), `SUMMARY.json`, `consolidate.py`, and each
session's returned `results.json`, per-instance JSON and log under
`../kaggle-miplib2017-02` to `-05`.
