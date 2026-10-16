# Next bounded hypothesis: separate retargeting from bound tightening

The repeated iteration23 screen does not recover misc07 or lotsize. Offering a
structurally compatible basis is insufficient: lotsize's first private solve
reports one compatible offer, zero primal/dual starts and one neither-feasible
rejection. Its best checked fractional distance is about 0.18936, but no
verified private point is returned within the existing slice. Keep the raw
replay and any diagnostic numerical failures visible, not just final points.

Changing both the rounded-target objective and a variable bound at once can
destroy both primal and dual feasibility. A plausible next mechanism is:

1. Retain the exact parent private model/bounds with the selected seed basis;
   do not infer the parent domain from the original MPS or a tightened child.
2. Under the SAME shared dive time budget, test a compatible private LP that
   changes the distance target/objective before any branch-bound tightening.
   The selected pump basis may still be primal feasible on that parent domain.
3. If that solve verifies, then tighten a branch bound with the distance
   objective fixed. The updated basis may now admit a cheap dual restart.
   This is a hypothesis to measure, not an assumed speedup or feasibility gain.
4. Incompatible auxiliary layouts, unsupported domains, numerical failures and
   exhausted budgets retain a safe fallback. Do not grant another two seconds
   per stage. No private proof/bound/basis may enter the global tree.
5. Compare actual saved LPs and independently check original-model candidates.
   Recheck MIN/MAX, free/negative/general-integer bounds, empty domains,
   differing auxiliaries, failed-primary/alternate ownership, zero budgets,
   disabled-option parity and the generated regression gate.

Misc07's first offer CAN restart: the retained replay takes nine pivots versus
784 cold, with independently checked answers. Yet subsequent private work still
does not find an integer point. Eil33-2 similarly takes 44 instead of 317 pivots,
while lotsize takes 2670 in all three replay modes. The longer diagnostic LP
budget is not the measured MILP budget. Do not assume lotsize staging will help
misc07: LP work savings and a useful integer-search trajectory are different.

Protect all prior gains (danoint/rout/eil33-2/blend2/p0201), mas74's known older
profile quality advantage, and mod008 completion. Iteration23's full-wave
candidate loses mod008 completion despite matching its incumbent objective;
do not silently label that a pass because a feasible vector exists. Mod008
retains seed bases but makes zero private handoff LP calls, so this is an
observed wall-clock completion loss, not established LP-mechanism causation.
Timing differences on inactive LP paths, such as pk1/mod008, are not mechanism
wins or demonstrated mechanism-caused losses.

Predeclare the next paired protocol before timing it. Keep candidate features
off by default until repeated evidence justifies promotion. Do not union best
answers across profiles and call that one solve. Five of the earlier ten
planning slots remain after iteration23; that is not a guarantee of 27/27.
Even complete handling of these development models would not establish
universal public-MILP support or competition rank. CPU tests remain local;
GPU, domain validation and submission/demo packaging remain separate work.
