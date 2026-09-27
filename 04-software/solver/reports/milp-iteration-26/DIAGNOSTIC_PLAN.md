# Iteration26 diagnostic declaration (before new solves)

First retain the exact later private LP, not a reconstructed original MPS.
Instrumentation will capture the first private child that is unsuccessful or
uses at least 256 total iterations (including fallback), plus the first later
failed child if distinct.
Store model coefficients/bounds/objective/auxiliaries, tagged input basis,
node/step/branch/alternate, LP return status, pivots, elapsed/available slice.
Caps: two retained fixtures, each at most 200000 nonzeros, 10000 columns and
20000 rows. Capture only on the explicit diagnostic switch.

Choose the retained iteration25 profile after its gate/paired screen. Do not
infer that stable ranking or staging caused a clock difference where unused.
Initially run root-only diagnostics on lotsize and danoint at 30 seconds,
twice each. Replay exact retained private LPs with cold, dual-only and adaptive
paths using a separate ten-second diagnostic limit and independent references.
Never import replay points/bounds into a measured MILP solve.

Classify genuine local infeasibility, numerical failure, basis rejection/cold
fallback, step cap and time exhaustion separately. Compare danoint pump/fixing
events before staging as well as the private dive. A failed global solve must
remain failed even if a diagnostic private replay succeeds.

Only if the evidence supports a budget policy, declare it separately before
timing. Candidate: cap each primary private child at half of the currently
remaining shared slice, leaving the rest available for its alternate if needed.
The overall dive deadline remains unchanged; no second slice. Fast warm primary
LPs finish naturally. Failed/interrupted primary must retain the parent basis
and bounds for its alternate. No private infeasibility becomes global proof.

The first measurement would be a small paired lotsize/danoint screen, three
repeats at 30 seconds per model/profile. Broaden to protected cases and all27
only if useful repeated point validity/coverage or reliability gains appear.
Reject an ineffective policy and preserve precise fixtures. A numerical defect
takes precedence over testing the policy. No source changes during a batch.
