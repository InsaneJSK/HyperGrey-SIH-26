# SIH26119 submission assessment — 17 September 2026

Assessment against the supplied problem statement, not against unseen teams.
Deadline: 30 September. This is a substantial, reproducible solver research
prototype. It is not yet an established industrial replacement for CPLEX,
Gurobi or Xpress, and there is no defensible basis for a top-0.1% prediction.

Latest evaluation: [iteration28](../reports/milp-iteration-28/REPORT.md) retains
25 checked feasible solutions plus one cross-checked infeasible model in the
27-case development wave. Ten optimization completions remain; lotsize has no
point and15 feasible cases have open gaps. Six untouched public models return
checked points, but none completes in30 seconds. Defaults are unchanged.

The four planning slots25–28 have been executed. Stable ranking, alternate
reserve and deferred restart are rejected for promotion. All39 final public/
default records and37 vectors pass validation;24 artificial answers pass
enumeration and an explicitly canonicalized reference after a retained
duplicate-objective input mismatch. Fifteen status/resource checks and a
corrected five-DLL isolated-folder smoke pass. These are useful engineering
results, not a release-readiness or universal performance claim.

Next work should test the [specific warm-dual infeasibility hypothesis](NEXT_PRIVATE_LP_HYPOTHESIS.md)
and address first-point reliability/completion. Final LP/QP breadth, matched-
accuracy performance, actual final-source GPU evidence, domain validation and
submission/demo preparation remain. No GPU upload or external submission was
performed. Historical evidence below retains the scope of its recorded build.

Previous local experiment: [iteration23](../reports/milp-iteration-23/REPORT.md)
does not increase coverage. Both profiles return 24 independently checked
solutions plus one corroborated infeasible status; misc07/lotsize remain
unresolved. Control has ten completions, candidate nine: mod008 retains its
objective but not completion at the cutoff. Its private handoff LP never runs,
so timing variation must not be assigned a demonstrated algorithmic cause.
The new flag stays off. All 94 records pass validation, and ten saved LP replays
pass 30 independent point checks. Local LP savings are not a stronger submission
coverage result. Next test staged retargeting/bound tightening within the same
budget, while protecting existing results. Five planning slots remain, without
any guarantee of 27/27; domain, unseen-case, GPU and delivery work still remain.

Previous local experiment: [iteration22](../reports/milp-iteration-22/REPORT.md)
returns 24 checked feasible solutions and one cross-checked infeasible status
in the 27-model wave; misc07/lotsize still have no point. Ten models complete
(two restricted exact, eight numerical/tolerance), with fourteen feasible
models still open. Thus 25/27 have a solution or corroborated terminal status,
not 25 proofs. Danoint's new point and rout's improved objective repeat across
three comparisons; mas74 instead loses solution quality. Keep the new private
pump reoptimizer optional. All 90 paired records pass validation; full gates,
parity, actual LP replays and MIN/MAX/domain tests pass on the same measured
binary. No GPU upload is needed for this CPU work.

This is stronger observed feasibility coverage, not an industrial replacement
or a percentile prediction. At that point six of the ten planned slots remained,
without any guarantee that they suffice. Next address the first cold distance
LP while protecting solution quality; domain validation, unseen cases, hard
resource containment, reproducible delivery and GPU evidence remain required.

Previous local experiment: [iteration21](../reports/milp-iteration-21/REPORT.md)
demonstrates repeated first-feasible gains on eil33-2/rout with a private L1
dive, but loses misc07 in the wave. Candidate: 23 checked solutions, of which
10 complete; one other model is cross-checked infeasible, while misc07/lotsize/
danoint have no point. Control has 22 solutions and the same 10 completions.
This is not uniformly stronger breadth than iteration20's historical 23-point
wave. A better distance metric is not a proof, and multiple-profile best-of-runs
coverage is not one 30-second solver result. Keep the feature optional.

The final build fixes a separately reproduced presolve-off domain exception.
Its full correctness gate, parity and MIN/MAX integration pass; its binary is
distinct from the build used for the 86 public timings. Both are preserved and
identified. The audit checks all 65 final vectors, 40 fractional seeds and four
restricted exact certificates. At the three-iteration checkpoint, seven slots
remain in the earlier ten-iteration planning budget, not a guarantee of 27/27
completion. Private LP reoptimization cost and proof-gap work remain, alongside
domain validation, resource containment and reproducible submission delivery.

Previous local experiment: [iteration20](../reports/milp-iteration-20/REPORT.md)
tests using fractional pump progress to guide one dive, without changing proof
bounds, tolerances or the time allowance. The repeated six-model screen has no
new first-feasible coverage. This is a tested research experiment, not a new
submission-readiness or competition-percentile claim. The gate passes 20 CTest
groups, 152 Python tests, 320 generated runs and 100 retained exhaustive cases;
the feature remains off by default. Consult the full 27-model comparison and
decision in the report before choosing an experimental profile. Frozen19 and
its checked blend2 repair are retained.

The complete wave has 23 checked solutions, nine completions and one
cross-checked infeasible model; lotsize/eil33-2/danoint remain no-point limits.
This is not increased reliable breadth over iteration19's historical 23-point
wave. Gt2's lower feasible objective repeats in three selected paired
observations (42649 -> 35673), but its gap is still about 61%. Pk1 instead
worsens from about 20 to 30. These findings improve our evidence and expose the
next failure mechanism; they do not establish uniform gains or industrial
readiness. The longer supplemental infeasibility reference changes no own-run
budget and preserves both original reference timeouts.

Previous local update: [iteration19](../reports/milp-iteration-19/REPORT.md)
turns a concrete missed feasible candidate into a bounded repair opportunity.
The retained blend2 integer fixing fails sparse numerical checks but succeeds
with our dense LP algorithm and independent original-model validation. A new
optional dive repair uses the existing budget and unchanged acceptance checks;
it supplies a point, not an optimality proof. The full gate passes 19 CTest
groups, 140 Python tests, 320 generated runs and 100 retained exhaustive cases.

The latest 30-second wave has 23/27 checked solutions, but only 9 optimality/
tolerance completions. Another model is cross-checked infeasible, while lotsize,
eil33-2 and danoint have no point. Blend2's new first-feasible gain repeats 3/3,
with about 13.6% still open; rout's extra point involves zero repairs and cannot
be credited as a direct feature gain. Both profiles lose the prior mod008
completion under this wave's timing. See the complete ledger and report for
the preserved reference timeout and supplemental same-model status check.
Numerical repair of one failure is not
universal first feasibility, consistent industrial speed or a competition
percentile. Existing domain-validation, deployment/resource containment and
final GPU-specific evidence gaps remain. No GPU or user upload is required for
this CPU-only work.

Previous local update: [iteration18](../reports/milp-iteration-18/REPORT.md)
preserves the numerical repair with selective decision-boundary checks and
adds independently checked correction-work accounting. Retained cold/warm
LP replays each need 3 attempts / 2 accepted corrections instead of always-mode
99/72 cold and 18/12 warm, at unchanged tolerances. This is a concrete, testable
engineering improvement, not evidence of uniformly faster MILP search.

The 17 CTest groups, 126 Python tests, 320 generated runs, 100 reused exhaustive
cases and transformed min/max checks strengthen correctness evidence. The
public protocol keeps all 24 development models and adds three locally unseen
instances. The development wave completes 10/24 in both profiles, with checked
points on 19 control versus 20 selective models. Binkar worsens, and eil33-2
finds points in all four screen runs but neither wave run. This remains mixed
performance with a real first-feasible reliability gap. See the complete report
for all outcomes. Danoint/rout have no point under either profile; mas76 has
checked points and improves from 7.50% to 5.24% gap, but no new case completes.
The new cases are moderate historical models, not the hardest industrial class,
and mas76 is related to mas74. Remaining no-point cases, large proof gaps,
unproven scalability, missing real refinery validation and narrow historical
GPU evidence still prevent an industrial-readiness or top-0.1% claim. Both
refinement modes remain optional, with a reproducible frozen control preserved.

Previous local update: [iteration17](../reports/milp-iteration-17/REPORT.md) adds
a real sparse-LP numerical repair: the retained cold and original warm failures
now pass independent original-model point checks at about 2.91e-11 violation,
with unchanged tolerances and resource allowances. Three full mas74 runs avoid
LP recovery/unresolved nodes, but still have about 15.7% gaps; one control finds
a better objective. This strengthens a concrete robustness demonstration, not
a claim of uniform speed, objective quality or industrial scalability.

The 24-case paired wave completes 9 controls versus 8 refined cases, including
2 restricted exact proofs in each. Both return points on 20 models. The
candidate gains misc07 feasibility but loses eil33-2 feasibility and p0201
completion. It remains opt-in. All 52 public experiment records and 44 returned
points pass re-audit, alongside 15 CTest groups, 115 Python units, 320 generated runs,
100 reused exhaustive cases, 12 transformed LP equivalents and genuine saved
warm replay. No fresh public holdouts or GPU evidence is added in this iteration.
The next priorities are selective accuracy work without those regressions,
unseen hard models, stronger bounds/feasibility, real domain validation and the
final reproducible demonstration. No defensible top-0.1% guarantee follows.

Previous local update: [iteration16](../reports/milp-iteration-16/REPORT.md) adds
an optional guard protecting first-feasible cut allocation. Both Binkar screen
runs now have independently checked points, but their gaps are worse than the
five-round controls. This repairs the experimental policy's feasibility trade-off,
not broad solver performance. A separate frozen15 diagnosis identifies the
mechanism of mas74's early unresolved exit and reproduces an LP numerical
failure that dense recovery solves accurately. That fixture is a concrete next
engineering target; it is not a fixed numerical bug or a completed mas74 solve.
See [next work](../reports/milp-iteration-16/NEXT_STEP.md). No GPU or user upload
is required for these CPU-only improvements.

The completed 24-case wave has the same counts under both profiles: 2 restricted
exact proofs, 8 numerical completions, 10 checked feasible limits, 1 unresolved
run with a valid point, 2 no-point limits and 1 cross-checked infeasible outcome.
All three guarded Binkar runs retain points but have worse gaps than controls.
The gate passes 14 CTest groups, 115 Python units, 320 generated regression runs
and 100 reused exhaustive MPS cases. These strengthen evidence discipline,
not the claim of broad solver dominance. All 24 models are development data.

Previous local update: [iteration15](../reports/milp-iteration-15/REPORT.md) adds
checked selective-cut decisions and tests 66 public outcomes on 24 distinct
models. This is stronger measurement/safety evidence, not a broad performance
breakthrough: Binkar loses its point in all four adaptive runs while all four
controls find one. Five rounds remain the default and the policy stays off.
The retained 21-case wave completes 10 under either profile, with baseline
9 additional checked feasible limits and 2 no-point limits; adaptive has 8
and 3. Three fresh cases add agreed numerical infeasibility, a feasible limit
and an unresolved-relaxation return with a valid point. The last is a real
remaining numerical/recovery weakness, not a completion. Four analytic min/max
integrations exercise an actual allocation stop without falsely certifying a
partial result. The gate passes 13 CTest groups, 100 Python units, 320 generated
regression runs and 100 reused exhaustive MPS cases. No GPU or user upload is
needed for this local iteration. First-feasible search, numerical recovery and
broader bound closure remain priorities; more passed tests are not a competition
percentile or a guarantee of solving every public model.

Previous local update: [iteration14](../reports/milp-iteration-14/REPORT.md) adds
work attribution and checked root cut-round controls. The matched 21-case 30s
wave completes 10 cases under the five-round baseline versus 9 under the
one-round candidate. Both include 2 restricted exact proofs. Baseline has 9
additional independently checked feasible limits and 2 no-point limits after
two separately retained validation retries; candidate has 10 and 2. No new
untouched models are tested here. These are configured experimental profiles,
not a claim about every default invocation or all public MILPs.

Three Binkar pairs improve median gap from 1.56% to 1.42%, but candidate loses
one pair and seriously weakens p0282. Five rounds remain the default. The full
gate passes 12 CTest groups, 88 Python units, exhaustive/partial model tests,
240 generated regression runs and 100 reused exhaustive cases. The saved audit
covers 59 public experiment runs and 51 final-point checks, including two linked
retries whose original watchdog failures are preserved. This strengthens
measurement and correctness evidence, but the candidate does not improve broad
completion. Large gaps, no-point outcomes, narrow GPU scope and missing real
industrial validation remain the main submission weaknesses.

Previous local update: [iteration13](../reports/milp-iteration-13/REPORT.md) adds
optional separation of search ordering from numerical proof-bound accounting,
plus independent queue/deferred/restart replay. All 24 fixed-node runs validate;
all 12 model/policy pairs repeat their semantic trace. The new 17-model timed
wave completes 7 cases in both policies, with mixed partial outcomes. It was
run on a shared, busy desktop and is not a controlled speed comparison against
earlier archives. This strengthens correctness evidence and test breadth, not
the claim that arbitrary public MILPs can be solved or proved. The feature
stays opt-in. See the report for repeated targets and predeclared holdouts.

The four new holdouts add no completion: two checked feasible limits and two
no-incumbent limits per policy. Across the combined 21-case timed selection,
each policy completes 7, has checked points with open gaps on 9, and has no
point on 5. This is a useful broadening of the evidence but a clear limitation
against the PS's consistent large-industrial-solve expectation.

Prior local update: [iteration12](../reports/milp-iteration-12/REPORT.md) adds
guarded, optional objective-lattice bounds. A matched 17-model 30s comparison
improves completion from 9 to 10 cases (2 restricted exact proofs and 8 numerical
completions), with mod008 newly closed. Seven remain unfinished, including
misc03, and gt2's short-budget incumbent regresses. The feature remains opt-in.
This is measurable progress in proof strength, not evidence of universal MILP
coverage, a top percentile or production readiness. General LP-bound validity
still relies on numerical checks, even when lattice algebra is checked exactly.

Prior safety/breadth update: [iteration11](../reports/milp-iteration-11/REPORT.md)
fixes a reproduced MPS integer-domain interpretation bug and passes all 28
independent domain tests. The 17-case public wave completes 2 restricted exact
proofs and 7 numerical solves at 30s each; 7 more return checked feasible
points with open gaps, and Blend2 returns no point under this short policy.
The same category counts hold before/after the parser correction, with no
validation failure in those public outputs. This is useful evidence but also
shows why broad MILP robustness is not yet established. Older readers retain
the documented marker-only-domain bug outside their checked examples.

The user's priority is now the [MILP robustness program](MILP_ROBUSTNESS.md):
broader cases, permanent regressions and proof-gap closure. Domain validation
and the submission demo remain necessary, but do not replace that work.

## What is genuinely strong

The deliverable is the optimization engine the PS asks for, not just a graphical
interface around an existing optimizer. The current CMake core implements its
own sparse simplex/LU, branch-and-cut/heuristics, convex-QP methods and CUDA
box-QP kernels. HiGHS/OSQP remain independent references. There are analytical,
generated, adversarial and selected public checks, original-model validation,
versioned inputs/binaries and reproducible failed experiments as well as wins.

Evidence-backed achievements include:

- [Markshare exact optimum 1](../reports/milp-iteration-07/REPORT.md), independently
  recomputed from original MPS literals in three runs. This uses a restricted
  small-binary integer-data engine, not a general exact MILP solver.
- [Blend2 numerical completion](../reports/milp-iteration-04/LOCAL_VALIDATION.md)
  at 7.598985 in the preserved iteration04 protocol, matching an independent
  optimum. Later strategies must be tested separately; this is not a promise
  that every mode or budget solves Blend2.
- [QPLIB 9002 numerical KKT/dual-gap checks](../reports/qp-iteration-01/REPORT.md)
  pass in about 4.2–4.8s locally. The original OSQP comparison still times out,
  and absolute constraint violation is about 2.381 despite small relative
  residuals. That limitation matters for operational interpretation.
- [P100 CUDA demonstration](../reports/KAGGLE_GPU_REPORT.md) through one million
  variables on a synthetic sparse convex box-QP family. The first return's
  5.62x CPU-one-thread/GPU observation is one pass on that family, not a
  general or repeated solver speedup. A [second snapshot](../reports/kaggle-gpu-02/REPORT.md)
  also passes CUDA checks; pooling different snapshots is not a controlled
  same-version repeatability study.
- Historical selected evidence includes 12 Netlib LPs, 4 historical MILPs and
  4 application examples. These counts belong to their recorded builds, not
  a new full-suite run of every latest candidate.

The completed [iteration10 report](../reports/milp-iteration-10/REPORT.md)
records three repeated root pairs: 2128 fewer rows, the same bound, median
6.70 to 2.47s. A fresh 180s full pair improves Binkar's reported gap from
0.9529% to 0.9132% at the same incumbent; it still times out. Blend2 reaches
7.598985 in 144.04s to its numerical gap tolerance while the matched control
times out at 8.015188. This is not faster than every older Blend2 protocol.
Independent checks pass for 49 retained cuts and 24 saved vectors. All four
application examples pass both new-build profiles against completed HiGHS
references; they remain literature/synthetic examples, not production data.
The method stays optional pending repeated, broader full-solve comparisons.

This is not only a convex-QP solver: LP and mixed-integer search are implemented
as well. The convex limitation concerns the continuous QP algorithms. General
nonconvex QP or MINLP support must not be inferred from having MILP support.

## Where we stand

| Area | Assessment | What prevents a stronger claim |
|---|---|---|
| Engineering depth and transparency | Substantial prototype | Provenance/build checks are not a third-party source audit |
| LP/MILP/convex-QP capability | Working selected scope | Broader hard-case robustness and completion remain uneven |
| Exact proof | Demonstrated restricted subset | Does not cover Binkar or arbitrary MILPs/rational data |
| GPU/scale | Real but narrow demonstration | Only synthetic box QP; repeated public GPU evidence missing |
| Industrial readiness | Not established | No MRPL production model or domain-expert operational validation |
| Submission defensibility | Credible technical foundation | Needs a bounded claim, final evidence freeze and clear live demonstration |

The PS asks for optimal OR near-optimal industrial solutions; proving every
public MILP is not a prerequisite for an honest submission. But a near-optimal
claim needs a checked feasible point and a defensible bound, not merely an
objective close to a published answer. Current general bounds are numerical.
Binkar's unresolved gap is one warning sign, not the whole readiness score.

## Highest-value remaining work before submission

1. Improve and repeat hard-MILP evidence at equal accuracy/budget; broaden the
   public subset and retain all timeouts. One tuned model is not generality.
2. Validate one convincing refinery/planning case with a domain expert or
   shareable MRPL-approved data, including units, constraints and decisions.
   Literature teaching cases are useful but not production validation.
3. For the final GPU snapshot, run repeated CPU/GPU comparisons on workloads
   where CUDA applies, with clear end-to-end timing and memory limitations.
   CPU work stays local; Kaggle is needed only for that actual GPU experiment.
4. Freeze a reproducible version and present the PS-to-evidence matrix, scope,
   limitations, benchmark comparisons and a short CLI/API demonstration.
   A polished GUI is not required by the supplied statement.

MIQP/NLP/MINLP are future extension classes in the supplied PS, not a reason
to dilute the current LP/MILP/QP validation with several untested new solvers.
Global nonconvex-QP expectations and permitted infrastructure still need
organizer clarification. No competition placement or completion percentage is
inferred from test counts.

## What is needed from the user

No new file or Kaggle run is needed for the present CPU iteration. The most
valuable external input is a shareable domain model or expert feedback, plus
organizer clarification of convex-QP scope and permitted execution libraries.
A future GPU notebook must remain separate and below 1 MB, with source/data
outside the notebook and one result ZIP, as already agreed.
