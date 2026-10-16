# MILP iteration15 — selective root-cut continuation

Completed local experiment: the adaptive policy is rejected for default
promotion. Broader checks pass, but no general performance improvement is
established. Five cut rounds remain the default; adaptive mode remains opt-in.

New optional policy and complete per-round decision logging are described in
the [method](../../docs/ADAPTIVE_CUT_ROUNDS.md) and [predeclared plan](PLAN.md).
Five rounds remain the default. No benchmark-specific core rule, imported
incumbent, proof logic or tolerance change is used.

## Preflight evidence

All 13 CTest groups and 100 Python unit tests pass. New C++ tests cover policy
thresholds, adjacent floating-point values, offset translation, nonfinite and
overflow guards. They run 720 full solves on 120 new exhaustive mixed min/max
models plus 1440 partial/zero-time checks; 272 cut rounds and 448 restarts are
observed. Tiny models generally do not reach the production work threshold;
direct policy tests exercise the stop branch separately.

Seven frozen14/current-off/current-capture triples have identical semantic
results: four 512-node cases without cuts, and Binkar/p0282/mod008 at three nodes
with cuts and a counter-triggered restart. Heuristics are disabled and the time
allowance is generous. This supports unchanged defaults and trace capture; it
does not establish identical time-limited heuristic trajectories.

All 28 independent MPS marker-domain checks pass. The reference checker's cached
sparse-array access returns identical vector-validation fields to frozen14 on
all 21 existing public models (saved points, or zero vectors for two no-point
cases). Accumulation order is unchanged. Both helpers use a zero solve limit
for that comparison: it is not an optimizer-trajectory or solver-speed test.

Candidate binary SHA256:
`57ce59edcc13d7717e0a8fd3f964dd8960d79cb86f9acb0dde9ee7d78003d159`.

## Paired results

All six screen outcomes and their decision traces pass independent checks.
The policy remains off by default and the candidate is not retuned afterward.

| Screen case | Baseline five rounds | Selective policy |
|---|---|---|
| Binkar | Point 6759.380024, gap 1.1931% | No point at 30s |
| p0282 | Point 266462, gap 3.4812% | Point 266462, gap 3.4868% |
| mod008 | Numerical completion 307 in 14.21s | Numerical completion 307 in 14.67s |

Binkar stops after two rounds at both roots: four cut LPs and 4.81s versus
eight LPs and 9.81s. However pump projection time grows from 1.21s to 10.01s,
diving from 1.95s to 6.04s, and the candidate finds no incumbent. Its different
root relaxation changes the subsequent feasibility search. Less cut time does
not guarantee better feasibility, and a small dual-bound gain does not measure
a cut's effect on heuristic starting points.

P0282 retains nine cut LPs in both profiles. Its final selective stop does not
establish a saved LP call: the baseline also finds no further cut to add. Mod008
retains five calls and makes no adaptive stop. The cheap-round safeguard avoids
the previous blanket one-round policy's large p0282 regression in this screen,
but does not fix the Binkar trade-off. Neither wall times nor the clock-driven
restart boundary are controlled comparisons against historical iterations.

## Two new repeat pairs per target

All 12 repeat outcomes and policy traces validate. Binkar's adaptive runs both
return no point; the baselines return 6791.720026 (gap 1.6614%) and 6757.190022
(gap 1.1590%). This repeats the first screen's feasibility failure and rules out
promoting the policy, even before the broader wave is considered.

P0282 keeps objective 266462 in all four runs. Baseline gaps are 3.4920% and
3.4872%, versus 3.4924% and 3.5056% for adaptive. No gain is established.
Mod008 numerically completes at 307 in all four runs. Baselines take 14.98s
and 14.47s; adaptive takes 27.18s and 14.75s. The slower adaptive run explores
17400 nodes versus 8781 in the other runs. The half-time restart boundary
remains clock-driven and can change total work abruptly; these are not purely
deterministic work-budget comparisons.

## Full retained 21-model wave

All 42 outcomes pass their saved-result checks. Both profiles complete 10
models: 2 restricted exact proofs (p0033 and markshare_4_0), plus 8 numerical
completions (enigma, flugpl, stein27, egout, lseu, mod008, p0201 and rgn).
The baseline has 9 further checked feasible limits and 2 no-point limits;
adaptive has 8 and 3. Blend2 and lotsize have no point in either profile.

Binkar again has no adaptive point, versus baseline objective 6794.860025 and
1.7109% gap. Across the screen, two repeats and wave, adaptive loses the point
in **all four runs**, while every paired control returns an independently
checked point. This is a repeated regression, not a default-promotion candidate.

Other partial results are mixed. Adaptive improves assign1-5-8's objective
226 to 224, but worsens pk1's 28 to 31 and misc03's gap 3.4216% to 3.8679%.
P0282 keeps objective 266462 with gaps about 3.48% in both profiles. None of
these isolated partial differences establishes a general gain. All models,
commands, timings, points and gaps remain in [wave results](wave-30s/results.json).

## Three predeclared fresh cases

These are members of the [official MIPLIB2017 benchmark](https://miplib.zib.de/tag_benchmark.html),
selected before any of their solver outcomes were observed. Their original
downloads, provenance and input hashes are retained. No published objective
or reference incumbent is supplied to the engine. They now become development
data, not untouched holdouts for a later iteration.

| Case | Five-round baseline | Adaptive | Independent check |
|---|---|---|---|
| mas74 | 14165.464078; reported gap 24.0491%; unresolved relaxations | 13972.790599; reported gap 23.0011%; unresolved relaxations | Both points have zero reported row/bound and integer violations |
| gen-ip054 | 6911.531524; gap 1.8263%; time limit | Same point; gap 1.8257%; time limit | Both points checked |
| neos859080 | Infeasible, 89 nodes | Infeasible, 89 nodes | Reference terminal status agrees; not an exact infeasibility certificate |

Mas74 returns at about 15.02s with unresolved relaxations, despite a configured
30s budget. A valid incumbent does not resolve those subproblems or establish
completion. This is a newly retained numerical/recovery limitation needing
diagnosis. General proof bounds remain numerical; the displayed gaps are the
engine's reported gaps, not independently exact rational certificates.

The six fresh outcomes pass their checks, with no pending reference point.
They generate no cut LP rounds in either profile, so they broaden numerical/
terminal-status coverage but do not independently exercise the new decision
branch. Differences in their partial points are not evidence of cut-policy gain.
Across the 21-case wave plus these 3 cases, each profile has 10 optimal/gap
completions and 1 cross-checked infeasible termination. Baseline additionally
has 10 feasible limits, 1 unresolved run with a checked point and 2 no-point
limits; adaptive has 9, 1 and 3 respectively. These are selected-case outcomes,
not a full-library completion rate. See [holdout results](holdout-30s/results.json).

## Production stop-branch safety test

Four supplementary integrations use two min/max versions of an analytically
solvable model: 40 independent binary pairs, each with 2x+2y<=3, plus a fixed
320-variable continuous chain. The known objectives are +51356000 (MIN) and
-51356000 (MAX); no point is injected. Cold LP work reaches the production
policy threshold, unlike the tiny exhaustive models.

With heuristics/presolve off and one tree node allowed, the baseline uses three
cut rounds and numerically completes at the known objective. Adaptive stops
after two rounds in both senses, leaves a correctly oriented partial bound,
and returns node_limit with no point and no gap. Original-model checks,
independent decision replay and work bookkeeping pass all four runs. This
exercises an actual allocation stop without falsely claiming completion. It
also provides a simple counterexample to assuming a small relative bound gain
means the next cut round is unnecessary. These generated cases are not added
to the public-model count. See [analytic checks](analytic-stop/SUMMARY.json).

## Final verification and decision

The full regression gate passes: 13 CTest groups, 100 Python unit tests, all
28 independent MPS-domain cases and all seven default/capture parity triples.
Four profiles (baseline five rounds, adaptive caps 0, 1 and 5) pass 320
generated runs on 80 binary/mixed cases. Another 100 reused exhaustive MPS
models complete with fresh references and match their known objectives. Those
generated gate runs record zero cut rounds, so they are general regression
coverage—not evidence that the production stop threshold was exercised.
The separate C++ and analytic integrations above provide that targeted coverage.
See [gate summary](final-gate/SUMMARY.json).

The independent saved-result re-audit passes all 66 public records across 24
distinct models. It checks 56 final vectors, with zero pending reference points;
4 restricted exact-proof recomputations on 2 models; 208 retained lifted covers;
and 115194 saved lattice events. Twenty-eight lattice traces explicitly truncate
at 4096 events: this is not a check of every internal lattice improvement.
All 176 recorded cut LP rounds replay, including 12 adaptive stop decisions.
No validation failure is observed in this evidence. Counts are checks of saved
artifacts, not distinct solved models. See [result audit](final-audit/AUDIT.json)
and [decision audit](final-audit/POLICY_AUDIT.json).

The [final state](FINAL_STATE.json), [source manifest](SNAPSHOT_MANIFEST.json)
and `final_solver_cli.exe` identify this archive. The freezer verifies the
candidate and all run-snapshotted source/checker/test files against every timed
run and checks iteration14's archived executable, source manifest and evidence
hashes before writing the new archive. Documentation is updated after results;
it is not part of the timed-source selection. Bulk inputs and older evidence
dependencies are separate; see [reproduction instructions](../../docs/V2_REPRODUCE.md).

Keep five rounds as default and adaptive continuation OFF. The useful additions
are checked decision telemetry, a reproducible rejected hypothesis, broader
negative/numerical cases and faster independent sparse-vector validation—not
a demonstrated broad solver-speed improvement. Existing proof and tolerance
rules are unchanged. See the [next bounded experiment](NEXT_STEP.md): protect
first-feasible search by considering cut reduction only after a checked
incumbent exists. That proposal is not implemented in this archive.

CPU tests ran locally on the shared Intel desktop. Measured own solves were
sequential and separated from this task's build/reference/test work; unrelated
desktop activity was not controlled. References have a configured 5s solve
limit and 150s external process watchdog, so these are not equal-budget speed
comparisons against HiGHS. General MILP proof, hard memory containment, broad
GPU acceleration and real industrial validation remain open. No Kaggle run or
user upload is needed for this iteration.
