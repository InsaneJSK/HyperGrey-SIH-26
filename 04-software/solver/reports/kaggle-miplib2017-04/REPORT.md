# MIPLIB 2017 benchmark sweep, batch 3 of 4 — cancelled at 44 of 60

18 September 2026. Instances 120 to 179 of the MIPLIB 2017 benchmark list, same
script, same frozen binary
(`e40e849f69d273777089e3cfd21fdfd7f29803f50cf0ef4f39e26691295c866c`) and same
settings as batches [1](../kaggle-miplib2017-02/REPORT.md) and
[2](../kaggle-miplib2017-03/REPORT.md): 300 seconds per instance, two at a time on
a Kaggle CPU session.

**The session ended as `CANCEL_ACKNOWLEDGED` after 21,346 seconds**, having
finished 44 instances (positions 120–163, the last being
`nursesched-sprint02`). The cancellation did not come from this project's
tooling; whether it was cancelled from the Kaggle interface or stopped by the
platform is not recorded in anything returned. Because the script writes
`results.json` after every instance, the 44 finished records were recovered
intact. **Positions 164–179 were never attempted** and remain to be run.

**No timing claim.** Two instances share four cloud vCPUs.

## Result, 44 recovered records

| | Count |
|---|---:|
| Proven optimal, agreeing with the published value | **1** (`neos8`) |
| Proven infeasible, agreeing with the published status | **1** (`neos859080`) |
| Feasible points returned and independently validated | **7** |
| Points rejected by the checker | **0** |
| Answers disagreeing with MIPLIB | **0** |
| Stopped by the open-node memory guard | 6 |
| Root LP never resolved | 5 |
| Process errors | 0 |

`neos859080` deserves a line: a declared-infeasible result is the easiest kind
of confident wrong answer, so it was checked before anything else. MIPLIB's
solution file lists it as `=inf=`; this project proved it infeasible in 2
seconds and 93 nodes. It is the same model the development suite has always
answered correctly.

This slice is the hard end of the list for this engine — 7 validated points in
44 instances against 21 and 25 in the first two batches of 60.

### Memory guard, again with the old representation

`neos-4954672-berkel`, `neos-787933`, `neos-848589`, `neos-911970`,
`nexp-150-20-8-5` and `nu25-pr12` stopped on the guard. This sweep runs the
pre-iteration-33 binary, where every open node stores dense bound vectors; the
[guard re-run](../milp-iteration-33/guard-rerun/REPORT.md) removed 15 of 16 such
stops on the new representation. `nu25-pr12` was within 0.004% of its published
optimum (53925 against 53905) when it stopped.

### Root LP

`neos-662469`, `neos-827175`, `neos-933966`, `neos-957323` and `ns1208400`
report `unresolved_relaxations` at the root.

## Running total, batches 1–3

**164 of 240 instances attempted.**

| | Count |
|---|---:|
| Proven optimal | **6**, all agreeing with the published value |
| Proven infeasible | **1**, agreeing |
| Validated feasible points | **53** |
| **Points rejected by the independent checker** | **0** |
| **Answers disagreeing with MIPLIB** | **0** |
| Stopped by the memory guard (old representation) | 23 |
| Root LP never resolved | 17 |
| Process errors | 1 (`buildingenergy`, LU fill budget) |

## Still to run

- Positions **164–179** (16 instances) from this batch.
- Batch 4, positions **180–239**, held while the iteration 33 holdout used
  positions 180–212. That iteration has now concluded, so the hold can lift; the
  ten holdout models become development data once batch 4 runs.

## Artifacts

`returned/results.json` (44 records, per-instance JSON under `returned/results/`)
and the session log. No `SUMMARY.json` or `carry_over.json` exists because the
session never reached the end of the script.
