# Codebase review on resumption, 17 September 2026

The current project is an independently implemented C++ optimization engine,
with unusually detailed experiment retention. The immediate engineering risk
is unreliable time-limited integer search and open proof gaps, not an absent
LP/MILP implementation. Submission readiness also requires work beyond MILP.

## Where the implementation lives

| Area | Current implementation and role |
|---|---|
| Input/contract | `src/mps.cpp`, `include/mps.hpp`: MPS parsing, linear model and validation; QPLIB reader in `src/qp.cpp` |
| LP | `src/sparse_lp.cpp`, sparse LU/matrix and refinement headers: sparse simplex, canonicalization, guarded basis reuse, checks; `src/solver.cpp` retains the dense method used for bounded recovery/repair |
| MILP | **`src/milp_v2.cpp` is the linked engine**; `src/milp.cpp` is historical and not in the library target. Branch-and-cut, presolve, frontier accounting, cuts, restarts, pump/dives, bounded incumbent repair |
| Private heuristic LPs | Pump guidance/distance/basis/stage headers; heuristic points must cross original-model acceptance; private objectives and infeasibility are not global proof certificates |
| Continuous convex QP | ADMM in `src/qp_admm.cpp`, diagonal-equality dual Newton in `src/qp_dual_newton.cpp`, projected-gradient box path in `src/qp.cpp`/`src/accelerated_qp.cpp` |
| GPU | Optional `src/cuda_box.cu`, selected by CMake; box-QP acceleration only. No GPU MILP engine or general constrained-QP GPU claim |
| CLI/API | `src/main.cpp` and public include headers; JSON results expose status, vectors, bounds, gaps, verification and optional diagnostics |
| Evidence | Python runners/checkers, CTest, generated/exhaustive cases, `reports/milp-iteration-*` frozen source/executables/raw records |

CMake links our numerical sources and optional OpenMP/CUDA, not HiGHS/OSQP.
Source inspection found no external solver invocation in `src/` or `include/`.
Reference solvers are Python validation dependencies under `tools/reference`.
This is a source/build inspection, not a comprehensive dependency/security audit.

## What changed in the recent work

Iterations17–19 focused on numerical LP refinement and recovering checked
incumbents from rejected nearly integral heuristic points. Iterations20–24
added pump seed guidance, a private distance objective, guarded primal/basis
reuse, and objective-only staging before branch bounds change. They are
experimental opt-in mechanisms; the README's best recorded staged result is
not the behavior guaranteed by a default invocation.

Frozen24's 27-case wave has 25 checked points and one cross-checked infeasible
case, with ten completions and fifteen feasible open gaps. `lotsize` is still
without a point; `danoint` fails both staged screen repeats, despite succeeding
in the wave. `misc07` succeeds three times but changes trajectory when near-tied
fractional coordinates differ by less than 1e-15. Solution-quality regressions
on `binkar10_1` and the older `mas74` comparison remain relevant.

These are reused development cases. They cannot establish unseen-model
robustness, industrial scale for all classes, or a competition percentile.

## Engineering assessment

1. **Continue isolated experiments.** The near-tie helper is an appropriate
   small next hypothesis, but stable branch ranking alone need not improve
   integer coverage. Preserve failures and reject ineffective policies.
2. **Diagnose exact private subproblems.** Faster first-stage LPs have moved
   `lotsize`'s bottleneck later. Its actual bounds, targets, auxiliary layout,
   basis and remaining slice must be retained before changing a budget policy.
3. **Make completion a separate objective.** Recent work primarily finds
   incumbents. Root relaxation strength, incumbent improvement and frontier
   progress must justify the next gap/completion experiment.
4. **Choose one release profile with current evidence.** Experimental flags
   have accumulated. Do not construct release claims from a union of historical
   best runs or silently promote a feature based on one saved example.
5. **Restore reproducibility on this machine.** Old build caches point to a
   different checkout and the global compiler is incompatible. A verified
   project-local matching compiler now works; fresh builds and frozen-binary
   parity checks are required. Historical timings are not matched comparisons
   to the new host environment.
6. **Keep the submission scope explicit.** QP is currently continuous/convex;
   MIQP/NLP/MINLP are extension boundaries. The QPLIB9002 retained absolute
   violation of about 2.381 is acceptable only under its stated relative
   contract, not an unspecified operational tolerance. Its OSQP timeout stays
   visible. Million-variable synthetic box-QP results do not establish equally
   large LP/MILP capability.
7. **Release work remains.** Final-source LP/QP revalidation, untouched MILPs,
   process/resource limits, industrial what-if validation, reproducible CLI/API
   demonstration and actual final-snapshot GPU evidence are independent tracks.

## Review after iterations25–28

The architecture and separation from reference solvers hold up under the new
checks. The bottleneck remains useful integer search and closing valid bounds;
the new experiments do not justify another default feature promotion.

| Iteration | Finding | Decision |
|---|---|---|
| 25 | Fixed-vector near-tie behavior stabilizes, but repeated checked points fall from22/24 to20/24 | Keep ranking off |
| 26 | Exact later lotsize LPs are locally infeasible; repeated phase-one work consumes the slice. Alternate reserve produces no new points | Keep reserve off; retain exact fixtures |
| 27 | Retaining the tree improves mas74 bounds and mod008 work, but weakens binkar bounds in both repeats | Keep normal restart policy |
| 28 | Development26/27 useful, ten completions; untouched6/6 feasible, zero completions; default subset6/6 completes | Freeze experimental staged evaluation profile; no release/default promotion |

All39 final public/default records and37 vectors pass validation. The artificial
tests expose a duplicate-objective reader convention mismatch; all24 unchanged
answers match enumeration and an explicitly equivalent reference input. Keep
that interoperability boundary visible. The process wrapper passes15 status
and pressure checks, and the isolated-folder test finds/fixes the missing
`libdl.dll` runtime dependency. The final peak working-set observation is
166.969 MiB, not evidence for arbitrary industrial scale.

The strongest next numerical hypothesis is narrower than another heuristic
flag: instrument the warm dual rejection and attempt a verified local
infeasibility certificate before restarting phase one. Existing replay uses
one preliminary pivot followed by1220 phase-one pivots. Preserve fallback
and all numerical checks; any performance gain still needs a repeated MILP
screen. See [the proposed work](NEXT_PRIVATE_LP_HYPOTHESIS.md).

Danoint's separate fixing-deadline reliability, broad completion, final LP/QP
coverage, actual GPU evidence, domain validation and submission work remain.
The objective's four experiment slots are handled; the overall SIH objective
is not complete. Use [iteration28's report](../reports/milp-iteration-28/REPORT.md)
and [run guide](RESUMED_RUN_GUIDE.md) for the frozen profile and its limits.

## Review after iteration 29 and continuous validation

The subsequent [verified private certificate](PRIVATE_DUAL_CERTIFICATE.md)
implements the proposed numerical shortcut with bounded exact coefficient
arithmetic and outward-enclosed original-domain checks. Unsupported arithmetic,
incompatible bases and uncertain signs retain the existing phase-one fallback.
The option is private and disabled by default; local infeasibility has no global
MILP proof or pruning role. Exact/interval checks, 26 CTest groups, 176 existing
Python tests plus eight new checker tests, generated/exhaustive tests and
feature-off parity all pass. Runtime loader failures and corrected checks remain
in the experiment record.

The repeated 12-model MILP screen validates all 48 observations and 44 vectors.
Both profiles return 22/24 checked points and four completions. All 35 accepted
certificates occur in lotsize, reducing its private phase-one pivots to zero and
allowing more checked local LP steps, but no integer point. Binkar/pk1 quality
variation occurs without invoking this path; it is not evidence of an arithmetic
regression caused by the certificate. The practical promotion gate fails and the
option stays off. No new 27-model score is claimed.

Current-source [LP/QP validation](../reports/cpu-validation-2026-09-17/REPORT.md)
refreshes all 12 retained LPs, adds four public LPs, and checks the three original
QPs. Default/refined LPs each complete 15/16; `bandm` returns an honest numerical
error. A separate [representation study](../reports/lp-bandm-01/REPORT.md) checks
one compact/refined profile on all 16, with 16 completions and one reported
compact fallback. This is useful explicit-profile evidence; the default source
failure remains unresolved.

All three default QPs pass relative KKT checks, but 9002's maximum absolute
violation remains 2.381 and its original-data OSQP run times out. Tighter probes
lower absolute violation to about 0.222 but worsen scaled feasibility and
stationarity, fail independent acceptance and hit their limits. Do not promote
a tolerance setting based only on one smaller residual.

Next trace the default LP rejection and QP accuracy floor/fallback, then broaden
supported structures and declare fair performance comparisons. Remaining MILP
private-dive decisions require fixed-work diagnosis. Industrial what-if, domain
review, final package/demo and supported GPU measurements remain independent
submission work; this checkpoint does not establish overall readiness.

## Review after iteration 30

The relaxation engine was the bottleneck: iteration 28 work data showed tree
LPs averaging about 2,300 pivots on misc07 and 6,800 on danoint, because the
sparse simplex adds a row per bound, recomputes everything per pivot and falls
back to a cold phase one on stalls and infeasible children.
[`src/bounded_simplex.cpp`](BOUNDED_SIMPLEX.md) is an independent bounded dual
simplex behind `--bounded-lp`, with original-model verification of optimal,
infeasible and cutoff outcomes and a fallback to the old engine. The MILP code
changed only at relaxation call sites, cutoff handling, a cut-row basis
extension and a flag-gated open-node memory guard.

[Iteration 30](../reports/milp-iteration-30/REPORT.md) measures it against the
same executable with the flag off: development completions 17 → 23, fresh
untouched MIPLIB completions 1 → 5, LP completions 15/16 → 16/16, zero
validation failures, peak commit 594 MiB. The fresh holdout also exposed MPS
reader gaps (free `N` rows, text after `ENDATA`, valued `BV` bounds), now
handled in both the solver reader and the exact checker.

With fast relaxations, bounds close quickly and incumbent quality becomes the
limit (gt2 regresses; rout, pp08a and set1ch are mixed; lotsize and p0548 have
no point). The half-time restart inherited from the old engine now discards a
large tree. Next: incumbent-phase dives, fix-and-propagate first points, the
restart decision, then Gomory cuts and reliability branching.

## Review after iteration 31

With fast relaxations the balance shifted from bounds to incumbents, so
iteration 31 added two point-only heuristics ([tree dives and
fix-and-propagate](SEARCH_HEURISTICS.md)) and removed a per-row allocation in
bound propagation. The allocation fix alone raised gt2 from about 148,000 to
about 390,000 nodes in 30 s at identical flags, which shows how much of the
search was spent in propagation rather than in relaxations.

[Iteration 31](../reports/milp-iteration-31/REPORT.md) measures the heuristics
over two development repeats and a declared 12-model untouched holdout: zero
validation failures, nine development models with better checked incumbents
against two marginal regressions, and 10 checked points against 8 on the unseen
set. The promoted profile also replaces the half-time restart with root lifted
covers, which is what the unseen evidence favours.

What the evidence now says about the remaining weaknesses: bound strength limits
gt2, pk1, misc07 and qnet1 far more than incumbents do; first points are still
missing on lotsize, mitre and p2756; propagation remains the largest single
phase on gt2; and the no-restart profile grows a larger frontier, reaching
1088 MiB on gt2 against the 1536 MiB threshold. The next mechanisms are
therefore cut generation (Gomory from bounded tableau rows), reliability
branching, incremental propagation and a lock-based first-point heuristic.

## Weak-pivot safeguard and QP diagnosis

The next diagnostic cycle proves exact singularity of the captured standard
bandm basis: two canonical rows are opposite across every basis column, with
zero RHS. An inaccurate small pivot precedes the factorization rejection.
The LU rejection is correct; accepting weaker/singular factors would mask the
problem. Refreshing the current basis alone postpones but does not cure it.

An independently implemented selective two-pass ratio safeguard completes the
retained LP. The opt-in `--stable-primal-ratio` rule preserves ordinary strong
pivots and Bland fallback, using existing tolerance only for eligible-step
selection. Both final 16-LP profiles and the expanded correctness gate pass.
The [report](../reports/lp-pivot-iteration-01/REPORT.md) retains the default
failures, unpromoted broader ratio variant and initial QP reporting correction.
This is no broad MILP performance result or default change.

The QP specialist trace shows repeated tiny line-search steps and alternating
feasibility residuals, with no zero-PCG-step iterations. Tight specialist points
fail original-model KKT before ADMM starts, and final dispatches hit limits.
Capture objective increments, slopes, allowance and active-set transitions to
test the next hypothesis. QP numerical sources remain unchanged; operational
accuracy, wider coverage, GPU, industrial and submission tracks remain open.
