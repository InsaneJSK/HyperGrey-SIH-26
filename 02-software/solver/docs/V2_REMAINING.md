# What is needed before final V2 submission

Updated user priority: [broad public-MILP robustness](MILP_ROBUSTNESS.md),
including proof-gap closure and correct handling of unfamiliar inputs. The
first 17-model wave and a reproduced marker-default parser correction are
tracked in [iteration11](../reports/milp-iteration-11/REPORT.md). Every unfinished
case remains on the ledger. Fix correctness first, then improve bounds/search
across predeclared cases and holdouts. Industrial/demo work remains necessary
for submission but is not a substitute for this solver-development target.

Latest experiment: [iteration24](../reports/milp-iteration-24/REPORT.md) reaches
25 checked solutions plus one cross-checked infeasible case in the wave, with
ten completions. Lotsize remains no-point; fifteen feasible gaps remain open.
Misc07's first-feasible gain repeats three times, but near-tie sensitivity and
danoint's two staged screen failures prevent calling this reliable 26/27 breadth.
Keep the new stage optional. All 98 public records and 48 private replay points
pass checks; no user upload is needed.

Next isolate a generic, deterministic near-tie rule for private-dive ranking,
without changing feasibility/proof tolerances. Preserve the later expensive
lotsize branch for a separate same-budget alternate/fallback experiment.
Protect danoint, Binkar/mas74 quality, blend2, eil33-2/rout and p0201/mod008
completion. Four planning slots remain, not four guaranteed steps to 27/27.
Unseen cases, domain validation, hard resource containment and submission/demo
packaging remain, alongside GPU-specific evidence when an actual GPU test is due.

Previous experiment: [iteration23](../reports/milp-iteration-23/REPORT.md) tests
guarded basis handoff without increasing coverage: 24 checked solutions plus
one corroborated infeasible case in both profiles, with misc07/lotsize still
unresolved. Candidate has nine completions versus ten controls; mod008 is the
lost completion, although no private handoff LP executes there. Keep the new
option off by default. Next test separating target changes from bound changes
inside the existing dive budget; saved lotsize diagnostics establish a
neither-feasible basis rejection. Protect mod008 completion, mas74 quality and
the earlier feasibility gains. Five planning slots remain, not a guarantee.
All 94 records and 30 independent replay-point checks pass. No GPU upload needed.

Previous experiment: [iteration22](../reports/milp-iteration-22/REPORT.md) raises
the wave to 24 checked solutions plus one cross-checked infeasible model, with
ten completions. Misc07/lotsize remain no-point limits, and fourteen feasible
models have open gaps. Danoint/rout gains repeat; mas74's worse objective means
the new pump reoptimizer stays optional. Next test exact-structure-compatible
basis reuse at the first private distance LP, without extra time or proof-state
leakage. Protect mas74 quality as well as the gained points. Six planning slots
remained then, not a guaranteed number to 27/27. All CPU testing remains local.

Previous experiment: [iteration21](../reports/milp-iteration-21/REPORT.md) gains
checked eil33-2/rout points in three paired observations but loses misc07 in the
wave. Candidate 23 solutions / 10 completions plus one cross-checked infeasible
model is not 27/27 handling; misc07/lotsize/danoint remain no-point limits.
Keep private distance diving optional. The next bounded mechanism is reducing
private LP cold/reoptimization work while protecting existing feasible paths,
not silently adding time or combining best outcomes across runs.

The final presolve-off domain guard passes separate regression/parity/MAX-MIN
checks; measured and patched binaries are explicitly separated. See the
[three-iteration checkpoint](../reports/milp-iteration-21/NEXT_STEP.md): seven
planned slots remain, but no fixed count guarantees all models or proof gaps.
Real refinery validation, deployment hardening and GPU-specific evidence remain
separate submission requirements. No CPU-only Kaggle upload is needed.

Prior experiment: [iteration20](../reports/milp-iteration-20/REPORT.md) tests
pump-guided diving without changing the existing time/proof envelope. The
repeated screen does not improve first feasibility on the three target models.
The missing work is useful integer fixing/generation and efficient LP work,
not merely saving a fractional point. Keep the option off by default, preserve
iteration19's repair, and use the full wave/report for remaining coverage and
gap work. Passing more tests is not equivalent to proving more public models.

Prior status: [iteration19](../reports/milp-iteration-19/REPORT.md) implements
bounded repair for rejected near-integer dive candidates. It follows a retained
blend2 rejection whose exact integer fixing can be solved accurately by our
dense LP method. This recovers a checked point, not a proof for the original
node or full MILP. Sparse/dense work shares the existing repair allowance and
current dive slice. The feature is optional; tolerances and proof logic remain
unchanged. The gate passes 19 CTest groups, 140 Python tests, 320 generated runs
and 100 retained exhaustive cases. The wave has 23 checked points, only 9
optimality/tolerance completions, and one cross-checked infeasible model.
Lotsize, eil33-2 and danoint still have no point in the repair wave. Rout remains
unreliable across runs; its latest point required zero repairs. Generating useful
integer assignments and closing the other 14 incumbent gaps remain separate
work. See the full paired evidence and
[next steps](../reports/milp-iteration-19/NEXT_STEP.md) for the remaining no-point
models, unresolved optimality gaps and submission work. No CPU-only Kaggle
upload is needed. The three iteration18 new inputs are now development cases.

Prior status: [iteration18](../reports/milp-iteration-18/REPORT.md) implements
the measurement and selective-checking experiment. The retained cold/warm
repair now needs three attempts and two accepted corrections in either replay;
tolerances, cuts/restarts and recovery allowances are unchanged. The full gate
passes 17 CTest groups, 126 Python tests, 320 generated runs and 100 reused
exhaustive cases. Repeated screen runs retain p0201 completion and eil33-2
points while avoiding mas74's unresolved exit; these are not general optimality
or speed guarantees. The broader experiment includes all 24 development cases
and three new public instances. See the report for every outcome and the
[bounded next step](../reports/milp-iteration-18/NEXT_STEP.md) for unresolved
first-feasible and proof-gap work. Both modes remain optional. Real domain
validation, deployment hardening and final GPU-only evidence remain distinct
submission requirements. No CPU-only Kaggle upload is needed.

Prior status: [iteration17](../reports/milp-iteration-17/REPORT.md) repairs
the captured cold and original warm sparse LP failures with opt-in residual
correction, without relaxing tolerances or changing recovery budgets. All three
refined mas74 runs avoid numerical recovery/deferred nodes but remain open.
The 24-case wave completes 9 controls versus 8 refined cases; eil33-2 loses a
point and p0201 loses completion, while misc07 gains a point. Keep the feature
optional. Next isolate correction overhead from changed pivots/restart timing,
test a selective schedule without losing the numerical repair, and evaluate
predeclared untouched hard cases. See the
[bounded next step](../reports/milp-iteration-17/NEXT_STEP.md). Numerical safety,
first feasibility and proof-gap closure remain distinct goals. No GPU or user
upload is needed for this local work.

Prior status: [iteration16](../reports/milp-iteration-16/REPORT.md) implements
optional incumbent-gated cut continuation. It protects first-feasible allocation
and restores points in both Binkar screen runs relative to the old ungated
failure, but both gaps are worse than the five-round controls. Keep it optional.
Prioritize the reproduced sparse LP accuracy failure in mas74's captured node:
dense recovery succeeds where the sparse result fails its numerical checks.
Do not loosen tolerances or reset spent recovery budgets. The separate
[diagnosis and next work](../reports/milp-iteration-16/NEXT_STEP.md) distinguish
the numerical failure from the restart/deferred-queue exit mechanism. All
24 public models remain development data; fresh holdouts are still required
before a final policy decision. No CPU-only Kaggle run is needed.

Prior status: [iteration15](../reports/milp-iteration-15/REPORT.md) tests
selective cut continuation across 66 public runs on 24 models. It repeatedly
loses Binkar's incumbent and is rejected for default promotion. The 21-case wave
still completes 10 cases in either profile; this is not a broad performance
improvement. Three fresh cases add an agreed numerical infeasibility result,
a feasible limit and mas74's unresolved-relaxation outcome with a checked point.
All 24 models are now development data. Prioritize protecting first-feasible
search, diagnosing mas74's early unresolved return, and stronger general LP/
search work. See the [next bounded experiment](../reports/milp-iteration-15/NEXT_STEP.md).
Keep the rejected policy and failures visible. No CPU-only Kaggle run is needed.

Prior status: [iteration14](../reports/milp-iteration-14/REPORT.md) adds
optional phase/work attribution and tests one versus five root cut rounds.
Binkar's short-budget trade-off is encouraging, but the p0282 regression rules
out promoting the one-round policy. Five remains the default. This adds useful
measurement and tested controls, not a universal solver-performance gain.
The [next experiment](../reports/milp-iteration-14/NEXT_STEP.md) is a predeclared,
general cut-continuation policy, followed separately by feasibility stalls,
stronger bounds and real resource-containment tests. Keep every existing failure
in the ledger and add genuinely new holdouts before a final policy choice.
All 21 current public cases are development data. No CPU-only Kaggle handoff
or user result ZIP is needed.

Prior status: [iteration13](../reports/milp-iteration-13/REPORT.md) separates
optional raw-LP search ranking from the minimum used for proof accounting.
Independent replay and fixed-node repeatability checks now cover that boundary.
The fresh 17-model 30s wave completes 2 exact + 5 numerical cases in BOTH queue
policies, with 10 unfinished; timing was on a busy shared desktop, not comparable
to iteration12's earlier 10-versus-9 completion count. Search improvements are
mixed, not a general speedup. See [the next experiment](../reports/milp-iteration-13/NEXT_STEP.md)
for the remaining proof, feasibility and resource-control work. No CPU-only
Kaggle handoff is needed. A full-library/arbitrary-input guarantee is not established.

In iteration13, its four new holdouts all remain unfinished: gen-ip002 and assign1-5-8 have
checked points with roughly 3% and 18% gaps; lotsize and eil33-2 have no point
within 30s. Prioritize phase/work attribution and budget-controlled feasibility
search, then stronger general relaxations. The next candidate must be tested
against all these failures and additional genuinely untouched cases.

Earlier long-budget [iteration10](../reports/milp-iteration-10/REPORT.md)
validated optional reduced-bound LPs that improve the equal-budget Binkar gap to
0.9132% and complete Blend2 to numerical tolerance in 144.04s. Binkar is not
proved, and broader repeated full-solve evidence is still missing. All four
teaching/synthetic application models pass both profiles, but real refinery/
expert validation is outstanding. Prioritize broader MILP robustness, domain
validation, repeated final GPU-only evidence and a clear reproducible demo.
No CPU-only Kaggle run or result ZIP is pending. The
[submission assessment](SUBMISSION_ASSESSMENT.md) supersedes historical
progress descriptions below when they conflict with later evidence.

Deadline: 30 September 2026. The local implementation is a V2 candidate while
the remaining performance/robustness gaps are unresolved. The first GPU run
has been received and audited; see `../reports/KAGGLE_GPU_REPORT.md`.
The second return also confirms the MILP iteration on Kaggle/P100; see
`../reports/kaggle-gpu-02/REPORT.md`. No rerun of either unchanged notebook is needed.

The previous [MILP cycle](../reports/milp-iteration-03/REPORT.md) adds
opt-in LP recovery and checked post-incumbent neighbourhood search.
Its [180-second Kaggle return](../reports/kaggle-milp-02/REPORT.md) is audited:
binkar improves7297.32 to6747.31 with1.23% reported gap; blend2 recovers5/5 LPs
but still finds no incumbent; markshare finishes unchanged. No rerun of the
unchanged notebook is needed. The new [candidate-repair cycle](../reports/milp-iteration-04/REPORT.md)
diagnoses a feasible fixing rejected by sparse numerical checks, adds bounded
dense repair, and fixes a reproduced whole-node false-proof edge case after
successful fixing. The [completed local180-second comparison](../reports/milp-iteration-04/LOCAL_VALIDATION.md)
now reaches blend2 objective7.598985 in114.53 seconds, matching the independent
optimum with gap_limit status. Five final candidates and two captured repairs
pass fresh original-model checks. Binkar retains6747.31 with about1.22% gap;
markshare remains incomplete. Subsequent CPU iterations also run locally;
the prepared iteration04 notebook does not need to be run. Kaggle is reserved
for actual GPU work. No tolerances were loosened. Remaining proof gaps, repeated broader evidence
and industrial relevance remain open. Unresolved nodes are not called solved.
The [local neighbourhood iteration05](../reports/milp-iteration-05/REPORT.md)
completed three experiments with fresh original-model audits. Diversification
and time spacing did not improve final hard-instance objectives; both remain
opt-in. Markshare exhausts local attempts before its best incumbent, and binkar's
late alternative has almost no budget left. Reserve useful late-search work and
test stronger neighbourhoods/bounds, rather than counting these options as a
completed performance improvement. No user result ZIP is pending.
The subsequent [local iteration06](../reports/milp-iteration-06/REPORT.md) now
improves markshare's final objective from~5 to~1 using a bounded, opt-in
meet-in-the-middle search for small binary/separable-continuous models. The
exact1 point passes independent zero-violation checks and three root-only
repetitions. The global proof gap remains about50% under the solver's metric;
completed heuristic enumeration is not an optimality certificate. Broaden this
structural validation and develop safe proof-gap closure, while continuing
general binkar/root-LP robustness work locally. No Kaggle run is needed.
The completed [local iteration07](../reports/milp-iteration-07/REPORT.md)
now closes markshare's proof gap with a separate checked-integer engine:
objective = bound = 1, gap zero, in three local runs. Independent literal-MPS
integer checks confirm each proof. P0033 also passes at 3089, but its existing
solver path is faster. This opt-in mode supports at most 36 binary variables
and 32 rows with integral data and tightly restricted continuous recourse;
it is not a proof engine for arbitrary MILPs. Unsupported/interrupted attempts
publish no proof bound. Next priority is binkar's remaining general-MILP gap,
followed by broader independent public-model evidence. No user result ZIP is
pending and no CPU-only Kaggle run is requested.
The [local iteration08](../reports/milp-iteration-08/REPORT.md) improves Binkar's
reported gap from1.214% to0.957% while retaining6747.31 in a fresh180s pair.
Checked small-row lifted covers are applied through an opt-in half-time restart;
direct root application regressed the incumbent and is not promoted. Cut and
original-point audits pass, but Binkar is still incomplete. Repeat this schedule
at varied budgets and on more public models before making broad performance
claims. All CPU work remains local; no user artifact is pending.
The [local iteration09](../reports/milp-iteration-09/REPORT.md) tests compact
equality LPs. Immediate activation regresses the Binkar incumbent despite a
faster root screen. Delayed activation keeps 6747.31 but changes the fresh 180s
gap only from 0.9574% to 0.9544%; this is marginal single-pair evidence, not
established full-solve acceleration. A separate 600s attempt reaches 0.9077%
gap with the same incumbent and still times out. All new modes remain optional, and the original CPU/Kaggle
policy is unchanged. Stronger general bounds and independent broader-model
validation still matter more than adding feature names.
The [QP iteration](../reports/qp-iteration-01/REPORT.md) now gives QPLIB `9002`
an independently checked numerical optimum locally. Its reference-solver
comparison remains incomplete; further CPU validation also runs locally.

1. **Next GPU evidence:** both returns passed all three CUDA scale cases
   and all 230 generated cases. Keep them as separate versioned evidence. After
   the next targeted iteration, collect repeated timings and public box-QP GPU
   checks. Memory diagnostics now show a solver-PID mismatch; process-attributed
   VRAM remains unresolved, although whole-device samples are available.
   The notebook must remain under 1 MB, with its source ZIP attached as input.
2. **Industrial relevance:** supply any MRPL-approved or shareable refinery,
   scheduling or supply-chain model, or domain-expert feedback on the literature
   case. Public teaching examples do not replace validation on actual operations.
3. **Organizer clarification:** confirm the acceptable QP scope (convex versus
   nonconvex) and use of GPU/general numerical infrastructure. No organizer
   approval has been obtained by this implementation work.
4. **Performance and robustness work:** extend local `9002` validation,
   expand beyond this three-instance QP subset, and improve the incomplete modern
   MILPs. The original unscaled OSQP `9002` run still times out; preserve it and
   treat any future scaled-reference experiment as a separately labeled protocol.
   Small relative QP residuals are not promises of small absolute operational error.
5. **Final report:** the first bundle matches its source snapshot. Keep its
   observations labeled single-pass; repeat equal-accuracy measurements and finalize
   the PS requirement matrix and submission claims.

The PS's general ambition of reliable industrial-scale LP/MILP/QP up to millions
of variables is not established by a synthetic million-variable box QP. Complete
MIPLIB/Netlib/Mittelmann library coverage is not claimed. MIQP, NLP, MINLP and
global nonconvex QP are not implemented. Additional algorithms should be added
against explicit scope and test gates rather than counted as completed features.
