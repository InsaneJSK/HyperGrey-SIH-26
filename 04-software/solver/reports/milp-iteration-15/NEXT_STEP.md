# Next experiment — protect first-feasible search

The predeclared selective policy failed Binkar in the screen, both new
target repeats and the full wave: no feasible point in all four 30s runs,
versus checked points in all four controls. Keep it OFF by
default. Its dual-gain metric does not measure the effect of a changed LP
solution on pump/diving starting points. Do not hide this counterexample or
retune the policy from the fresh holdouts.

## First bounded candidate to investigate

Permit adaptive cut reduction only when an original-model-checked incumbent
already exists. Keep the existing full cut policy before the first feasible
point. In the current architecture this mainly targets the existing full-domain
restart after successful first-feasible search, rather than changing the first
pump's root relaxation. This is a proposal, NOT implemented in iteration15.

Predeclare one candidate with the same round/work thresholds, versus the
five-round control. Record whether an incumbent was present when a cut decision
was made, and retain/check the restart incumbent. Do not obtain it from a
reference solver or a published answer. Cover no-point, known-point, min/max,
restart, zero/tiny limits and failed-LP rollback cases with regression tests.
Test Binkar, p0282 and mod008, then the whole retained development ledger and
genuinely new holdouts. Keep the existing adverse ungated policy as evidence.
Incumbent gating may protect feasibility behavior but does not guarantee a
better final gap: weaker bounds can still hurt proof progress.

## Separate high-value work

- Investigate safe warm-start extension for root LPs after adding cuts. The
  current loop clears the basis and cold-solves each cut LP. Reusing validated
  structure could reduce work while retaining cuts, but row/column transforms,
  invalid bases and changed optimal corners require careful guards and tests.
  Do not combine this with the next gating experiment and obscure attribution.
- Diagnose pump/diving stalls and bounded recovery from their saved starting
  points. More time in a heuristic is not evidence that it made useful progress.
- Broaden negative-outcome, malformed-input, numerical and process-resource
  tests. Reference conflicts/timeouts must remain explicit; numerical terminal
  status agreement is not a general exact certificate.
- Diagnose the newly retained mas74 unresolved-relaxation return at about 15s
  under a 30s configuration, before changing its recovery or proof behavior.
  Both profiles retain valid points, but neither completes. Do not mask that
  status or loosen feasibility tolerances to make the result look solved.
- Keep the reference-array caching improvement separate from engine performance.
  Retain its frozen-reader comparison and original iteration14 timeout evidence.
- Before submission: real domain validation, a reproducible CLI/API demo and
  repeated final GPU-only evidence where applicable remain necessary. No
  all-public-MILP, industrial-readiness or competition-percentile guarantee.

CPU work stays local. No Kaggle notebook or result upload is needed for this
next CPU experiment. All three iteration15 holdouts become development data
after their first run and must not be called untouched again.
