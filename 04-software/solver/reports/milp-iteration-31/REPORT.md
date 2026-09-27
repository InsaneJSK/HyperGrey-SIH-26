# Iteration 31 — search heuristics for fast relaxations

18 September 2026. Two bounded heuristics and one allocation fix, measured
against the promoted iteration 30 profile on the same executable and host, with
**zero validation failures** in every set. The candidate improves checked
incumbents on nine development models against two marginal regressions and adds
a checked point on the fresh holdout. A third profile that replaces the
half-time restart with root cuts is the strongest on unseen models and is
promoted together with the heuristics.

| Set | Profile | Completions | Checked points | Validation failures |
|---|---|---:|---:|---:|
| Development, 27 models, repeat 1 / repeat 2 | control | 10 / 11 | 25 / 25 | 0 |
| | candidate | 11 / 11 | 24 / 25 | 0 |
| | norestart | 11 / 11 | 25 / 25 | 0 |
| Fresh holdout, 12 unseen models | control | 1 | 8 | 0 |
| | candidate | 1 | **9** | 0 |
| | norestart | 1 | **10** | 0 |

## What changed

One executable (`final_solver_cli.exe`, SHA-256 `40270cdb…8c47`):

1. **`--tree-dives`.** After an incumbent exists, the existing dive block also
   runs during the search: interval 32 nodes, halved on improvement, doubled on
   failure, bounded to 16–1024 nodes and to about a tenth of elapsed time. A
   third dive mode selects the fractional coordinate closest to the incumbent
   and rounds toward it. Dives create no node and export no bound; every point
   passes the existing acceptance checks.
2. **`--fix-propagate`.** Fix integer columns one at a time (nearest-integral
   LP values first, or toward lower/upper bounds), propagating after each
   fixing, with bounded chronological backtracking (16 retained frames, at most
   32 backtracks), then solve the LP over the remaining continuous columns and
   offer the point to `accept()`. Runs at the root and, while no incumbent
   exists, in the tree with geometric backoff.
3. **Propagation buffer (shared, no semantic change).** Bound propagation reused
   one scratch vector instead of allocating per row and pass. Fixed-budget
   observation on gt2 with identical flags: nodes in 30 s rise from about
   148,000 to about 390,000 and propagation time falls from 11.4 s to 8.3 s.
   Both profiles carry this fix, so the comparison below does not measure it.
4. **Profile variant `norestart`.** The same heuristics with
   `--late-lifted-covers`, `--late-compact-equalities` and
   `--late-reduced-bound-lp` replaced by `--lifted-covers`: lifted cover cuts at
   the root instead of a restart at half time, which since iteration 30 discards
   a much larger tree.

## Correctness gate (before timed runs)

`sparse_accuracy_gate.py --bounded-lp --search-heuristics`: 27/27 CTest groups,
180 Python tests plus the new `check_search_heuristics.py` tests, disabled
parity against frozen 16 on gt2/lseu/mod008/misc03, **480** generated
binary/mixed runs across six profiles and **300** retained lattice runs (three
engine settings), all matching their expected answers.

## Development set, two repeats

Consistently better with the candidate, both repeats (control → candidate):

| Model | Control | Candidate | Published optimum |
|---|---|---|---:|
| gt2 | 50894 / 50894 | **35409 / 35409** | 21166 |
| rout | 1305.77 / 1305.77 | **1131.72 / 1131.72** | 1077.56 |
| misc07 | 3130 / 3130 | **2810 / 2810** | 2810 |
| p0282 | 266462 / 266462 | **262642 / 258682** | 258411 |
| mas74 | 12590.37 / 12590.37 | **12421.39 / 12341.95** | 11801.19 |
| mas76 | 41519.99 / 41519.99 | **40962.97 / 41278.03** | 40005.05 |
| gen-ip002 | -4681.76 / -4681.76 | **-4737.34 / -4715.11** | -4783.73 |
| gen-ip054 | 6911.53 / 6911.53 | **6907.86 / 6898.67** | 6840.97 |
| pk1 | 17 / 17 | 17 / **16** | 11 |

Regressions, both retained: `eil33-2` 989.39 against 987.67 in one repeat
(0.17%), and `assign1-5-8` 213 against 212 in repeat 2 (0.5%). `binkar10_1` is
mixed (6769.74/6775.25 against 6797.60/6759.38).

`danoint` is **variable, not a regression**: control found 86 and 71.25,
candidate none and 72, norestart 86 and 86. The first repeat's apparent lost
point (24 against 25) did not reproduce; the plan amendment declared this second
repeat before the result was read.

`mod008` counts as a completion for the control only in repeat 2: the solver
closed it in both, but the 5-second HiGHS reference confirmed optimality only in
the second run. This is a reference budget effect, not a solver difference.

`lotsize` still has no point in any profile: fix-and-propagate reaches about
2,300 fixings without completing an assignment, and pump projections and dives
consume most of the budget.

## Fresh untouched holdout (12 MIPLIB 3 models, declared before download)

| Model | Control | Candidate | Norestart | Published |
|---|---|---|---|---:|
| qnet1 | 29189.42 | 18591.41 | **17290.93** | 16029.69 |
| pp08aCUTS | 7890 | 8090 | **7770** | 7350 |
| nw04 | 17514 | 17514 | **17004** | 16862 |
| mod011 | none | none | **-51986929** | -54558535 |
| gesa2_o | none | **25972278** | 25973474 | 25779856 |
| gesa3_o | 28061180 | **27991430** | **27991430** | 27991043 |
| harp2 | -70381679 | **-71531923** | -70566414 | -73899798 |
| cap6000 | **-2451336** | -2450867 | **-2451336** | -2451377 |

`air03` completes in all three profiles at 340160, the published optimum.
`10teams` is 934 in all three (optimum 924). `mitre` and `p2756` have no point
in any profile. The norestart profile also repairs the candidate's pp08aCUTS
regression and is the only profile to find an mod011 point.

## Resources and retained observations

Peak sampled commit: control 501 MiB, candidate 350 MiB, norestart 1088 MiB
(gt2, repeat 2) against the 1536 MiB threshold. Without the half-time restart
the frontier grows larger, and the open-node guard's estimate is conservative
for gt2, so the margin is thinner than the guard implies. No watchdog stop,
memory-guard stop or process failure occurred in any set.

The fresh holdout shows more bounded-engine fallbacks under norestart (18
against 3 and 5): more root cut rows make some node LPs harder, and those LPs
are then solved by the existing engine, as designed.

A reporting defect is retained for the next iteration: when the global time
budget expires inside a node relaxation, the result message still reads "LP
relaxation did not pass its numerical checks" instead of naming the time limit.
The status itself (`time_limit`) is correct.

## Decision

Promote both heuristics and the cut-timing change. The recommended MILP
evaluation profile becomes the iteration 28 flags with `--bounded-lp
--tree-dives --fix-propagate`, and with `--lifted-covers` in place of the three
`--late-*` flags (`CANDIDATE_PROFILE.json`, field `norestart_flags`).
Justification against the declared rule: zero validation failures; completions
never fall; checked points never fall across repeats (danoint is variable);
incumbent quality improves on nine development models against two marginal
regressions; and on the unseen set the promoted profile returns 10 checked
points against the control's 8, including one model no other profile solved.

Executable defaults remain unchanged. The gt2 memory margin, the `eil33-2`,
`assign1-5-8` and `binkar10_1` regressions, `lotsize`, `mitre` and `p2756`
first-point failures, and the bound weakening on `p0282` without the restart
(gap 5.2% against 2.0%, with a better incumbent) are all retained as open items.

## Next

1. Incremental propagation: propagation is still the largest single phase on
   gt2 after the buffer fix.
2. Gomory mixed-integer cuts from bounded tableau rows, and reliability
   branching now that probes are cheap, to attack the bound side.
3. First points for lotsize, mitre and p2756: a shift-and-propagate style
   heuristic with locks, and a longer fix-and-propagate budget on large models.
4. Fix the time-limit message and tighten the open-node guard estimate.
