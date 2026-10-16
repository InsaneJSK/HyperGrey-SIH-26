# Iteration18 — measured and selective numerical repair

16 September 2026. Preserve frozen17. CPU-only; no Kaggle handoff.

Stage A adds optional refinement-work telemetry only. Preserve arithmetic,
tolerances, pivot/fill/time budgets, cuts, restart policy and recovery allocation.
Retain this instrumented binary/source separately before Stage B edits.
Use fixed-node, no-heuristics and counter-restart checks on p0201, lseu,
enigma, mas74 and eil33-2 to distinguish elapsed cost from search-path changes.
Check frozen17 versus telemetry-off versus telemetry-on semantic identity.

Stage B will be chosen after Stage A evidence. Test a general selective schedule,
not model-name rules or known answers. Preserve cold and original warm repair,
transformed equivalents, final certificates, and all regression gates. The
screen predeclares p0201/eil33-2/mas74, two alternating pairs, 30s each. Compare
the unchanged control to the selected candidate. Record every failure.

Run the full 24-case development wave if the screen and correctness gates allow
it. Add predeclared untouched public cases before any default-promotion claim.
Changing sampling or stopping early must be recorded, not silently substituted.
All existing 24 cases are development data. No universal MILP or ranking claim.

Stage A completed: 16 CTest groups, 11 new Python checker units, and six
three-way fixed-node parity cases pass. The separately retained profile binary
and source show unchanged arithmetic. P0201's counter-restart diagnostic scans
5,776 RHSs / 5.29 million entries with zero corrections. Eil33-2 scans 1,004 RHSs
with 27 corrections. These short diagnostic timings are not robust speedups.

Stage B choice: `--refine-basis --refine-at-checks`. Check at numerical rejection,
warm-basis rejection, optimality or unboundedness decisions, then re-evaluate
that same basis once. Keep the two-correction-per-RHS cap, existing final proof
checks and all other policies/budgets. No residual scan on every ordinary pivot.
