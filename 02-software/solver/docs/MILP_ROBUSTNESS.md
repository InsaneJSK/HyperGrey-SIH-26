# MILP robustness program

User priority, 15 September 2026: pursue broad public-MILP completion and
reliable handling of unfamiliar models. This replaces a narrow demo-first
performance target. It does not turn passing a subset into universal support.

Current evaluation: [iteration28](../reports/milp-iteration-28/REPORT.md)
retains26/27 useful development outcomes and ten optimization completions.
Six untouched public models return checked points but no completions in30
seconds. The ranking, alternate-reserve and restart-deferral experiments
from25–27 are rejected for promotion; the staged profile remains experimental.
All39 public/default records pass validation. The artificial duplicate-objective
reference mismatch is explained and retained separately. Process memory and
bounded external termination are now measured; internal limits remain cooperative.
See [the review](CODEBASE_REVIEW_2026_09_17.md) and
[next evidence-selected hypothesis](NEXT_PRIVATE_LP_HYPOTHESIS.md).

## Historical iteration24 checkpoint

[Iteration24](../reports/milp-iteration-24/REPORT.md) separates
objective retargeting from the first private bound change inside the same slice.
Candidate wave: 25 checked solutions, ten completions, one cross-checked
infeasible model, and lotsize unresolved. Control has 24 solutions and the same
ten completions. Misc07's gain repeats three times, but danoint fails two staged
screen runs and Binkar's wave solution worsens. Keep the option off by default.

All 98 public records and 48 saved-LP replay points pass validation. Lotsize's
parent/child replay drops to one/four pivots but still has no MILP solution.
Misc07's zero-pivot stage changes nearly tied branch ordering; its saved child
is slower warm than cold. Specific LP savings are not universal speedups.
Next test stable private-dive near-tie selection, with later expensive branch
fallback treated as a separate bounded hypothesis. All 27 remain development
data; feasible outcomes are not completed proofs or universal model coverage.

Previous experiment: [iteration23](../reports/milp-iteration-23/REPORT.md) adds a
guarded private basis handoff, off by default. Both profiles have 24 checked
solutions plus one corroborated infeasible result, with no new coverage.
Misc07/lotsize remain no-point limits. Candidate has nine completions versus
ten controls; mod008 has the same objective but an open gap at the cutoff.
Its private LP path is inactive, so do not infer mechanism causation.
All 94 records pass validation; ten actual LP replays pass 30 point checks.
Misc07's initial private LP uses nine pivots instead of 784, yet finds no
integer solution. Lotsize's compatible but neither-feasible basis falls back
to the same 2670-pivot cold solve. Next test staged retargeting/tightening
within the unchanged budget, not extra time or model-specific rules.

Previous experiment: [iteration22](../reports/milp-iteration-22/REPORT.md) adds
an exact-structure-guarded primal restart for private pump LPs. The full wave
has 24 checked candidate solutions versus 23 controls, ten completions each,
and one cross-checked infeasible model. Misc07/lotsize remain unresolved.
Danoint's new point and rout's lower objective repeat across screen and wave;
mas74 has worse candidate quality. The new option stays off by default.
All 90 paired records pass validation. Fourteen saved LP replays (42 independent
point checks) establish specific work reductions, not universal speedups. See
the complete ledger and next-step diagnosis; all 27 are still development data.

Previous experiment: [iteration21](../reports/milp-iteration-21/REPORT.md) tests
a private distance objective in the first guided dive. The screen gains checked
eil33-2/rout solutions in both repeats; both recur in the wave. Misc07 instead
loses its control point. The 27-model wave has 23 candidate solutions versus 22
guided controls, 10 completions each, and one independently cross-checked
infeasible model. Candidate misc07/lotsize/danoint remain no-point limits.
Preserve adverse outcomes and leave the feature off by default.

The final artifact additionally guards a reproduced presolve-off empty-integer
domain exception, without changing presolve-on search or introducing a proof
bound. Separate gates/parity/MAX-MIN integration pass on it; do not attribute
the earlier 86 timings to that different binary. The complete audit checks all
65 final solution vectors. See the full ledger and three-iteration checkpoint:
reoptimization cost and large proof gaps remain, not just missing features.

Prior experiment: [iteration20](../reports/milp-iteration-20/REPORT.md) tests
bounded pump-guided diving. Actual guidance and retained fractional seeds pass
the root-only integration checks, but the repeated six-model screen produces
no new first-feasible coverage. The existing blend2 repair and p0201 completion
survive. Preserve all negative outcomes; do not promote the new flag simply
because it is implemented or passes regression gates. See the full paired wave,
model ledger and next-step diagnosis in the report. All 27 remain development
data and CPU work remains local.

The full wave has 23 guided points versus 21 control points, nine completions
each, one infeasible status cross-checked by a separate longer reference, and
three guided no-point limits. The gt2 quality gain repeats in three pairs, but
pk1 worsens and no targeted no-point case is fixed. The saved first-step traces
show original-objective LPs undoing much of the seed's integer-distance progress;
the next bounded hypothesis is a distance-preserving heuristic LP, not a
guaranteed fix or a reason to relax checks/budgets.

Prior: [iteration19](../reports/milp-iteration-19/REPORT.md) diagnoses first-feasible
failures with bounded pump/dive traces and adds optional repair of rejected
near-integer dive candidates. A retained blend2 fixing is independently shown
feasible after accurate dense recovery. That fixing result supplies only a
checked incumbent, never a whole-node certificate. Existing time allowances,
tolerances and proof accounting remain in force. See the full repeated screen
and 27-model paired wave for gains and regressions; this is not an arbitrary-input
or full-library guarantee. The repair wave returns checked points on 23/27,
with 9 optimality/tolerance completions, one cross-checked infeasible model and
3 no-point limits (lotsize, eil33-2, danoint). Blend2's direct first-point gain
repeats 3/3; rout's extra wave point had no repair attempt. The paired profiles
both leave mod008 open in this wave, unlike earlier iteration18 timings.
All 27 are development data. The
[next work](../reports/milp-iteration-19/NEXT_STEP.md) separates other no-point
mechanisms from stronger proof-bound work. CPU testing stays local.

Prior: [iteration18](../reports/milp-iteration-18/REPORT.md) preserves that
cold/warm numerical repair while checking at selected simplex decisions.
Detailed residual-work accounting and an instrumentation-only parity stage
separate measurement from the algorithm change. The repeated three-model
screen retains p0201 completion and eil33-2 points, and eliminates observed
mas74 recovery/deferred nodes. The full experiment also keeps all 24 previous
models and adds three predeclared new instances. These are moderate historical
models, not hardest-instance or full-library coverage. See the complete report
for regressions and remaining gaps. Both refinement options stay opt-in; the
[next work](../reports/milp-iteration-18/NEXT_STEP.md) separates first feasibility
from stronger proof bounds. No GPU or user upload is needed for CPU work.

Prior: [iteration17](../reports/milp-iteration-17/REPORT.md) repairs a retained
ill-conditioned sparse LP from both cold and original warm starts. Its opt-in
refinement eliminates observed mas74 recovery/deferred-node failures in three
runs, but does not close its proof gap. The 24-model wave has mixed outcomes,
including p0201 completion loss and eil33-2 incumbent loss; no default promotion.
All 24 are development cases. Next measure refinement work, preserve the repair
with fewer whole-solve regressions, and add predeclared untouched hard cases.

## Meaning of robust

1. Read the intended model: objective sense/offset, integrality, bounds, ranges,
   duplicate coefficients and supported syntax have independent parser checks.
   Unsupported extensions and malformed data must be rejected explicitly.
2. Return valid decisions: check original rows, bounds and integrality. Never
   publish a rounded infeasible candidate as a solution.
3. Preserve proof logic: valid cuts/bounds, correct node coverage, no false
   pruning, distinct optimal/infeasible/unbounded/limit/numerical outcomes.
4. Survive difficult runs: time/node/memory budgets, guarded fallbacks, useful
   diagnostics and honest partial results. An LP relaxation ray alone does not
   prove a MILP unbounded; no incumbent does not mean infeasible.
5. Generalize: fixed profiles, public failures retained, new holdouts, repeated
   equal-budget runs, min/max and transformed equivalents. No named-model rules
   or published answers inside the solver.

## Coverage ladder

- First wave: 17 predeclared small/moderate historical and modern public models,
  including 10 not previously tuned here. Diagnose before making scale claims.
- Next: expand by model structure and size, including general integers,
  continuous recourse, negative/free domains, equalities and degeneracy. Select
  new cases before seeing outcomes and retain holdouts for the final profile.
- Target: the full 240-instance MIPLIB2017 benchmark with an explicit per-case
  resource envelope, then a declared larger collection. Completion rate, checked
  incumbent rate, remaining gaps and failures must all be reported separately.
- Alongside public models: analytically known feasible/infeasible/unbounded
  cases, exhaustive tiny MILPs, invalid inputs, numerical stress and metamorphic
  tests (variable permutations, redundant rows, objective changes and scaling).

Every failure becomes a reproducible input, cause, regression and same-budget
retest. Correctness failures take priority over new heuristics or speed gains.
The [iteration11 plan](../reports/milp-iteration-11/PLAN.md) freezes first-wave
selection and protocol. Its ledger is generated by `scripts/milp_robustness.py`.

Iteration12 keeps all 17 cases in matched control/lattice runs. Its optional
[lattice-bound method](OBJECTIVE_LATTICE.md) closes one additional numerical
case, mod008, while retaining the remaining limits and adverse search outcomes.
See the [paired evidence](../reports/milp-iteration-12/REPORT.md) and
[next deterministic search/proof experiment](../reports/milp-iteration-12/NEXT_STEP.md).
Stronger valid bounds can change queue order and do not guarantee better
incumbents within a fixed time budget. This is why an optional candidate is
tested broadly before changing the default policy.

Iteration13 implements that separation with an independent queued-bound index,
deferred-node accounting and optional event replay. A 24-run fixed-node screen
reproduces all 12 model/policy pairs. The matched 17-model timed wave completes
7 cases per policy on a busy shared desktop, with mixed incumbent/gap changes;
it is not comparable to earlier wall-clock results. Four untouched members
of the MIPLIB2017 benchmark are predeclared by structure, downloaded unchanged,
and kept regardless of outcome. Read the
[new evidence](../reports/milp-iteration-13/REPORT.md) and
[remaining experiment](../reports/milp-iteration-13/NEXT_STEP.md). Defaults remain
unchanged and all historical archives are retained.

Iteration14 adds [exclusive phase/work attribution](MILP_WORK_BUDGETS.md), then
tests a predeclared one-round root-cut allowance against the previous five.
The diagnostic cases have different bottlenecks. Cutting work helps Binkar's
short-run search but seriously weakens p0282, so the candidate stays optional.
The full 21-case ledger retains that regression; these are all development
cases now, not a new holdout set. Counter-only restart tests, exhaustive mixed
models and independent bookkeeping checks exercise the new controls without
changing proof/feasibility tolerances. Read the
[iteration14 evidence](../reports/milp-iteration-14/REPORT.md) and
[next bounded experiment](../reports/milp-iteration-14/NEXT_STEP.md).

## Proof categories are not interchangeable

Iteration16 implements first-feasible protection for the optional cut policy.
Analytic min/max examples exercise both the protected root and stopping after
a checked incumbent. The Binkar screen preserves feasibility but still weakens
gaps versus five rounds; no default promotion follows. Separate frozen15 mas74
ablations and cold LP replay distinguish an exhausted recovery/restart exit
from an underlying sparse numerical failure. Prioritize that retained fixture
for guarded accuracy work. Read [iteration16](../reports/milp-iteration-16/REPORT.md)
and [the next bounded step](../reports/milp-iteration-16/NEXT_STEP.md). No new
untouched public cases are claimed here; all 24 are development data.

Iteration15 adds independently replayed selective cut decisions, with fixed
thresholds and no post-screen tuning. Binkar's repeated no-point regression
rejects default promotion. All 21 retained wave cases and 3 fresh MIPLIB2017
cases remain in the ledger, totaling 66 paired/repeated public outcomes on
24 distinct models. The fresh cases expose an unresolved numerical/recovery
case (mas74), a feasible limit (gen-ip054), and a cross-checked but not exactly
certified infeasible result (neos859080). Tiny exhaustive tests are supplemented
by analytic MIN/MAX cases that actually cross the production stop threshold.
Read [iteration15 evidence](../reports/milp-iteration-15/REPORT.md) and
[next bounded work](../reports/milp-iteration-15/NEXT_STEP.md). Broader testing
has strengthened the failure ledger, not established universal completion.

An independently checked restricted integer proof is exact within its supported
input class. General solver optimality is currently floating-point/numerical.
A completed independent reference comparison supports that result but is not
an exact rational certificate. A checked incumbent with an open bound remains
unfinished even when its objective matches a published optimum.

The [official MIPLIB page](https://miplib.zib.de/) distinguishes its selected
benchmark from the larger collection, which includes open instances. A promise
to solve every arbitrary public MILP quickly is not defensible. Our operational
commitment is expanding measured coverage, closing more proof gaps, and never
disguising unsupported, interrupted or unchecked outcomes as success.

CPU runs stay local. GPU execution remains limited to applicable CUDA work;
no CPU-only Kaggle notebook or upload is needed for this program.
