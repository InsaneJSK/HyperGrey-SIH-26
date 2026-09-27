# MILP iteration27 — completion trade-off, restart deferral rejected

17 September 2026. Retain the staged control with its existing restart policy.
Suppressing the restart improves mas74's bound and reduces mod008's work, but
weakens binkar10_1's bound in both repetitions. The predeclared gate requires
an improvement without a material counterpart regression; that gate fails.
No larger comparison wave is warranted. Defaults remain unchanged.

| Four-model screen, two runs/profile,30 seconds | Stage | Retain tree |
|---|---:|---:|
| Checked feasible points | 8 / 8 | 8 / 8 |
| Numerical completions | 4 | 4 |
| Feasible with open gap | 4 | 4 |
| Validation failures | 0 | 0 |

The candidate adds only existing `--restart-nodes 250000`, equal to the node
limit, so the node-limit check precedes any optional restart. It keeps the
original frontier through the run. No cut formula, bound formula, numerical
tolerance, heuristic allowance or solution acceptance changed.

## What improved and regressed

- **mas74:** both profiles retain13588.56430256. Candidate bounds are
  10949.295671 /10947.673598 versus10907.264213 /10905.288271. Gaps improve from
  19.731% /19.745% to19.421% /19.433%. This is bound progress, not an improved
  integer plan or recovery of the older better incumbent.
- **binkar10_1:** candidate objective6789.670035 repeats; control objectives
  are6810.690026 and6787.820026. The candidate wins one pairing and loses the
  other. Its bounds6658.021652 /6657.892748 are below the controls6677.972221 /
  6677.755233 in both repetitions. One candidate gap is slightly better and
  one materially worse; there is no repeated objective/gap gain.
- **p0201:** all four solves complete at7615 with4196 nodes.
- **mod008:** all four complete at307. Candidate uses8781 nodes twice versus
  16619 /16004 under the control. This useful reduction does not erase the
  binkar bound regression or establish universal superiority.

[The ledger](MODEL_LEDGER.md) records each objective, bound, gap, first-point
time, total time, status, node and LP-iteration count; phase work and restart
counts remain in `FACTS.json` and raw results. No best-of-profile union or
timeout-derived speedup is reported.

## Correctness and protocol

The core and binary are unchanged from26. Its full25-group CTest,176 Python,
320 generated and100 retained exhaustive gate is reused by binary hash,
rather than rerunning identical checks without a new change. Additional
fixed64-node frontier comparisons use forced restart at node2 versus deferred
restart: p0033 and markshare_4_0 retain restricted exact proofs under both;
gt2 and lseu retain honest node limits. The latter cases exercise actual
restarts in the control and zero in the candidate. Eight records pass
independent frontier/cut/lattice/status checks.

Then the16 timing runs use alternating profile order, serial own solves,
30 seconds,250000 nodes and1e-6 gap. Independent five-second HiGHS validation
follows all own runs. It is validation rather than a matched performance race.
All24 records and20 returned final vectors pass the saved-run audit, including
exact source/model/result identities and original-model acceptance checks.
All models are reused development cases. Shared desktop clocks/load remain
a limitation; process-memory monitoring begins separately in28.

CLI SHA256:
`f74d9fe31411ec2c94452eb302b1967ad8bf85be44df3d6d4d177e93a162cf2c`.
The same binary is frozen here with the source, runtime dependencies, measured
plans, raw results, gate reference and explicit retained-profile decision.

## Final evaluation decision

Use the staged profile for28, with stable ranking and alternate reserve off
and the normal restart policy retained. This is an experimental evaluation
candidate, not an assertion that reliability is solved or a release promotion.
Select it before viewing the six predeclared untouched-model outcomes.
Recheck all27 development cases, a default-profile subset, artificial
transformations and process limits on the same binary. Submission LP/QP/GPU,
industrial validation and packaging tracks remain separate.
