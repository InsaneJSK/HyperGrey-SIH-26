# Next: stabilize feasible search, without hiding the remaining gaps

Keep the new stage off by default. Its checked misc07 gain is useful, but the
danoint screen regression and unresolved lotsize prevent a blanket promotion.
The full wave and all quality/completion trade-offs are recorded in REPORT.md;
do not combine best results from different profiles into one coverage number.

## First bounded hypothesis: private-dive near-tie stability

In the retained misc07 screen, a zero-pivot parent stage reconstructs an almost
identical fractional point, yet the first dive branch changes from column 218
to column 12. The staged dive then reaches an accepted integer point at step16.
The strict largest-fractionality comparison is sensitive to tiny differences
among equally fractional variables (about 0.25 from an integer here).
TRACE_DIAGNOSIS.json retains the actual
point differences, score ties and branch events; it does not invent new solves.

Test a model-independent, deterministic near-tie rule for PRIVATE dive ranking
as one isolated next experiment. A ranking tolerance is not permission to relax
integrality, feasibility, LP verification or proof tolerances. Do not change
global proof pruning or use instance names/reference targets. Preserve the
original strategy as control. Check translated/negative domains, MIN/MAX,
permutations and small perturbations explicitly, with unsuccessful alternatives
and exhausted budgets retaining valid parent state.

Compare original/staged/tie-stable diagnostic paths before choosing a single
predeclared public comparison. Protect misc07's new points, danoint's earlier
points, blend2 repair, eil33-2/rout, p0201/mod008 completion, and mas74/Binkar
quality. A favorable tie outcome on one reused model is not a general heuristic
improvement. Retain every regression and keep source/settings fixed in timings.

## Separate remaining bottleneck: lotsize's later private work

The parent stage removes the initial neither-feasible handoff bottleneck, but
does not produce an integer solution. The saved root trace gets through several
verified child LPs, takes an expensive infeasible primary branch and an alternate,
then reaches the slice deadline later in the dive. Replacing one cold LP is not
enough. Preserve the exact next expensive private model/basis for diagnosis;
do not reconstruct a tightened child from the original MPS alone.

A later, separately measured hypothesis can reserve part of the SAME slice for
an alternate when a primary requires expensive fallback. No extra total time,
no unverified basis advancement, no private infeasibility promoted to global
proof, and no reference answer fed into search. First determine whether the
saved failure is a budget, numerical or genuinely infeasible local branch.

Danoint also needs first-feasible deadline/trajectory diagnosis: a solution in
one time-limited run does not establish reliable coverage. Keep the losses
visible even when a later wave succeeds. Completing proof gaps on already
feasible models remains different work from finding the first point.

## Submission boundary

Six of the earlier ten planning slots are consumed after iteration24; four
remain as planning slots, not a guarantee of 27/27. These 27 are development
cases. Unseen cases, broader scalable/GPU evidence, real refinery validation,
hard resource containment and reproducible demo/delivery still matter. CPU
work stays local. No Kaggle upload is needed until an actual GPU test is due.
