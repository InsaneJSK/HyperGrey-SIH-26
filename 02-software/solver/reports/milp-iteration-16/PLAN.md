# Iteration16 — protect first-feasible search; diagnose mas74 separately

CPU only. Keep iteration15 and older archives immutable. No named-model core
rules, imported incumbents, tolerance changes or general exact-proof claims.

## Fixed candidate before implementation and timing

Add opt-in `--cut-after-incumbent`, valid only with `--adaptive-cut-rounds`.
Keep iteration15's thresholds and explicit round caps. On a successful cut LP,
retain the normal cut schedule if no original-model-accepted incumbent exists.
Record `no_incumbent` instead of evaluating the marginal-gain policy. Once an
incumbent exists, use the unchanged selective rule. Record its objective with
every attempted cut round; independently check the retained source vector
(restart incumbent or initial partial binary-proof witness). No new heuristic,
restart, LP recovery or proof-bound rule belongs to this candidate.

Default remains five rounds, adaptive OFF, incumbent protection OFF. Preserve
the ungated adaptive mode and all its failed iteration15 outputs.

## Bounded evidence

1. New no-incumbent/known-incumbent min/max, round-cap, invalid CLI and partial/
   zero-time tests. Independent replay and mutation tests. Default/legacy
   semantic parity against frozen15 on fixed-node cases. Analytic integration
   must exercise actual stop and protected no-stop branches.
2. Two paired 30s runs per profile on Binkar, p0282 and mod008: five-round
   baseline versus unchanged-threshold incumbent-gated policy. Rotate order.
3. One paired 30s wave on all 24 retained public development models. No fresh
   holdouts are claimed this iteration. No retuning from the results; any
   promotion requires later genuinely fresh data and broader repeated evidence.
4. Final generated/exhaustive regression gate and independent saved-result
   audit. Snapshot code, tests, checker identities, inputs, commands and binary.
   Keep no-points, failures, open gaps and original reference errors.

Own limits: 30s, 250000 nodes, relative gap 1e-6, external watchdog45s.
Reference solves: configured5s, external watchdog150s. Validate cut-incumbent
vectors separately with zero reference solve time; this is a point check, not
an optimization comparison. Same raw/lattice/late-cut profile as iteration15.
Sequential own runs before references; no overlapping builds or CPU-heavy
checks during performance runs. Shared-desktop load is not controlled.

## Separate mas74 diagnosis

The frozen15 saved run shows recovery time6.00028s (allowance6s), a half-time
restart at15.003s, three subsequent nodes, and two unresolved nodes. Reproduce
with frozen15 and full frontier capture. Compare the same frozen build with
late LP transforms disabled and with the clock restart disabled. These are
diagnostic ablations, not a mixed candidate or a claimed speed benchmark.
Replay the first captured relaxation cold using sparse/dense/reference methods
with the ordinary iteration allowance, not the failure's five spent iterations
as a newly imposed limit. Retain the warm basis but do not pretend cold replay
duplicates its pivot trajectory. Diagnose before any recovery change.
