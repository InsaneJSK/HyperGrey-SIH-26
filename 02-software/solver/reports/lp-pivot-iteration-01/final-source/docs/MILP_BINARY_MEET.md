# Small-binary meet-in-the-middle incumbent search

Optional CLI flag: `--binary-meet`. This is CPU-only, uses the existing C++ core,
and is disabled by `--no-heuristics`. It does not require Kaggle, Python in the
solver process, or an external optimization library.
For the separate, stricter exact-integer algorithm introduced afterward, see
[binary proof mode](MILP_BINARY_PROOF.md). The heuristic described here remains
non-certifying; its completed flag has not been reinterpreted as a proof.

## Eligible structure

The original model must have1–8 rows, at most128 columns and1–36 movable binary
variables. Fixed integer variables must be exactly integral. Other movable
integers are unsupported. A movable continuous variable is supported only when
it appears in one equality and is the only movable continuous variable in that
row. Otherwise the detector declines and the general MILP solver continues.
Input coefficients and transformed values also have finite/magnitude guards.

For an equality `a*x + c*y = b`, with its continuous `y` unique to that row,
substitute `y = (b - a*x)/c`. Its original lower/upper bounds become a ranged row
on the binary variables; its linear cost is substituted into the binary cost
and objective offset. Negative coefficients, finite or infinite continuous
bounds, fixed-variable contributions, offsets and either objective sense are
handled. No model name, known optimum or reference solution is consulted.

## Search and resource limits

Split the binaries into two halves. Enumerate the first half into coefficient
sum / cost / assignment records and build a leaf-blocked spatial range tree.
Enumerate the second half using incremental Gray-code updates; query compatible
first-half ranges using row-activity boxes and subtree objective estimates.
The split-enumeration principle is due to
[Horowitz and Sahni](https://www.cise.ufl.edu/~sahni/papers/computingPartitions.pdf).
The multi-row range search and separable-continuous reconstruction here are
independently implemented, not copied from a reference solver.

At most2^18 first-half records and2^18 second-half assignments are permitted.
The point table is about20 MiB at that cap, plus a bounded tree and small model
arrays; this is an estimate of those structures, not a measured process peak.
One optional root attempt receives at most min(5 seconds,5% of the original
global limit,10% of remaining time). This is a separate heuristic allowance
within the unchanged global time limit, not part of the neighborhood allowance.
Timer checks cover preparation, enumeration, tree construction and queries;
individual allocations/partition operations may slightly overrun the slice.

## Proof and numerical boundary

Every prospective point is reconstructed in original variable space. It must
pass the unchanged original absolute feasibility check <=1e-7. The existing
MILP acceptance gate checks finite values and integrality again, rounds integers
only within its tolerance, and recomputes the original objective.

The floating-point range search is an INCUMBENT HEURISTIC. Its pruning estimates,
completed search, lack of a point or numerical rejection NEVER become a global
bound, optimality status or infeasibility certificate. Only the best checked
point is exported. The global LP/branch-and-bound proof machinery is unchanged.
Thus `binary_meet_completed=true` alone does not mean the MILP is solved.

The CLI records eligibility, attempted/completed/improved flags, allowed/used
time, left/right state counts, query-node count and the accepted point. This
captures the final improved vector from this root attempt, not every internal
range-search update. Independent audits re-evaluate it using the original MPS.

## Tests and local reproduction

`tests/test_mitm.cpp` checks180 small models by separate exhaustive enumeration:
signed costs/rows, ranged constraints, positive/negative continuous coefficients,
fixed variables, offsets and minimization/maximization. Additional tests cover
unsupported structures, resource/domain caps, infeasibility without a returned
point, zero time/nodes, no-heuristics and a one-node global-bound regression.
The generated MILP gate separately checks40 binary and40 mixed models under
three option profiles (240 checks on80 models).

Preserve archived builds. For the current snapshot, use a fresh build directory:

```powershell
cmake -S . -B build-current-local -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-current-local -j 4
ctest --test-dir build-current-local --output-on-failure
./build-current-local/solver_cli.exe datasets/miplib2017/markshare_4_0.mps --milp --json --lp-recovery --improve-incumbent --repair-candidates --binary-meet --time-limit 180 --node-limit 250000
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_focus.py --build build-current-local --output reports/my-meet-comparison --limit 180 --nodes 250000 --reference-limit 30 --experiment binary_meet --models markshare_4_0
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_local_milp.py reports/my-meet-comparison --binary build-current-local/solver_cli.exe --output reports/my-meet-audit
```

The focused public-model experiment is a small-structure result, not evidence
of a general MILP speedup or million-variable coverage. Results, limitations and
the preserved unsuccessful reserved-search experiment are in
`reports/milp-iteration-06/REPORT.md`. The feature remains opt-in.
