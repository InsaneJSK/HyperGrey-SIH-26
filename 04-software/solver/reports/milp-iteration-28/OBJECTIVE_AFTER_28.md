# SIH26119 — remaining objectives and iteration plan

Updated: 17 September 2026, after MILP iterations25–28. Submission deadline: 30 September 2026.

Status: The four planned CPU MILP iterations25–28 have been executed and reviewed. Ranking, alternate reserve and deferred restart were rejected for promotion. Iteration28 retains an experimental staged evaluation profile:26/27 useful development outcomes, ten optimization completions, six checked untouched-model points with no completions. Defaults are unchanged; overall submission readiness is not achieved. No GPU run, upload, external message or submission occurred.

This file deliberately sits outside the source project and Kaggle delivery folders. Paths below are relative to this outer folder.

## 1. Main objective

Deliver a defensible, reproducible optimization engine for SIH26119: our own LP, MILP and currently supported convex-QP algorithms, with useful industrial examples, independently checked answers and GPU acceleration where measured evidence justifies it.

The immediate engineering priority is reliable MILP feasibility and completion. The submission also needs LP/QP coverage, numerical robustness, scalability, industrial relevance and a clear CLI/API demonstration. A polished GUI is not required by the supplied problem statement.

Keep the core developed from mathematical foundations. HiGHS/OSQP or another established solver may be independent references, not the optimization engine hidden behind our interface. Never inject their answers or bounds into our measured solves.

## Completed resumption checkpoint

- [Iteration25](SIH-backup-solver/reports/milp-iteration-25/REPORT.md): stable ranking satisfies its narrow contract but loses measured useful-point reliability; keep off.
- [Iteration26](SIH-backup-solver/reports/milp-iteration-26/REPORT.md): exact later LP replay establishes local infeasibility and phase-one cost; alternate reserve yields no new points; keep off.
- [Iteration27](SIH-backup-solver/reports/milp-iteration-27/REPORT.md): tree retention helps mas74/mod008 but repeatedly weakens binkar bounds; retain existing restart policy.
- [Iteration28](SIH-backup-solver/reports/milp-iteration-28/REPORT.md): all39 public/default records and37 final vectors validate. The24 artificial answers pass exact enumeration and explicit equivalent-reference checks after a retained duplicate-objective parser mismatch. Fifteen resource/status checks and a corrected isolated-folder smoke pass.

The next proposed numerical investigation is [verified local dual infeasibility before cold phase one](SIH-backup-solver/docs/NEXT_PRIVATE_LP_HYPOTHESIS.md). It is not implemented, assigned a guaranteed new iteration count or a promised MILP gain. The broader LP/QP/GPU/domain/delivery tracks below remain open. See [the codebase review](SIH-backup-solver/docs/CODEBASE_REVIEW_2026_09_17.md).

## 2. Starting point — preserve this evidence

Latest frozen experiment: [iteration24 report](SIH-backup-solver/reports/milp-iteration-24/REPORT.md).

- The experimental staged profile returns 25 checked feasible solutions plus one cross-checked infeasible model in the 27-model, 30-second wave: 26/27 useful outcomes.
- Ten models complete: two restricted exact proofs and eight numerical/tolerance completions. Fifteen feasible models still have open optimality gaps.
- `lotsize` remains without an integer solution within that budget.
- `misc07` gains a checked solution in all three candidate observations, but still has a large gap and near-tie branch sensitivity.
- `danoint` succeeds in the wave but fails both staged screen runs. Its first-feasible reliability is not established.
- `binkar10_1` loses some wave solution quality; `mas74` has not recovered the better objective from an older profile.
- All 98 public comparison records, 84 final solution vectors and 48 private-LP replay points pass validation. The gate includes 24 CTest groups, 176 Python tests, 320 generated runs and 100 retained exhaustive cases.
- The stage remains experimental and off by default. The 26/27 figure belongs to its recorded profile, not every default invocation.
- All 27 models are reused development cases, not fresh holdouts or every public MILP.

Preserve the frozen executable, source snapshot, raw results and failures. Starting from a new iteration must not overwrite earlier evidence.

## 3. What “done” means

Keep these goals separate:

1. **Correct handling:** parse supported input correctly; return a checked answer or an honest unsupported/error/limit status; do not crash or publish a false proof.
2. **Useful coverage:** return a checked feasible point or an independently corroborated terminal result within the declared budget. An infeasible model does not need a feasible point.
3. **Completion:** close the optimality gap to the declared numerical tolerance, or substantiate the appropriate terminal status. A feasible point alone is not completion.
4. **Robustness:** repeat the result across declared runs, transformations and new models without unacceptable correctness, coverage or quality regressions.
5. **Submission readiness:** demonstrate the required scope from a clean, reproducible package, with evidence-backed claims and explicit limitations.

The aspiration is reliable useful coverage on all 27, followed by broader completion and unseen-model coverage. There is no defensible promise that four iterations will prove all models, solve arbitrary MILPs within finite budgets, or achieve a competition percentile.

## 4. Remaining MILP iteration map

Iterations25–28 are the four remaining slots in the earlier ten-slot planning budget. The following allocation is a proposed roadmap, not four guaranteed fixes. Refine later hypotheses using earlier results, and declare each experiment before timing it.

| Iteration | Main objective | Required outcome/artifact |
|---|---|---|
| 25 | Stabilize near-tied private-dive branch choices | Tested generic ranking rule, fixed-work diagnostics, repeated paired results and an explicit accept/reject decision |
| 26 | Tackle `lotsize`'s later dive bottleneck and diagnose first-feasible reliability | Exact failed/expensive private-LP fixtures, one bounded budget/alternate experiment, checked solutions or a precise retained failure diagnosis |
| 27 | Improve completion and solution quality, not just first feasibility | One evidence-selected bound/search change, repeated gap/completion measurements, original-model checks and a complete regression ledger |
| 28 | Test generalization and choose a release-candidate profile | Untouched holdout results, full development-suite recheck, resource/status tests, configuration decision and frozen candidate |

If a gate fails, retain or revert to the safer configuration; do not silently call the iteration successful. Additional focused cycles may be needed. Do not invent a guaranteed iteration29+ count before seeing the evidence.

## 5. Iteration25 — stabilize private-dive choices

### Objective and reason

Make near-tied branch selection less sensitive to insignificant floating-point differences. In iteration24, `misc07`'s integer-coordinate changes of at most about 7.36e-16 changed the first branch from column218 to column12. Both points had the same aggregate integer distance, yet the search trajectories differed substantially.

### Work to do

- [x] Read the retained `TRACE_DIAGNOSIS.json` and actual source path; reproduce the ranking difference without substituting a reference solution.
- [x] Specify a generic deterministic rule for near-equal fractionality scores in the PRIVATE dive. No model-name or column-number special case.
- [x] Distinguish ranking tolerance from acceptance tolerance. Do not relax feasibility, integrality, LP verification or proof checks.
- [x] Test strict-original, staged and proposed ranking paths diagnostically before choosing the measured control/candidate pair.
- [x] Test ties, just-outside-tie cases, small perturbations, negative/translated integer domains, MIN/MAX, variable permutations, empty domains and nonfinite inputs at the appropriate validation boundary.
- [x] Verify failed-primary/alternate ownership, disabled-option parity, zero budgets and exhausted budgets. No unverified basis may advance.
- [x] Declare a focused screen covering `misc07`, `lotsize`, `danoint`, `blend2`, `eil33-2`, `rout`, `p0201`, `mod008`, `mas74`, `binkar10_1`, `gt2` and `pk1`; keep screening economical and expand only for a stated reason.
- [x] Run the correctness gate before timed comparisons. If the candidate merits broader testing, run all 27 with unchanged source/settings and equal budgets.

### Completion/promotion gate

The ranking behavior must satisfy its defined stability contract, all correctness checks must pass, and measured gains/losses must be reported. Preserve `misc07`'s useful result and check the existing feasibility/completion paths explicitly. A feature is not promoted merely because it stabilizes one reused fixture.

If stability improves but broad search worsens, keep the finding and reject default promotion. Record the reason and the next hypothesis instead of accumulating another unexplained flag.

## 6. Iteration26 — remaining feasibility bottleneck

### Objective and reason

Obtain reliable first-feasible progress on `lotsize`, while understanding `danoint`'s inconsistent first-feasible outcome. Staging already reduces the saved `lotsize` parent/first-child LPs from 2670 cold pivots to one/four warm pivots, but later work still consumes the dive slice without an integer solution.

### Work to do

- [x] Capture the exact next expensive or unsuccessful private LP, including current bounds, target objective, auxiliaries, input basis and remaining budget.
- [x] Classify the obstruction: genuinely infeasible local branch, numerical failure, incompatible basis/cold fallback, unhelpful integer choices, step cap or time exhaustion.
- [x] Replay the retained model independently outside timed MILP runs. Keep diagnostic budgets separate; never feed replay answers into the solver.
- [x] If evidence supports it, test reserving some of the SAME dive slice for an alternate when a primary needs expensive fallback. Do not grant a second full slice.
- [x] Preserve parent state after interruption/failure. Local infeasibility must never become global infeasibility or a pruning certificate.
- [x] Separately inspect `danoint`'s pump/fixing/dive timing and trajectory. Identify whether its missed point happens before staging; do not assume staging caused every difference.
- [x] Repeat first-feasible tests and compare time-to-first-point, point validity, final objective, gap and total work. Retain every failed run.
- [x] Decide whether to expand before promotion: not triggered for reserve, because the focused screen found no coverage gain. The retained staged profile receives the full27 recheck in28.

### Completion/promotion gate

Desired gain: repeated independently checked `lotsize` solutions and more reliable `danoint` behavior without lost existing coverage or extra hidden time. If that is not achieved, deliver the exact failure fixtures and reject the ineffective policy. A smaller fractional distance or faster private LP is not a completed MILP objective.

If the diagnosis instead identifies a numerical defect, fix and validate that defect before spending the slot on a budget policy. Do not combine several unmeasured changes and attribute the result to one of them.

## 7. Iteration27 — close gaps and protect solution quality

### Objective

Increase numerical completion or materially improve independently checked solution/bound quality under fair budgets. Finding an incumbent and proving its quality are different tasks.

### Work to do

- [x] Inspect incumbent and bound progress, root relaxation, cuts, tree work, restarts, recovery and deferred/unresolved nodes.
- [x] Choose ONE general mechanism justified by that evidence: for example a bounded cut-selection change, stronger supported relaxation, node/restart policy, or checked incumbent-improvement method. These are choices, not a requirement to implement all of them.
- [x] Test cut/bound validity and frontier accounting independently before measuring any speed or gap gain.
- [x] Protect all existing completions, especially `p0201` and `mod008`, and both restricted exact-proof cases.
- [x] Address `binkar10_1`/`mas74` quality losses explicitly. Keep historical better objectives labeled with their actual versions and budgets.
- [x] Run repeated equal-budget comparisons. If a longer practical budget is added, use a separate predeclared experiment, not a replacement for failed short runs.
- [x] Report every model's objective, bound, gap, status, first-feasible time and resource/work data. Check accepted incumbents on the original model.

### Current open-gap ledger

These are the 15 feasible-but-incomplete models in the iteration24 staged wave, not claims about their outcomes under every budget:

| Group | Models | Main purpose of follow-up |
|---|---|---|
| Large gaps | `pk1`, `gt2`, `misc07` | Diagnose weak bounds versus poor incumbents; do not call their current points near-optimal |
| Significant gaps | `eil33-2`, `rout`, `mas74`, `blend2`, `assign1-5-8`, `danoint` | Improve useful integer decisions and bound progress; retain feasibility reliability |
| Smaller but still open gaps | `mas76`, `p0282`, `misc03`, `gen-ip002`, `gen-ip054`, `binkar10_1` | Target measurable closure without assuming these are easy to finish |

### Completion/promotion gate

Require correct bounds/cuts, repeated measurable improvement, and an explicit account of any regressions. Do not trade away existing completions without a documented, justified release decision. A smaller reported gap is meaningful only with a valid incumbent and defensible bound.

## 8. Iteration28 — unseen cases, robustness and profile decision

### Objective

Determine whether the retained improvements generalize and select a coherent, reproducible release-candidate configuration. This is not a license to claim universal MILP coverage.

### Work to do

- [x] Select six untouched public holdouts before outcomes, plus separately labeled artificial weak-relaxation, duplicate/near-parallel-row and scaling stress. This small related set does not establish broad ill-conditioned industrial coverage.
- [x] Separate development and holdout scores. Once holdout results influence tuning, those cases become development data; obtain another holdout for a fresh claim.
- [x] Re-run all 27 development cases and the broader correctness tests on the exact candidate binary.
- [x] Test supported MIN/MAX, offsets, row senses, free/fixed/negative/general-integer bounds, empty integer domains, duplicates, scaling and malformed input.
- [x] Exercise infeasible, unbounded, time/node/iteration-limit, interrupted, numerical-error and unsupported outcomes. Never publish a false success or infeasibility claim.
- [x] Exercise memory/time pressure with bounded tests. Identify whether limits are hard or cooperative; implement/check process containment in the release wrapper where needed.
- [ ] Matched-accuracy external performance study remains pending. Iteration28 uses separately labeled five-second validation and thirty-second stricter references; no fair speed ranking is claimed.
- [x] Choose one documented configuration for the demo/release. Preserve experimental profiles and rejection reasons. Do not report a best-of-profile union as one solve.
- [x] Freeze source, executable, configuration, dataset hashes, dependency versions, raw results, checks and limitations.

### Completion/promotion gate

No unexplained validation failure; no hidden timeout or missing model; independently checked returned points/statuses; a clear supported-input contract; and a defensible configuration decision. If a holdout reveals a serious defect, retain the failure and use a focused corrective cycle before release. Iteration28 is not an automatic “all done” milestone.

## 9. Other submission work — not covered by four MILP slots

These tracks remain necessary even if all 27 MILPs eventually have useful outcomes. They may be scheduled alongside or after the MILP work when development resumes; they are not running now.

### A. LP breadth and numerical robustness

- [ ] Revalidate the final binary on the retained LP suite; older 12-model Netlib results are evidence for their recorded builds, not a fresh final-version score.
- [ ] Add independent public LPs covering degeneracy, ill-conditioning, sparse size, equality-heavy and ranged/bounded formulations.
- [ ] Check primal feasibility, objective reconstruction, dual/bound behavior and terminal statuses against original coefficients.
- [ ] Compare cold/warm/scaled paths where supported and retain numerical failures as regression fixtures.
- [ ] Publish supported scale and observed memory honestly. A million-variable box QP does not establish million-variable LP or MILP support.

### B. QP scope, correctness and broader comparison

- [ ] Re-run current convex-QP methods and independent original-model KKT/gap checks on the final source snapshot.
- [ ] Expand beyond the existing three-public-QP subset; test supported sparse/Hessian/constraint structures and difficult scales.
- [ ] Preserve QPLIB9002's original OSQP timeout. Its existing independent KKT result is not a completed head-to-head reference comparison.
- [ ] Resolve or clearly explain relative versus absolute accuracy: the retained 9002 report has about 2.381 maximum absolute violation despite small relative residuals. Establish domain-appropriate tolerances before an operational claim.
- [ ] If testing a scaled reference protocol, label it separately and verify the original unaltered model; do not substitute a lossy export.
- [ ] Clearly reject/report unsupported nonconvex cases rather than returning an unsupported global-optimality claim.

### C. Actual GPU evidence — Kaggle only for this track

- [ ] Select and CPU-validate the exact snapshot to test. Do not rerun an unchanged historical notebook just to create another result ZIP.
- [ ] Test only CUDA-supported workloads; current acceleration is the box-QP path, not a GPU MILP solver or general constrained-QP GPU claim.
- [ ] Add applicable public box-QP evidence and repeated synthetic scale measurements. State what each family demonstrates and what it does not.
- [ ] Compare CPU one-thread, supported multicore and GPU at equal accuracy. Record hardware, warm-up, repeats, variation, transfers/setup and end-to-end timing.
- [ ] Resolve the prior solver-PID/VRAM attribution issue, or explicitly retain the distinction between whole-device samples and process memory.
- [ ] Keep a separate notebook under 1 MB; use less than 1,000,000 bytes as the save-size gate. Keep source/data in an external input ZIP, not embedded notebook content/outputs.
- [ ] Use standard Kaggle code/current Python environment, clear GPU checks, and one result/diagnostic ZIP. Installation or execution failures must also export useful logs.
- [ ] After the user returns the GPU ZIP, verify its source identity and results before adding any GPU claim.

All CPU-only development, LP/MILP testing and CPU-QP testing stay local. Do not use Kaggle merely for Linux or longer CPU runs without a newly discussed need.

### D. Industrial relevance and domain validation

- [ ] Retain the existing literature/synthetic refinery, transportation and production-planning examples, with provenance and assumptions.
- [ ] Obtain a shareable MRPL-approved/domain model or expert review if available. Do not label a teaching example as production data.
- [ ] Validate units, capacities, balances, demands, integrality, objective meaning and the actual decisions an operator would use.
- [ ] Demonstrate a realistic what-if change, recompute the plan and independently check the changed model's answer.
- [ ] Explain infeasible scenarios or limits honestly; do not fabricate feasibility explanations or operational approval.

### E. Integration, resources and reproducibility

- [ ] Provide a clean build/run path, dependency inventory, provenance/license notes and supported-platform instructions.
- [ ] Audit that the numerical core is not calling an existing solver library; keep reference dependencies clearly separated.
- [ ] Document CLI/API inputs, options, defaults, output schema, objective sense/offsets, limits, status meanings and error behavior.
- [ ] Validate both default and selected submission profiles. Avoid requiring the demonstrator to guess among many experimental flags.
- [ ] Add/check timeout, cancellation, memory-limit and partial-result behavior with clean process shutdown; state remaining cooperative-limit limitations.
- [ ] Verify safe input handling, logs, deterministic fixed-work checks and fresh-directory reproduction. Do not overwrite evidence during packaging.
- [ ] Test the final package from a clean environment and verify artifact hashes. Revalidate if numerical source changes after the freeze.

### F. Submission material and demo

- [ ] Finish a problem-statement-to-evidence matrix covering own core, LP/MILP/QP, sparse numerical robustness, supported parallel/GPU paths, benchmarks and industrial examples.
- [ ] Prepare an architecture/algorithm explanation showing our implementation and the strict separation from reference solvers.
- [ ] Prepare complete benchmark tables with failures, limits, gaps, accuracy, hardware, budgets and reproducible commands—not only wins.
- [ ] Provide a short CLI/API demo: load a model, solve it, inspect/check the answer, show an industrial what-if, and show an honest incomplete/unsupported case.
- [ ] Show GPU execution separately and only for a validated supported workload. Do not imply the MILP demo ran on the GPU.
- [ ] Prepare slides/write-up, concise README, limitations, demo script and a saved fallback recording/output in case live infrastructure fails.
- [ ] Rehearse from a fresh directory on the exact frozen package. Keep a final checklist for files required by the submission portal.

## 10. Solver classes: what is and is not remaining core scope

- LP and MILP already exist; the current project is not only a convex optimizer.
- The convex limitation applies to current continuous-QP support. Global nonconvex QP must not be implied.
- MIQP, NLP and MINLP are future extension classes in the supplied problem statement. Document extension boundaries, but do not count them as implemented or automatically add several untested engines before the deadline.
- Obtain organizer clarification on expected QP/nonconvex scope and permitted numerical/GPU infrastructure. If requirements change, explicitly replan resources and acceptance tests.
- Do not treat adding every named algorithm—interior point, every cut family, every nonlinear solver—as mandatory completion. Prioritize demonstrated capability and the actual supplied requirements.

## 11. Rules for every resumed iteration

- [ ] State the hypothesis, control, candidate, model set, accuracy, resource budget, repetitions and promotion criteria before measurements.
- [ ] Use saved failures to guide development, but no instance-name rules, imported reference points/bounds or hidden model-specific answers.
- [ ] Run focused tests and the correctness gate first; verify feature-off behavior and failure/resource paths.
- [ ] Start with the smallest useful screen. If it fails the declared gate, preserve the failure and avoid an unnecessary large timing batch. Correctness tests do not replace broad validation of a candidate intended for release.
- [ ] Keep timed own configurations serial and source/settings fixed. Run references afterward. Record environmental/load limitations.
- [ ] Validate original-model solutions, integrality, objectives, bounds/proof claims and status handling. Keep numerical completion distinct from exact proof.
- [ ] Save every result, including regressions, watchdog failures and no-point limits. A retry must not erase the original attempt.
- [ ] Report feasibility count, completion count, quality/gaps, time-to-first-point and resource use separately. No historical best-of-runs union or timeout-derived finite speedup claim.
- [ ] Write an accept/reject decision, freeze identities and leave a precise next objective. Keep an experimental feature off when evidence does not justify promotion.

## 12. User/team inputs still needed

- [ ] Organizer clarification of QP/nonconvex and infrastructure scope, if obtainable.
- [ ] Shareable industrial data or domain-expert feedback, with permission to use it in the submission.
- [ ] An NVIDIA Kaggle run and its output ZIP only when a validated GPU experiment is ready; no CPU-only upload is pending.
- [ ] Final submission format, required files, team details and exact portal cutoff/time zone if not already known.
- [ ] Approval of any material scope expansion or external coordination. This document itself authorizes no messages, uploads or submissions.

## 13. Deadline and completion checklist

Reserve the final two days before 30 September for package checks, rehearsal and submission contingencies. A proposed engineering freeze is 28 September, subject to the actual portal cutoff. Do not consume that reserve chasing one extra benchmark result without an explicit trade-off decision.

- [ ] No known unresolved correctness defect in the advertised scope; unsupported/limited outcomes are explicit.
- [ ] One frozen, documented candidate reproduces its stated results; all unresolved cases and scope limits are visible.
- [ ] The 27-model ledger is current, repeated reliability is reported, and untouched holdout evidence is separately identified.
- [ ] Final LP and convex-QP evidence is checked, not inferred from older builds or only from MILP tests.
- [ ] GPU claims have matching final-snapshot evidence, or are limited to clearly identified historical evidence.
- [ ] At least one convincing, accurately labeled industrial demonstration is ready, with its validation status stated.
- [ ] Equal-accuracy benchmark comparisons, original-model validation, resource limitations and failure cases are included.
- [ ] Clean build, CLI/API demo, report/slides and fallback artifacts have been rehearsed.
- [ ] Source/dependency provenance and reference-solver separation are documented.
- [ ] Remaining backlog is explicitly accepted as a limitation or assigned a further targeted cycle—not silently marked complete.

Strong submission target: a reliable, transparent engine with repeatable evidence and a useful domain demonstration. Not a promise to replace every industrial solver, prove every public MILP or finish in a particular competition percentile.

## 14. Evidence and resume pointers

- [Supplied problem statement](SIH-backup-solver/Problem%20Statement.txt)
- [Iteration24 report](SIH-backup-solver/reports/milp-iteration-24/REPORT.md)
- [Complete 27-model ledger](SIH-backup-solver/reports/milp-iteration-24/MODEL_LEDGER.md)
- [Iteration24 next-step diagnosis](SIH-backup-solver/reports/milp-iteration-24/NEXT_STEP.md)
- [Frozen artifact/evidence identities](SIH-backup-solver/reports/milp-iteration-24/FINAL_STATE.json)
- [Submission assessment](SIH-backup-solver/docs/SUBMISSION_ASSESSMENT.md)
- [Broader remaining work](SIH-backup-solver/docs/V2_REMAINING.md)
- [QP iteration01 evidence and limitations](SIH-backup-solver/reports/qp-iteration-01/REPORT.md)
- [Execution policy](SIH-backup-solver/docs/EXECUTION_POLICY.md)

When the user resumes: read this file and the frozen iteration24 report, confirm the intended objective, then start iteration25 in a new directory. Do not resume benchmarks merely because this plan exists.
