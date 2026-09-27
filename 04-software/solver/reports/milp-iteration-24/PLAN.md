# Iteration24: objective-only parent stage before private branch tightening

Predeclared CPU-local, opt-in experiment. Preserve iteration23. No additional
heuristic time, relaxed tolerance, instance-name rule, external point/bound
injection, or private/global proof-state mixing. Keep flag off by default.

At the same event as selection of a checked pump seed, optionally retain its
exact private parent model/bounds as well as the tagged basis. Only stage when
the new private distance model has identical rows, row bounds, variable bounds
and variable layout: a conservative objective-only prefilter. The LP engine
still verifies canonical identity, current feasibility and its result.
Under the existing shared two-second slice, first optimize the new distance
objective on unchanged parent constraints; if verified and absolutely feasible,
advance only the private basis/point, then run the existing bound-tightening dive.
Failure preserves seed state and uses only the remaining original time. No
private objective, dual bound or proof status enters the global tree.

Before measurements: full CTest/Python/generated/retained gate; transformed
MIN/MAX, scaling/compact, free/negative/general integer, invalid/duplicate basis,
auxiliary/domain mismatch, parent snapshot ownership, alternate and resource
guards. Frozen23 flag-off parity and disabled-pump/heuristic parity. Actual
MIN/MAX/domain integrations, including an eligible stage.

Screen models: misc07, lotsize, danoint, eil33-2, rout, blend2, p0201, mas74,
mod008, gt2, pk1. Two repeats/profile. Full wave: all27 reused development models,
one repeat/profile. Control is the iteration23 handoff profile; candidate adds
only --pump-distance-stage. Same executable,30 seconds/model/profile,250000
nodes,1e-6 gap, alternating order. Own runs serial, references after each own
batch;5-second references validate answers, not an equal-budget speed contest.
Capture feasibility and bounded parent/child LPs in screen; no capture in wave.
Do not change source or flags between screen and wave. Retain all regressions.

Replay captured stage and child LPs outside measurements with the existing
10-second diagnostic limit and independent checks. Classify stages separately
from the unchanged private branch counts. A faster LP is not a solved MILP.
Freeze executable/source/raw outputs/checks/report with hashes. No Kaggle work.
