# Guarded candidate after exact replay passed

The four retained diagnostic captures reproduce no-entering-column rejection
after one dual pivot and pass exact binary64 and original-domain checks in
both warm modes. Their nonzero multipliers are integers. This supports a
narrow native candidate, not a tolerance-only general certificate.

Implement bounded integer coefficient arithmetic (operands at most 2^26,
accumulators at most 2^52), strict signs for every true canonical column and
an independent original-domain check. Use outward bounds for RHS/domain
products and sums. Reject uncertain, nonfinite, noninteger, overflowed or
expired checks and retain existing phase one. No general MILP proof use.

Feature: `--private-dual-certificate`, off by default, requires private distance
reoptimization. Only compatible private LP bases can offer a row. No basis or
point from an infeasible local LP may become an incumbent or parent state.

Gate before any timed screen: focused transformed MIN/MAX/domain/equality/
invalid-basis/deadline/fallback tests; adversarial tiny-negative feasible case;
replay all four saved fixtures; existing full correctness gate including
disabled fixed-work parity, generated and retained exhaustive cases.

After those pass, screen the twelve iteration25 models at 30 seconds, 250000
nodes, 1e-6 gap, two observations per profile, rotating serial profile order.
Control = frozen28 staged flags on the new binary. Candidate = control plus
the single new flag. Reference runs follow measured own solves. No builds or
other solver runs overlap timings. Keep every failure and independently check
incumbents and bounds. A retained fixture speed/work gain is only diagnostic.

Promotion requires repeated useful-point/completion or quality gains without
lost protected coverage/completions or unexplained quality/bound regressions.
If it fails, keep the option experimental/off and stop the broad timing batch.
If it passes, predeclare the full development recheck before any promotion.

Scope limitation: arbitrary floating coefficient certificates are intentionally
unsupported by this shortcut. The normal solver still handles those models.
