# Next MILP iteration — selective cut continuation and feasibility failures

Iteration14 makes work observable and tests a deliberately simple one-round
cut allowance. The p0282 regression rules out promoting that blanket policy.
Keep five rounds as the default; keep the one-round option and its full adverse
ledger for reproducibility. Neither numerical accounting nor more tests makes
an unfinished MILP a proved optimum.

## First bounded experiment

1. Use the saved cut/root/tree phase ledgers to design a general continuation
   rule based on observed bound improvement and LP effort. Do not branch on a
   model name, published optimum, or an independently computed incumbent.
2. Before coding, specify normalization, minimum work allowance, fallback for
   unavailable/nonfinite metrics, and hard stopping semantics. A round count
   alone is not a pivot, memory, or reliable elapsed-time limit. Decide whether
   the first experiment is deterministic work-based or explicitly clock-based.
3. Freeze one candidate and a five-round control. Test Binkar for the suspected
   feasibility benefit AND p0282/mod008 for lost bound strength. Retain every
   adverse result. Do not choose a global default from Binkar alone.
4. Repeat the unchanged profiles, then run all 21 retained development cases
   and genuinely new, predeclared holdouts. The four iteration13 holdouts are
   now development data; they cannot count as fresh validation again.
5. Recheck cuts, original-model points, partial bounds, global frontier
   accounting, exact-subset claims, parser domains and default/capture parity.
   Add exhaustive tiny cases that actually exercise every new stopping branch.

This is an experiment proposal, not an implemented adaptive policy or a
promise that it will beat the current default.

## Separate work still needed

- Feasibility failures: Blend2, misc07, lotsize and eil33-2 have different
  pump/diving/tree bottlenecks in the saved diagnostics. Instrument bounded
  heuristic attempts and their acceptance/failure reasons before changing
  them. A global cut cap does not solve these stalls.
- Stronger general bounds and reliable LP recovery: many checked incumbents
  still have large open gaps. Numerical validation is not a general exact
  rational LP/MILP certificate. Preserve unresolved nodes on failures.
- Resource containment: test process-level memory/watchdog behavior, malformed
  inputs and larger sparse instances before scaling to the full public suite.
- Independent validation throughput: retain the two original eil33-2 checking
  timeouts and their separate retries. Cache binding-backed sparse arrays in
  the reference point checker only after equivalence tests, and do not report
  such a checker improvement as optimization-engine speedup.
- Breadth: enlarge the fixed ledger by model structure and size, recording
  completions, feasible limits, no-point limits and errors separately. Do not
  erase failures or count repeated runs as additional distinct models.
- Submission: retain the independent optimizer, reproducible evidence and
  explicit limitations; add real domain validation and a clear end-to-end demo.
  The latest MILP test gate is not a fresh full GPU/QP/industrial validation.

All CPU work stays local. Kaggle is needed only for a specifically planned GPU
experiment. No result ZIP or notebook run is needed from the user for this step.
