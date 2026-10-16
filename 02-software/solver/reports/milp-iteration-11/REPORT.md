# MILP iteration11 — breadth-first robustness and an input correctness fix

15 September 2026. Corrected CPU build `build-milp-iter11`, SHA256
`867191540898cb1ea7a4bb91a85949734d476b900ca94039025ae818f4ece0cf`.

Expanded to a predeclared 17-model public wave and fixed a reproduced MPS
integer-default bug. Both public sweeps give 2 checked restricted exact proofs,
7 numerical completions and 8 unfinished cases at 30s per model. These are
not 17 exact proofs, not the full MIPLIB benchmark, and not universal robustness.

## Correctness defect fixed

A marker-declared integer with no explicit bound record must default to [0,1]
under the documented convention. The old reader used [0,+infinity]. A minimal
minimize -X model with X <= 7 consequently returned X=7 and claimed optimal -7;
the independently parsed original permits X=1 and has optimum -1. Bounds for
another column must not change X's default. Four of 28 min/max domain tests
failed before the correction. All 28 now pass against HiGHS 1.12.0.

The fix tracks explicit bound records per column, preserving explicit LO-only
unbounded upper sides and continuous defaults. The independent literal proof
reader is corrected too. Programmatic C++ variable domains are unchanged. See
[domain semantics, references and guards](../../docs/MPS_DOMAIN_CONTRACT.md),
[before](marker-baseline/results.json) and [after](marker-fixed/results.json).
Older binaries remain preserved but have this known affected-syntax defect.

Only `src/mps.cpp` changed among core source/header files since iteration10.
No new branching, LP numerical algorithm, heuristic or default search policy
is introduced in this release. The parsing correction is always active; the
previous search experiments remain optional.

## Predeclared public sweep

The [plan](PLAN.md) specifies seven existing cases plus ten new originals
from the official historical MIPLIB3 archive. Selection prioritizes small/
moderate cross-family diagnosis; it is not a representative random sample
of the 240-instance MIPLIB2017 benchmark. No failed case was replaced.
The [download manifest](../../datasets/milp-robustness-wave1/manifest.json)
retains official URLs and raw/model hashes.

One fixed profile for all models: recovery, guided incumbent improvement and
repair, delayed lifted cuts/compact equations/reduced bounds, and the bounded
eligibility-guarded binary-proof option. Budget 30s, node cap 250000, gap 1e-6,
external watchdog 45s. Sequential own runs precede all independent references.
The reference uses one thread, 5s and 1e-9 relative/absolute MIP gap. Reference
answers never enter the solver; these unequal budgets are NOT a speed contest.

### Corrected build outcomes

| Model | Outcome | Objective | Bound | Reported gap |
|---|---|---:|---:|---:|
| p0033 | Exact proof checked | 3089 | 3089 | 0.000% |
| enigma | Numerical completion | 0 | -9.9999999626e-8 | 0.00001000% |
| flugpl | Numerical completion | 1201500 | 1201499.8798 | 0.00001000% |
| stein27 | Numerical completion | 18 | 17.9999981 | 0.00001000% |
| markshare_4_0 | Exact proof checked | 1 | 1 | 0.000% |
| blend2 | No point, time limit | — | 7.3972011506 | — |
| binkar10_1 | Feasible, time limit | 6773.150024 | 6678.5655435 | 1.396% |
| egout | Numerical completion | 568.1007 | 568.1007 | 0.000% |
| gt2 | Feasible, time limit | 42649 | 13941.313483 | 67.31% |
| lseu | Numerical completion | 1120 | 1119.9991503 | 0.00007580% |
| mod008 | Feasible, time limit | 307 | 306.50646394 | 0.1602% |
| p0201 | Numerical completion | 7615 | 7614.9992384 | 0.00001000% |
| p0282 | Feasible, time limit | 266462 | 257121.91316 | 3.505% |
| misc03 | Feasible, time limit | 3360 | 3229.9996769 | 3.868% |
| misc07 | Feasible, time limit | 2920 | 1538.749846 | 47.29% |
| pk1 | Feasible, time limit | 31 | -1e-7 | 96.88% |
| rgn | Numerical completion | 82.19999923 | 82.19999072 | 0.00001023% |

The reported minimization gap uses `(objective - bound)/(1 + abs(objective))`.
Numerical completion is within the requested tolerance, not an exact rational
certificate. Only p0033 and markshare have independently recomputed exact
proofs here, using the restricted engine. A reference solution alone cannot
close our open bound. This is why mod008 and misc03 remain unfinished despite
matching completed reference objectives.

Both old/new sweeps have the same category counts. Wall-clock-driven restart
and heuristic budgets produce some different incumbents/bounds; this single
pair does not establish a performance improvement or regression from the parser
fix. Blend2's earlier 144s completion used a 180s protocol; failure to return
a point in this 30s profile is retained, not hidden by that historical result.

The corrected sweep has 13 completed HiGHS references and 4 reference timeouts.
Reference timeout incumbents are not called reference optima. The independent
exact checker validates Markshare even though the bounded reference run does
not complete. Full settings, points, traces, stdout/stderr and errors remain in
[baseline results](baseline-30s/results.json) and [corrected results](fixed-30s/results.json).

## Gates and audit

- CTest 9/9, including the new marker-domain group: 28 models on normal and
  proof-enabled paths, direct bound assertions, an infeasible domain, a no-row
  bounded case and invalid/unsupported-input rejection.
- Python checker/classifier tests 52/52. The final classifier explicitly allows
  the requested gap-limit accuracy instead of demanding tighter objective
  equality; two regressions cover min/max. This post-timing harness correction
  changes NONE of the 34 saved public classifications. Timed runners are archived.
- Generated binary/mixed MILPs 80/80 on the corrected build.
- [Audit](final-audit/AUDIT.json): both binaries/source identities and all 34
  saved result/reference identities checked; 52 retained cuts rechecked;
  four exact proofs recomputed across two models/two builds. Sixteen final
  points per sweep have independent original-row/bound/integrality/objective
  checks. No observed validation failure in the public sweep.
- General internal LP dual bounds and unsaved intermediate points are not
  independently certified by this audit. Limits are unfinished work, not
  correctness successes or claims that the public model is solved.

## Next work and scope

The [next experiment](NEXT_STEP.md) targets general proof strengthening,
starting with guarded objective-lattice bounds and retained open-gap cases.
Follow with broader predeclared holdouts and repeatability, then expand toward
the full benchmark under explicit resource limits. Keep improving input
semantics, numerical behavior and safe failure handling alongside performance.

The [robustness program](../../docs/MILP_ROBUSTNESS.md) records the user's
long-term target. The [official MIPLIB status](https://miplib.zib.de/) includes
open collection instances; no fast universal completion or competition rank
is promised. CPU runs stay local; no GPU/Kaggle upload is needed.

[Final state](FINAL_STATE.json) and [source snapshot manifest](SNAPSHOT_MANIFEST.json)
identify this release. Earlier archives and all baseline failures are preserved.

