# Iteration27: retain tree work in the short-budget completion search

Declared before iteration27 measurements. Choose the retained profile after
iterations25–26. Test ONE scheduling mechanism: defer the optional full-domain
restart until the node cap, using the existing generic `--restart-nodes 250000`
with the same 250000-node limit. This leaves the original tree and its valid
frontier bounds live throughout the short run. No new cut, bound formula,
acceptance tolerance, incumbent or heuristic budget is introduced.

Evidence for the hypothesis: in frozen24's staged 30-second wave,
`binkar10_1` spends 10.201 seconds in cut LPs and 2.696 in root LPs and performs
one full-domain restart; `mas74` restarts despite adding zero cuts. Both have
quality concerns in objective.md. Root-only cut strengthening and restart
benefits can still be useful elsewhere; this experiment must measure the
trade-off rather than presume all restart work is waste. The current loop
checks the node cap before the restart trigger, so this declared threshold
suppresses optional restart within the measured budget.

Control: retained profile with current half-time restart policy. Candidate:
same executable/settings plus only the node-only restart trigger above.
30 seconds/model/profile, 250000 nodes, 1e-6 gap, unchanged accuracy and serial
alternating-order solves. Independent five-second references follow own runs;
they validate answers, not a matched speed contest.

First economical screen: binkar10_1, mas74, p0201, mod008; two repeats/profile.
Keep every result. Require existing completion on p0201/mod008 and a repeated
material improvement in objective/bound/gap on at least one quality target,
without a counterpart material regression. If this screen fails, reject the
policy and do not launch a large timing wave. If it passes, predeclare the
broader protected comparison including the two exact-proof cases and all27,
with unchanged binary/profile settings. No best-of-runs union.

Before comparisons: existing CTest/generated/exhaustive correctness gate on
the exact binary, frontier accounting checks with restart both enabled and
deferred, and independent original-model incumbent checks. Suppressing a
restart must not drop queued/deferred nodes or fabricate a stronger bound.

Report final objective, bound, gap, status, first-feasible time, node/pivot/phase
work for every measured solve. No finite speedup ratio from time limits.
An unchanged default or rejected release promotion is a valid outcome.
