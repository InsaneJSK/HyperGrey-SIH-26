# Guarded exact small-binary proof mode

`--binary-proof` enables a separate CPU-only algorithm before the root LP or
floating-point presolve. `--binary-meet` remains the earlier floating-point
incumbent heuristic; completing that heuristic still cannot certify anything.
Neither option is enabled by default. No external optimizer is linked into the
C++ implementation.

## Exact subset and source-data guard

The exact algorithm accepts1–36 movable binary variables,1–32 rows and at
most128 original columns. Movable integers must have precisely [0,1] bounds.
Other variables may be fixed at integral values. A movable continuous variable
must appear in exactly one equality, be that row's only movable continuous
variable, and have coefficient +1 or -1. Thus its reconstructed value is integral
for every binary assignment. General-integer domains, coupled continuous
variables, nonunit continuous coefficients and nonintegral data are unsupported.

Costs, offsets, finite bounds and coefficients must be integers. MPS parsing
also tracks decimal-literal integrality BEFORE double conversion, and limits
literal magnitudes/column accumulations to2^50. A literal such as
1.00000000000000000000000000001 cannot silently round to1 and acquire proof
eligibility. Unsafe/cancelling large source accumulations are declined. Ordinary
floating-point parsing values and existing solver behavior are retained.
Programmatic LinearProblem inputs have no source text; their supplied numerical
values still undergo every integer/range/domain check.

The algorithm's finite additions, multiplications and absolute-sum envelopes are
guarded within2^50, using signed64-bit integers. Separate infinity sentinels are
never mixed into finite objective arithmetic. This is NOT arbitrary-precision
support for arbitrary MPS files, and is not a general exact MILP solver.

## Search and proof boundary

Substitute the independent continuous equality variables to obtain binary
ranged rows, integer costs and an integer offset. Enumerate disjoint halves and
query a spatial range tree for compatible assignments. The method uses the
split-enumeration principle of
[Horowitz and Sahni](https://www.cise.ufl.edu/~sahni/papers/computingPartitions.pdf),
with an independently written checked-integer multi-row implementation.

All pruning comparisons use integers. The search starts WITHOUT any external or
floating-point incumbent. Every selected witness is reconstructed and checked
against the original integer coefficients, bounds, rows and objective; a failed
internal identity check invalidates the proof attempt. The original and reduced
objective must agree exactly, including maximization sense and offsets.

Only completion of all required half-state and tree work permits a proof result:
the best exact witness proves optimality, or absence of any witness proves
infeasibility. Successful results publish the exact point, objective/bound
equality and zero gap. They cannot publish a slightly lower tolerance-feasible
floating-point incumbent. The root wrapper reports one main node and zero LP
iterations; millions of private enumeration/query operations are separately
counted. Do not equate this with one unit of conventional branch-and-bound work.

Unsupported input, time/work exhaustion, allocation failure or failed internal
checking never contributes a proof bound. A previously checked partial witness
may still be used as an incumbent; the ordinary MILP engine continues.

## Budgets and controls

The one root proof attempt receives min(5 seconds,10% of the global time limit,
remaining global time). `--binary-proof-work N` caps counted enumeration,
tree-build and query operations (default50000000). Both halves contain at most
2^18 states. The maximum fixed32-coordinate point/tree structures occupy roughly
90 MiB together, plus model/allocator overhead; this is not a measured RSS peak.
Smaller models allocate proportionately fewer states.

Global zero-time and zero-node limits prevent an attempt. Work limit0 declines
the attempt and falls back. This is a proof algorithm, so `--no-heuristics` does
NOT disable an explicitly requested `--binary-proof`; it still disables the
older binary-meet and neighborhood heuristics. Limits are cooperative: an
allocation, partition or bounded block operation can slightly overrun its slice.

## Independent checks and limitations

`scripts/exact_binary_check.py` rereads the original MPS decimal text with exact
fractions, rejects nonintegral literals, verifies the integer witness, and
independently rules out better solutions using unbounded Python integers.
It uses a different half split/tree implementation. Where a nonnegative integral
objective would need to equal0 to beat1, it instead uses an independent exact
equality hash join to rule out zero; this is a structural condition, not a
model-name/known-answer shortcut. This latter argument applies to markshare.

The checker RECOMPUTES the proof. The CLI metadata is not a compact standalone
proof trace that can be verified without search. C++ tests independently
enumerate600 new small models and retain the earlier180 heuristic cases.
Adversarial tests cover source-literal rounding, domains, signs, offsets,
infeasibility, overflow guards, interrupted work, zero limits and fallback.
The separate Python checker has tampering and false-proof tests.

Public evidence is currently limited to markshare_4_0 and historical p0033,
three paired runs each. P0033's ordinary solver is faster. Unsupported binkar,
broader MILPs and industrial-scale problems still need other algorithms.
See `reports/milp-iteration-07/REPORT.md` for measured results and caveats.

## Reproduction

Use a new build/output directory; preserve archived versions:

```powershell
cmake -S . -B build-current-local -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-current-local -j 4
ctest --test-dir build-current-local --output-on-failure
./build-current-local/solver_cli.exe datasets/miplib2017/markshare_4_0.mps --milp --json --binary-proof --time-limit 30 --node-limit 250000
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_exact_binary_check.py
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_binary_proof.py --build build-current-local --output reports/my-exact-proof-run
```

The validation runner executes240 generated checks,40 independent generated
proof checks, twelve sequential public timings, and then independent point and
proof checks. It preserves source/model/binary hashes and all runs. No Kaggle,
GPU, new dependency installation or user result upload is needed.
