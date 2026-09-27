# MIPLIB 2017 benchmark sweep, batch 1 of 4

18 September 2026. The first run of this solver against a full public benchmark
set. 60 instances — positions 0 to 59 of the MIPLIB 2017 benchmark list,
alphabetically, so four batches cover all 240 with no overlap. 300 seconds per
instance, two instances at a time on a Kaggle CPU session, 8,011 seconds total.

Solver SHA-256 `e40e849f69d273777089e3cfd21fdfd7f29803f50cf0ef4f39e26691295c866c`,
built inside the session from the `sih26119-solver-source` dataset. Reference
optima from MIPLIB's own published solution file
(`https://miplib.zib.de/downloads/miplib2017-v32.solu`); every returned point
checked for feasibility and integrality by an independent HiGHS 1.12.0 reader on
the original file.

**No timing claim is made from this run.** Two instances share four cloud
vCPUs, so every outcome is "at this budget, under contention".

## Result

| | Count |
|---|---:|
| Proven optimal, agreeing with the published value | **3** |
| Feasible points returned and independently validated | **21** |
| Points returned but rejected by the checker | **0** |
| Objectives disagreeing with a published optimum | **0** |
| No point returned at all | 39 |
| Instances attempted | 60 |

The two numbers that matter for trust are both zero: nothing we returned failed
its independent feasibility and integrality check, and nothing we claimed as
optimal disagreed with the published optimum.

### Proven optimal

| Instance | Objective | Published | Relative error | Seconds | Size |
|---|---:|---:|---:|---:|---|
| `app1-1` | -3 | -3 | 0 | 49.0 | 4926 × 2480 |
| `decomp2` | -160 | -160 | 0 | 44.8 | 10765 × 14387 |
| `eil33-2` | 934.007916 | 934.007916 | 1.1e-15 | 80.6 | 32 × 4516 |

### Closest approaches without a proof

`assign1-5-8` reached the optimum exactly (relative error 9.3e-15) without
closing its gap. Then `gmu-35-40` (0.47%), `binkar10_1` (0.49%), `gmu-35-50`
(0.50%), `gen-ip054` (0.58%), `gen-ip002` (0.92%), `cost266-UUE` (4.2%) and
`glass-sc` (4.2%).

At the other end the points are poor but valid: `beasleyC3` is 2.77x the
published optimum, `fastxgemm-n2r6s0t2` 2.58x, `b1c1s1` 1.06x.

## Where it fails, and why

This is the part worth reading.

### Our own memory guard stops 8 instances

All eight `node_limit` results carry the message `Open-node memory guard` — the
960 MiB open-node frontier limit, not the node count.

| Instance | Nodes at stop | Size | Point? |
|---|---:|---|---|
| `gen-ip054` | 1,142,795 | **27 × 30** | yes |
| `glass4` | 175,328 | 396 × 322 | yes |
| `exp-1-500-5-5` | 59,262 | 550 × 990 | yes |
| `gmu-35-40` | 49,194 | 424 × 1205 | yes |
| `gmu-35-50` | 31,208 | 435 × 1919 | yes |
| `50v-10` | 29,864 | 233 × 2013 | yes |
| `binkar10_1` | 25,940 | 1026 × 2298 | yes |
| `fiball` | 1,775 | 3707 × 34219 | no |

`gen-ip054` is the diagnosis in one line: a **27-row, 30-column** model whose
open frontier reached a gigabyte. The guard is not miscalibrated — each open
node stores full lower and upper bound vectors plus basis state, and 1.1 million
of them really is that large. The defect is the representation. Storing the
branching decisions per node instead of complete bound vectors would cut this by
roughly two orders of magnitude and let the search continue.

Six of the eight still returned a validated point, so the guard is doing its job
of failing safely rather than being killed by the operating system.

### Five instances never get past the root LP

`academictimetablesmall`, `brazil3`, `CMS750_4`, `dano3_3` and `dano3_5` all
report `unresolved_relaxations` at **node 1**: the root relaxation did not pass
its numerical checks inside 300 seconds. These are 3,200–23,300 rows and
11,700–28,900 columns. This is the clearest structural gap against established
solvers, and no cut or heuristic work touches it — it is LP throughput at
scale.

### One resource-limit exit

`buildingenergy` (277,594 × 154,978) exits with
`error: resource_limit: sparse LU fill budget`. The limit is honest, but the
process exits 2 like a rejected input rather than reporting a limit status with
a bound. That reporting should be fixed; a model that is too large should say
so as a status, not as a parse-style error.

## What this changes

It gives the submission a real public benchmark table, failures included, and it
reorders the engineering queue. The open-node representation now looks like a
larger win than any further cut work: it affects 8 of 60 instances here, one of
them a 27-row model, and the fix is bounded and mechanical.

## Carry-over

`returned/carry_over.json` lists every instance that reached its budget without
proving optimality, for a later run at a larger budget, and records
`next_slice_start: 60` for batch 2.

## Artifacts

`kernel/sweep.py` (the submitted script), `returned/results.json` (all 60
records with per-instance JSON under `returned/results/`),
`returned/SUMMARY.json`, `returned/carry_over.json` and the session log.
