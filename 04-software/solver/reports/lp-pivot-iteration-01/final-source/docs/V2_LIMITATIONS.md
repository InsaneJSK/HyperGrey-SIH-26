# V2 limitation register

Iteration28 update: the retained experimental staged profile has26/27 useful
development outcomes, ten optimization completions and lotsize unresolved.
Six new public holdouts all have checked points but none completes in30 seconds.
The three experiments from25–27 were not promoted. Danoint's previous failed
repetitions and broad open gaps remain relevant; defaults are unchanged.

The Windows wrapper now measures process peaks and passes timeout, cancellation
and sampled-memory pressure checks, but it is neither an allocation cap nor
arbitrary process-tree containment. A corrected five-DLL snapshot passes a
same-host isolated-folder smoke. This is not full clean-OS/submission validation.
Repeated MPS objective entries have an [explicit additive input convention](MPS_DUPLICATE_OBJECTIVES.md)
that differs from the tested reference reader. Raw mismatch failures are retained;
canonical reference checks and exact enumeration validate the intended models.
See [iteration28](../reports/milp-iteration-28/REPORT.md) for complete limitations.

Iteration24 update: [objective-only staging](PUMP_DISTANCE_STAGE.md) raises the
wave to 25 checked points plus one cross-checked infeasible model, but only ten
completions. Lotsize is unresolved and fifteen feasible models have open gaps.
Danoint's two staged screen failures coexist with wave success; misc07's new
points expose near-tie branch sensitivity to sub-1e-15 integer-coordinate
changes. Binkar's objective regresses. This is not uniformly reliable 26/27
coverage or evidence of every public MILP being handled.

The strict parent-domain guard intentionally excludes changed auxiliary RHS,
layouts and bounds; the existing guarded direct path remains the fallback.
Retaining the exact parent costs model-sized memory, with cooperative clocks
and no new hard global containment. Parent and child LP work are separately
counted; a verified private point is not an incumbent or global proof. All 98
public records and 48 replay points pass validation, but misc07's saved child
is slower warm than cold and lotsize's large local LP savings do not solve it.
Flag stays off. See the [full report](../reports/milp-iteration-24/REPORT.md).

Iteration23 update: [private basis handoff](PUMP_DISTANCE_REOPT.md) is tested,
not promoted. It leaves coverage at 24 checked points plus one corroborated
infeasible case. Misc07/lotsize are unresolved; only nine candidate models
complete versus ten controls. The mod008 completion loss occurs without a
private handoff LP call; timing-limited outcomes do not establish causation.
Thirty independently checked replay points confirm local LP results, not an
end-to-end MILP improvement. Lotsize's first compatible offer is neither primal
nor dual feasible after simultaneous retargeting/tightening, so it still falls
back. Older best-basis retention adds model-sized storage, not a hard memory
cap. Existing absolute candidate checks and private/global boundaries remain.
The new flag stays off; all 94 benchmark records pass validation. See the
[full report](../reports/milp-iteration-23/REPORT.md), including the lack of gains.

Historical iteration22 update: [private pump reoptimization](PUMP_PRIMAL_REOPT.md) raises
observed breadth to 24 checked solutions plus one corroborated infeasible
status, not 25 optimality proofs. Only ten models complete; misc07/lotsize
still have no point and fourteen feasible models retain open gaps. Mas74 loses
solution quality, so the new flag remains optional despite repeated danoint/
rout gains. A compatible basis is not retained into the initial distance LP;
that cold solve still exhausts lotsize's slice despite a near-integer seed.

Structure tags add model-sized storage; only diagnostic replay has explicit
capture caps. Neither provides hard global memory/process containment.
Exact structure comparison is not an
exact rational LP certificate. Shared-desktop time-triggered outcomes vary;
the specific replay pivot reductions must not be presented as universal speedup.
All 27 are development models. Same measured/final binary in this iteration;
frozen21 remains preserved. See the full [report](../reports/milp-iteration-22/REPORT.md).

Iteration21 update: [private distance diving](PUMP_DISTANCE_DIVING.md) remains
off by default. Eil33-2/rout gains coexist with a lost misc07 point and continued
lotsize/danoint limits. Candidate 23 solutions include only 10 completions;
one additional case is cross-checked infeasible. It is not 27/27 completion.
The cold private LP can consume the whole dive slice; general-integer targets
also add columns/rows, without new hard memory containment. Fixed-target
distance need not improve nearest-integer distance monotonically.

The final build fixes a presolve-off empty-domain exception and passes separate
gates, parity and actual MIN/MAX integration. Its binary differs from the
measured build; the 86 timed comparisons were not rerun on the patched binary.
Keep those identities explicit. New scalar samples are bounded to eight dives;
4516-column eil33-2 intermediate dive vectors exceed the existing trace limit.
Its final point and retained seed are checked, not every intermediate point.
All 27 are development data; see [iteration21](../reports/milp-iteration-21/REPORT.md).

Iteration20 update: [pump-guided diving](PUMP_GUIDED_DIVING.md) remains optional
and off by default. Better seed distance does not ensure useful integer fixings:
the following original-objective LP often moves back away from that seed.
Lotsize/eil33-2/danoint remain no-point limits. Gt2's objective gain repeats, but
pk1 regresses and misc07/rout gains are not repeatable breadth guarantees.
Nine completions and 23 checked points are distinct measures, not 23 proofs.

New seed telemetry is limited to 8 scalar records, 10000 columns per vector and
20000 total vector values. Independent original-row/bound checks of retained
fractional seeds are not integrality certificates, exact LP proofs or validation
of unsaved current-node/cut domains. The separate terminal reference uses a
larger allowance solely to resolve status agreement; original own-run budgets
and reference timeouts are preserved. The exploratory gt2 repeats are selected
after observing its gain and are not fresh holdouts. See the full evidence and
adverse outcomes in [iteration20](../reports/milp-iteration-20/REPORT.md).

Iteration19 update: [heuristic candidate repair](HEURISTIC_CANDIDATE_REPAIR.md)
is optional and applies to rejected near-integer dive points. It cannot create
an integer-feasible fixing from arbitrary fractional pump progress, guarantee
first feasibility, or turn a fixing-LP optimum into a whole-MILP proof. A local
repair consumes the existing dive slice and shared repair allowance, so it can
displace other useful search. Duplicate suppression and a 16-attempt cap can
also leave later opportunities unexplored. The original point checks remain.

The trace retains at most 512 events and 100000 vector values, with 2048-column
vector limits. Priority capture may discard older vector payloads; missing or
truncated history is explicit, not counted as independently replayed. Reported
cooperative budgets are not hard process-memory/time isolation. All 27 public
models are development inputs; no fresh holdout, uniform speedup, full-library
proof or industrial-readiness claim follows from this iteration. See its
[complete evidence](../reports/milp-iteration-19/REPORT.md).
The current reported MILP gap is `max(0, incumbent-bound)/(1+abs(incumbent))`
in minimization sense. Comparisons with other solvers must use a matched
definition or the raw objective and bound, not assume all `gap` fields agree.

Iteration18 update: [selective basis checks](SELECTIVE_BASIS_REFINEMENT.md)
retain the captured cold/warm repair with fewer correction attempts, without
loosening tolerances. They do not guarantee recovery from every numerical
stall, failed pivot or inaccurate direction solve. Checks happen at selected
simplex decision boundaries; this is still floating-point LP/MILP, not general
exact proof. The new detailed counters measure residual work and a subset of
phase time, not extra time to add to the total or hard resource isolation.

The public protocol adds three locally unseen instances, but all are moderate
historical cases and mas76 belongs to the already tested mas74 family. Once
used, they join the development set. This does not establish hardest-instance,
full-library or arbitrary-input coverage. Fixed-node diagnostic timings and
shared-desktop 30s comparisons are distinct experiments; neither supports a
blanket speedup. See [iteration18](../reports/milp-iteration-18/REPORT.md) for
the complete paired outcomes and retained regressions. GPU acceleration of
general MILP, real refinery validation and final deployment hardening remain
separate work; this CPU-only iteration supplies none of those claims.

Iteration17 update: [sparse basis refinement](SPARSE_BASIS_REFINEMENT.md) is
opt-in and remains a numerical method. It repairs the retained mas74 cold and
original warm-basis failures without relaxed tolerances or removed bounds;
both repaired points pass an independent check. Both paired full mas74 runs
avoid LP recovery and unresolved nodes, but finish with about15.7% open gaps,
not optimality proofs. Correction need not converge on arbitrary ill-conditioned
bases and is limited to basic primal/dual values, not pivot directions. It adds
work per LP iteration, uses platform-dependent long-double precision, and does
not provide hard OS resource isolation. Unfamiliar models, no-point cases and
broad proof-gap closure still need work. See the complete
[iteration17 evidence](../reports/milp-iteration-17/REPORT.md) for regressions
and promotion status; all24 public cases here are development data.

Iteration16 update: [incumbent-gated cuts](INCUMBENT_GATED_CUTS.md) protect
the ordinary cut schedule before a checked point exists. They do not guarantee
first feasibility or better proof progress. Both Binkar screen pairs retain
points but have worse gaps than control, so neither adaptive option becomes
the default. Source-incumbent validation is independent, but existing restart
vector storage is capped at 10000 columns; an unavailable source fails the
evidence check explicitly rather than being counted as verified.

Mas74's frozen15 sparse cold replay returns numerical_error and about 9.77e-5
absolute violation; dense recovery matches the independent optimum with about
4.37e-11 violation. The existing recovery allowance is exhausted before a
full-domain restart, whose children remain unresolved and empty the active queue.
That explains the early return, but the underlying sparse arithmetic issue is
not fixed here. Turning off restart uses more time while leaving thousands of
unresolved nodes. These diagnostic controls do not establish a universal fix.
See [iteration16](../reports/milp-iteration-16/REPORT.md); all tested public models
are development data, not fresh holdouts for this candidate.

Iteration15 update: [selective cut continuation](ADAPTIVE_CUT_ROUNDS.md) is
experimental and OFF by default. A small normalized dual gain is not a reliable
measure of a cut's importance to feasibility search: all four Binkar adaptive
runs lose the point while all controls find one. The 21-case wave has 10
completions in both profiles, but adaptive has an additional no-point limit.
Stopping decisions are independently replayed; that checks allocation and
bookkeeping, not every cut/LP certificate or a guaranteed number of LPs saved.

Three predeclared fresh cases broaden the ledger to 24 models. Neos859080's
infeasibility agrees with the reference but has no exact rational certificate;
gen-ip054 remains open; mas74 returns valid points with unresolved relaxations
at about 15s under a 30s setting. That numerical/recovery issue is retained,
not called solved. Four analytic min/max integrations exercise actual early
stops and honest partial bounds. No broad speedup, hard resource containment
or industrial readiness follows from these tests. See [iteration15](../reports/milp-iteration-15/REPORT.md).

Iteration14 update: [phase attribution and root cut-round controls](MILP_WORK_BUDGETS.md)
make MILP-visible LP work and exclusive wall time observable. They are not exact
CPU/FLOP accounting and do not add hard pivot, process-memory or elapsed-time
containment. Parsing, initial model validation/copying and output serialization
are outside the measured interval. Clock-driven search remains variable on a
shared desktop, even when both compared policies enable the same telemetry.

The one-round candidate reduces optional cut work but seriously worsens p0282's
point and bound in the retained screen and broader wave. It is not promoted;
five rounds remain the default. No heuristic or general exact-proof expansion
is part of this change. A counter-only restart trigger makes that trigger
deterministic, not all time-limited solver behavior. The independent reader
optimization is validation speed work, not an optimization-engine speedup.
All 21 timed public cases are development data, including the four previously
untouched iteration13 holdouts. See the [iteration14 ledger](../reports/milp-iteration-14/REPORT.md)
for completed, partial and adverse outcomes; none establishes all-library or
industrial robustness. Earlier evidence below belongs to its recorded build.

Iteration13 update: [raw-LP queue ranking](MILP_FRONTIER.md) is optional and
maintains an independent minimum over queued/deferred numerical proof bounds.
Event replay checks saved bookkeeping, not the validity of every LP bound or
all branching domains. Frontier traces retain the first 20000 events with
explicit truncation; performance runs omit capture. The 17-case wave completes
7 cases in each policy, not a completion-rate improvement. Shared-desktop load
and clock-triggered search make comparisons with earlier timings uncontrolled.
All adverse outcomes and untouched holdouts remain in the
[iteration13 report](../reports/milp-iteration-13/REPORT.md). No total process-RSS
limit, universal proof, GPU expansion or production-readiness claim is added.

Iteration12 update: [objective-lattice bounds](OBJECTIVE_LATTICE.md) are optional
and support only checked integral effective costs and restricted unit-equality
continuous definitions. Unsupported structures use the prior bounds. The
17-case 30s pair adds mod008 numerical completion (10 versus 9 completed cases),
but 7 cases remain unfinished and gt2 has a worse short-run incumbent. misc03
remains open. No default promotion or universal speedup claim is justified.
The independent lattice audit checks exact parsed-model algebra and up to
4096 saved improvements per run, not the validity of every input LP bound.
Truncated traces are explicit. General certificates remain numerical; see
[iteration12](../reports/milp-iteration-12/REPORT.md).

Iteration11 safety update: [MPS integer-marker defaults](MPS_DOMAIN_CONTRACT.md)
are corrected in `build-milp-iter11`. Older readers can falsely report optimality
for the wrong domain when a marked integer has no explicit bound record.
The independent 28-case domain gate now passes. A new 17-case public ledger
retains unfinished solves instead of declaring universal support; see
[iteration11](../reports/milp-iteration-11/REPORT.md) and the
[robustness program](MILP_ROBUSTNESS.md).

Earlier long-budget evidence: [iteration10](../reports/milp-iteration-10/REPORT.md) adds
guarded reduced-bound LPs but keeps them optional. Binkar still times out at
0.9132% reported gap; Blend2 reaches its numerical gap tolerance in 144.04s
in the fresh pair. Full-solve results have only one repetition per profile.
Three root pairs establish a narrow root-time reduction, not general MILP
speedup. Failed reduced attempts retry full bounds and can add work. Four
application models pass new-build reference checks but are not production data.
See the [submission assessment](SUBMISSION_ASSESSMENT.md) for current priorities.

1. **Convex QP scope:** only continuous convex QPs. Conservative numerical PSD
   tests can reject some valid matrices when fill budgets are exhausted. Global
   nonconvex QP, MIQP, NLP and MINLP are not implemented.
2. **Constrained-QP convergence:** the later [QP iteration](../reports/qp-iteration-01/REPORT.md)
   passes original-model numerical KKT/dual-gap checks on `9002` locally, but
   the original OSQP reference comparison remains incomplete. Its absolute
   constraint violation is about2.381 despite passing relative tolerances;
   that is not a promise of small absolute operational error. Sparse KKT
   polishing has a bounded attempt budget; bad active sets are discarded.
3. **Modern MILP difficulty:** `binkar10_1` remains incomplete. Markshare's
   ordinary branch-and-bound path remains incomplete, but the separate opt-in
   [iteration07 exact path](../reports/milp-iteration-07/REPORT.md) now proves
   its optimum of 1 in three local runs, independently checked from MPS literals.
   The later [local iteration04 comparison](../reports/milp-iteration-04/LOCAL_VALIDATION.md)
   completes `blend2` to its numerical gap tolerance, matching the independent
   optimum. This single-pass result and historical four-case MIPLIB success
   do not establish broad modern industrial MILP coverage.
   Iteration05's tested neighbourhood-selection and pacing options did not
   improve the final objectives on this subset and remain opt-in.
   Iteration06's small-binary meet-in-the-middle heuristic improves markshare
   from~5 to~1, independently checked, but does not close its proof gap. Its
   structure/memory limits are explicit; blend2 and binkar are unsupported by
   that helper and continue through the general solver. The later exact path
   is limited to <=36 movable binaries, <=32 rows, integral data and unit,
   single-equality continuous recourse. It also proves p0033, but is slower than
   the existing solver on that model and stays opt-in. Two eligible public
   models and generated exhaustive tests do not establish general speedup or
   industrial coverage. No new binkar/blend2 long-run claim comes from iteration07.
   Iteration08 now retains Binkar6747.31 at0.957% reported gap in a fresh180s
   delayed-cut comparison, versus guided1.214%. This remains incomplete and
   single-pair evidence. Direct root cuts worsened the incumbent; both modes
   stay opt-in. The exact-valid small-row cuts apply to parsed binary64 data,
   not arbitrary-precision MPS literals, and do not make global LP bounds exact.
   Half-time restart can repeat work and is not guaranteed to improve a solve.
4. **Sparse factorization:** sparse storage removes the dense-tableau architecture
   from the main LP/MILP path, but LU fill, refactoring and basis conditioning
   still limit difficult problems. A small-problem dense recovery path remains.
5. **Numerical certificates:** the general LP and MILP paths use floating-point
   tolerances. Their bounds have a safety margin, not an exact/interval proof.
   Only the restricted opt-in binary-proof path uses checked integer arithmetic,
   literal-input guards and complete enumeration. Unsupported, out-of-range or
   interrupted attempts cannot publish an exact bound; arbitrary rational input
   and arbitrary MILPs are not covered. The independent Python checker recomputes
   the proof rather than checking a compact portable proof trace. QP optimality
   uses KKT checks; its objective-error bound may be unavailable on unbounded
   boxes. General QP infeasibility/unboundedness certificates remain incomplete.
   Iteration09's optional compact equality representation does not make these
   bounds exact. Dependent/numerically rejected equations can trigger a cold
   fallback; the extra work may hurt performance. Immediate compact LPs worsened
   Binkar's incumbent in a 180s pair. Delayed activation retained it but gave
   only a marginal gap change, so neither is promoted as a general speedup.
6. **GPU scope and evidence:** CUDA currently accelerates box QPs only and uses
   one GPU. The first P100 Kaggle run passed three synthetic scale cases, but
   only one timing repetition was made. Public box-QP GPU comparisons and
   repeated measurements remain outstanding; LP/MILP/constrained QP are CPU-only.
7. **Parallel scope:** OpenMP parallelizes QP products/iterations. LP and MILP
   search remain sequential. Four threads can be slower than one on small cases.
8. **Scale interpretation:** the million-variable experiment is synthetic,
   sparse, convex, box-constrained and has a planted optimum. It does not prove
   general industrial-scale LP/MILP/constrained-QP performance.
9. **Dataset and industrial coverage:** selections are small. Mittelmann runs
   are pending. Literature examples are historical teaching cases, not MRPL
   production data; the multi-period production inputs are synthetic.
10. **Format/platform limits:** MPS/QPLIB remain documented subsets. Local tests
    use GCC 14.2 on Windows; the first Kaggle run passed on Linux/GCC 11.4/CUDA
    12.8/P100. Broader platforms, GPUs and compiler versions remain untested.
11. **Resource accounting:** host/device memory sampling can miss short peaks.
    Parsing, curvature checking, setup and an individual numerical operation
    can slightly overrun limits. The Python harness enforces an external timeout.
    First-run GPU-memory values were unavailable. Updated diagnostic sampling
    separates process memory from whole-device observations; it needs GPU rerun validation.
12. **Open questions:** numerical-library/GPU-runtime permissions, convex-QP
    acceptance, and the supplied statement's truncated final paragraph remain
    outside information gaps. The confirmed deadline is 30 September 2026.
