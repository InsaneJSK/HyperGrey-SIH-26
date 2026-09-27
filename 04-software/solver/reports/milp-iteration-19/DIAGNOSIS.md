# Chosen change, before candidate timings

Stage A passes 18 CTest groups, including 40 small min/max trace-on/off parity
pairs. Five 30s public diagnostic outputs pass independent checks: blend2,
lotsize and danoint have no point; eil33-2 and rout have checked feasible limits.
This variability is not a candidate gain: the algorithm is still unchanged.

Pump progress exists: blend2 improves integer distance from 1.1896 (six
fractionals) to 0.2271 (one); danoint improves 5.8192 to 0.0350. Nevertheless,
these points need not extend to feasible integer assignments. Pump targets
repeat before perturbation but not afterward in the retained blend2 trace.
Lotsize instead has hundreds of fractional variables and expensive projections.

A more directly reproduced issue changes the chosen implementation priority:
blend2's dive produces a near-integer point that accept() correctly rejects.
The first trace's vector cap loses its vector, so a separately built second
capture prioritizes that rejection within the same 100000-value cap. The
repeated rejection is retained at node185/call3/step28. Independent checks show
raw violation 2.01e-6 and rounded violation 2.129e-6, above 1e-7 acceptance.

Cold integer-fixing replay with frozen18: sparse LP still gives numerical_error,
whereas the project's dense LP solves to 8.788661 in about 0.32s. Its point has
4.55e-13 original-model violation and zero integrality error independently.
The integer choices are feasible; the missing heuristic repair path loses a
useful point. This is a cold fixing replay, not a warm-pivot equivalence claim.

Therefore test optional repair of rejected near-integer dive candidates, not
pump-seed handoff in the same change. Use existing sparse tightening and dense
recovery, bounded by the current dive slice and existing shared repair allowance
min(15s,10% of total time). At most16 unique integer fixings are attempted;
duplicate fixings are not repeatedly charged. Points alone may update the
incumbent. No fixing-LP objective/status can prune or certify the global node.
No tolerances, root/cut/restart rules, or total time allowance are relaxed.

Repeated screen: blend2, p0201, eil33-2, binkar10_1 and mas74, two pairs each,
with bounded feasibility capture enabled in both profiles. Full wave: all27
development cases, one pair each, without the detailed feasibility trace to
avoid its measurement overhead. Both profiles retain selective basis refinement;
only the candidate enables heuristic repair. Keep all outcomes, including
regressions. No new untouched holdout or default-promotion claim this iteration.
