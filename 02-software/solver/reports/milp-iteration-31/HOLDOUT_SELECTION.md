# Second fresh holdout, declared before download or solve

18 September 2026. The iteration 30 fresh set became development data: its
p0548 and gesa2 outcomes informed the fix-and-propagate backtracking design.
This iteration therefore declares a new untouched set of 12 public MIPLIB 3
models from the same retained historical index (`datasets/miplib/index.html`):

`10teams`, `air03`, `cap6000`, `gesa2_o`, `gesa3_o`, `harp2`, `mitre`,
`mod011`, `p2756`, `pp08aCUTS`, `qnet1`, `nw04`.

Selection rule: MIPLIB 3 instances with published optimal values that are not
in the 27-model development suite, the iteration 28 holdout or the iteration 30
holdout. A search of `docs`, `scripts`, `tests`, `examples`, `README.md`,
dataset manifests and the outer planning file found none of these names; they
appear only in the retained MIPLIB index listing. None was downloaded or solved
before this declaration and no outcome informed the choice.

The set deliberately spans structures and sizes: set partitioning/covering
(air03, nw04 with about 87,000 columns, 10teams), fixed-charge and network
models (gesa2_o, gesa3_o, p2756, pp08aCUTS), difficult scaling and structure
(harp2, mitre, mod011, cap6000, qnet1). gesa2_o/gesa3_o are variants of the
earlier gesa2/gesa3 models and are not independent families. This is a
moderate historical set, not evidence for arbitrary industrial scale.

Run each model once per profile with the declared iteration 31 settings,
serially, control and candidate only. Published optima are used only when
reading the report, never as solver input. Once any result here influences
tuning, this set also becomes development data.
