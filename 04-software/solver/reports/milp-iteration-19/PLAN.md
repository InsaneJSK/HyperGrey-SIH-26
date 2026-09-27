# Iteration19 — first-feasible search, before timings

Stage A adds bounded optional pump/dive traces without intentionally changing
the search. Preserve the frozen18 executable and source. Test trace-on/off
semantic parity on small completed min/max cases and hard trace memory caps.
Run the five retained no-point cases at 30s with the same selective18 profile,
then independently validate outputs and diagnose the trace. This is diagnostic
data, not a speedup comparison or untouched holdout experiment.

The code currently discards pump fractional progress before the first dive:
dives use the initial original-objective LP point. Investigate whether pump
progress is real and materially closer to integrality before changing that
handoff. Also distinguish repeated targets, propagation rejection, LP numerical
failures and local/global time exhaustion. Do not presume one cause explains
all five models.

Stage B, only if supported: one opt-in general first-feasible change. Keep
tolerances, cuts, restarts, recovery and 30s total/heuristic time allowances
unchanged. Never export a heuristic LP objective as a proof bound. Gate with
exhaustive/generated models, saved sparse cold/warm repairs, original-model
checks and disabled-mode parity. Repeat targets and p0201/binkar/mas74 sentinels,
then compare all 27 development models. All adverse outcomes remain in scope;
no default promotion on one favourable run. Additional untouched cases are a
later generalization gate, not required to diagnose these known failures.

CPU-only local work. No Kaggle upload, new user input, published solution feed,
model-name rules, relaxed tolerances or claim of universal public-MILP proof.
