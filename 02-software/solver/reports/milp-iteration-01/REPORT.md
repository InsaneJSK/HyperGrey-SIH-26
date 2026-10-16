# V2 MILP iteration 01 — first-incumbent improvement

14 September 2026. This is a bounded CPU MILP iteration after the first audited
Kaggle P100 return, not a claim that the full submission is finished.

Update: [the second Kaggle return](../kaggle-gpu-02/REPORT.md) now verifies this
snapshot on Linux/P100 and confirms the binkar10_1 incumbent in 13.79 seconds.
The initial handoff wording below is historical; no unchanged rerun is needed.

## Outcome

`binkar10_1` now returns an independently checked feasible solution at objective
**7297.320029**, within the same 30-second/10,000-node limits. The original V2
and no-pump ablation returned no incumbent in the paired exploratory run.
The retained binary reproduced that candidate in two 30-second repeats;
the independent HiGHS reader measured zero row/bound and integrality violation.
This is a feasibility improvement, not an optimality or speedup claim.

| Modern MILP | Previous V2 | Iteration outcome | Completion |
| --- | --- | --- | --- |
| binkar10_1 | No feasible answer in 30 seconds | Feasible 7297.320029; first incumbent 20.75–21.74 s in two retained-binary repeats; gap approximately 8.79% | Incomplete |
| blend2 | No feasible answer in 30 seconds | Still no feasible answer | Incomplete |
| markshare_4_0 | Feasible approximately 33, large gap | Same approximately 33; 10,000-node limit | Incomplete |

HiGHS found a better `binkar10_1` incumbent, 6746.760023, within its 30-second
reference run, but also timed out. Do not call either incumbent a proven optimum.
The reported MILP gap is `(incumbent - lower_bound)/(1 + abs(incumbent))` in
normalized minimization sense. Different runtime conditions change tree progress.

## What changed

- Independently implemented L1 feasibility pump: integer rounding, sparse LP
  projection, deterministic cycle perturbations, and fixed-integer polishing.
  Supports binary and general integers, including negative/interior targets.
- Pump budget: at most 40 projections, within min(5 seconds, remaining global
  time). Root cut processing reserves up to five seconds for the pump. All
  auxiliary LPs use the project's own sparse simplex.
- If a new cut LP misses its time/numerical checks, restore both its prior
  model and validated LP result/basis. Report discarded attempts as
  `cut_rollbacks`; their bounds do not enter the search.
- Heuristic distance objectives never enter branch-and-bound proof bounds.
  Every accepted candidate must satisfy the unchanged original-model absolute
  feasibility and integrality tolerances of 1e-7. Nonfinite coordinates are
  explicitly rejected before rounding.
- Diving and dense-recovery sub-solves now share their allocated heuristic
  deadline rather than receiving the entire remaining global budget. Limits are
  cooperative and can overshoot slightly due to setup/checking overhead.
- Added `--no-pump`, pump counters and `first_incumbent_seconds` to JSON output.
  `--no-heuristics` also disables the pump.
- Added analytical regressions for interior/general and negative integers,
  maximization, fractional bounds, cycling/reproducibility, infeasible rounding,
  zero time, ablation controls, and separation of incumbent from proof bound.
- Packaging now selects and verifies the matching CPU evidence explicitly.
  Earlier source, binary, notebook and GPU evidence remain preserved.

The mathematical basis is
[Fischetti, Glover and Lodi, The Feasibility Pump](https://www.dei.unipd.it/~fisch/papers/feasibility_pump.pdf).
No optimizer source or reference solutions are incorporated into the core.

## Experiments retained, including unsuccessful ones

Local `experiment-01/` contains sequential baseline/pump/no-pump comparisons
on all three modern MILPs, with source/input/binary hashes and independent
candidate checks. The initial pump found `binkar10_1` at 14.42 s with 8.7579%
final gap. Timings are exploratory, not controlled repeated speedup evidence.

`experiment-02/` tried deeper backtracking and a pump-guided dive seed. It still
failed to find a `blend2` incumbent and was not retained. `experiment-03/`
tried 200 projections and wider perturbations; it also failed on `blend2` and
was not retained. Their exact sources, binaries and results remain on disk.
An additional repeat of the first candidate failed to find the incumbent:
`final-ablation/` preserves that failure. Its shrinking 20%-of-remaining pump
budget was too fragile after expensive root processing. `experiment-04/` tried
moving the pump before cuts and a smaller cut allowance; neither of its two
pump runs found the incumbent, so early placement was not retained.

The final policy reserves up to five seconds at the end of root cut processing,
and does not shrink that allocation by another factor of five. `experiment-05/`
contains two sequential 30-second runs of the retained binary: both independently
verified feasible at 7297.320029; both still timed out without proving optimality.
Their first-incumbent times were 21.7381 and 20.7504 seconds. This is limited
same-machine repeat evidence, not a guarantee on all hardware or instances.
The subsequent complete CPU gate reproduced the same independently checked
candidate at 19.7005 seconds, with final gap 8.8121% and bound 6654.185061.
No instance-name-specific logic was added.

## Validation and identity

The complete retained-binary CPU evidence is in `validated-cpu/`, including raw
candidates, independent references, generated tests, CTest log and summary.
All 230 generated cases, all 12 selected Netlib LPs, all four historical MILPs,
and all four application cases passed. QPLIB remains 2/3; modern MILP completed
count remains 0/3. All six CPU scale checks (1,000, 100,000, and 1,000,000
variables, one/four threads, one repetition each) passed. QPLIB 9002 and all
modern MILP incompletes are preserved. See `validated-cpu/summary.json` for counts.
The earlier `final-cpu/` is the first candidate's full gate, not current evidence.

Retained executable SHA-256:
`696b8518fdec9325fb75231bbe21e02b08e37b3722bcb60e0ac4e4b428e0d22b`.

Previous executable SHA-256:
`9740e7ee673fd65062dde2769895d0d7be55b7bf35ef74d839147a12fd8b3aab`.

The previous executable remains at `build-v2/solver_cli.exe` and a copied
baseline is in this report directory. The new build is `build-milp-iter1`.

## Kaggle and next work

The new separate delivery is `kaggle_delivery/milp_iteration_01` beside the
project. Upload its matching source ZIP as private input and import its small
notebook. Run All and return `sih26119_kaggle_results.zip`. Do not mix the old
notebook with the new source ZIP. No manual paths or second environment needed.

The numerical CUDA/QP/LP implementations are unchanged. New GPU-memory
diagnostics are included, but this snapshot still needs its own Linux/Kaggle
run. The old P100 measurements apply to the archived snapshot, not this build.

Next priorities: improve incumbent quality and bound progress; investigate why
the search does not find a `blend2` incumbent (the model is not declared infeasible);
evaluate extending basis reuse across new cut rows to reduce cold root LP solves;
then run a separate constrained-QP
iteration on QPLIB 9002. Industrial validation, broader benchmark coverage,
repeated equal-accuracy GPU measurements and final submission material remain.
No competition percentile or selection outcome is guaranteed.
