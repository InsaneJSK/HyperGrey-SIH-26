# Iteration29 — verified local certificates avoid phase one, without MILP coverage gain

17 September 2026. Keep `--private-dual-certificate` experimental and off by
default. The numerical shortcut works on the retained private LPs and avoids
phase one during both lotsize observations. The repeated MILP screen does not
establish a useful-point or completion gain. All 48 records and 44 final vectors
pass the independent checks. This is not a new 27-model score or release promotion.

## What was established and implemented

The isolated diagnostic reproduces the exact no-entering-column rejection
after one pivot for the expensive fixture and zero pivots for the failed
fixture. The four captures represent two repeated local LPs, not four models.
Their candidate rows pass exact rational checks of every captured binary64
canonical column and the original private LP domains. References separately
corroborate local infeasibility. No reference result enters search.

The guarded implementation accepts only bounded integer coefficient and
multiplier arithmetic, exact signs, and a strict contradiction enclosed
outward on the original LP coefficients and bounds. Uncertain/noninteger,
nonfinite, overflowed, incompatible or expired cases keep the existing
fallback. It is enabled only in compatible private heuristic LPs. Local
infeasibility cannot prune the global MILP, produce an incumbent, or replace
the retained parent basis. See [the method and limits](../../docs/PRIVATE_DUAL_CERTIFICATE.md).

| Saved LP | Existing adaptive pivots | Certificate pivots | Phase-one pivots afterward |
|---|---:|---:|---:|
| Expensive, both captures |1221|1|0|
| Failed, both captures |1222|0|0|

These are diagnostic work counts. Logging affects the diagnostic executable;
no finite elapsed-time speedup is claimed from that comparison.

## Repeated thirty-second screen

Twelve reused development models, two observations per profile, rotating
serial profile order. Both profiles use the exact same new executable and
the frozen28 staged flags; the candidate adds only the new option. Each solve
has 30 seconds, 250000 nodes and 1e-6 relative gap. The watchdog allows 45 seconds
and samples a 1536 MiB process-commit threshold. References run afterward with
their separately labeled five-second validation budget.

| Outcome | Staged control | Certificate candidate |
|---|---:|---:|
| Observations |24|24|
| Checked feasible points |22|22|
| Numerical completions |4|4|
| Feasible but incomplete |18|18|
| No incumbent at limit |2|2|
| Local certificate attempts |0|41|
| Accepted local certificates |0|35|

Both p0201 and mod008 complete in both repeats and both profiles. Lotsize
remains without an integer point in all four observations. All 35 accepted
certificates occur in lotsize; the six rejected attempts occur in misc07.

| Lotsize observation | Control | Candidate |
|---|---:|---:|
| First repeat: checked private LP points |11|37|
| Second repeat: checked private LP points |7|34|
| First repeat: private phase-one pivots |1483|0|
| Second repeat: private phase-one pivots |1220|0|
| First repeat: tree nodes |667|782|
| Second repeat: tree nodes |624|812|

The same private time slice achieves more checked steps, but a fractional
private point is not an integer solution. Total MILP pivots can increase as
the solver uses the saved work elsewhere; they are not a proxy for completion.

Observed solution quality does not support promotion. Binkar candidate
objectives are 6810.6900 in both repeats, versus 6808.5000 and 6784.2200 for the
control. Pk1's second candidate observation returns 35 versus 31 for the control.
Neither model attempts a certificate or a private distance LP in these runs.
Therefore these differences cannot be attributed to certificate arithmetic;
they expose variability in the surrounding time-limited search. Bound changes
also vary across observations. Preserve them without claiming a causal loss
or a reliable overall speed improvement.

The [complete ledger](MODEL_LEDGER.md) includes each objective, bound, gap,
first-feasible time, nodes, pivots, certificates, memory and validation result.
Peak observed working set is 188.484 MiB; peak commit is 190.012 MiB. These are
process observations on this small screen, not arbitrary-scale guarantees.

## Correctness and retained failures

- 26 CTest groups pass, including 24 transformed local/alternate/budget cases
  in the new certificate group and a fractional-coefficient fallback case.
- 176 existing Python gate tests and eight new offline verifier tests pass.
- 1600 generated floating-point operand pairs give 3200 independently checked
  exact-rational product/sum enclosures, including overflow and underflow.
- 320 generated MILP runs and 100 retained exhaustive cases pass.
- Four fixed-work feature-off comparisons retain the older control semantics.
- All 48 screen records pass original-model/status/work checks; 44 final vectors
  are feasible. The four no-point results remain honest limits.

The initial missing header include, mistaken replay pivot-count assertion,
and Windows DLL loader failures are retained. Five matching runtime DLLs
beside the executables resolve the loader failures. The source/runtime issue
and successful full gate are documented in [ENVIRONMENT.md](ENVIRONMENT.md).
No historical evidence was overwritten and no tolerance was loosened.

## Decision and continuation

Retain the arithmetic-verified shortcut as an opt-in research feature; do not
promote it as a MILP reliability improvement. The broad 27-model batch is not
triggered because the focused promotion gate found no coverage/completion
gain. Frozen28 remains the earlier broader evaluation with its own limitations.

The next MILP question concerns private-dive work allocation and remaining
integer decisions after this work reduction. First isolate those effects with
fixed-work diagnostics; do not add a larger time slice or another heuristic
without a predeclared shared-budget comparison. The current continuation
has completed current-source LP/QP checks and retained their unresolved LP
failure and QP accuracy limits. See [NEXT_STEP.md](NEXT_STEP.md).
