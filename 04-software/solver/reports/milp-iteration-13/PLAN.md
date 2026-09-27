# Iteration13 — separate search ranking from proof bounds (predeclared)

Keep iteration12 archived and use a separate build-milp-iter13. CPU only.
No benchmark names, reference objectives or external incumbents in the solver.
All new settings remain opt-in unless broader evidence justifies promotion.

Candidate: retain a monotone, unrounded validated LP search priority while
keeping lattice-strengthened bounds for pruning. Maintain an independent
minimum proof-bound index over queued nodes; combine it with every deferred
node for gap checks, restart inheritance and final reporting. Preserve the
legacy priority policy when the new option is disabled. Reset must retain
the selected comparator and clear both indexes together.

Safety gates: randomized dual-index queue operations against a linear scan;
adversarial priority-top versus proof-minimum cases; exhaustive min/max MILPs;
node/time/LP limits, late restart, original witnesses, failed/repaired nodes.
Optional event traces permit an independent replay of priority selection and
queued/deferred minimum accounting. These do not certify raw LP dual bounds.

Predeclared experiments, only after correctness gates pass:

1. Node-budget screen: gt2, lseu, mod008, misc03; control, iteration12 lattice
   ordering, new raw-LP ordering. Two runs each; 2048 nodes, no heuristics or
   cuts, gap0, time safety cap120s. Record semantic trace repeatability; a
   time-capped/numerical outcome is not a completed deterministic node comparison.
2. Keep all17 wave1 models in a fresh 30s pair: lattice ordering versus new
   raw-LP ordering, using the same incumbent/recovery/late-cut profile as12.
3. Repeat mod008 and gt2 three times per profile at30s: control, lattice,
   raw-LP ordering. Rotate order. Retain adverse outcomes and censored times.
4. If the candidate passes those correctness checks, predeclare a small
   untouched modern-MIPLIB holdout selection before any outcomes, with a
   bounded local resource envelope. Keep failures; do not replace hard cases.

Run own timings sequentially before reference work within each experiment.
HiGHS is a separate read/check/reference worker, never part of the solver.
Freeze source/binary/checker/model/command identities and all outcomes. Do not
claim universal proof, full MIPLIB coverage, or a general speedup from a subset.
