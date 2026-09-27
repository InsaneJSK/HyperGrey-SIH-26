# MILP iteration08 — Binkar reported gap below1%, locally

15 September2026. Final separate build: `build-milp-iter8c`. The new opt-in
delayed-cut schedule keeps Binkar's best incumbent6747.310015 and reduces its
reported numerical gap from1.21447% to0.95713% in the fresh180s comparison.
This is a21.19% reduction in the remaining reported gap, **not** a21% speedup,
not exact optimality, and not repeated broad performance evidence.

## Final equal-budget comparison

Same final binary, same recovery/repair/guided heuristic settings. The only
strategy difference is `--late-lifted-covers`. Two sequential models, one run
per profile/model, alternating profile order: p0033 guided then delayed; Binkar
delayed then guided. Limits180s,250000 nodes,gap1e-6. References and independent
cut checks ran only after all four timed runs. No external candidate was seeded.

| Model | Mode | Objective | Final lower bound | Reported gap | Solve seconds |
|---|---|---:|---:|---:|---:|
| Binkar | Guided control | 6747.310015 | 6665.353567 | 1.21447% | 181.177 |
| Binkar | Delayed lifted cuts | 6747.310015 | 6682.719904 | 0.95713% | 180.239 |
| P0033 | Guided control | 3089 | 3089 | 0 | 0.077 |
| P0033 | Delayed lifted cuts | 3089 | 3089 | 0 | 0.093 |

Both Binkar runs remain `time_limit`. Both P0033 runs are `optimal` and finish
before any restart:277 nodes, no new cuts. Small timing differences are not a
speedup claim. Cooperative time-limit overruns are preserved above; the measured
solver times are not rounded down to the nominal180s limit.

Binkar's delayed run finds6747.310015 at61.46s, restarts once at90.017s after
2117 nodes, and retains that same-run incumbent. Its inherited global lower
bound is6662.370749. The new root reaches6662.930958, and subsequent search raises
the final bound to6682.719904. Total nodes5022 versus5684 in the control: a
stronger final bound does not imply more nodes processed. There are25 new
retained lifted cuts,43 total cuts including ordinary covers. Separator work
takes0.175s; root reoptimization time is separate and included in solve time.

## What changed and why

Saved diagnostics showed weak/slow bound progress, not failed global LP recovery.
Binkar has2298 columns,170 binaries,1026 rows, and ten17-binary capacity rows.
We added a limited exact-valid row separator: enumerate all feasible assignments
of a small binary capacity row, strengthen promising minimal covers by sequential
up-lifting, then check each proposed cut again against every row-feasible point.
No instance name, published answer or reference incumbent enters the algorithm.

The [initial direct-cut experiment](DIRECT_EXPERIMENT.md) strengthened the bound
but regressed Binkar's incumbent to6775.20 and gap to1.37765%. P0033 also became
slower. That experiment is preserved and NOT promoted. The subsequent delayed
schedule lets the established incumbent search run first, then strengthens the
relaxation during a single half-time full-domain restart.

The restart covers the ENTIRE original domain, including every old live/deferred
node. It carries only the already valid global minimum bound and the independently
checked same-run incumbent. Global time, total nodes and spent heuristic budgets
are not reset. This may repeat search work; it is not guaranteed to help.
The earlier exact markshare engine and all existing defaults remain unchanged.
See [method, arithmetic scope and controls](../../docs/MILP_LIFTED_COVERS.md).

## Verification and limitations

- Final CTest6/6, including400 new exhaustive signed/dyadic row cases (391
  generated cuts checked), deterministic min/max restart/incumbent tests and
  budget/domain/boundary controls. Earlier600 exact-proof and180 heuristic
  structural cases remain passing.
- Final generated240/240 across guided, delayed and direct-cut-plus-exact-proof
  profiles. These are80 generated models under three profiles, not240 distinct
  public models. They export no new lifted cuts: their role is fallback and
  general solver regression. Cut coverage comes from dedicated exhaustive tests
  and public retained cuts.
- Independent Python unbounded-integer enumeration confirms all25 final-run
  cuts against an independent MPS reader's parsed binary64 rows. This is not
  arbitrary-precision interpretation of the original decimal text.
- All four final candidates pass independent original-MPS checks.
- [Additional audit](late-audit/AUDIT.json) confirms all25 cuts again,74 timing-
  source identities, hashes/commands/budgets/trace accounting, and15 captured,
  restart and final vectors. Maximum audited violation is below1e-8; the Binkar
  carried and final point has about6e-9 violation under the unchanged1e-7 gate.
- Diagnostic tests15/15, parser3/3, exact checker9/9 and cut checker6/6 pass.
- Final guided numerical results match iteration07 on80 generated runs,
  excluding timing/new fields: [nonregression](NONREGRESSION.json).
- Markshare's original-literal independent exact-proof sentinel still passes
  at objective1/gap0. HiGHS independently proves p0033's numerical3089. Its
  Binkar30s reference times out with6746.760023, not a proven optimum.

Valid row cuts do not turn the general floating-point MILP engine into an exact
proof system. The cut helper is limited to2–20 binary variables per source row
and guarded exact representations of parsed binary64 coefficients. Unsupported
rows/arithmetic and interrupted candidate checks cannot export an unchecked cut.
The core still uses existing numerical LP bounds and original feasibility gates.
There is no new blend2 long run, QP/GPU sweep, million-variable MILP evidence,
industrial validation or full benchmark-library coverage in this cycle.

## Saved evidence and reproduction

Final CLI SHA256:
`bea877af55f4d790f692640f1787b750627d0525797af2e7f0067e655cd9e148`.
Windows11, Intel i5-10210U, GCC14.2, CMake3.30.4 Release, CUDAOFF.
[Protocol/source hashes](late-180s/metadata.json),
[raw result table](late-180s/results.json),
[summary](late-180s/summary.json), [cut checks](late-180s/cut_checks.json),
[final snapshot state](FINAL_STATE.json). Separate final-source/ and
final_solver_cli.exe preserve this exact build. Earlier root/direct prototypes,
failed experiments and all iteration07 source/binaries remain intact.

From the project root, reproduce the final strategy with the preserved binary:

```powershell
./build-milp-iter8c/solver_cli.exe datasets/miplib2017/binkar10_1.mps --milp --json --lp-recovery --improve-incumbent --repair-candidates --late-lifted-covers --time-limit 180 --node-limit 250000 --gap 1e-6
```

For a fresh full comparison, use the validation command in the method document,
add `--late`, and choose a NEW output directory. Do not rebuild archived binaries
in place. No Kaggle run, GPU allocation or user result upload is needed.

## Submission position and next work

This is a useful measured bound improvement while preserving the incumbent,
but it is one paired run per model for the final schedule. The new modes remain
opt-in. Next: repeat the final schedule across varied time budgets/public models,
then target Binkar's remaining bound/incumbent gap. Markshare proof closure and
the earlier blend2 numerical result remain separate achievements. Industrial
requirements, broader solver scope and submission claims still need their
existing validation gates; this does not guarantee a competition ranking.
