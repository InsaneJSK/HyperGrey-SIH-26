# SIH26119 — remaining objectives and iteration plan

Updated: 23 September 2026, merging the MILP search track (through iteration 37) with the continuous LP/QP track (through the weak-pivot safeguard of 17 September). Submission deadline: 30 September 2026.

Status: MILP iteration 33 changes what an open node costs, after the MIPLIB 2017 sweep showed 17 of the first 120 benchmark instances stopping on our own open-node memory guard, including a 7-row model and irp, which had the optimum to nine digits and was stopped before it could prove it. Queued nodes now share a trail of branching decisions instead of each storing complete bound vectors. A representation change must be invisible at fixed work and it is: 0 mismatches in 32 fixed-work comparisons against the previous build. Memory at a fixed node count falls 1.44x to 9.39x with column count; on development peak commit falls 762.8 to 183.9 MiB while nodes per second rise 19.8 percent, completions (24) and checked points (50) are unchanged, and there are zero validation failures in 74 checked records. Retained honestly: this bought headroom, not solving power, and nodes fell to 0.85x on the wide-column holdout because materialization walks the whole trail; capping total path entries is iteration 34 item 1, and re-running the 17 guard-stopped MIPLIB instances side by side at 300 s cuts guard stops from 16 to 1, explores 2.6x the nodes and improves checked incumbents on 10 against 1 (mas76 1.57% to 0.28% from the optimum), but proves nothing: 0 to 0. Earlier: iteration 32 added tableau Gomory cuts, gated by enumerating every integer point of 3,000 models, improving the root bound on 26 of 28 changed development observations and 4 of 4 unseen while leaving the 30-second gap a wash; iteration 31 added tree dives and fix-and-propagate; iteration 30 replaced the relaxation engine behind --bounded-lp. Three default QPs pass relative KKT checks; QPLIB 9002 still has about 2.381 absolute violation. On the continuous track, the opt-in `--stable-primal-ratio` safeguard resolves the retained standard-form bandm failure under its explicit profile: both stable-only and stable/refined profiles complete 16/16 checked LPs and the full gate passes, while default and refined bandm still fail and no broad MILP gain is claimed. The QP diagnosis identifies repeated short Newton steps and oscillating feasibility. Defaults are unchanged and overall submission readiness is not achieved. No submission occurred.

This file deliberately sits outside the source project and Kaggle delivery folders. Paths below are relative to this outer folder.

## 1. Main objective

Deliver a defensible, reproducible optimization engine for SIH26119: our own LP, MILP and currently supported convex-QP algorithms, with useful industrial examples, independently checked answers and GPU acceleration where measured evidence justifies it.

The immediate engineering priority is reliable MILP feasibility and completion. The submission also needs LP/QP coverage, numerical robustness, scalability, industrial relevance and a clear CLI/API demonstration. A polished GUI is not required by the supplied problem statement.

Keep the core developed from mathematical foundations. HiGHS/OSQP or another established solver may be independent references, not the optimization engine hidden behind our interface. Never inject their answers or bounds into our measured solves.

## Completed resumption checkpoint

- [Iteration25](../../04-software/solver/reports/milp-iteration-25/REPORT.md): stable ranking satisfies its narrow contract but loses measured useful-point reliability; keep off.
- [Iteration26](../../04-software/solver/reports/milp-iteration-26/REPORT.md): exact later LP replay establishes local infeasibility and phase-one cost; alternate reserve yields no new points; keep off.
- [Iteration27](../../04-software/solver/reports/milp-iteration-27/REPORT.md): tree retention helps mas74/mod008 but repeatedly weakens binkar bounds; retain existing restart policy.
- [Iteration28](../../04-software/solver/reports/milp-iteration-28/REPORT.md): all39 public/default records and37 final vectors validate. The24 artificial answers pass exact enumeration and explicit equivalent-reference checks after a retained duplicate-objective parser mismatch. Fifteen resource/status checks and a corrected isolated-folder smoke pass.

- [Iteration 29](../../04-software/solver/reports/milp-iteration-29/REPORT.md): guarded private dual certificates pass exact/interval and full correctness gates. Both screen profiles return 22/24 checked points and four completions; lotsize remains without an integer point. All 48 records and 44 vectors validate. Keep the option experimental and off; frozen 28 retains the prior broader 26/27 evaluation.
- [Current-source LP/QP validation](../../04-software/solver/reports/cpu-validation-2026-09-17/REPORT.md): 12 retained LPs pass both profiles, three of four additional LPs pass, and three default QPs pass the declared relative KKT contract. All failures and OSQP limits remain visible.
- [LP representation study](../../04-software/solver/reports/lp-bandm-01/REPORT.md): one consistent `--compact-equalities --refine-basis --refine-at-checks` profile completes all 16 LPs, including `bandm`; no numerical source change or default promotion.
- [MIPLIB 2017 benchmark, complete](../../04-software/solver/reports/miplib2017-benchmark/REPORT.md): all 240 instances at 300 s, full per-instance table with failures. 7 proven optimal and 1 proven infeasible, all matching MIPLIB; 69 validated feasible solutions; 0 rejected solutions; 0 answers disagreeing with MIPLIB; 170 with no solution. Failure causes: 31 memory-guard stops (fixed in iteration 33), 27 unresolved root LPs (fixed for most in iteration 34), 2 LU fill-budget exits reported as input errors. Run on the pre-iteration-33 engine; a re-run on the current engine is the next measurement.
- [Iteration 37](../../04-software/solver/reports/milp-iteration-37/REPORT.md): --gomory-cuts REMOVED from the recommended profile. A single-flag ablation over 60 MIPLIB 2017 instances at 300 s gives 2 proven and 19 validated solutions with the cuts against 3 and 21 without, 5.95M nodes against 7.75M, and 1,984 engine fallbacks against 305; decomp2 is proven at the root in one node without them and returns nothing with them. Both declared criteria failed. Iteration 32 promoted the flag on a bound criterion that did not measure what the shipped profile is for; its bound evidence stands, the default was wrong. The separator, its enumeration gate and its documentation remain, opt-in.
- [Iteration 36](../../04-software/solver/reports/milp-iteration-36/REPORT.md): a factorization limit is returned as a failed relaxation instead of aborting the solve, and separator rows are discarded so the node can be retried. neos8, one of the seven instances the benchmark proves optimal, went from exit 2 to proven optimal at -3719 (gap 0, 67 nodes, 91 cut rows discarded); buildingenergy and supportcase10 now report a status rather than exiting like rejected input. Development unchanged with the new path never firing; the eight largest unused benchmark instances identical to control. Zero validation failures. Promoted; defaults unchanged. Not addressed: the iteration 32 support cap allowing 5,000-nonzero cuts, the underlying cause.
- [Iteration 35](../../04-software/solver/reports/milp-iteration-35/REPORT.md): the basis is carried through the tableau-cut purge instead of being discarded, so the root's children warm start. On the six affected instances nodes rise 16 to 6,618 with cold starts 21 to 7, four of six reaching zero fallbacks and zero unresolved nodes; a fresh seven-instance set shows cold starts 37 to 8 and fallbacks 88 to 72 at unchanged throughput. One declared criterion was NOT met (unresolved nodes 6 to 7 in absolute count, 375 to 1.1 per thousand nodes) and is recorded as a deviation rather than restated. Promoted; defaults unchanged.
- [Iteration 34](../../04-software/solver/reports/milp-iteration-34/REPORT.md): the root LP gets a time budget instead of the 10,000-iteration cap meant for warm node LPs. Diagnosis of 12 root-stuck MIPLIB instances found every root stopped at exactly that cap with most of its time unused. At 300 s, paired: root solved on 8 of 12 diagnosed and 3 of 5 never-run instances (control 0 and 0); neos-827175 proven optimal at 112.00152, matching MIPLIB. Development unchanged (26 completions, 50 points), zero validation failures, zero rejected points. Exposed: the iteration 32 Gomory purge discards the basis so children cold start and hit the node cap; keeping the basis is iteration 35 item 1. Promoted; defaults unchanged.
- [Iteration 33](../../04-software/solver/reports/milp-iteration-33/REPORT.md): trail-based open nodes. Fixed-work equivalence 0 of 32 mismatches; memory at fixed node count 1.44x-9.39x lower; development peak commit 762.8 to 183.9 MiB with nodes per second up 19.8 percent; completions 24 to 24 and checked points 50 to 50; zero validation failures in 74 checked records across development and a 10-model untouched MIPLIB 2017 holdout declared before download. Retained: nodes fell to 0.85x on that wide-column holdout because materialization walks the whole trail. Added --open-node-memory-mib so the guard is testable. Promoted; defaults unchanged.
- [MIPLIB 2017 benchmark sweep, batch 3 of 4](../../04-software/solver/reports/kaggle-miplib2017-04/REPORT.md): cancelled after 44 of 60 instances (CANCEL_ACKNOWLEDGED, source not recorded); all 44 records recovered. One proven optimal and one proven infeasible, both agreeing with MIPLIB; 7 validated points; zero rejected points; zero wrong answers. Positions 164-179 remain unrun. Running total over 164 of 240: 6 proven optimal and 1 proven infeasible (all agreeing), 53 validated points, 0 rejected, 0 wrong answers, 23 guard stops on the old representation, 17 unresolved root LPs, 1 LU fill-budget exit.
- [MIPLIB 2017 benchmark sweep, batch 2 of 4](../../04-software/solver/reports/kaggle-miplib2017-03/REPORT.md): instances 60-119. Two proven optimal and both agree with the published value, 25 validated points, zero rejected points, zero disagreements, 35 with no point. Running total over 120 instances: 5 proven (5 of 5 agreeing), 46 validated points, 0 rejected, 0 wrong answers, 17 stopped by our own memory guard, 12 never past the root LP.
- [MIPLIB 2017 benchmark sweep, batch 1 of 4](../../04-software/solver/reports/kaggle-miplib2017-02/REPORT.md): the first run against a full public benchmark set. 60 instances at 300 s each on a Kaggle CPU session, reference optima from MIPLIB's own published solution file, every returned point checked by an independent HiGHS reader. Three proven optimal and all three agree with the published value; 21 validated feasible points; zero rejected points and zero objectives disagreeing with a published optimum; 39 with no point at all. Failures are the useful part: eight instances stop on our own open-node memory guard (including gen-ip054, a 27-row model whose frontier reached a gigabyte because each open node stores complete bound vectors), five never get past the root LP at 3,200-23,300 rows, and buildingenergy exits on the sparse LU fill budget as an error rather than as a limit status. No timing claim: two instances shared four cloud vCPUs.
- [Iteration 32](../../04-software/solver/reports/milp-iteration-32/REPORT.md): tableau Gomory mixed-integer cuts off the bounded simplex basis at the root. Validity gated by enumeration before any benchmark (2,706 cuts against 64,430 enumerated integer points; 400 mixed models where each cut is maximized over the continuous variables per assignment). Two development repeats and a 10-model untouched holdout declared before download: zero validation failures in 128 checked records, root bound better on 26 of 28 changed development observations and 4 of 4 unseen, peak commit 1139 to 763 MiB with the only memory-guard stop removed, separation 0.114 s per 54 records. Retained honestly: the 30-second gap is a wash (better 15, worse 13), the apparent extra completion is a HiGHS reference timing artifact on neos859080, and p0282 regresses because tableau cuts crowd out stronger cover cuts. Promoted on the declared bound criterion; defaults unchanged.
- [Iteration 31](../../04-software/solver/reports/milp-iteration-31/REPORT.md): periodic tree dives and fix-and-propagate, plus a propagation allocation fix (gt2: about 148,000 to about 390,000 nodes in 30 s at identical flags). Gate passes with 480 generated and 300 retained runs. Two development repeats and a 12-model untouched holdout declared before download: zero validation failures, nine development models with better checked incumbents, 10 unseen checked points against 8. Promoted with `--lifted-covers` replacing the three `--late-*` flags; defaults unchanged. Retained: lotsize/mitre/p2756 have no point, gt2 peaks at 1088 MiB without the restart, and p0282's bound weakens without it.
- [Iteration 30](../../04-software/solver/reports/milp-iteration-30/REPORT.md): independent bounded dual simplex for MILP relaxations and LPs, verified outcomes with fallback. Full gate plus 400 generated and 200 retained runs pass. Development completions 17 to 23, fresh untouched holdout 1 to 5 (15 models declared before download), iteration 28 holdout unchanged, LP 16/16, zero validation failures. The MPS reader now accepts free `N` rows, text after `ENDATA` and valued `BV`/`MI`/`PL`/`FR` bounds. Promoted as the recommended evaluation profile; executable defaults unchanged.
- [Numerical diagnosis](../../04-software/solver/reports/numerical-diagnosis-01/REPORT.md): exact captured row dependence proves the failed bandm basis singular. Refresh-only recovery fails later; full and selective stable-ratio candidates pass. QP 9002's tighter runs show short Newton steps and feasibility oscillation, not zero inner solves.
- [LP pivot safeguard](../../04-software/solver/reports/lp-pivot-iteration-01/REPORT.md): select the narrower opt-in rule. Both final 16-LP profiles pass, alongside 27 CTest groups, 176 Python tests, 400 generated MILPs, 100 exhaustive cases and four feature-off parity checks. Preserve the corrected QP applicability classification and initial records.

The [dual-certificate hypothesis](../../04-software/solver/docs/NEXT_PRIVATE_LP_HYPOTHESIS.md) has now been tested. The broader LP/QP/GPU/domain/delivery tracks remain open. See [the codebase review](../../04-software/solver/docs/CODEBASE_REVIEW_2026_09_17.md).

### Next bounded work, in order

1. Preserve the iteration 30 checkpoint and its input/source/binary identities. The fresh holdout becomes development data once any result influences tuning; obtain another holdout for fresh claims.
2. Stronger bounds (iteration 33): separate cover cuts before tableau cuts, or fall back to tableau cuts only when covers add nothing (p0282); then presolve strengthening (coefficient tightening, probing, dominated columns), reliability branching with cheap probes, and incremental propagation, since propagation is still the largest single phase on gt2.
3. First points for lotsize, mitre and p2756 (lock-based shift-and-propagate), the time-limit message fix, and a tighter open-node guard estimate. Then: Gomory mixed-integer cuts from bounded tableau rows and reliability branching with cheap probes; decide whether `--bounded-lp` and `--lp-method bounded` become executable defaults.
4. Larger LP/MILP instances (Mittelmann scale) and 9002's QP accuracy floor. Keep new-model scores separate from reused cases and compare external performance only at declared matched accuracy.
5. QP 9002: capture line-search objective increments, directional derivatives, Armijo allowance, PCG convergence and active-set changes. Test whether the allowance contributes to feasibility oscillation before combining any line-search, active-set or fallback change. The LP failure now has an opt-in safeguard; retain its limits and the earlier compact profile.
6. Add further supported LP/QP structures after resolving any correctness issue. Keep new-model scores separate from reused cases and compare external performance only at declared matched accuracy.
7. Diagnose lotsize's remaining fractional decisions, branch failures, 64-step cap and shared time slice under fixed work. Only then consider another shared-budget heuristic comparison; no guaranteed iteration count or integer solution is promised.
8. Prepare an independently checked industrial what-if and coherent CLI/API demonstration. Prepare a fresh CPU-validated package for supported box-QP GPU tests on Kaggle, with a notebook under 1,000,000 bytes. Actual GPU results, domain review and organizer deliverables/cutoff remain external inputs.

## 2. Starting point — preserve this evidence

Historical starting experiment for the completed iteration 25–28 plan: [iteration24 report](../../04-software/solver/reports/milp-iteration-24/REPORT.md). Its figures below are historical; the current checkpoint is above.

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

Iterations 25–28 were the four remaining slots in the earlier ten-slot planning budget and are complete. The following table preserves their original allocation. Iteration 29 followed the resulting evidence; future experiments remain bounded hypotheses, not guaranteed fixes.

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

These tracks remain necessary even if all 27 MILPs eventually have useful outcomes. Completed checks below apply to the recorded iteration 29 source; later numerical changes require appropriate revalidation.

### A. LP breadth and numerical robustness

- [x] Revalidate the current binary on all 12 retained LPs with default and refined profiles; both complete 12/12 with independent checks.
- [x] Add four preselected public LPs and retain the newly exposed `bandm` numerical failure. Default/refined each complete 15/16 overall; one explicit compact/refined profile completes 16/16.
- [x] Diagnose the failed bandm basis with an exact row-dependence witness. Validate an opt-in weak-pivot ratio safeguard on two complete 16-LP profiles; retain the failed refresh candidate and unchanged defaults.
- [ ] Add independent public LPs covering degeneracy, ill-conditioning, sparse size, equality-heavy and ranged/bounded formulations.
- [x] Check original-model primal feasibility, objective reconstruction, native verification and reference optima for the current 16-LP study; retain honest noncompletion statuses.
- [x] Iteration 30: an independent bounded dual simplex completes all 16 LPs with default flags (`--lp-method bounded`), including `bandm`, with HiGHS checks; the default sparse method still fails `bandm`.
- [ ] Compare cold/warm/scaled paths where supported and retain numerical failures as regression fixtures.
- [ ] Publish supported scale and observed memory honestly. A million-variable box QP does not establish million-variable LP or MILP support.

### B. QP scope, correctness and broader comparison

- [x] Re-run three retained public convex QPs on the current source, with independent original-model KKT/applicable gap checks; all three default results pass the declared relative contract.
- [ ] Expand beyond the existing three-public-QP subset; test supported sparse/Hessian/constraint structures and difficult scales.
- [x] Preserve QPLIB9002's original and new OSQP timeouts; the current independent KKT result is not a completed head-to-head reference comparison.
- [ ] Resolve or clearly explain relative versus absolute accuracy: the retained 9002 report has about 2.381 maximum absolute violation despite small relative residuals. Establish domain-appropriate tolerances before an operational claim.
- [x] Test separately declared 1e-10 and 1e-12 tolerance probes. Both time out and fail full independent checks despite lower absolute violation; neither is an improved accepted profile.
- [x] Trace the specialized-method exits and subsequent ADMM dispatch. Repeated short Newton steps and oscillating feasibility justify a focused line-search/active-set investigation; no QP algorithm fix has yet been made.
- [ ] If testing a scaled reference protocol, label it separately and verify the original unaltered model; do not substitute a lossy export.
- [ ] Clearly reject/report unsupported nonconvex cases rather than returning an unsupported global-optimality claim.

### C. Actual GPU evidence — Kaggle only for this track

- [x] Iteration 31 source, after its local correctness gate, was rebuilt with CUDA in the session itself (`reports/kaggle-gpu-03/`); no historical notebook was rerun.
- [x] Only the box-QP path was tested; no GPU MILP or general constrained-QP claim is made.
- [ ] Public box-QP evidence is still missing; only the planted synthetic family has repeated measurements.
- [x] Tesla T4 session, five sizes to one million variables, three repeats per backend at one accuracy contract: 45/45 pass, worst relative objective error 8.2e-14. Medians at one million: 15.92 s (1 thread), 8.34 s (4 threads), 3.50 s (GPU); the GPU is SLOWER below about 50,000 variables. End-to-end process timings include transfers and setup; warm-up is not separated.
- [ ] Resolve the prior solver-PID/VRAM attribution issue, or explicitly retain the distinction between whole-device samples and process memory.
- [ ] Keep a separate notebook under 1 MB; use less than 1,000,000 bytes as the save-size gate. Keep source/data in an external input ZIP, not embedded notebook content/outputs.
- [ ] Use standard Kaggle code/current Python environment, clear GPU checks, and one result/diagnostic ZIP. Installation or execution failures must also export useful logs.
- [x] Results were fetched through the Kaggle API and checked here: the planted optima were recomputed independently in Python and match. Binary-level source attestation inside the session is still not established.

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
- [x] Document CLI/API inputs, options, defaults, output schema, objective sense/offsets, limits, status meanings and error behavior: `docs/CLI_API.md`, written from the source and checked against live LP, MILP and QP runs of the frozen iteration 31 binary.
- [ ] Validate both default and selected submission profiles. Avoid requiring the demonstrator to guess among many experimental flags.
- [ ] Add/check timeout, cancellation, memory-limit and partial-result behavior with clean process shutdown; state remaining cooperative-limit limitations.
- [ ] Verify safe input handling, logs, deterministic fixed-work checks and fresh-directory reproduction. Do not overwrite evidence during packaging.
- [ ] Test the final package from a clean environment and verify artifact hashes. Revalidate if numerical source changes after the freeze.

### F. Submission material and demo

- [ ] Finish a problem-statement-to-evidence matrix covering own core, LP/MILP/QP, sparse numerical robustness, supported parallel/GPU paths, benchmarks and industrial examples.
- [ ] Prepare an architecture/algorithm explanation showing our implementation and the strict separation from reference solvers.
- [x] Prepare complete benchmark tables with failures, limits, gaps, accuracy, hardware, budgets and reproducible commands—not only wins: `SIH-backup-solver/reports/miplib2017-benchmark/` (all 240 MIPLIB 2017 benchmark instances, every failure listed, independent checking, budget and machine stated). Timing is not claimed from that run.
- [x] Provide a short CLI/API demo: load a model, solve it, inspect/check the answer, show an industrial what-if, and show an honest incomplete/unsupported case — `scripts/demo_cli.py`, `docs/DEMO.md`, output in `reports/demo-2026-09-18/`. Refinery LP, a tightened sulfur specification with a sensitivity sweep, a proven MILP, a `time_limit` on mas74 and an exit-2 rejection, every answer rechecked by an independent HiGHS process. The refinery case is a teaching model, not operating data.
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

- [Supplied problem statement](../../04-software/solver/Problem%20Statement.txt)
- [Latest LP safeguard and final-binary checks](../../04-software/solver/reports/lp-pivot-iteration-01/REPORT.md)
- [Exact LP diagnosis and QP trace](../../04-software/solver/reports/numerical-diagnosis-01/REPORT.md)
- [Iteration 29 decision and evidence](../../04-software/solver/reports/milp-iteration-29/REPORT.md)
- [Current LP/QP results and limits](../../04-software/solver/reports/cpu-validation-2026-09-17/REPORT.md)
- [Explicit 16-LP profile and retained default failure](../../04-software/solver/reports/lp-bandm-01/REPORT.md)
- [Earlier broader MILP evaluation](../../04-software/solver/reports/milp-iteration-28/REPORT.md)
- [Iteration24 report](../../04-software/solver/reports/milp-iteration-24/REPORT.md)
- [Complete 27-model ledger](../../04-software/solver/reports/milp-iteration-24/MODEL_LEDGER.md)
- [Iteration24 next-step diagnosis](../../04-software/solver/reports/milp-iteration-24/NEXT_STEP.md)
- [Frozen artifact/evidence identities](../../04-software/solver/reports/milp-iteration-24/FINAL_STATE.json)
- [Submission assessment](../../04-software/solver/docs/SUBMISSION_ASSESSMENT.md)
- [Broader remaining work](../../04-software/solver/docs/V2_REMAINING.md)
- [QP iteration01 evidence and limitations](../../04-software/solver/reports/qp-iteration-01/REPORT.md)
- [Execution policy](../../04-software/solver/docs/EXECUTION_POLICY.md)

When the user resumes: read the current checkpoint, LP pivot safeguard report and next-step file, and the numerical diagnosis. Keep iteration 29 and the broader frozen 28 MILP decision separate from the latest LP-only profile score. Continue bounded numerical and delivery work in fresh evidence directories; do not restart completed iterations or treat historical best scores as current defaults. This plan alone does not schedule background work, uploads or external messages.
