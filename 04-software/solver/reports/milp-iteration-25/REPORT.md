# MILP iteration25 — stable private ranking, promotion rejected

17 September 2026. The generic ranking rule passes its stability contract and
correctness gates, but does not establish reliable useful coverage. Keep
`--pump-distance-stable-ranking` off. Continue with the staged control for the
next diagnostic. No 27-model timing wave is warranted after this screen fails
the predeclared reliability gate.

| 12-model screen, two runs/model/profile | Staged control | Stable ranking |
|---|---:|---:|
| Checked feasible points | 22 / 24 | 20 / 24 |
| Numerical/tolerance completions | 2 | 3 |
| Feasible with an open gap | 20 | 17 |
| No point within budget | 2 | 4 |
| Validation failures | 0 | 0 |

All **48 records and 42 returned final vectors** pass original-model checks.
There are no restricted exact-proof models in this focused screen. It is not
a fresh 27-model score. [The complete ledger](MODEL_LEDGER.md) retains every
objective, bound, gap, first-point time, status, node count and LP work value.
Raw phase/resource accounting remains in each result and `FACTS.json`.

## What changed

Only the private distance dive gains an opt-in two-pass ranking helper. Find
the true maximum integer fractionality, then choose the first original column
within absolute 1e-12, still requiring its score to exceed the unchanged integer
tolerance. No model-name/column-specific rule, reference answer, new time slice,
LP arithmetic change, global branching change or acceptance/proof relaxation.
The helper rejects invalid/nonfinite inputs. Fixed layout and unchanged
eligibility/tie membership define stability; arbitrary perturbation-boundary
or tied-column permutation invariance is not claimed. See
[the contract](../../docs/PRIVATE_DIVE_RANKING.md).

The retained misc07 vectors reproduce strict first choices 218 and 12. The
new helper chooses 12 for both, with the same ten-column anchored tie set.
These are our saved vectors passed only to a ranking helper, never injected
into measured MILP solves. In measured candidate runs, the helper executes
311 times and changes 16 selections relative to the strict rule on the same
point. An enabled flag alone does not establish performance causation.

## What the repetitions show

- **misc07:** control returns 3970 twice. Candidate misses once and returns
  3610 once, still with a roughly 58% gap. In the miss, the second private LP
  exhausts its deadline at 2681 pivots; the successful repeat completes it at
  2836. No different ranking decision has occurred before that failed cutoff.
  The earlier root-only diagnostic also finds 3610, but is not a substitute
  for repeated equal-budget success.
- **lotsize:** all four runs still have no integer point. Ranking does not
  resolve its later private-LP bottleneck.
- **danoint:** both controls and one candidate return 69.5. The failed
  candidate's pump fixing ends at 1862 pivots; successful runs complete the
  identical saved 521-coordinate target at 1876. This happens before staging.
  `DANOINT_FIXING_DIAGNOSIS.json` records matching target hashes. Ranking has
  made no different choice before the missed point; do not attribute this
  clock-sensitive loss to a demonstrated ranking mechanism.
- **p0201:** all four runs complete at 7615 with identical node counts.
  **mod008:** all four retain 307, but only one candidate completes; the other
  three retain a roughly 0.325% gap. There are no private-ranking calls on
  these completion paths. The extra completion is not established ranking gain.
- **blend2, rout, mas74 and gt2:** paired objectives are retained. Mas74 remains
  at 13588.5643; the older better-profile objective is not recovered.
- **eil33-2:** candidate is 1204.099899 twice; controls are 1204.099899 and
  1397.046538. **binkar10_1:** candidate 6787.820026 / 6796.770030 versus control
  6787.820026 / 6810.690026. **pk1:** controls are about 20 twice; candidates
  return about 28 and 31. These are incomplete solves and clock-dependent quality
  observations, not uniformly demonstrated ranking benefits.

The option is retained as an explained, tested experiment, not a new default.
Better fixed-vector behavior and one improved incumbent do not outweigh the
unresolved first-feasible reliability requirement. No failed run is erased,
and no best-of-profile union is presented.

## Protocol and correctness

`PLAN.md`, `SCREEN.json`: same Release executable, staged control versus add
only stable ranking, 30 seconds/model/profile, 250000 nodes, gap1e-6, two
alternating-order repeats. Own solves serial; independent five-second HiGHS
references afterward. Reference times are validation, not matched speed races.
All 12 models are reused development cases. `WAVE.json` was declared but not run.

Before timings, 25 CTest groups, 176 Python tests, 320 generated runs and 100
retained exhaustive cases pass, including the candidate-enabled generated
profiles. The inherited LP fixture, MPS/domain and disabled-option gates pass.
New tests cover anchored ties versus pairwise tie chains, just-outside cases,
small perturbations, negative/translated domains, MIN/MAX, permutations, empty
domains, nonfinite input, prerequisites and zero/exhausted budgets. Inherited
staged-LP tests check failed-primary/alternate ownership and invalid bases.
Five additional parity pairs pass (three against frozen24 and two inactive
features). Nine actual root-only strict-original/staged/stable diagnostics pass
their independent checks. Root-only diagnostics still have clock-limited
heuristic slices; only the saved-vector ranking replay is fixed numerical work.

The complete saved-run audit passes after timing. It verifies all current
source snapshots and exact model/result hashes, statuses, final vectors,
frontier/cut/lattice checks and inherited heuristic telemetry. It explicitly
records LF-normalized equivalence for the historically unchanged reader rather
than pretending checkout CRLF bytes match an old LF fingerprint.

## Reproducibility repairs and limitations

The checkout moved and its former x64 compiler/runtime was absent. A verified
project-local matching GCC14.2 toolchain restores execution; a fresh build
avoids old absolute-path caches. The first sandboxed CTest launch failed at
process startup; its logs remain. The full gate passes outside that sandbox.

The first screen attempt stopped before any solve because Git had converted
benchmark line endings. All27 model files were recovered from retained
archives with **exact original manifest hashes**, including two mixed-ending
files. The prior checkout bytes are preserved in `dataset-byte-recovery/`;
manifests were not edited. Scoped `.gitattributes` rules prevent recurrence.

Host: Intel i5-12450H, 12 logical processors, Windows; see `HOST.json` and
`ENVIRONMENT.md`. Shared desktop load/clock limits remain, including light
filesystem review during initial runs. No controlled thermal/load claim or
process peak-memory measurement is made. Limits remain cooperative. Historical
timings and the old ten-completion wave are not fresh scores on this host.

Measured CLI SHA256:
`d1fccd2992876b8faf47bac5c68f0a1fe096878658c8e5707d485231fd1d7022`.
The final archive preserves the executable, runtime DLLs, source, raw outputs,
failed attempts, checks and identities. Frozen24's executable is unchanged.
CPU-local only; no GPU run, Kaggle upload or external submission.

## Next objective

Iteration26 retains exact later expensive/failed private LPs for lotsize and
diagnoses the separate danoint fixing deadline. Independently replay those
private models before choosing a bounded same-slice alternate policy. Private
infeasibility remains local, and no replay solution/bound enters measured search.
Iteration27 then measures completion/quality; iteration28 checks untouched
cases and a coherent candidate profile. None is an automatic success milestone.
