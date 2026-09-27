# MILP iteration12 — stronger numerical bounds, one additional public completion

15 September 2026. CPU candidate `build-milp-iter12`, SHA256
`3d29e6a0d5f0ed3bfb6c35e0a3ccee0bc158dda987b619242ed201aff3235a7d`.

The 17-model, 30-second matched wave improves from **9 to 10 completed cases**:
2 restricted exact proofs and 8 numerical completions. `mod008` is the added
completion, with objective 307. Seven cases remain unfinished. This is useful
proof-strengthening progress, not a universal-MILP or competition-rank claim.

The new `--objective-lattice` option remains OFF by default. Some outcomes
regress, notably gt2's incumbent and misc03's final bound. Stronger individual
bounds do not guarantee a better search trajectory within a fixed time limit.
Iteration11's input-reader correction and all prior archives are preserved.

## What changed

Own C++11 code detects a model-wide lattice of attainable objective values:
checked integral objective coefficients on integer variables, optionally after
substituting restricted unit-coefficient defining equalities for continuous
objective variables. It supports both objective senses, negative/zero costs,
checked dyadic offsets and overflow/range guards. Unsupported structures keep
the prior solver, with a diagnostic reason.

The method rounds only optimality-verified, safety-adjusted MAIN-TREE LP bounds.
It retains the old LP safety margin, subtracts an additional arithmetic margin
before rounding and publishes one double ULP downward. Heuristic/fixing
objectives, failed LPs and incumbent values are not converted into proof bounds.
No reference objectives, external incumbents or instance-name rules are used.

For misc03, a unit equality yields a step-5 objective lattice. That structural
fact is independently checked, but is not enough to close its remaining gap.
See [algebra, implementation guards and audit limits](../../docs/OBJECTIVE_LATTICE.md).
Exact lattice algebra does NOT make the underlying floating-point LP bound an
exact rational certificate. The restricted binary-proof engine stays separate.

## Protocol and evidence identity

The [predeclared plan](PLAN.md) retains all 17 wave1 models. Separate new build,
same executable for control and candidate; the only profile difference is
`--objective-lattice`. Common flags enable the existing LP recovery, incumbent
improvement, candidate repair, delayed lifted cuts/compact equalities/reduced
bounds and restricted binary proof. Gap target 1e-6, node cap 250000, own budget
30 seconds and external watchdog 45 seconds. No tolerances were loosened.

Run order alternates between profiles. All own timings within each experiment
finish before independent optimization/auditing. HiGHS 1.12.0 uses one thread,
5 seconds, 1e-9 MIP relative/absolute gaps and 1e-8 feasibility tolerances. These
unequal budgets are NOT a speed contest against HiGHS. References only validate
outcomes; none feed the solver. CPU: Intel i5-10210U, Windows, GCC 14.2 Release,
CUDA OFF. Local runs need no Kaggle notebook, upload or result ZIP.

Source, binary, model, command and checker hashes are recorded per experiment.
No core code or timed checker changed after the first public run. Supplemental
edge-case tests were added afterwards and are included in the final gate.
The benchmark is a small, mostly historical diagnostic selection, not the full
240-instance MIPLIB2017 benchmark or a representative performance sample.

## Full 17-model matched wave

[Raw results](wave1-paired-30s/results.json), [summary](wave1-paired-30s/SUMMARY.json).
All 34 saved outcomes passed their checks. Completion categories below are
independently cross-checked; limits are not counted as solved.

| Model | Control | Lattice candidate | Important comparison |
|---|---|---|---|
| p0033 | Restricted exact proof | Restricted exact proof | Objective 3089 in both |
| enigma | Numerical completion | Numerical completion | Objective 0; 9.70 / 9.84s |
| flugpl | Numerical completion | Numerical completion | Objective 1201500; lattice unsupported |
| stein27 | Numerical completion | Numerical completion | Objective 18; 5.00 / 2.43s, single pair |
| markshare_4_0 | Restricted exact proof | Restricted exact proof | Objective 1 in both |
| blend2 | Time limit, no incumbent | Time limit, no incumbent | Still a short-budget feasibility failure; lattice unsupported |
| binkar10_1 | Feasible time limit | Feasible time limit | Objective 6755.32 / 6784.22; lattice unsupported |
| egout | Numerical completion | Numerical completion | Objective 568.1007; lattice unsupported |
| gt2 | Feasible time limit | Feasible time limit | Objective 42649 / 92866: candidate regression |
| lseu | Numerical completion | Numerical completion | Objective 1120; 27.64 / 27.56s, essentially tied |
| mod008 | Feasible time limit | **Numerical completion** | Objective 307; control gap open at 30s, candidate closes at 13.58s |
| p0201 | Numerical completion | Numerical completion | Objective 7615; 11.45 / 11.23s |
| p0282 | Feasible time limit | Feasible time limit | Objective 266462; gaps 3.4753% / 3.4767% |
| misc03 | Feasible time limit | Feasible time limit | Objective approximately 3360; gaps 2.3059% / 2.9753% |
| misc07 | Feasible time limit | Feasible time limit | Objective approximately 2920; gaps 46.5581% / 46.3882% |
| pk1 | Feasible time limit | Feasible time limit | Objective 28, gap 96.5517% in both; lattice unsupported |
| rgn | Numerical completion | Numerical completion | Objective approximately 82.2; lattice unsupported |

For minimization, our reported gap is `(objective - bound)/(1 + abs(objective))`.
Near-zero numerical gaps must not be relabelled as exact proofs. Approximate
table values are for readability; raw JSON retains full precision.

The control has 2 exact + 7 numerical completions, 7 checked feasible limits and
1 no-incumbent limit. The candidate has 2 exact + 8 numerical completions,
6 checked feasible limits and 1 no-incumbent limit. No public validation failure
was observed. Unfinished candidate models are blend2, binkar10_1, gt2, p0282,
misc03, misc07 and pk1.

## Repeatability and regressions

The initial [target screen](target-screen-30s/SUMMARY.json) closed mod008 at
13.97s versus an open control at 30s. The full wave reproduced completion at
13.58s. A separate [three-pair target experiment](target-repeats-30s/results.json)
then completed mod008 in **13.94, 14.23 and 14.36 seconds**, median **14.23s**.
All three matched controls retained objective 307 but an open bound at 30s.
This is 3/3 versus 0/3 new repeated completions, not an exact runtime ratio:
the controls' completion times are censored by their limits. Both earlier
screens are reported separately, not pooled into the repetition statistic.

misc03 is NOT a second new completion. Both profiles match the independent
optimal objective in their feasible points, but their proof gaps remain open.
All three candidate repeats time out; median gap is 3.1241% versus the control's
2.3059%, with candidate bounds 3255, 3255 and 3260 (approximately). The paired
results, including adverse bounds, are retained. The same distinction
applies generally: knowing a good point is not proving it optimal.

The code currently uses one node-bound field for BOTH proof accounting and
priority ordering. Lattice rounding can create ties, alter depth/ID tie-breaking
and change how much time goes to different branches/heuristics. This is a
plausible explanation for search regressions, not a completed causal diagnosis.
Clock-triggered restarts also cause variation in unsupported cases such as
Binkar, where no lattice rounding occurs. Such timing differences must not be
credited to stronger mathematical bounds. lseu's apparent slowdown versus the
older iteration11 baseline was NOT a slowdown against its new matched control.

## Correctness gates and audit scope

The new C++ regression group checks 300 exhaustively enumerated general-integer
and equality-derived mixed models, both senses, original witnesses, 600
partial/zero-time outcomes, 10,005 near-grid checks and additional structural,
large-magnitude, infeasible/unbounded-relaxation and marker-default guards.
A controlled ten-variable example reaches the same optimum with 8 versus
659 nodes; this is an isolated mechanism test, not a public performance claim.

Another [100 generated MPS cases](generated-lattice/SUMMARY.json) pass exhaustive
625-point enumeration and independent completed HiGHS references: 34 direct
and 66 derived lattices. Their 742 recorded rounding events pass independent
Fraction-arithmetic checks. Mutation tests ensure wrong steps, shifts, signs,
coefficients, equations, missing definitions and skipped lattice points fail
the independent checker. The final regression/audit records are linked below.

The final gate passes all **10 CTest groups**, **65 Python checker tests**,
**28 independent marker-domain checks** and **160 additional generated MILP
runs** (the same 40 binary + 40 mixed cases in each profile, not 160 unique
models). No core or checker changed during the timed experiments.

The final re-audit passes **all 50 public run records** across the screen,
full wave and repeats: **48 saved final-point checks**, **65,710 saved lattice
events**, **64 retained lifted cuts** and **4 recomputed restricted exact proofs**
on 2 distinct models. Sixteen runs have truncated lattice traces. These counts
are checks of specific recorded evidence, not claims that 50 distinct public
models were solved or that every internal LP proof was certified exactly.

- [Final regression gate](final-gate/SUMMARY.json)
- [Evidence identity, lattice/cut/proof re-audit](final-audit/AUDIT.json)
- [Per-experiment matched comparison](final-audit/COMPARISON.json)
- [Frozen version identity and limitations](FINAL_STATE.json)

Lattice telemetry retains the FIRST 4096 improved-bound events per run;
truncation is explicit and occurs on hard cases. The independent audit checks
all SAVED events, not the omitted events. It proves exact parsed-model
substitution/GCD algebra and correctness of rounding relative to the supplied
input bound, NOT exact validity of every internal LP dual bound. Saved final
points, retained lifted cuts and restricted binary proofs have separate checks.

## Submission position and next work

We now have one more repeatable numerical public completion and a tested
general-purpose bound mechanism. We still do not have robust completion on
all 17 cases, full-library coverage, arbitrary-input exact certification,
industrial operational validation or a defensible top-percentile ranking.

Keep the feature optional. Next isolate proof-bound strength from search order
under deterministic node budgets, with correct minimum-bound bookkeeping for
queued/deferred nodes and restarts. Preserve gt2 as a regression sentinel and
misc03 as an unresolved proof target, then broaden cuts/search and predeclare
untouched holdouts. See [the concrete next cycle](NEXT_STEP.md). Domain/expert
validation, final applicable GPU repeats and a reproducible submission demo
remain necessary alongside CPU solver work.
