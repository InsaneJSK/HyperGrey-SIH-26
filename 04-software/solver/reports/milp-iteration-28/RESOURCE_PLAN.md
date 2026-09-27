# Bounded Windows resource/status checks

Run after iteration27 comparisons and before final model timings, on the
unchanged CLI binary, so the wrapper is checked before collecting results. The core has
cooperative internal limits. Test a separate Windows process wrapper for an
external deadline, cancellation, and sampled process-commit threshold. Record
peak working set and commit. The memory threshold is not an OS allocation cap;
sampling can overshoot. Core executables do not spawn children; arbitrary
process-tree containment is outside this wrapper's claim.

Retain stdout/stderr even for forced termination and mark forced stops before
considering any native JSON. Normal CLI exit 1 may mean a valid limit or
infeasibility status. A nonzero exit paired with an optimal claim must never
be published as success. Check cleanup and no surviving process handle.

Cases: ordinary checked solve; native zero time/node/LP-iteration; infeasible
and unbounded; malformed/unsupported input; large bounded synthetic box-QP
for external timeout, cancellation and memory pressure; an intentionally
inconsistent synthetic process-exit/JSON pair for wrapper error classification.
Synthetic pressure and fault injection are separate from public performance.
The existing exact-binary, MPS/domain, MIN/MAX, scaling, frontier and numerical
regressions remain part of the same-binary full gate. An existing numerical-error
fixture is exercised where reproducible; absence of a natural error is not
fabricated as a measured solver defect.
