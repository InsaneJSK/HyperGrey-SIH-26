# MILP iteration 02 — focused branching experiment

Update: the [Kaggle return is now audited](../kaggle-milp-01/REPORT.md).
The notebook works, but reliability is not an overall winner; blend2 exposes
an early tree-LP iteration-limit exit. The original experiment description and
local results below remain historical evidence, not the latest ranking.

The user requested a faster move to hard MILP experiments on Kaggle. This
iteration adds opt-in reliability-style branching and a dedicated notebook;
it does not require the pending QP-only notebook to be run first.

The new strategy learns directional pseudocosts from independently checked LP
relaxations, then uses them to rank fractional variables. It probes at most four
candidate variables per selection, with at most 128 trial LPs per solve. Each
trial has a 250-iteration / 0.5-second ceiling. The overall probe allowance is
the smaller of 15 seconds or 15% of the solve limit. All work shares the global
deadline. Failed or incomplete probes do not supply pseudocost observations.

Probe scores, including infeasibility preferences, only select a branch. They
do not replace tree bounds or prune nodes. A probe can supply an incumbent only
through the unchanged original-model integrality/feasibility check. Parent LP
bounds are retained when the chosen branch is expanded. Maximization signs,
general-integer distances, zero budgets and control-mode behavior have explicit
C++ regression tests. The established fractionality mode remains the default.

The mathematical background is
[Achterberg, Koch and Martin, Branching Rules Revisited (2005)](https://www.zib.de/userpage/koch/biblio/paper/achterbergkochmartin2005_pp.pdf).
The implementation uses our sparse LP core; no external optimizer enters search.

## Local smoke evidence — not a final performance study

Both strategies passed 40 exhaustive binary and 40 mixed continuous/general-
integer cases: 160 total checks. All three CTest groups passed. The shared LP
and QP numerical implementations are unchanged from the previous QP iteration.

One sequential pair per hard model used 15 seconds and 250,000 nodes for each
strategy. Unlike older 10,000-node runs, both controls have the same higher cap.

| Model | Fractionality objective | Reliability objective | Interpretation |
| --- | ---: | ---: | --- |
| markshare_4_0 | 20.999999976 | 12.999999984 | New strategy found a better independently checked incumbent |
| blend2 | None | None | Neither found an incumbent in this short run |
| binkar10_1 | 7127.780038 | 7127.780038 | Same verified incumbent, gaps approximately 6.67% |

All six runs hit the time limit; no hard model was proved optimal. All four
returned incumbents passed independent original-MPS checks. The local reference
worker was run with zero solve time to parse/check candidates; it did not provide
new optimum comparisons. Full raw vectors, commands, hashes and traces are in
`local-smoke/`. No invalid candidate or process-error run was observed.

## Kaggle handoff

Separate delivery: `kaggle_delivery/milp_iteration_02`. Two small code cells:
unpack the matching private-input source ZIP, then build and run. CPU only;
enable Internet but GPU quota is unnecessary. The proposed experiment uses
180 seconds and 250,000 nodes per strategy/model, six sequential runs total,
plus 160 generated checks and 30-second references. Allow about 20-25 minutes.

Download and return **sih26119_milp_results.zip**. Failures also produce that ZIP.
It includes each verified candidate, first-incumbent time, incumbent improvement
history, final bound/gap, nodes, LP iterations and branching-probe costs. These
data decide whether the extra branching work is worthwhile per instance.

This is an opt-in experiment, not a claimed overall MILP improvement or a finished
submission. The new notebook contains the latest QP source but does not repeat
the QP/public-GPU sweep. Prior builds/notebooks and both audited P100 returns
are preserved. Current build: `build-milp-iter2`; prior numerical baseline:
`build-qp-iter1`, also copied to this report folder before edits.
