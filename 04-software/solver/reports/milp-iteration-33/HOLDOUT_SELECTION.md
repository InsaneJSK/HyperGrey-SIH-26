# Fourth fresh holdout, declared before download or solve

18 September 2026. The MIPLIB 3 index is now exhausted: iterations 28, 30, 31
and 32 have consumed every name in it except `air05`, `fast0507` and `qnet1_o`,
and the first two are inside the Kaggle sweep's batch 1 while the third is a
variant of an already-used model.

This iteration therefore declares a set of 10 models from the **MIPLIB 2017
benchmark list, positions 180 to 212**, which falls inside batch 4 of the sweep
and has **not been run** by this project in any form:

`rail507`, `ran14x18-disj-8`, `reblock115`, `rmatr100-p10`, `rocI-4-11`,
`roll3000`, `s250r10`, `sct2`, `sorrell3`, `sp150x300d`.

## Selection rule

Take the benchmark list positions 180 onward, in the order the list gives them,
and keep the first ten that are not already used by this project. `seymour`
(position 202) is skipped because it is in the iteration 32 holdout. No other
name in that range has been downloaded, solved or referenced here; the sweep has
so far covered positions 0 to 179 only (batches 1 and 2 completed, batch 3
running at the time of this declaration).

**Batch 4 of the sweep is held until this iteration concludes**, so these ten
stay unseen for the duration of the comparison. Once batch 4 runs they become
development data and this is recorded.

## Why this set suits this iteration

The change under test is what an open node costs, and the win scales with
column count. This set spans small-column and wide models — `rail507` and
`sp150x300d` are set covering and partitioning with many columns, `rmatr100-p10`
and `rocI-4-11` are structured, `roll3000` and `sct2` are production and
scheduling models — so it tests the representation where it should help and
where it should not.

It is also hard. Few completions are expected in either build, and a result of
"no new failure, no new memory-guard stop, no rejected point" is a pass. Any
completion either way is reported as the exception it would be.

## Protocol

Run each model once per build with the declared iteration 33 settings (30 s,
gap 1e-6, node limit 100,000,000), same flags for both, with a 30 s HiGHS
1.12.0 reference on the original file. The control is the frozen iteration 32
executable; the candidate is the iteration 33 executable. Failures are retained,
never rerun away.
