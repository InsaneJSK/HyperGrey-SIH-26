# Iteration17 — guarded sparse basis accuracy

Completed locally on 16 September 2026. The captured sparse LP failure is
repaired with unchanged tolerances, but broader performance is mixed. Keep
`--refine-basis` opt-in; it is not a new default or a universal MILP solution.

## Change and safety boundary

`--refine-basis` is an opt-in sparse-LP arithmetic correction. It computes
long-double residuals against the actual current basis, then tries at most two
corrections using the existing LU/eta solves. A correction must be finite and
strictly reduce the RHS-relative residual. It refines basic primal values and
dual multipliers, not pivot directions. Cancellation checks use the existing
LP wall budget. All bounds, tolerances, pivot/fill limits, recovery allowances,
cut rules and restart rules are unchanged. Shared SparseLU and dense simplex
are unchanged. The final original-model primal/dual/gap checks remain required.

The flag defaults to false. The disabled path matches frozen16 in four
fixed-node comparisons. General LP/MILP certificates are numerical, not exact
rational proof. Restricted exact binary witnesses remain a separate category.

## Retained numerical fixture

The original mas74 first-failed child node has 151 continuous variables,
13 rows, 1706 nonzeros and a finite 1e12 variable upper bound. Its original
input basis and full node domain are retained. The normalized MPS SHA256 is
`3de0d967366662e95d8918c68b5cca7b077459d386c9cdb27525faa1a1e81339`.
See `fixture-provenance.json` for the original result and warm-basis hashes.

On the frozen arithmetic path, cold sparse solving takes 130 pivots but fails
the final numerical check: original violation about 9.77e-5, relative gap
3.38e-8 against the unchanged 1e-8 threshold. The initial saved warm input also
fails. Diagnostic correction of that same final basis reduces the violation to
about 7.71e-12, without changing its basis or factors. Fresh factorization alone
does not fix it (about 2.18e-4 violation). The separate source and binary of this
diagnostic are retained; its operations are not benchmark performance results.

The integrated guarded solver passes both cold (130 pivots) and genuine saved
warm (5 pivots, warm_started true) replay. Both objectives are
10515.606014154158. Independent HiGHS1.12.0 solves the unchanged LP to
10515.606014154164 and checks both returned points at about 2.91e-11 absolute
violation. The solver's long-double checks report about 7.71e-12 and 7.94e-12.
Small differences between independent accumulation orders are not material.
No reference point or objective is supplied to the solver.

The 130-pivot cold replay accepts 72 of 99 correction attempts; the 5-pivot warm
replay accepts 12 of 18. The direct one-step diagnostic and integrated iteration
counts measure different experiments. This is an effective repair on the
retained failure, not a proof of convergence for every ill-conditioned basis.

## Paired mas74 screen

Predeclared `SCREEN.json`: two repeats, alternating profile order, identical
30s / 250000-node / 1e-6-gap limits and all other flags. All four points pass
independent original-model validation and proof/work bookkeeping checks.

| Pair | Control outcome | Refined outcome |
| --- | --- | --- |
| 0 | unresolved, objective13533.44858, gap20.5829%,1935nodes | time limit, objective12914.4386906, gap15.7361%,19553nodes |
| 1 | unresolved, objective13954.9471587, gap23.0619%,1669nodes | time limit, objective12914.4386906, gap15.7049%,21093nodes |

Both controls exhaust the unchanged 6s recovery allowance and return around 15s
with 2 unresolved nodes after restart. Both refined runs reach 30s with **zero
LP recovery attempts and zero unresolved/deferred nodes**. The same clock
restart remains enabled. This removes the observed numerical-recovery failure
in these runs and improves feasible objective and gap; it does not prove the
full mas74 MILP optimal. Shared-desktop timing influences the search path.

## Full 24-case development wave

`WAVE.json` predeclares all 24 retained development models, one 30s run per
profile, alternating order. The same executable is used; only `--refine-basis`
differs. No competing task builds/tests/reference runs overlap own-solver
timings. The local desktop is not dedicated benchmark hardware, and wall-clock
heuristic/restart boundaries affect search. Reference solves have a 5s allowance
and separate 150s watchdog, after all own runs; they are correctness references,
not equal-budget performance competitors.

Rounded final gaps are below; raw objectives, points, bounds, times and statuses
remain in `wave-30s/results.json` and per-run JSON. `complete` means the recorded
numerical completion or restricted exact subset, not a general exact proof.

| Model | Control | Refined |
| --- | --- | --- |
| p0033 | complete: 3089 | complete: 3089 |
| enigma | complete: 0 | complete: 0 |
| flugpl | complete: 1201500 | complete: 1201500 |
| stein27 | complete: 18 | complete: 18 |
| markshare_4_0 | complete: 1 | complete: 1 |
| blend2 | no point | no point |
| binkar10_1 | 1.9733% | 1.9700% |
| egout | complete: 568.1007 | complete: 568.1007 |
| gt2 | 67.3177% | 67.3224% |
| lseu | complete: 1120 | complete: 1120 |
| mod008 | 0.3247% | 0.3247% |
| p0201 | complete: 7615 | 0.1970% |
| p0282 | 3.6095% | 3.5960% |
| misc03 | 6.8432% | 2.9753% |
| misc07 | no point | 48.2035% |
| pk1 | 96.2963% | 96.8750% |
| rgn | complete: 82.19999923 | complete: 82.19999923 |
| gen-ip002 | 2.9091% | 2.9201% |
| assign1-5-8 | 17.7728% | 15.3822% |
| lotsize | no point | no point |
| eil33-2 | 31.6800% | no point |
| mas74 | unresolved, 15.4407% | time limit, 15.7015% |
| gen-ip054 | 1.8371% | 1.8455% |
| neos859080 | infeasible | infeasible |

Final categories: control has 2 restricted exact proofs, 7 numerical
completions, 10 checked feasible limits, 1 unresolved checked point, 3 no-point
limits and 1 cross-checked infeasible result. Refined has 2 restricted exact
proofs, 6 numerical completions, 12 checked feasible limits, 3 no-point limits
and 1 cross-checked infeasible result. Both profiles return checked points on
20 of 24 models. There is no general completion-rate or point-coverage gain.

The third mas74 pair again has zero refined recovery attempts and zero
unresolved/deferred nodes at 30s, versus the control's early unresolved exit.
But its **control objective 12708.1019813 is better** than refined 12914.4386906,
and its gap is better too. Thus the paired screen's objective/gap gain does
not generalize even to every repeated mas74 run. The numerical-recovery gain
is present in all three refined runs; no claim of uniformly better objectives
is made.

P0201 returns objective 7615 under both modes, but control finishes at 29.01s
while refined remains open at 30.01s. Control/refined restarts occur after 2943/
3537 nodes, so this is not an isolated arithmetic-overhead experiment. Enigma
takes 12.86/16.82s, lseu 14.13/21.38s and egout 3.43/4.05s (control/refined).
These are single paired desktop timings, not stable speed ratios.

Eil33-2 loses its point under refinement; misc07 gains a point with objective
about 2810 but a 48.2% gap. Assignment improves from about 228 to 221. PK1 worsens
from 26 to 31, both with gaps above 96%. Binkar's slightly smaller relative gap
comes with a worse objective 6812.50002 versus 6810.69003, not overall dominance.
Both mod008 runs stop open in this batch; earlier completions are not reused
to call these new runs complete.

**Decision: keep refinement opt-in.** Preserve the numerical repair, diagnose
its cost and first-feasible trade-offs, and require repeated whole-solve and
fresh-holdout evidence before promoting a general profile.

## Regression gates

`final-gate/SUMMARY.json` records passing 15 CTest groups, 115 Python units,
28 MPS-domain cases, 4 disabled-option fixed-node parity comparisons, 320
generated regression runs on 80 distinct models, and 100 reused exhaustive MPS
cases. The four generated profiles are baseline, refinement, refinement plus
equality compaction, and refinement plus incumbent-gated adaptive cuts.

The dedicated accuracy test covers both retained starting modes, 12 shifted/
scaled min/max LP equivalents, degeneracy and singular bases, infeasible/
unbounded certificates, zero time/pivot allowance, fill rejection, cancellation,
nonfinite/worsening/stagnating corrections and the two-correction cap. Existing
C++ suites preserve their earlier proof/partial-result regression checks.

These are correctness regressions, not 320 newly held-out public benchmarks.
Long-double behavior was tested on local GCC14.2/MinGW; platforms where it has
no extra precision need separate verification. This is not a hard OS resource
sandbox or general exact numerical proof.

## Reproduction and remaining work

The final re-audit passes all **52 public experiment records and 44 returned
points**, with no pending point checks or observed candidate-output validation
failures. It recomputes 4 restricted exact proofs on 2 models, checks 64 retained
lifted covers, 63,548 saved lattice events, 70 cut rounds and 7 cut-source
incumbents. Fourteen lattice traces are explicitly truncated; these saved
events are not a complete replay of all search history. Infeasibility of
neos859080 is cross-checked, not an exact general certificate.

The failed control LP remains an explicitly failing diagnostic, not a valid
LP solve counted among these public-output checks. All numerical regression
and comparison scripts, raw points and independent references are retained.
Source and checker hashes are unchanged through the public timings and audit.
Documentation was finalized afterward. The previous iteration16 source, binary
and recorded evidence are verified unchanged by the freezer.

Final executable: `final_solver_cli.exe`, 764605 bytes, SHA256
`a4b9f9350638f97a5230923554c5788af3c4c95bb552282686aeb408524f88c4`.
`SNAPSHOT_MANIFEST.json` and `FINAL_STATE.json` record the final source and
evidence identities; `FINAL_CMakeCache.txt` preserves the Release MinGW/GCC14.2
CPU-only build configuration. Screen results SHA256:
`5308179f9148aa38297557da409a82b7e8c1c18e4b3a9de8cdd6ca3136f45104`;
wave results SHA256:
`12079666ee450369f1bac22d4cd2e558fc5ed54e1098eba1f749169b76f0c635`.

See [the algorithm](../../docs/SPARSE_BASIS_REFINEMENT.md) and
[local reproduction](../../docs/V2_REPRODUCE.md). CPU only, no Kaggle upload.
Use retained inputs and fresh output directories. Do not rerun setup/freezer
scripts against existing archives. Iteration16 remains the frozen control.
The 24 public cases are development models, not untouched holdouts. No
competition-percentile or universal-public-MILP claim is supported.
