# Fresh untouched MILP holdout, declared before download or solve

17 September 2026. Select 15 public MIPLIB 3 models from the same historical
index already retained in `datasets/miplib/index.html`:

`dcmulti`, `dsbmip`, `fiber`, `fixnet6`, `khb05250`, `l152lav`, `misc06`,
`mod010`, `p0548`, `pp08a`, `qiu`, `set1ch`, `stein45`, `gesa3`, `modglob`.

Selection rule: MIPLIB 3 instances with published optimal values and at most
about 3,000 columns, excluding every model in the development suite and in the
iteration 28 holdout. A search of `docs`, `scripts`, `tests`, `examples`,
dataset manifests, `README.md`, the outer planning files, and report Markdown,
JSON and Python files at report top level found none of these names; they
appear only in the retained MIPLIB index listing. None was downloaded or solved
before this declaration, and no outcome informed the choice.

The set mixes structures: fixed-charge networks (fixnet6, set1ch, modglob),
set covering/packing and knapsack-like binaries (p0548, stein45, l152lav,
mod010), and mixed general models (dcmulti, dsbmip, fiber, khb05250, misc06,
pp08a, qiu, gesa3). gesa3 is related to the earlier gesa2 holdout. It is a
moderate historical set, not evidence for arbitrary industrial scale.

Download the original archives with the iteration 28 URL pattern, keep any
failure in the manifest, bound sizes, and record exact hashes. Run each model
once per profile with the declared iteration 30 settings, serially. Published
optimal values are used only when reading the report, never as solver input.
Once a result from this set influences tuning, the set becomes development data.
