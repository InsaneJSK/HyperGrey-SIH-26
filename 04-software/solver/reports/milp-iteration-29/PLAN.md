# Iteration29: verified dual-row feasibility diagnostic

Declared 17 September 2026 before new replay measurements.

Hypothesis: the retained lotsize later private LP reaches a dual row with no
entering variable; a verified Farkas certificate might avoid cold phase one.
First establish the actual rejection and certificate validity. No promotion
or MILP gain is assumed. The production numerical sources remain unchanged
until this gate supports an implementation.

- Control: current source and the frozen iteration26 replay outputs; verify
  current numerical files match frozen28 before preparing an instrumented copy.
- Diagnostic: same algorithm, logging the exact dual rejection, candidate row,
  canonical columns/RHS and row mapping. No early return or changed pivot.
- Inputs: all four retained iteration26 private-replay text fixtures, in their
  existing cold / legacy dual / adaptive order, one diagnostic observation per
  mode. The four captures contain repeated trajectories, not four new models.
- Budget: existing ten-second per-mode LP limit and 45-second process watchdog,
  10,000 pivots, unchanged tolerance/scaling/refinement flags. Serial processes.
  Instrumented wall times are diagnostic and cannot establish speedups.
- Verification: exact rational products/sums of the captured binary64 values;
  every true canonical column, including basic and slack columns, must have
  the right sign, and the RHS must give a scaled strict contradiction. Check
  original-domain coefficients separately before calling a certificate usable.
- Tests: exact contradiction, feasible near-zero negative coefficient,
  equality/free-variable signs, malformed and nonfinite certificate inputs.
- Gate: first reproduce the precise rejection and arithmetic. If certificates
  fail, keep phase one, record the failure and specify the narrower next step.
  If they pass, implement only a guarded opt-in private mechanism with all
  correctness/budget tests before predeclaring a repeated MILP screen.

Any private infeasibility remains local. Reference answers and certificate
checks run outside search and never feed its incumbents, bounds or pruning.
The certificate convention follows Farkas' lemma; our sign convention is
`A^T y >= 0, b^T y < 0` for nonnegative canonical variables.
Background: https://docs.mosek.com/modeling-cookbook/linear.html

After the diagnostic decision, continue the independent final-source LP/QP
revalidation track. Preserve every raw outcome and prepare the next bounded
plan from observed failures. GPU execution and domain/organizer input remain
separate dependencies.
