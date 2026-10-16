# Iteration 36 — a resource limit is a failed LP, not a dead solve

20 September 2026. Plan declared before any code change, with an amendment
declared before further measurement (`PLAN.md`). Binary SHA-256
`e379b12cb5136cdf04ae22539d00073730dd94672b1b2075c7e8e5012bf11dad`, 213 frozen
source files. Control is the iteration 35 frozen executable (`58faf7cf…b79a`) on
**identical flags**; only the executable differs.

## What was wrong

`neos8` (46,324 × 23,228) is one of the seven instances the MIPLIB 2017
benchmark proves optimal, at -3719. Under the recommended profile it **aborted**
with `resource_limit: sparse LU fill budget` and exit 2 — the code for a
rejected input. The factorization budget threw, nothing caught it, and a limit
hit on one strengthened relaxation destroyed the whole solve, including a valid
pre-cut relaxation. The same throw made `buildingenergy` and `supportcase10`
look like malformed models in the benchmark.

## Two mechanisms, the second declared as an amendment

1. A relaxation that raises `resource_limit:` **returns a failed relaxation**
   instead of propagating the exception. One catch point, restricted to that
   message prefix so real faults still propagate.
2. The first mechanism alone stopped the abort and found -3719, but could not
   prove it: `cut_rollbacks=0, cuts=91` showed the limit is not hit during
   cutting but at a node with 91 separator rows already in the model. So: **when
   a relaxation hits the limit and separator rows are present, discard every one
   and retry the node once.** Those rows are optional by construction, and the
   model without them is the one the benchmark proved in 153 nodes.

The amendment is in `PLAN.md`, declared before any further measurement, and says
plainly that this is recovery and not prevention: the underlying cause is
iteration 32's support cap, which lets one cut carry up to 5,000 nonzeros.
Changing that alters cut selection on every model and belongs in its own
iteration.

New counters `lp_resource_limits` and `separator_rows_discarded` in the JSON.

## Correctness gate

CTest 28/28. `sparse_accuracy_gate.py` with the full flag set: `all_pass`, 14
generated profiles.

## The three known resource-limit instances, 300 s, paired

| Instance | Control | Candidate |
|---|---|---|
| **`neos8`** | **aborted, exit 2** | **`gap_limit`, -3719, gap 0, 67 nodes, 83 s** |
| `buildingenergy` (277,594 × 154,978) | `time_limit`, no root | `time_limit`, no root |
| `supportcase10` (165,684 × 14,770) | `time_limit`, no root | `time_limit`, no root |

| | Control | Candidate |
|---|---:|---:|
| Roots solved | 0 | **1** |
| Proven optimal | 0 | **1** |
| Rejected points / disagreements | 0 / 0 | 0 / 0 |

`neos8`'s objective, -3719, is exactly MIPLIB's published value. **91 separator
rows were discarded** on the retry; the bound it then reached was the proven
optimum, against a control that produced nothing at all.

`buildingenergy` and `supportcase10` are genuinely too large to factorize and
still return no root. That is the correct outcome; what changed is that they say
so as a status with a full JSON result rather than exiting like rejected input.

## Development: 27 models, two repeats, 54 records

| | Iteration 35 | Iteration 36 |
|---|---:|---:|
| Completions (our status) | 26 | 26 |
| Checked points | 50 | 50 |
| Validation failures | 0 | 0 |
| Resource limits hit / rows discarded | 0 / 0 | **0 / 0** |

The new path never fired here, which is the expected result: no model in this
set approaches the factorization budget, and the change is inert where no limit
is hit.

## Fresh set: the eight largest unused benchmark instances

Declared in `PLAN.md` before any run, by size, because size is the property
under test: `neos-3402454-bohle` (2,897,380 rows), `neos-5114902-kasavu`,
`supportcase19` (1,429,098 columns), `supportcase12`, `neos-5104907-jarama`,
`gfd-schedulen180f7d50m30k18`, `ns1760995`, `savsched1`.

**Control and candidate are identical on all eight**: no root solved in 300
seconds, no crash, no rejected point, no disagreement. `neos-5104907-jarama`
reached the external watchdog in both builds.

Nothing regressed and nothing improved. These instances never get far enough to
add a separator row, so there is nothing for this change to act on — which is
the honest reading, and it is why the mechanism set is where the evidence is.

## Decision

| Declared criterion | Result |
|---|---|
| Zero validation failures and zero rejected points in every set | ✅ |
| No objective disagreeing with a published or proven optimum | ✅ `neos8` = -3719 |
| **`neos8` proven optimal at -3719 under the full recommended profile** | ✅ gap 0, 67 nodes |
| No instance exits 2 on a resource limit; each reports a status | ✅ all three |
| Development completions and coverage do not fall | ✅ 26 → 26, 50 → 50 |
| Fresh set: no instance worse than its control | ✅ identical on all eight |

**Promoted.** Executable defaults unchanged.

Required by the amendment: the only instance where separator rows were
discarded is `neos8` — 91 rows, reaching a proven -3719 against a control that
aborted. No instance in any set ended with a worse bound than its control.

## What this does not show

- It does not make large models solvable. Two of the three mechanism instances
  and all eight fresh instances still return no root. It converts a crash into
  an honest answer and recovers one proof.
- The support cap that allows a 5,000-nonzero cut is untouched and remains the
  underlying cause.

## Iteration 37 candidates, in order

1. **Cut density**: bound a tableau cut's support so a strengthened model stays
   factorizable, instead of discarding every cut after the fact. Needs its own
   measurement — it changes cut selection everywhere.
2. LP throughput: `dano3`, `mzzv`, `brazil3`, `irish-electricity` cannot finish
   a root in 300 s.
3. Carried: frontier-aware search for `markshare2`; the trail path-entry cap.
4. **Re-run the full MIPLIB 2017 benchmark on the current engine.** Iterations
   33 to 36 each fixed a failure category the benchmark exposed; the table in
   `reports/miplib2017-benchmark/` still records the engine from before them.

## Artifacts

`PLAN.md` (with amendment), `SOURCE_IDENTITY.json`, `gate/`,
`development-30s/` (54 records), `mechanism-300s/` and `fresh36-300s/` (every
monitor record, `results.json`, `SUMMARY.json`), `paired.py`, and the frozen
binary with runtime DLLs and `final-source/`.
