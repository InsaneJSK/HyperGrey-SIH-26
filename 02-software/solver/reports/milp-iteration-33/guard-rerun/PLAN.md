# Guard re-run — does the headroom convert into proofs?

Declared 18 September 2026, before any of these runs.

## The question

Iteration 33 was justified by 17 MIPLIB 2017 benchmark instances that stopped
on our own open-node memory guard in the Kaggle sweep. It then showed 1.44x to
9.39x less memory per node and 24 against 24 completions on the development set
— headroom, not proofs. This run is the direct test of whether that headroom
turns into anything on the instances that motivated it.

## These are not unseen models

All 17 informed the design of iteration 33. Nothing here supports a
generalization claim; it is the mechanism test on the cases it was built for.
The generalization evidence is the iteration 33 holdout, already reported.

## Models

The 17 guard stops from sweep batches 1 and 2:

`50v-10`, `binkar10_1`, `exp-1-500-5-5`, `fiball`, `gen-ip054`, `glass4`,
`gmu-35-40`, `gmu-35-50`, `h80x6320d`, `irp`, `markshare2`, `mas74`, `mas76`,
`neos-2657525-crna`, `neos-3004026-krka`, `neos-3046615-murg`,
`neos-3381206-awhea`.

## Design

- **Old**: iteration 32 frozen executable (`6e073229…351a4`), dense open nodes.
- **New**: iteration 33 frozen executable (`db61dd26…f045`), trail open nodes.
- **Exactly the sweep's flag list**, 300 seconds, gap 1e-6, node limit
  100,000,000, default 960 MiB guard. Only the executable differs.
- **Paired and simultaneous**: for each model, old and new start at the same
  moment on this 8-core, 40 GB host and run side by side. Whatever load the
  machine carries in those five minutes, both builds carry it together. The MILP
  path is single-threaded, so two processes on eight cores do not compete for a
  core.
- Peak commit sampled by the same `run_contained.py` monitor the iterations use.

## Checks

- Every returned point is checked for feasibility and integrality against the
  original file by an independent HiGHS 1.12.0 reader.
- Objectives are compared with MIPLIB's published solution file.

## What will be reported, fixed in advance

1. **Primary: memory-guard stops, old against new.** The iteration exists to
   remove these.
2. Completions, validated points, and each objective's distance from the
   published optimum.
3. Nodes explored and peak commit per model.
4. Every rejected point and every disagreement with a published optimum, which
   must both be zero.

Neither outcome changes iteration 33's promotion, which was decided on its own
declared evidence. If the guard stops disappear but no proof follows, that is
the result and it is reported as that.
