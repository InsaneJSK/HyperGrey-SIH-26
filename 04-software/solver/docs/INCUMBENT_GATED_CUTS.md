# Incumbent-gated cut continuation (experimental)

Iteration16 adds `--cut-after-incumbent`, which requires
`--adaptive-cut-rounds`. Both remain OFF by default. The existing ungated
adaptive option and five-round default are preserved.

After a successful numerically verified root cut LP, the order is:

1. Adaptive disabled: retain ordinary continuation.
2. Explicit round cap reached: stop at that cap.
3. Protection enabled and no accepted incumbent: retain ordinary continuation.
4. Otherwise apply the unchanged [iteration15 marginal-gain rule](ADAPTIVE_CUT_ROUNDS.md).

The protection controls allocation only. It neither creates an incumbent nor
changes LP recovery, cut validity, numerical tolerances, node coverage, global
bounds or restart budgets. The ordinary time reserve, cut exhaustion and failed
optional-LP rollback still apply. It is not a promise of finding a first point.
An incumbent comes through the existing original-model validation routine;
neither a reference answer nor a fractional root relaxation supplies it.

At the first root there is usually no incumbent. At the existing full-domain
restart, an incumbent may already be available. A feasible but incomplete
restricted binary-proof search can also supply an initial witness through the
same validation path. Completed restricted proofs return before these cuts.

## Evidence contract

`cut_policy.version` is now 2. `require_incumbent` records the extra option.
Every attempted cut LP records `incumbent_objective` in original objective
sense; null means absent. It is constant during a root's cut loop. The new
`no_incumbent` reason continues under the ordinary limits without evaluating
the marginal-gain rule. Rollback and verified-infeasible reasons still precede
allocation decisions. `stops` counts decisions, not guaranteed LP calls saved.

Independent replay remains backward-compatible with version 1. It checks
context consistency, option combinations, arithmetic, order and phase counts.
A separate original-MPS point check verifies each saved source incumbent once
per cut root, using the retained restart vector or partial binary witness.
The independent reader is HiGHS; the core never calls it. Zero reference solve
time is used for this validation-only work, without using an optimum.

The existing restart-vector capture cap is 10000 columns. If a required source
vector is unavailable, the audit explicitly fails to verify it rather than
silently counting it as checked. This is an evidence-storage limit, not a
restriction on the engine's accepted incumbent or solve domain.

The tests include analytic MIN/MAX models where ungated stopping loses the
first point and protection retains it, plus cases where a later checked
incumbent enables stopping. General certificates remain numerical. Protecting
the first search does not guarantee a better final gap; fewer later cuts may
still weaken proof progress. See [the fixed plan](../reports/milp-iteration-16/PLAN.md)
and [results](../reports/milp-iteration-16/REPORT.md). CPU work stays local.
