# MILP iteration06 — objective improvement, proof gap still open

Completed locally on15 September2026. No GPU, Kaggle notebook or user upload
was needed. Previous binaries and all unsuccessful evidence are preserved.

## Main result

The new opt-in `--binary-meet` root heuristic reaches a markshare_4_0 point with
objective exactly1 and zero original constraint/integrality violation. The full
solver reaches this point at0.2411s. Three later root-only repetitions reproduce
it at0.1969–0.1982s. These are one-model observations, not a general MILP speedup.

| Equal180s/250000-node budget | Guided control | Guided + binary meet |
| --- | ---: | ---: |
| Final objective, approximately | 5 | 1 |
| Final status | node_limit | node_limit |
| Processed main nodes | 250000 | 250000 |
| Best global bound | -1e-7 | -1e-7 |
| Reported gap | 83.333335% | 50.000005% |
| Total solver time, single pass | 118.9473s | 103.8847s |

The final candidate is numerically0.999999998 after a later neighborhood update,
with absolute violation about2e-9. Do not present that numerical crumb as an
improvement below1. The exact1 point from binary meet has zero violation.

The reported gap uses `(incumbent-bound)/(1+abs(incumbent))`; it is not a standard
absolute-objective-denominator percentage. Neither run proves optimality.
The independent30s reference run also times out, with incumbent3, not a proven
optimum. A better valid point does not establish an overall reference-solver win.

## Implementation and limits

The detector supports at most36 movable binaries and8 rows, optionally with a
single eliminable continuous variable per equality. It rejects unsupported
structures, including the actual blend2 and binkar10_1 models. No instance name,
known answer or reference vector enters the algorithm. See
[method, resources and proof boundary](../../docs/MILP_BINARY_MEET.md).

It enumerates32768 states per half on markshare and visits2990204 range-tree
nodes. The root slice used0.2406s of an allowed5s. Candidate reconstruction and
the unchanged original-model acceptance gate remain mandatory. Completed
floating-point enumeration exports only an incumbent, never a proof bound.
General LP/MILP proof behavior and LP/QP/CUDA numerical modules are unchanged.

The preceding [reserved coupled-neighborhood experiment](RESERVED_REPORT.md)
fixed late-call scheduling but did not establish an improvement over our best
earlier results. Preserve it as a separate experiment, not the source of this
gain. Competing application activity and baseline variability were observed;
do not infer a reliable wall-clock speedup from the timings above.

## Verification and identity

- CTest4/4, including180 new structural cases compared with exhaustive enumeration.
- Existing generated gate240/240:80 models under three configurations.
- Diagnostic tests15/15; result-parser tests3/3.
- Focused hard comparison: both final candidates independently verified; no
  unsafe/error run. Seven captured/final vectors pass fresh original-MPS checks.
- Three root-only repeats: six independent final/root-vector checks pass, with
  zero violation on all three binary-meet points. These are repeated checks on
  one model, not six new instances or repeated full-search timings.
- Default guided outputs exactly match iteration05 on80 generated models for
  status, objective, primal, bound, gap, node count and LP iterations.

Final executable: `final_solver_cli.exe` / `build-milp-iter6b/solver_cli.exe`.
SHA256: `65686ab54dd8e073989f9a93f9e75bbb8d06ba4143b1ca6d639307360f7d007a`.
Numerical source: `final-source/`; run identities: `meet-180s/metadata.json`.
Raw results: `meet-180s/`; fresh audit: `meet-180s-audit/AUDIT.json`;
repeats: `root-repeats/CHECKS.json`; prototype: `PROBE_CHECK.json`.
Later documentation and repeat-check script additions are not part of the
original timing metadata; numerical source hashes remain matched and verified.

## Submission implications and next work

This adds a tested structure-aware C++ algorithm and a substantial incumbent
improvement on a previously difficult public model. It remains opt-in; the
best historical binkar incumbent6747.31 and verified blend2 objective7.598985
are retained as separate earlier evidence, not claims about this latest binary's
unrun full comparisons on those two models.

Next local work should target safe proof-gap closure and broader structural
tests. An exact-arithmetic completed-search certificate is a possible follow-up,
but it is NOT implemented: it needs explicit arithmetic/domain/overflow checks,
complete-search accounting and adversarial proof tests before any bound export.
Binkar still needs general LP/root-pump robustness and bound/search improvements.
MIQP, NLP, MINLP, nonconvex QP and industrial million-variable coverage remain
outside implemented/established scope. No ranking or top0.1% claim is justified.
