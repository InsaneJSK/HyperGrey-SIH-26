# Next experiment — useful fixings, not merely a better starting point

Full-wave priorities: lotsize, eil33-2 and danoint still have no solution in
either profile. The guided profile returns 23 checked points but only nine
completions; one other model is independently cross-checked infeasible.
Misc07/rout gains are not repeated reliability guarantees, and pk1 worsens.
Keep guidance off by default and treat gt2's selected repeat separately.

Preserve frozen19/20 and the repeated blend2 repair regression. Keep numerical
candidate repair and pump guidance as separate options. Do not inject reference
solutions, identify models by name inside the algorithm, or spend hidden extra
time to obtain a desired result.

The lotsize screen exposes a specific limitation: a closer fractional seed
still leads to hundreds of fractional variables after a full 64-step dive.
The existing original-objective LP can move away from the seed. Before another
feature, compare fractional count, variable refractionality, fixed-domain
progress, LP work and time exhaustion on retained successful/failed paths.

The retained trace comparison now favors testing a distance-preserving
heuristic LP objective as the next single mechanism: danoint's 0.03501 seed
jumps to distance 5.6678 with 51 fractional variables after its first
original-objective dive LP. Lotsize/eil33-2/blend2/rout show analogous first-step
drift. Keep any projection auxiliary columns, RHS, objective and compatible
basis separate from the original tree LP. Do not copy a distance objective's
bound into the global frontier. Preserve the root-only mechanism and
independent seed/final-point checks. This is a hypothesis, not an implemented
or proven fix. Do not simultaneously add batch fixing, increase depth/time
limits or alter restart/cut policy in that experiment.

A low L1 distance or an infeasible rounded fixing does not establish that
nearby integer choices can be completed.
Keep every such heuristic objective/basis separate from global proof bounds.

Require seed/fixing original-row/bound checks, final integrality checks, shared
resource accounting, MAX/MIN/general-integer cases and no-false-proof gates.
Then run a predeclared repeated target/regression screen and the 27-model wave.
Keep failures, objective/gap regressions and variable clock-driven outcomes.
Add new untouched cases only after declaring the protocol; these 27 are all
development data. Closing large incumbent gaps is a separate bound/search task.

The ten-iteration planning budget is not a promise of 27/27 optimality proofs.
Review measured progress at the agreed three-iteration checkpoint, rather than
assuming feature count equals progress. Real refinery/domain validation,
resource containment and final reproducible delivery still remain submission
requirements. CPU work stays local; GPU-only testing goes to Kaggle separately.
