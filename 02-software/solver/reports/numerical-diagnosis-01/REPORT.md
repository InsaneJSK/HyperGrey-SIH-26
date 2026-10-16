# Continuous numerical diagnosis and isolated LP candidates

The default bandm failure is traced to an exactly singular basis created after
an inaccurate small pivot. A selective stable ratio candidate completes the
retained LP and preserves the other tested LP pivot counts. QP 9002 exhibits
repeated short Newton steps and oscillating feasibility; no QP fix or accuracy
improvement is established in this study.

## LP failure and independent diagnosis

The logging-only executable reproduces default/refined bandm failure at 200
pivots and compact/refined completion at 1279 pivots. At iteration 194, an
eta-based direction reports a pivot of 2.7228116161127502e-8. The factorization
at iteration 200 rejects an exactly zero pivot column.

The captured 610-by-610 basis has canonical rows 500 and 501 exactly opposite,
both with zero RHS. A nonzero vector with one in both positions has exactly
zero product with every basis column. `analysis/EXACT_SINGULARITY.json` checks
this over the exact binary64 values using rational arithmetic. It proves basis
singularity, not LP infeasibility. Independent SVD reports numerical rank 609
and a smallest singular value about 9.53e-28. The original LP has a separately
checked feasible optimum; no reference result enters the engine.

## Separately declared candidates

| Candidate | bandm default/refined | bandm compact/refined | All 18 checks | Decision |
|---|---|---|---|---|
| Refresh current basis before a weak pivot | numerical_error at 273 | optimal, 1279 pivots | 16 pass; two failures | Reject as insufficient |
| Two-pass stable ratio on all non-Bland primal choices | optimal, 2818 pivots | optimal, 1170 pivots | 18 pass | Works, changes many trajectories |
| Two-pass ratio only when original selected pivot is weak | optimal, 3254 pivots | optimal, 1279 pivots | 18 pass | Select for opt-in integration |

The refresh candidate encounters another weak pivot immediately after fresh
factorization: about 2.23e-9 at a nearly zero basic value. Its next point has
negative basic value about -1.045, so a refresh alone does not solve the issue.
The full ratio rule completes the set but changes many already-successful LP
pivot counts. The selective rule activates nine times in each standard bandm
run and zero times on the other 15 default LPs or compact bandm. Their previous
pivot counts are retained. This is a finite reused-input observation, not a
guarantee of parity on unseen LPs or a timing improvement.

The rule uses the existing tolerance to bound the first-pass step and selects
a larger eligible pivot in the second pass. It is based on the established
Harris ratio-test idea, independently implemented here; see
[Huangfu and Hall, section 2.2.2](https://www.maths.ed.ac.uk/hall/HuHa13/ERGO-14-011.pdf).
Original-model acceptance tolerances are unchanged. The selective threshold
is a numerical heuristic, not a condition-number certificate.

## QP 9002 findings

| Tolerance | Specialist exit | Iteration | Original scaled violation at exit | Absolute violation at exit | Steps shorter than 1e-4 |
|---|---|---:|---:|---:|---:|
| 1e-7 | optimal | 180 | 8.57e-8 | 2.3810 | 71 |
| 1e-10 | time_limit | 290 | 4.35e-6 | 1076.84 | 125 |
| 1e-12 | time_limit | 341 | 6.90e-6 | 421.40 | 149 |

The specialist's last tight-tolerance points fail independent original-model
KKT checks. They are discarded and ADMM starts within the existing shared
30-second budget. The final dispatched tight runs also time out. These
logging-only runs have different cutoff iterations from the earlier measured
runs; no finite speedup or deterioration is inferred from their wall times.

There are no zero-PCG-step iterations. The trace does not support the initial
suspected mechanism that the 1e-12 inner residual floor simply prevents further
linear solves. Instead it shows alternating small-gradient points and much
larger feasibility residuals, with many backtracked steps and expensive PCG
solves. A tiny dual gap alone remains insufficient for acceptance.

Next capture line-search objective differences, directional derivatives and
active-set changes on the same steps. The absolute allowance in the current
Armijo check may admit decreases near a small expected gain, but that causal
hypothesis has not yet been tested. Investigate it before proposing a line
search, active-set or warm-fallback change; do not combine all three at once.
Domain-appropriate absolute tolerances remain an external input.

## Evidence and scope

Plans precede each candidate. Source copies, hashes, build logs, six original
diagnostic calls, three sets of 18 candidate calls, raw stdout/stderr and
independent checks remain separate. No working QP numerical source changed.
The selected LP policy proceeds to [integration and full validation](../lp-pivot-iteration-01/PLAN.md)
as `--stable-primal-ratio`, off by default. No broad MILP score, GPU result,
default promotion or submission-readiness claim follows from this diagnosis.
