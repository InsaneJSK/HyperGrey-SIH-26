# MILP iteration05 — measured, opt-in neighbourhood diversification

This is a CPU-only search experiment, not a new optimization problem class.
`--improve-incumbent --neighborhood guided` retains iteration04's local search.
`--neighborhood diversified` changes restricted-variable selection only after
four consecutive neighbourhood calls fail to improve the incumbent, and gives
those calls more of the existing allowance. Selecting a mode alone does not
enable heuristics; `--improve-incumbent` is still required.

## Restriction and proof boundary

Each neighbourhood starts from the original variable bounds, the current
incumbent, and the current relaxation. All continuous variables remain free.
Most integer variables are fixed to their incumbent values; the selected
integers retain their original domains, including general-integer bounds.
The model includes the same retained globally valid cover cuts as the tree.

The restricted search uses the existing sparse LP engine and a private
depth-first stack. Its accepted points must pass the unchanged original-model
absolute feasibility check <=1e-7 and integer check <=1e-7. Integer values are
rounded only inside that integer tolerance. Objectives are recomputed from
original coefficients in the original optimization sense.

A restricted optimum/infeasibility result is NOT a proof about the full MILP.
Local bounds, failures and exhausted stacks never replace a global tree bound
or prune assignments outside the restriction. Only a checked incumbent is
exported. `frontier_exhausted` is a diagnostic, not a global proof certificate;
local numerical failures can also discard heuristic-only work.

## Guided and diversified selection

Guided selection is unchanged: rank movable integers by normalized difference
between the current relaxation and incumbent, with the same small deterministic
tie perturbation. Release min(number of movable integers,48,max(8,n/5)).

After four unsuccessful calls, the optional selector keeps the top two-thirds
of the chosen free set guided, and uses a deterministic64-bit index/call-number
mixing function to select the remaining third from other ranked variables.
Success resets the stall count. On alternating stalled calls it doubles the
free count, capped by the number of movable integers and96. Selection does
not use model names, known optima, reference candidates or external optimizers.

The first probe switched after two unsuccessful calls and regressed on binkar
at90 seconds:6789.67 versus guided6757.19. Those source/binary/results are
preserved in `reports/milp-iteration-05/probe-source`, `probe_solver_cli.exe`
and `probe-90s/`. The retained experiment delays the trigger; the failed probe
is not presented as a successful improvement.

## Budgets and diagnostics

Both modes have the same global local-search allowance:
min(30 seconds,15% of the MILP time limit), at most16 calls, separated by at
least128 processed global nodes. Guided calls get up to2 seconds/64 local
nodes. After the four-stall trigger, diversified calls get up to4 seconds/128
nodes. All calls are further limited by20% of remaining global time and the
remaining cumulative allowance. Limits are cooperative: setup/factorization
can slightly overrun a deadline. No-heuristics and zero-time controls still
disable the search.

## Separate time-spacing option

`--pace-neighborhood` retains the selected variable-ranking method and all
existing call, node and cumulative-time caps. In addition to the128-main-node
gate, it spaces successive call starts by at least min(5 seconds,2% of the
MILP time budget). The first call is not delayed. It does not increase the
heuristic time allowance. The option is off by default.

This addresses the observed markshare call exhaustion before1 second, well
before the main tree's better incumbents. It is tested with the guided selector
to separate scheduling from diversification. CLI output records
`neighborhood_paced` and `neighborhood_min_spacing_seconds`; the independent
audit checks the actual recorded start-time intervals.

`--capture-neighborhood` records start time, elapsed time, budget, node count,
LP failures, stall count, selection mode, released integer indices, before/after
objectives and whether each call improved the incumbent. It captures the final
improved vector of each successful call on models with at most10000 variables.
At most32 trace entries are retained (the current call cap is16). Intermediate
improvements within a call may have only objective/time records, not vectors.

The local audit rechecks captured vectors with the independent original-MPS
reader after all timed runs. It also verifies integer-index sets, call/node/time
accounting, command-line budgets, incumbent traces, model/core/binary hashes and
generated correctness records. These are floating-point checks, not exact proofs.

## Reproduction

Build `build-milp-iter5` with CUDA disabled. Use a new output directory:

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_focus.py --build build-milp-iter5 --output reports/my-neighborhood-run --limit 180 --nodes 250000 --reference-limit 30 --experiment neighborhood
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_local_milp.py reports/my-neighborhood-run --binary build-milp-iter5/solver_cli.exe --output reports/my-neighborhood-audit
```

The runner checks CTest and240 generated checks across guided, diversified and
legacy modes, then six sequential paired hard runs. Independent reference solves
follow the timed runs. Do not run competing numerical benchmarks concurrently.
No Kaggle notebook or GPU is needed. Default promotion requires evidence beyond
one exploratory timing pass.

Use `--experiment pacing` for a fresh guided-versus-paced comparison. Optional
`--strategies paced` runs only the candidate hard cases while still running
all240 generated checks; label that result as a single-strategy screen, not a
new paired/repeated timing comparison. Older archived evidence retains its own
source/binary/audit identity and must not be attributed to the newer build.
