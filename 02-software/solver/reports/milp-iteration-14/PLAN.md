# Iteration14 — measured work allocation, CPU only

Preserve iteration13 and its archives. First add optional exclusive phase-time
and reported-LP-iteration attribution, without changing search settings.
Diagnose binkar10_1, blend2, misc07, lotsize and eil33-2 at30s, sequential own
solves before reference work. Do not infer all elapsed time from node counts.
The four previous holdouts are now development cases, not untouched again.

After diagnostics, predeclare ONE bounded work-allocation candidate. Keep
pruning, original-model feasibility and gap tolerances unchanged. Exhausted
optional searches must export no proof; failed optional cuts must roll back.
Expose deterministic restart/node tests independently of the wall-clock trigger.
Test zero/tiny work caps, interrupted LPs, min/max, mixed/negative domains,
restarts, exact sentinels, and unchanged defaults. Run a same-budget target
screen, all21 retained cases, then repeat any apparent target improvement three
times. Keep adverse and no-incumbent outcomes; do not tune after the final sweep.
No GPU, new notebooks, imported incumbents or benchmark-name rules.

Phase telemetry is optional and exclusive wall time, not CPU time or exact FLOP
accounting. It excludes parsing, initial argument/model validation and output
serialization. LP counts describe calls visible to MILP, including reported
iterations from wrappers, not every internal factorization. Broad exact proof,
total memory limits, production validation and all-library coverage remain open.
