# Guard re-run — the 17 instances that motivated iteration 33

18 September 2026. Declared in `PLAN.md` before any run. Iteration 33 was
justified by 17 MIPLIB 2017 benchmark instances that stopped on our own
open-node memory guard in the Kaggle sweep. This re-runs exactly those, on
exactly the sweep's flags at 300 seconds, with the iteration 32 executable
(dense open nodes) and the iteration 33 executable (trail open nodes) **started
at the same moment on the same host**, so machine load hits both together.

These 17 informed iteration 33's design. Nothing here is a generalization
claim; it is the direct mechanism test on the cases the change was built for.

Binaries: old `6e073229…351a4`, new `db61dd26…f045`. Every returned point was
checked for feasibility and integrality by an independent HiGHS 1.12.0 reader,
and every objective compared with MIPLIB's published solution file (`v32`).

## Result

| | Old build | New build |
|---|---:|---:|
| **Memory-guard stops** | **16** | **1** |
| **Proven optimal** | **0** | **0** |
| Validated points | 13 | 13 |
| Rejected points | 0 | 0 |
| Objectives disagreeing with a published optimum | 0 | 0 |
| Nodes explored, all 17 | 4,301,938 | **11,239,624 (2.61x)** |
| Checked incumbent vs published optimum | — | **better 10, worse 1, same 2** |

The mechanism works and the proof does not follow. **Fifteen of sixteen guard
stops are gone, the search goes 2.6 times deeper, and the solutions it finds
are substantially better — but not one instance closes its gap at 300
seconds.** The plan fixed in advance that this outcome would be reported as
exactly this, and it is.

## Per instance

| Instance | Old stop | Old nodes | New stop | New nodes | Old peak | New peak | Distance from optimum, old → new |
|---|---|---:|---|---:|---:|---:|---|
| `50v-10` | guard | 29,864 | time | 469,263 | 1025 | 447 | 66.8% → **12.5%** |
| `binkar10_1` | guard | 25,940 | time | 158,306 | 982 | 232 | 0.49% → 0.37% |
| `exp-1-500-5-5` | guard | 59,262 | time | 511,875 | 1161 | 496 | 72.0% → 42.8% |
| `fiball` | guard | 1,775 | time | 5,627 | 1055 | 201 | no point either |
| `gen-ip054` | **time** | 2,153,378 | time | 2,129,946 | 1307 | 1023 | 0.58% → 0.58% |
| `glass4` | guard | 174,546 | time | 953,155 | 1161 | 513 | 141.7% → 116.7% |
| `gmu-35-40` | guard | 49,194 | time | 258,444 | 1022 | 286 | 0.25% → **0.40% (worse)** |
| `gmu-35-50` | guard | 31,208 | time | 238,123 | 1015 | 294 | 0.35% → 0.34% |
| `h80x6320d` | guard | 4,759 | time | 40,562 | 989 | 324 | 213.6% → 213.6% |
| `irp` | guard | 6,451 | time | 32,042 | 984 | 238 | optimum in both, not proven |
| `markshare2` | guard | 664,509 | **guard** | 1,723,514 | 1045 | 1143 | 30.0 → 21.5 (absolute, optimum 1) |
| `mas74` | guard | 350,255 | time | 1,310,573 | 1119 | 519 | 9.8% → **2.0%** |
| `mas76` | guard | 358,711 | time | 1,601,830 | 1120 | 525 | 1.57% → **0.28%** |
| `neos-2657525-crna` | guard | 154,173 | time | 526,935 | 1215 | 297 | no point either |
| `neos-3004026-krka` | guard | 3,499 | time | 16,468 | 1046 | 230 | no point either |
| `neos-3046615-murg` | guard | 209,124 | time | 1,072,597 | 1158 | 814 | 5.9% → **1.4%** |
| `neos-3381206-awhea` | guard | 25,290 | time | 190,364 | 1012 | 228 | no point either |

Peak commit in MiB.

## Three things this run says that were not known before

**The old stops reproduce, mostly exactly.** On a different machine, uncontended,
twelve of the sixteen old guard stops happened at *exactly* the node count the
Kaggle sweep recorded (29,864, 25,940, 59,262, 1,775, 49,194, 31,208, 4,759,
664,509, 154,173, 3,499, 209,124, 25,290). Four more landed within 1%
(`glass4`, `irp`, `mas74`, `mas76`). The search is deterministic up to the point
where time-budgeted heuristics start to diverge.

**One did not reproduce at all, and that limits what can be claimed.**
`gen-ip054` stopped on the guard at 1,142,795 nodes on Kaggle but ran the full
300 seconds here, to 2,153,378 nodes, in the old build too. Its dives, pump and
repair allowances are measured in seconds, so a run long enough on a machine of
different speed takes a different path, and this one never grew a frontier big
enough to trip the guard. It is counted as a non-reproduction, **not** as a
guard removed. The earlier statement in this project that the search is
deterministic up to the guard was too strong; it holds for most instances, not
all.

**`markshare2` is delayed, not fixed.** It was the headline example of the
defect — a seven-row model exhausting a gigabyte. The new build hits the guard
too, 2.6 times later (1,723,514 nodes against 664,509). That matches the fixed
node-count measurement of 2.27x at 74 columns: its dense vectors were only about
1.2 KB per node, so there is less to save, and a market-share instance opens
nodes far faster than it closes them because its relaxation is famously weak.
What fixes `markshare2` is a different search strategy — switching to depth-first
diving when the frontier explodes — not a cheaper node.

## What the extra depth bought

Where the old build stopped early and the new one kept going, it found better
solutions on ten of the thirteen instances that returned a point:

- `mas76` from 1.57% above the optimum to **0.28%**, with the gap down to 0.7%.
- `mas74` from 9.8% to **2.0%**, gap halved from 0.140 to 0.069.
- `50v-10` from 66.8% to **12.5%**.
- `neos-3046615-murg` from 5.9% to **1.4%**.

`irp` already had the optimum in both builds (to nine digits); five times the
nodes tightened its bound slightly (gap 0.0015 → 0.0013) and still did not prove
it. `gmu-35-40` is the one regression, 0.25% to 0.40%.

Four instances return no point in either build — `fiball`,
`neos-2657525-crna`, `neos-3004026-krka`, `neos-3381206-awhea`. Depth does not
help an instance that cannot find its first feasible point, which is the
lock-based first-point work already on the queue.

## What this changes

The representation change was worth making: on the instances it was built for
it removes the stop, goes 2.6x deeper, and improves ten solutions. But it has
not produced a proof, and the gap to proving these at 300 seconds is bound
strength and search strategy, not memory. Next, in order of what this run
points at:

1. **Frontier-aware search**: switch to depth-first diving when the open
   frontier grows faster than it closes. That is what `markshare2` needs, and it
   would also cap memory without a guard.
2. First points for the four instances that return nothing.
3. The path-entry cap already declared from the iteration 33 holdout.

## Artifacts

`PLAN.md`, `rerun.py`, `rerun.log`, `rerun-attempt1-harness-crash.log` (the
first attempt crashed while *writing* `50v-10`'s results, after both solves had
finished; the resumed run read those two records back rather than re-running
them), `runs/` with every monitor record, stdout and stderr, `runs/results.json`
and `runs/SUMMARY.json`. Models and their SHA-256 in
`datasets/miplib2017-guard17/manifest.json`.
