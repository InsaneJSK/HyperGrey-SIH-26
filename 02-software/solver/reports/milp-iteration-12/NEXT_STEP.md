# Next local robustness cycle

Keep objective-lattice strengthening opt-in. Its structural proof and numerical
rounding checks do not guarantee better short-budget search. Preserve all 17
public cases, both profiles, both target models and every unfinished outcome.

## First: isolate the proof-bound/search-order interaction

The current Node.bound controls BOTH the priority queue order and certified
pruning/global-gap accounting. Rounding valid bounds creates ties and can
change depth/ID tie-breaking, branching trajectories and available heuristic
time. The 30s gt2 pair has a worse candidate incumbent despite a slightly
stronger final bound. Search-order coupling is a plausible mechanism, not a
fully isolated diagnosis of that regression. Clock-triggered restarts and
heuristic budgets also make wall-clock variation significant, even on models
whose objective lattice is unsupported.

Predeclare a deterministic node-budget experiment that separates search ranking
from proof strength. If introducing a raw LP priority, maintain an independent
minimum of the VALID proof bounds across ALL queued and deferred nodes. Never
use the top of a differently ordered queue as a global lower bound. Include
late full-domain restarts, interrupted LPs and candidate repair in coverage tests.
Do not name-dispatch settings for mod008, misc03 or any benchmark model.

Compare the control, current lattice policy and a candidate ordering policy
with identical node budgets first, then repeated equal wall-clock budgets.
Use gt2 and lseu as regression sentinels as well as mod008/misc03 targets. Keep
original-model point checks, cut checks and the restricted exact sentinels.

## Then: broader proof/search strength and untouched holdouts

misc03 still needs substantially more than step-5 rounding to close its bound.
Inspect its remaining relaxation gap and queue before choosing a general
mixed-integer cut or branching improvement. Blend2's 30s no-incumbent outcome
requires a different feasibility/LP-recovery diagnosis, not stronger claims
from an old 180s completion. Binkar, p0282, misc07 and pk1 remain on the ledger.

After a fixed candidate passes regressions, predeclare a separate modern-MIPLIB
holdout wave by structure and size BEFORE running it. Save official sources,
hashes, eligibility/rejections, watchdog/memory limits and all outcomes. Do not
replace difficult cases after observing a timeout. Full 240-instance coverage
requires an explicit resource envelope and remains a measured target.

## Submission work remains

An arbitrary-public-MILP exact solver is not established. Continue numerical
certificate hardening, parser/metamorphic stress and resource-limit behavior.
Separately, obtain domain-model/expert validation, repeat applicable final GPU
comparisons, and freeze the demonstration/evidence matrix before 30 September.
Those external inputs are not blockers for the next CPU cycle, which runs
locally and needs no Kaggle notebook or user result ZIP.
