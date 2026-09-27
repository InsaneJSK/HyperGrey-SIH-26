# Datasets

Benchmark and holdout **problem instances** — the models this solver is tested
on. These are not training data; nothing in this project learns from them.

## Model files were removed on 21 September 2026

The `.mps` files for the iteration holdouts, the mechanism sets and the
diagnosis sets were deleted to save disk. **Every `manifest.json` was kept**, and
each one records, per instance:

- the exact download URL,
- the SHA-256 of the model bytes,
- its size, and the date it was fetched.

So each set is reproducible and verifiable: re-download from the recorded URL and
check the hash against the manifest. Any silent change upstream would be
detected. The download scripts are kept too, one per set, in the matching
`reports/milp-iteration-NN/download_fresh_holdout.py`.

Still present:

- `miplib2017-parta/` — the 60 benchmark instances of the iteration 37
  ablation, kept while that comparison runs.
- `milp-iteration-28-holdout/`, `milp-iteration-30-holdout/` and the other
  model files committed to git, which are unaffected.

## What each set is

| Folder | Set |
|---|---|
| `miplib`, `miplib2017`, `netlib`, `qplib` | Public benchmark libraries |
| `milp-robustness-wave1`, `milp-*-holdout` | The 27-model development suite and each iteration's declared untouched holdout |
| `miplib2017-guard17`, `miplib2017-regression`, `milp-iteration-36-mechanism` | Instances that exposed a specific defect, retained as the mechanism sets for iterations 33, 36 and 37 |

A holdout is declared in its iteration's `HOLDOUT_SELECTION.md` **before** the
models are downloaded, and becomes development data once its results have been
read.
