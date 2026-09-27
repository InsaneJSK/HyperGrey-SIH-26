# MILP iteration05 — local experiments completed, defaults unchanged

15 September 2026. Three local CPU experiments tested stalled-neighbourhood
selection and scheduling. **None improved the final hard-instance objectives.**
The early diversification probe regressed; a later trigger retained the previous
results. Time spacing spread attempts later but did not improve
final solution quality. Neither option is promoted to a default.

The retained development build adds useful bounded diagnostics and tested opt-in
controls. It is not described as a faster or more capable industrial solver
on the strength of these experiments. No GPU/Kaggle run is required or claimed.

## Current checked outcomes

| Model | Guided (180s) | Diversified (180s) | Paced screen (180s) | Remaining status |
| --- | ---: | ---: | ---: | --- |
| markshare_4_0 | 4.999999994 | 4.999999994 | 4.999999994 | node_limit;83.33% reported gap |
| blend2 | 7.598985 | 7.598985 | 7.598985 | gap_limit; matches independent optimum |
| binkar10_1 | 6747.310014559 | 6747.310014559 | 6747.310014559 | time_limit; about1.22% reported gap |

Guided versus revised diversified is a fresh six-run, alternating-order
comparison. The paced column is a later single-strategy screen against that
historical guided baseline, NOT a fresh paired/repeated timing comparison.
All runs use180-second budgets and250,000-node caps. Reference solves follow
all timed runs, with30 seconds per model. No reference solution enters our core.

Paced solve times: markshare 120.983s, blend2 124.603s, binkar 180.700s.
The earlier blend2 pair took 145.508/146.236s. Machine/timing variation and a
single screen do not support a speedup claim. Binkar's reported gaps are
1.221003% guided,1.223310% diversified, and1.225704% paced: the paced screen
does not improve the proof bound either. Limits remain incomplete outcomes.
Independent references time out on markshare and binkar with incumbents3 and
6746.760023; neither reference incumbent is called a proven optimum.

## What was implemented and learned

- `--neighborhood guided|diversified`: the guided selector is retained. The
  optional selector varies released integer variables after four unsuccessful
  neighbourhood calls, with up to4s/128 local nodes for those attempts. The
  cumulative allowance remains min(30s,15% of total solve time), with16 calls.
- `--pace-neighborhood`: a separate, opt-in minimum start-time spacing of
  min(5s,2% of global solve time). The first call remains immediate, and total
  call/node/time allowances do not increase. Tested with guided selection.
- `--capture-neighborhood`: bounded per-call records of budgets, released
  integer indices, LP failures, before/after objectives and the last improved
  vector of each successful call on models with at most10000 variables.
- The independent audit now checks these vectors, trace/counter accounting,
  released-index validity and actual call spacing. Eleven adversarial checker
  tests reject malformed or inconsistent evidence.

The first two-stall probe regressed on binkar at90s:6789.67 versus6757.19 guided.
All raw data and its earlier binary/source remain preserved. Four-stall
diversification retains6747.31 at180s, but its one diversified binkar attempt
gets only0.2022 seconds of remaining neighbourhood allowance and explores one
local node. A late trigger alone does not reserve useful late-search budget.

Markshare originally spends all16 calls by0.90 seconds around incumbent73,
well before the tree reaches~5 at76.19s. Diversification improves the early
incumbent to~61 but still ends at~5. Pacing spreads calls through54.03s, with
better intermediate centers, but still uses its last call before the eventual
best incumbent at75.62s. It also finishes at~5. This identifies remaining
budget scheduling and restricted-domain limitations, not a solved bottleneck.

## Verification and preserved evidence

- CTest3/3 and generated240/240 in each of the three experiment gates. These
  are repeated checks across configurations, not720 distinct test problems.
- Fresh original-MPS vector audits:7/7 for the first probe,28/28 for the full
  pair,12/12 for the paced screen. These47 checks include repeated vectors;
  they are not47 distinct solved problems. All satisfy the unchanged absolute
  feasibility and integrality tolerances <=1e-7.
- All11 timed hard runs return independently checked final incumbents, with
  no unsafe/error run flagged. The first probe is nevertheless a performance
  regression; correctness alone does not justify promotion.
- Current guided-mode outputs match the previous build exactly on80 generated
  models for status, objective, primal, bound, gap, nodes and LP iterations.
  Timings and new diagnostic fields are excluded; see `DEFAULT_NONREGRESSION.json`.
- Tests retain no-heuristics, zero-time, maximization and repaired-node
  proof-bound regressions, and exercise stalled selection with an analytic
  30-binary-variable model. No local subproblem bound is exported to the tree.

Evidence: `probe-90s/`, `probe-90s-audit/`, `local-180s/`, `local-180s-audit/`,
`pacing-180s-screen/`, `pacing-180s-audit/`. Each run saves source/model/binary
identity and raw candidates/references. `EXPERIMENTS.md` records the sequence.
Only captured vectors can be recomputed; uncaptured intermediate incumbents
have objective-only traces. Floating-point checks are not exact certificates.

Current CLI: `build-milp-iter5/solver_cli.exe`, SHA256
`ef1856d074862aa754a81e5bff7bfc44c350c02eae4f0a6b43a309c4f4e53cd6`.
The binary and source are also preserved as `final_solver_cli.exe` and
`final-source/`. Earlier binaries/source folders remain separate. LP/QP/CUDA
numerical files are unchanged from iteration04; no new GPU result is claimed.

## Submission decision and next work

Keep guided selection and unpaced scheduling as defaults; incumbent improvement
itself remains opt-in as before. These experiments improve observability and
reproducibility, not the current final-objective scoreboard. Submission claims
must still say markshare and binkar are incomplete and industrial coverage is
limited. No top-percentile ranking is established.

The next meaningful CPU experiment should reserve usable search allowance for
later, materially improved incumbents and test larger/coupled integer domains,
with tighter global bounds as a separate avenue. Compare under unchanged
acceptance checks and equal budgets. Preserve blend2 completion and all proof
regressions. Do not keep rerunning unchanged notebooks or add GPU work to this
CPU-only MILP path. See the [method and budgets](../../docs/MILP_NEIGHBORHOOD_METHOD.md).
