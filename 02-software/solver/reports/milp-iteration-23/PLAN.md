# Iteration23: guarded private pump-to-distance basis handoff

CPU-local experiment. No default promotion, extra heuristic time, relaxed
tolerances, instance-name rules, reference-point injection or global proof
reuse. Keep iteration22 immutable. The public pump seed remains point-only.

Retain a separate tagged basis only when its checked fractional point replaces
the best seed. A selected point without a tagged basis clears the old basis.
Offer it to the first distance LP (and an alternate if the primary fails).
Exact canonical structure and current primal/dual feasibility are checked by
the existing LP reoptimizer. Incompatible/neither-feasible bases fall back.
Successful private LPs advance only private basis state; no private proof or
bound enters the MILP tree. Existing pump/dive time slices stay unchanged.

Before measurements: CTest, Python/checker tests, generated and retained
correctness gate, MIN/MAX and bound/auxiliary/invalid-basis/resource guards,
frozen22 option-off parity and disabled-pump/heuristics parity.

Predeclared screen: misc07, lotsize, danoint, eil33-2, rout, blend2, p0201,
mas74, gt2, pk1, two repeats/profile. Full wave: existing27 development models,
one repeat/profile. Both profiles use pump-primal-reopt and distance diving;
candidate adds only --pump-distance-reopt. Same binary,30 seconds/model/profile,
250000 nodes,1e-6 gap, alternating profile order. Capture feasibility in the
screen, not the wave. Own runs serial;5-second independent reference checks
after each own batch are validation, NOT equal-budget performance comparison.
Do not tune code/flags between screen and wave. Record every regression.

Bounded first seed-offer LP replay is diagnostic only, outside measured runs.
Check replay vectors independently; replay iteration savings alone do not
establish end-to-end MILP benefit. Freeze source, executable, raw outputs and
hash-linked report. Preserve failures rather than overwriting evidence.
