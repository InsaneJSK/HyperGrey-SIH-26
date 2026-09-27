# Iteration20 — pump-guided diving experiment

Completed CPU experiment: full regression gate, 78 main paired runs, four
exploratory gt2 repeats, independent point checks and final re-audits. Results
are mixed: gt2 quality improves repeatedly, but no targeted no-point case is
fixed and pk1 regresses. The new option remains off by default.

The [predeclared plan](PLAN.md) tests one heuristic change: retain a checked
fractional pump point with reduced integer distance and use it to guide the
first existing dive mode. The original LP objective/basis, second dive mode,
proof bounds, feasibility/integrality checks and resource allowances remain.
The option is off by default. Both profiles keep iteration19's candidate repair.
See [algorithm and limits](../../docs/PUMP_GUIDED_DIVING.md).

## Mechanism and correctness

Frozen19 diagnostics show lost fractional pump progress on lotsize, eil33-2
and danoint. The root-only mechanism check is separate from timed comparisons;
small exhaustive instances can finish in the pump and not exercise the actual
handoff. All public final points and retained fractional seed points are checked
independently against the original model. A fractional seed is not a feasible
MILP solution and a fixing-LP result is not a global proof bound.

The full gate passes 20 CTest groups, 152 Python units, 28 MPS-domain cases,
320 generated MILP integrations, 100 retained exhaustive MPS cases, 24
transformed LP checks and four independently checked cold/warm LP points.
The new C++ unit group includes 40 exhaustive MIN/MAX models (80 solves), seed
eligibility/ranking and integer target clipping. It records 39 pump selection
calls but zero guided dives because those small models finish in the pump.
That limitation is explicit; test counts alone do not demonstrate integration.
The retained blend2 dense-polish regression still passes.

Twelve fixed-node runs on p0201/mas74/lseu/enigma retain three-way semantic
parity between frozen19, new guidance-off and new guidance-off with capture.
These and the separately retained no-heuristic frozen16 parity checks are
correctness controls, not performance speedup measurements.
Four additional suppression checks confirm guidance is inert with --no-pump
or --no-heuristics, retaining fixed-node semantic parity with the flag off.
Those post-build checks are saved separately in inactive-guidance.

The root-only public mechanism batch has four independently checked outcomes
on blend2/danoint, with no integer incumbent in any run. Both guided runs
actually use a seed. Blend2 selects distance 0.227147869 from initial 1.189603412,
then takes 64 guided steps. Its retained fractional point has independently
checked original-row/bound violation 5.82e-11. Danoint selects distance
1.575757576 from 5.819184247, taking two guided steps, with original violation
2.84e-14. Only one projection finishes in this danoint run, so the older
diagnostic's better 0.03501 point is not available here. Pump time-slice
variation remains real; no saved reference point is injected to force that
earlier outcome. The mechanism is exercised, but this is not a first-feasible gain.

## Protocol

One final binary; only --pump-guided-diving differs between profiles. The
six-model screen uses two alternating pairs at 30 seconds, 250000 nodes and
requested gap 1e-6. The same 27 development models follow with one pair each.
Screen capture is enabled in both profiles; full-wave capture is off. All own
runs finish before reference work. No competing task builds/reference solves
run during measured own solves. Shared-desktop clock variation remains a limit.

References get five solver seconds with a 150-second external watchdog; this
is not an equal-budget solver contest. Preserve every timeout, failed check,
regression and raw source identity. All 27 cases are development data. No
untouched holdout, GPU MILP evidence or universal proof guarantee is claimed.
Reported gap is max(0, incumbent-bound)/(1+abs(incumbent)) in minimization sense;
no-point runs have no meaningful incumbent gap.

## Results and decision

The targeted screen does not improve first feasibility. The full wave has two
additional points relative to its paired control and an exploratory repeat
confirms a better gt2 objective, but pk1 regresses and all three targeted
no-point cases remain. Keep pump guidance optional and OFF by default. Retain
the iteration19 repair and use the ledger, not feature count, to assess progress.

### Repeated six-model screen

All 24 screen records validate with no failures. All eight returned integer
points pass independent original-model checks. Both profiles have two checked
numerical completions, two feasible limits and eight no-point limits. There is
no first-feasible coverage gain on any of the three target models.

| Model | Control repeats | Guided repeats | Outcome |
| --- | --- | --- | --- |
| lotsize | No point / no point | No point / no point | Still unresolved |
| eil33-2 | No point / no point | No point / no point | Earlier successful runs are not reliably reproduced |
| danoint | No point / no point | No point / no point | Still unresolved |
| blend2 | 8.788661 / 8.788661 | 8.788661 / 8.788661 | Repair retained; all optimality gaps open |
| p0201 | Complete at 7615 / 7615 | Complete at 7615 / 7615 | Completion retained |
| rout | No point / no point | No point / no point | No repeatable feasibility improvement |

Blend2's first points arrive at 4.396/5.021s for control and 4.190/4.569s for
guidance. All four runs require one accepted iteration19 numerical repair.
Guidance is used in both candidate runs but does not eliminate that need.
Reported gaps are 13.9151/13.9500% control versus 13.9018/13.7556% guided.
These small timing/gap differences do not establish broad speed or proof gains.
The older iteration19 times are not directly comparable across desktop loads.

Both guided p0201 runs use guidance and complete at the same optimum as control.
Three runs visit 4196 nodes; control repeat zero crosses a clock-triggered
restart and visits 6626. Do not treat that single trajectory difference as an
isolated algorithmic speed measurement. All completed and failed repeats remain
in the saved record. Screen results SHA-256:
`4cf76e96f7bf85d1f9afc91aca677da55303145b5cb2d952ff3a8cfdee66b10e`.

### Full 27-model development wave

All 54 records have zero validation errors. All 44 final integer points pass
independent original-model row/bound/integrality/objective checks.

| Outcome at the 30-second budget | Control | Guided |
| --- | ---: | ---: |
| Restricted exact-subset completion | 2 | 2 |
| Independently checked numerical completion | 7 | 7 |
| Checked feasible point, optimality still open | 12 | 14 |
| No point at limit | 5 | 3 |
| Cross-checked infeasible after supplemental reference | 1 | 1 |
| Total | 27 | 27 |

This is 21 versus 23 checked solutions, with only nine completions each, not
23 optimality proofs. See the [complete model ledger](MODEL_LEDGER.md).
The target failures remain lotsize/eil33-2/danoint. Guided misc07 and rout have
points where this paired control does not. They had points in earlier versions,
and rout fails in every screen repeat, so this is not reliable universal first
feasibility. Historical iteration19's best wave also had 23 points; do not
present this experiment as increased robust coverage from 23 to a higher count.

Rout's guided first point is 1473.32 at 18.12s, later improved to 1311.03 and
then independently checked 1247.32 at 22.37s, with about 20.01% reported gap.
It has one guided dive with two steps and zero numerical candidate repairs.
That short early dive does not establish direct causality for the later tree
incumbent. Mas76 returns 41519.995740 in both profiles but its guided gap is
slightly worse (5.3304% versus 5.3037%). Mod008 stays at 307 with 0.3247% gap in
both, rather than reproducing its older iteration18 completion.

Both neos859080 five-second references time out. Their original raw categories
remain terminal_reference_pending in the wave/main audit. A separate identical-
model reference solve with a 30-second allowance reports Infeasible after
14.9137 seconds and cross-checks both saved statuses. See the
[supplemental terminal check](terminal-references/SUMMARY.json). No own solver
run is repeated or extended, and no timeout is overwritten. This is numerical
status agreement, not an exact general infeasibility certificate or an
equal-budget performance comparison against the reference solver.

Wave results SHA-256:
`f155309ceb643ad2ba17e465da0aff64a38000ef94e5e20a3794e68c888e226f`.

### Observed diagnostic limitation: lotsize

Both screen pairs end without an incumbent. In the first guided run, the root
seed has integer distance 5.0 with 600 fractional variables. After the existing
64 guided steps it still has 530 fractional variables and distance 13.9519.
The matched control starts at distance 9.7737 with 530 fractional variables and
ends its first 64-step mode at 16.2018, also with 530 fractionals. The recorded
guided seed changes the path but does not produce an integer point. Scalar
trace metrics are not a certificate for every unsaved intermediate vector.
Original-objective reoptimization can move away from the seed: a low initial
integer-distance score by itself does not guarantee a productive fixing path.

The full wave differs sharply: its guided lotsize run processes only two nodes,
with about 22.97s in root LP work, 5.05s in pump projection and 1.63s in diving.
No projection finishes as a usable seed (zero guidance candidates/dives); the
clock-triggered restart occurs at about 22.59s. Control processes 30 nodes and
also returns no point. This is an important shared-desktop/time-budget limitation,
not evidence of a guided-dive gain or loss. Do not replace these results with the
faster screen trajectories, or assume guidance ran merely because its flag was on.

### Observed diagnostic limitation: danoint

The first screen pair processes only five tree nodes in each profile. The
guided root seed has distance 1.5758, is used for two steps, and still yields no
integer point. Its later restarted-root seed is selected but not used, because
the unchanged dive scheduling does not trigger there. Exclusive phase totals
show about 4.05s root LP, 8.91s tree LP, 9.08s pump projections, 0.93s pump
fixing, 2.01s dive and 5.02s LP recovery. The control has similar allocations.
The saved accounting localizes expensive LP work; it does not demonstrate that
any proposed scheduling or LP algorithm change would necessarily solve the case.

### Exploratory repeat selection

The full wave's first gt2 pair returns a lower candidate objective (35673
versus 42649), with guidance actually used. No numerical candidate repair is
used by either profile. The candidate incumbent sequence differs early and
reaches 35673 at about 2.44s, but that alone is one observation, not a repeated
performance claim. The reported gap remains about 60.93% versus 67.32%.
The separately declared [gt2 follow-up](GT2_FOLLOWUP_PLAN.md) adds two alternating
pairs with identical binary/settings, after the full wave/reference work.
This model was selected from observed results; the follow-up is explicitly
exploratory, not a new holdout or an unbiased full-suite average. Its four runs
and audit remain separate from the 78 main comparison runs.

The same wave also exposes adverse outcomes: pk1 returns about 20 under control
but 30 under guidance (minimization), with both reported gaps above 95%.
That regression remains in the full ledger and decision. The exploratory gt2
repeat cannot override an unfavorable result on another model or justify a
uniform-benefit claim. Misc07 instead returns 3785 only under guidance in this
pair, at about 6.71s and a 60.35% reported gap. It uses one 26-step guided dive,
without numerical candidate repair. Earlier iteration19 runs found a better
misc07 point under both profiles, so this is not a previously unsolved model
or a guarantee that guidance improves its solution quality across runs.

Both additional gt2 pairs repeat objective 42649 control versus 35673 guided.
Together with the wave, this is three paired observations of a roughly 16.4%
lower feasible objective, with all six returned points independently checked.
All three guided runs use guidance; none of the six uses numerical candidate
repair. The two additional guided gaps are 60.9772% / 60.9744%, versus
67.3623% / 67.3623% for control. Those large gaps remain open: no gt2 optimality
completion is obtained. The repeat's four records pass a separate full re-audit.
See [repeat audit](gt2-repeat-audit/PUMP_GUIDANCE_AUDIT.json) and
[supplemental evidence audit](SUPPLEMENTAL_AUDIT.json).
Repeat results SHA-256:
`a023f59fa50c728a12e3e1dab873e9a56c19278704e60848e7430ade723e900c`.

## Retained-path diagnosis for the next experiment

The post-timing [trajectory summary](GUIDANCE_DIAGNOSIS.json) checks seed/start
consistency and summarizes retained scalar traces without new solves. In the
repeated screen, the first original-objective dive LP moves away from the seed:

| Screen case | Seed integer distance | Distance after first dive LP |
| --- | ---: | ---: |
| lotsize, both repeats | 5.0000 | 9.7737 |
| eil33-2, both repeats | 2.1931 | 3.6156 |
| danoint, repeat zero | 1.5758 | 6.0964 |
| danoint, repeat one | 0.03501 | 5.6678 |
| blend2, both repeats | 0.2271 | 1.1896 |
| rout, both repeats | 0.6667 | 10.0742 |

Danoint repeat one really does retain the better 0.03501 seed (unlike its
root-only replay); that does not fix first feasibility, because the next
original-objective solve returns a point with 51 fractional variables. This
narrows the missing mechanism beyond simply obtaining a better seed. P0201
also moves away initially but reaches an accepted integer point within eight
guided steps, so drift is not proof that all guided runs must fail.

The next focused hypothesis is a point-only dive LP objective that keeps
distance to a promising assignment, with correct structural/basis handling,
the same budgets, independent point checks and no projection proof bound in
the tree. That mechanism is NOT implemented or proven effective here. These
scalar summaries are bounded traces, not independent certificates for every
unsaved LP vector. See NEXT_STEP.md for the scoped next experiment.

## Final audit and decision

All 78 main records pass re-audit, including 52 independently checked final
integer points and 20 retained fractional seed points. No final integer point
remains pending. The two original terminal-reference timeouts remain in the
raw main audit and are resolved by the separate longer reference described
above; they are not hidden by the zero-pending-points count.

The main audit checks four restricted exact proof records, 81,392 saved
objective-lattice events, 79 retained cuts, 96 cut-policy rounds and nine saved
cut-source incumbent vectors. Eighteen lattice traces are truncated at their
declared cap, so this is not exact proof coverage of every node. There are 24
actual guided dives and 702 guided steps in the main comparison; ten numerical
repair attempts accept ten valid points, not necessarily improved incumbents.

The four exploratory gt2 repeats pass their separate full audit, with four
additional independently checked final points and two actual guided dives.
Four root-only mechanism runs, twelve frozen19 parity runs and four suppression
checks remain separately identified, not inflated into the main benchmark
sample. The [supplemental audit](SUPPLEMENTAL_AUDIT.json) binds the repeat,
terminal reference, suppression checks and scalar diagnosis to their hashes.
See [main audit](final-audit/AUDIT.json) and
[guidance audit](final-audit/PUMP_GUIDANCE_AUDIT.json).

Keep the iteration19 repair and preserve its archive. Do not enable new pump
guidance by default: its selected gt2 quality benefit is repeatable, but it does
not solve the three target failures, pk1 loses solution quality, and rout's
wave point does not repeat in its screen. Overall robust coverage has not
been established beyond the historical 23-point wave, and only nine models
complete at the stated tolerance. The next single hypothesis is documented in
[NEXT_STEP.md](NEXT_STEP.md); arbitrary-input robustness, hard process resource
containment and real refinery/domain validation remain submission work.

## Archive and reproduction

Build in build-milp-iter20 with MinGW Makefiles, Release, CUDA off. Keep original
datasets, old gate dependencies, and the frozen19 archive. The C++ retained
repair test uses datasets/miplib2017/blend2.mps; final-source is not a standalone
dataset bundle. HiGHS independently checks/reads models, never supplies solver
incumbents and is not the project's optimization backend.

The final archive includes the tested executable, source manifest, raw outputs,
per-run source snapshots, gate/parity/mechanism results and final audits. Prior
iteration19 and all its evidence are preserved. CPU work stays local; no Kaggle
upload is needed.

Candidate executable: 812,878 bytes. SHA-256:
`0da07acbe45aaf097162c93eb8c33ef41321d692337e31dfbb5bab3612ef53d4`.
Frozen19 SHA-256:
`bb14f6adeb88e869a618a185c0fd48d5666134812534d8c350d08166f6642b35`.
