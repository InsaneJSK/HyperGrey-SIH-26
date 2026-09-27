# Iteration 31 plan — search heuristics for fast relaxations

Declared 18 September 2026, before any timed comparison or fresh-holdout solve.

## Hypothesis

Iteration 30 made relaxations fast, so bounds now close quickly while incumbent
quality limits several models (gt2 regressed to 50894 against a 35673 control;
p0282, rout, mas76, gen-ip054 keep large primal gaps; lotsize, p0548 and
danoint had no point in the formal run). The tree finds few good leaves because
dives run only at the root or while no incumbent exists, and no heuristic
searches for a first point by fixing variables.

Adding two bounded heuristics and removing an allocation hot spot should
improve checked incumbents and first-point coverage at the same 30-second
budget, without losing completions or validation.

## Mechanisms (measured together, ablated by profile)

1. `--tree-dives`: after an incumbent exists, run the existing dive block
   periodically (interval 32 nodes, halved on improvement, doubled on failure,
   capped 16–1024), limited to about a tenth of elapsed time, with a third
   dive mode that rounds toward the incumbent and selects the fractional
   coordinate closest to it. Dives are heuristics: they add no node, export no
   bound, and every point passes the existing acceptance checks.
2. `--fix-propagate`: fix integer columns one at a time (nearest-integral LP
   values first, then rounding policies toward lower and upper bounds),
   propagating after each fixing, with bounded chronological backtracking
   (16 retained frames, at most 32 backtracks), then solve the LP over the
   remaining continuous columns and offer the point to `accept()`. Runs at the
   root and, while no incumbent exists, in the tree with geometric backoff.
3. Shared, no semantic change: bound propagation reuses one scratch buffer
   instead of allocating per row and pass. On gt2 this alone raises nodes in
   30 s from about 148,000 to about 390,000 and cuts propagation time from
   11.4 s to 8.3 s. Both profiles below carry this fix, so it is not what the
   comparison measures; it is reported separately as a fixed-budget observation.

## Profiles

- Control: the iteration 30 promoted profile (iteration 28 flags plus
  `--bounded-lp`) on the iteration 31 executable.
- Candidate: control plus `--tree-dives --fix-propagate`.
- Candidate-norestart (development set only): candidate with
  `--late-lifted-covers`, `--late-compact-equalities` and
  `--late-reduced-bound-lp` replaced by `--lifted-covers`, i.e. root cuts
  instead of the half-time restart that now discards a much larger tree.

Serial runs, rotating profile order, 30 s, gap 1e-6, node limit 100,000,000,
45 s watchdog, 1536 MiB sampled commit threshold, same executable.

## Model sets

1. Development: the 27 reused models, one repeat per profile (three profiles).
2. Fresh holdout: 12 public MIPLIB 3 models never downloaded or solved by this
   project, declared in `HOLDOUT_SELECTION.md` before download, control and
   candidate only. The iteration 30 fresh set is now development data: its
   p0548 and gesa2 outcomes informed the backtracking design, so it cannot
   support a generalization claim here and is not rerun for that purpose.

## Validation

Every record is checked against HiGHS 1.12.0 on the original model (5 s
development references, 30 s holdout references), with the existing
work/frontier/cut/pump/bounded checks and a new `check_search_heuristics.py`
accounting check. The correctness gate runs first with `--bounded-lp
--search-heuristics`, adding a fifth generated profile and a third engine pass
over the 100 retained lattice cases.

## Decision rule

Promote the candidate only if, against the control:

- zero validation failures in every set;
- completions do not fall in either set;
- checked-point coverage does not fall;
- checked incumbent quality improves on more models than it worsens, counting
  only differences above 1e-6 relative.

The norestart profile is decided separately on the development evidence and is
not promoted without its own holdout run. Executable defaults stay unchanged.
Report every regression, including any model where a dive or fixing consumed
budget without producing a point.

## Amendment after the first repeat (declared before the second)

The first development repeat gives control 10 completions / 25 checked points,
candidate 11 / 24, norestart 11 / 25. The candidate's only lost point is
`danoint`, a model whose first feasible point is marginal on this host: the
iteration 30 formal run found no danoint point in EITHER profile, while
development screens found 86 and 94 with the candidate. One repeat cannot
separate a real loss from run-to-run variation, and the declared rule
("checked-point coverage does not fall") must not be judged on it.

Therefore, before reading any further result: run a second full development
repeat for all three profiles, and run the norestart profile on the already
declared iteration 31 holdout so all three profiles have holdout evidence.
Both repeats are reported; the decision uses per-model outcomes across both,
and any model that differs between repeats is named as variable rather than
counted as an improvement or a regression.
