# MILP iteration04 — checked blend2 completion and proof-safety fix

Execution-policy update: the user requests local CPU validation and iteration.
The prepared CPU notebook below no longer needs a user run. The180-second
paired comparison is complete locally in `local-180s/`; Kaggle is GPU-only.
**Latest result:** repair reaches blend2 objective7.598985 in114.53 seconds,
matching the independent optimum, with gap_limit status and reported gap1e-7.
All five final incumbents and both captured accepted repairs pass independent
original-model checks. See [the full local validation](LOCAL_VALIDATION.md).

The initial90-second repair experiment below found a strictly checked feasible
blend2 solution where the baseline had no incumbent; that shorter run did not
close its gap. The later180-second comparison above does. A separate correctness issue in closing repaired
nodes was also found, reproduced on the previous binary, and fixed in BOTH new
comparison modes, not hidden behind an experimental flag.

Final CLI SHA-256: `17ba159a72eaf04e34f6754795ac0013c8bc6c0a75b7bca9d1ce46318139a679`.
Build: `build-milp-iter4`. Previous CLI
`ae6d294de68e932ae3c48ea784a34651a040cc530f1e91540eab0ad96e88e19f` is preserved
as `baseline_solver_cli.exe`, with its original build/source ZIP unchanged.
Diagnostic-only build `build-milp-iter4-diagnostic` is also separate; its modified
source is retained in `diagnostic-source/`.

## Diagnosis: a feasible integer assignment was being lost

`capture/` reproduces a rejected blend2 point at node10612. The original rounded
candidate has maximum absolute violation2.000999984e-6, so rejecting it was
correct. The primary scaled sparse exact-integer-fixing LP returns numerical_error
after212 iterations. The same fixing model is feasible and has optimum8.015188:

| Method | Status | Iterations | Objective | Independent absolute violation |
| --- | --- | ---: | ---: | ---: |
| Own scaled sparse, tolerance1e-11 | numerical_error | 212 | None | No candidate |
| Own dense simplex, tolerance1e-11 | optimal | 424 | 8.015188 | 2.27e-13 |
| Own unscaled sparse, tolerance1e-11 | optimal | 808 | 8.015188 | 3.64e-12 |
| Independent HiGHS | Optimal | Not recorded | 8.015188 | Reference solve |

Full original points, integer fixings, primary repair output and independent
diagnostics are in `capture/` and `diagnosis/`. These results justify a bounded
alternative for this repair, not globally disabling scaling. Reference solutions
are never fed into our MILP algorithm.

`--repair-candidates` now tries our existing dense simplex when the primary
sparse fixing repair fails. It retains the same original feasibility/integrality
checks, dense allocation guard, per-call and global time allowances. A valid
point updates only the incumbent. Method details and diagnostic semantics:
`docs/MILP_CANDIDATE_REPAIR.md`.

## Correctness: repaired fixing is not proof for the whole node

The new asymmetric-V regression exposes a real false-optimality edge case in
the previous binary: an almost-integer LP optimum rounds to an assignment with
cost80, but another integer assignment costs0.99999992. The previous code
returned `optimal`, bound80 and zero gap after solving the first fixing.

The new shared logic branches on the remaining tiny integer fraction when its
children strictly tighten the integer domain; otherwise it keeps the node's
checked bound unresolved. It never exports a fixing objective as proof for the
other assignments. Running the exact same model/flags now finds integer2,
objective0.99999992 in three nodes. See `PROOF_REGRESSION.json` and
`proof-counterexample.mps`. This new counterexample limits previous broad
robustness claims; earlier benchmark observations remain individually checked
evidence, not a claim that older binaries are free of false-proof edge cases.

CTest covers the correction without the experimental fallback flag, one-node
proof-bound preservation, maximization, genuinely infeasible almost-integer
assignments, diagnostic capture and zero budgets. All three CTest groups pass.
Generated tests pass240/240 across baseline, repair mode and legacy control.
Shared LP/QP/CUDA numerical source files are unchanged in this iteration.

## Equal90-second final-source blend2 comparison

Both modes use fractionality, LP recovery and incumbent neighbourhood search,
identical ORIGINAL-model acceptance checks, and250,000-node caps. Only the optional
dense fixing fallback differs; both include the shared proof correction.

| Mode | Incumbent | Best bound | Reported gap | Main nodes | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline | None | 7.563968067 | Undefined | 8055 | time_limit |
| Candidate repair | 8.015188 | 7.563968067 | 5.0051% | 8055 | time_limit |

The repair mode finds its incumbent at58.4317 seconds. One dense fallback
succeeds, costing0.3822 seconds; one tiny-fraction node branches safely. The
baseline retains two unresolved nodes, while this repair run has none deferred
at its deadline. The active proof tree is still unfinished. The returned point
passes independent ORIGINAL MPS checks: maximum absolute violation2.2737e-13,
integrality violation0. The reference solves blend2 to7.598985.

No better incumbent is found before90 seconds. Neighbourhood search spends
8.7642 seconds across16 calls/1024 local nodes without improving this first
candidate. The shared lower bound is unchanged, so this is a feasibility gain,
not evidence of faster bound progress or global superiority. No unsafe/error
run is reported in this final-source pair. Raw results are in `blend-90s/`.

## Final-source short checks on all three hard models

`final-smoke/` repeats CTest3/3 and generated240/240, then runs six equal15-second
pairs. Both modes reach markshare objective20.999999976 and binkar6810.690026;
neither reaches a blend2 candidate within this much shorter budget. All four
returned incumbents pass independent original-MPS checks. There are no unsafe/
error runs; every hard run remains time-limited. The zero-second reference
workers in this short gate only parse/check candidates, not establish optima.
This checks retained behaviour at a short limit, not broad non-regression or
repeatable timing equivalence. Selected package evidence is this final-source gate.

## Preserved optional notebook — superseded by local CPU execution

Delivery: `kaggle_delivery/milp_iteration_04`. Two code cells, notebook below1MB,
matching private source ZIP as Input, current Kaggle Python, no second environment,
Internet enabled and no GPU needed. It compares baseline vs candidate-repair mode
on the same three hard MILPs at180 seconds/250,000 nodes each, with240 generated
checks and30-second separate reference runs. Allow roughly20-25 minutes.

The notebook would produce `sih26119_milp_results.zip`, including diagnostics after
errors. It records rejected near-integer points and fixing-LP outcomes, fallback
attempts/successes/time, proof-safe branching counts, incumbent history and final
independent feasibility checks. Actual Kaggle execution of this snapshot has not
been performed and is no longer requested: this algorithm is CPU-only. Old
successful Kaggle runs must not be attributed to this source.

The local results confirm blend2 completion at7.598985 and retained binkar
progress. Next: investigate binkar's remaining gap and plateaued neighbourhood
work locally, with broader and repeated checks before changing defaults.
Completion beyond this one hard instance, industrial validation, nonconvex
problem classes and top-percentile submission rankings are not established.
