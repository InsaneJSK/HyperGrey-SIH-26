# Guarded reduction of derived upper-bound rows

Iteration10 adds optional `--reduced-bound-lp` and `--late-reduced-bound-lp`.
They apply only to main-tree MILP LP relaxations, including root cut re-solves.
Heuristic, pump, fixing and strong-branch probe paths keep their established
formulations. Standalone LP/QP and GPU numerical algorithms are unchanged.

## Mathematical contract

Propagation may introduce finite continuous upper bounds where the input model
had none. The smaller LP restores those selected upper bounds to positive
infinity, while retaining all rows, lower bounds, original finite upper bounds
and every integer branch bound. It is a relaxation of the full node: the node's
feasible set is contained in the smaller LP's feasible set.

For minimization, a valid dual lower bound for this relaxation is also a lower
bound for the full node. If the relaxed optimum additionally satisfies EVERY
full-node row/bound, primal and dual bounds meet for the full node under the
existing numerical tolerance. The missing bound multipliers can be set to zero.
Maximization uses the existing minimization-sense normalization.

We do not assert arbitrary tightened bounds are redundant. A tighter bound may
be essential. Therefore an optimal relaxed solution must pass full-node
absolute violation <=1e-7 and scaled violation <=10 times the LP tolerance,
in addition to the sparse LP's numerical primal/dual/gap checks. Every final
integer incumbent still passes the original MILP acceptance gate.

An infeasible relaxation implies the full node is infeasible. The reverse is
not used. An unbounded relaxation does NOT imply an unbounded full node. Failed
full-node checks, unbounded relaxed LPs and other unsuccessful reduced attempts
retry the full LP cold within the remaining wall-clock allowance. If time is
exhausted, no relaxed ray, primal or optimality flag is published as a full-node
certificate. The solver's existing incomplete-node handling remains in force.

The original domain is the eligibility source: integer columns and originally
finite upper bounds are never removed. In the current MILP implementation,
additional continuous bounds arise from propagation; explicit integer fixings
remain untouched. The full-node gate and retry also guard against an arbitrary
nonredundant tightening passed to the helper. This is numerical optimization,
not an exact rational proof system or a general presolve equivalence certificate.

## Activation, warm bases and limits

Immediate mode is available for root screens. Delayed mode implies delayed
compact equations and lifted covers, activating once at the existing half-time
full-domain restart. It keeps the established early incumbent search. Global
time, node counts, spent heuristic budgets, incumbent and valid global bound
are retained. `--no-cuts` prevents delayed activation. If both immediate and
delayed reduction flags are requested, delayed activation takes precedence.

`LpBasis::reduced_upper_bounds` prevents main-helper reuse across full/reduced
representations. The sparse LP's existing compact-mode/dimension/basis checks
still apply. A full retry starts cold. Numerical operations and allocation use
cooperative deadlines; measured overruns must not be hidden. Iteration limits
are per formulation attempt, and recorded attempt iteration counts are added.

JSON reports requested enable/late-enable flags, `reduced_bound_lp_calls`,
`reduced_bound_lp_accepted`, `reduced_bound_lp_fallbacks`,
`reduced_upper_candidates` and `root_reduced_upper_bounds`. The candidate count
sums considered bounds over calls, not distinct model variables. An accepted
infeasible relaxation also counts as accepted. Root counts describe the last
root relaxation result; fallbacks report zero removed root bounds. These are
not peak-memory measurements. Main-helper calls do not count direct recovery,
pump, fixing or strong-branch subcalls as additional attempts.

## Test gates and reproducibility

The eighth CTest group covers full-node validation, finite original and integer
domains, false relaxed unboundedness, genuine full-node rays, infeasibility,
warm-mode crossing, zero time, 200 generated MILP comparisons and delayed
min/max activation. An additional Python check compares 80 mixed models with
HiGHS; these models actually exercise originally unbounded continuous columns.
The older 240-case profile gate is retained as regression evidence, not relabeled
as 240 distinct industrial models or comprehensive new-path coverage.

```powershell
cmake -S . -B build-milp-iter10 -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-milp-iter10 -j 4
ctest --test-dir build-milp-iter10 --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_reduced_bound_reference.py --binary build-milp-iter10/solver_cli.exe --output reports/my-new-reduced-reference
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_reduced_bound_lp.py --output reports/my-new-reduced-screen --root-only --nodes 1 --limit 60 --models binkar10_1 p0033
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_reduced_bound_lp.py --output reports/my-new-reduced-pair --limit 180 --models p0033 binkar10_1 blend2 --generated
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_reduced_bound_run.py reports/my-new-reduced-pair --binary build-milp-iter10/solver_cli.exe --output reports/my-new-reduced-audit
```

Use fresh output directories; old evidence is never overwritten. Timings are
sequential and alternate profile order. Independent cut/point checks follow
the timed runs. No external incumbent enters the core. The new path remains
optional; public outcomes and limitations belong in the iteration report.
