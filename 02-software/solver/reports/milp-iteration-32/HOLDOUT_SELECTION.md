# Third fresh holdout, declared before download or solve

18 September 2026. The iteration 31 holdout became development data: its
`mod011` outcome was cited when the iteration 31 profile was promoted, and its
models have been solved. This iteration declares a new untouched set of 10
public MIPLIB 3 models from the same retained historical index
(`datasets/miplib/index.html`):

`air04`, `arki001`, `dano3mip`, `gen`, `markshare1`, `markshare2`, `mkc`,
`rentacar`, `seymour`, `swath`.

## Selection rule

Every MIPLIB 3 name in the retained index that is not in the 27-model
development suite, the iteration 28 holdout, the iteration 30 holdout or the
iteration 31 holdout. That leaves 13 names; three are excluded for stated
reasons, not for any outcome:

- `qnet1_o` is a variant of `qnet1`, which is in the iteration 31 holdout, so
  it is not an independent model.
- `air05` and `fast0507` are positions 4 and 48 of the MIPLIB 2017 benchmark
  list, inside the first batch of the Kaggle sweep now running. Their results
  will be visible before this iteration concludes, so they cannot support an
  unseen claim here.

A search of `docs`, `scripts`, `tests`, `examples`, `README.md`, the dataset
manifests, the iteration reports and the outer planning file found none of the
ten names, including a targeted check that `gen` appears nowhere except as a
prefix of the unrelated `gen-ip002` and `gen-ip054`. None was downloaded or
solved before this declaration and no outcome informed the choice.

## What this set is and is not

It is the hard end of MIPLIB 3 and that is deliberate — it is what remains
untouched, and it is where cuts are most likely to do damage rather than good:
`air04` is set partitioning with about 8,900 columns where dense tableau cuts
could swamp the relaxation, `seymour` and `mkc` are known hard covering and
capacitated models, `dano3mip` and `arki001` are historically difficult, and
`markshare1`/`markshare2` are market-share instances that no solver closes at
this budget.

So this set is a **safety and generalization check**, not the primary
discriminator. Few completions are expected in either profile. A result of
"no completions in either profile, no failures, no rejected points" is a pass
for the holdout and the development evidence then decides. Any completion,
either way, is reported as the exception it would be.

`markshare2` and `seymour` appear in later MIPLIB 2017 benchmark batches. Once
those batches run they stop being unseen for future iterations, and that will
be recorded.

Run each model once per profile with the declared iteration 32 settings
(30 s, gap 1e-6, node limit 100,000,000), with a 30 s HiGHS 1.12.0 reference
on the original file. Failures are retained, never rerun away.
