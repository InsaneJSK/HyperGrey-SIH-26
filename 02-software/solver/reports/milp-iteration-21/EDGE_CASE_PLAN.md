# Additional correctness check, separate from the timing experiment

During the fixed-binary wave, source review identified a possible nondefault
option edge case: `--no-presolve` can leave an integer interval containing no
integer. A pump seed might then reach the private distance builder, whose
domain precondition rejects that interval with an exception. Mathematically,
the MILP should be reported infeasible by the existing tree instead.

Do not alter source or compete with the running measured solves. After the
wave finishes, reproduce with retained `empty_integer_domain.mps`, guidance
on/off and distance on/off, no cuts and no presolve. Preserve actual results.
If confirmed, add a narrowly guarded presolve-off heuristic eligibility check;
do not export a new proof or change presolve-on search, tolerances or budgets.
Test both objective senses and preserve the default and no-heuristics paths.

This is correctness repair, not retuning on public outcomes. If a repair is
needed, keep the original benchmark binary and per-run source snapshots intact,
build the repaired artifact in a separate directory, rerun the full correctness
gate and fixed-node parity, and run MIN/MAX private-dive integration on it.
Bind the final artifact and the measured binary separately in the final archive.
Do not claim that the exact repaired binary ran the earlier 86 timed comparisons.
