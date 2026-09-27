# Iteration11 — breadth-first MILP robustness

Predeclared 15 September 2026, before new-case solver outcomes. User priority:
general MILP robustness and closing public proof gaps, not just a polished demo.

First wave: existing p0033, enigma, flugpl, stein27, markshare_4_0, blend2,
binkar10_1; new egout, gt2, lseu, mod008, p0201, p0282, misc03, misc07, pk1,
rgn. The ten new originals come from the official historical MIPLIB3 archive;
they are not ten new MIPLIB2017 benchmark instances. This intentionally small
cross-family wave diagnoses correctness before scaling up. No replacement of
failed downloads or unsolved models based on results.

Baseline: preserved iteration10 binary/source. One fixed profile on all models:
LP recovery, guided incumbent improvement/repair, delayed lifted cuts, compact
equations and reduced bounds, plus the bounded eligibility-guarded binary proof.
30s per model, 250000 nodes, 1e-6 gap; watchdog limit 45s. Sequential timings;
independent HiGHS references (5s, one thread, 1e-9 relative gap) run afterwards.
Known answers never enter the solver. Save every output and error immediately.

Classify independently checked exact proof, numerical completion, feasible
limit, no-incumbent limit, unsupported input, numerical failure, validation
failure and incomplete reference evidence separately. A timeout is unfinished
work, not a correctness success or a model to discard. A finite incumbent is
not a proof. Objective matches without a complete bound are not proof either.

Fix reproduced correctness/input/status problems first, add permanent
regressions, then run the same suite under the same budgets. No default tuning
from one model. Preserve baseline and changed-binary identities. If no bug is
found, retain the failure map and investigate the dominant numerical/search
bottleneck, without claiming completion of all public MILPs.

Longer-term coverage target: MIPLIB2017's 240-instance benchmark, then a declared
larger collection, plus adversarial infeasible/unbounded/invalid/numerically
difficult tests and holdouts. Every model stays on the ledger. MIPLIB's
[official status page](https://miplib.zib.de/) includes open instances; arbitrary
MILPs cannot be promised fast universal completion on this laptop. General
floating-point certificates must remain distinct from restricted exact proofs.

CPU work is local. No GPU/Kaggle work or user ZIP is required for this wave.
