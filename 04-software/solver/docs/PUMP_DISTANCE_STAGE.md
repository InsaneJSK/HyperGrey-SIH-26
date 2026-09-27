# Objective-only stage before a private distance dive

`--pump-distance-stage` is experimental and off by default. It additionally
requires `--pump-distance-reopt --pump-primal-reopt --pump-distance-diving
--pump-guided-diving`. It is inert when the pump or heuristics are disabled.
It is a CPU-local search experiment, not a new proof rule.

## Two separate changes

The previous handoff changed both the private objective and the first branch
bound at once. A saved basis could then be neither primal nor dual feasible,
forcing a cold solve despite compatible structure. This option first solves
the new distance objective on the unchanged parent domain. A verified result
can supply a private basis for the subsequent bound-only branch solve.
The LP engine still independently chooses the applicable restart or fallback.

The exact parent model is retained at the same selection event as the checked
fractional seed, and only when a usable tagged basis is retained. Non-selected
projections do not replace it. A newly selected point without a usable basis
clears stale state. The snapshot owns its data; it does not alias a mutable
projection. The public `PumpDiveSeed` remains point-only.

Staging requires exact equality of parent/new rows, row bounds, variable bounds,
integer flags and variable count. Only costs/offset may change. This conservative
prefilter rejects changed general-integer auxiliary RHS/layouts and bound
orientations; mathematical equivalence alone is not enough. The LP engine also
checks its canonical structure tag and current primal/dual feasibility.

## Safety and budget boundary

The stage runs inside the existing shared dive slice (at most two seconds).
Construction, comparison, solve and optional diagnostic capture consume that
same allowance. There is no additional stage budget. A failed/unverified stage
leaves the original seed and basis available for the remaining time.

Advancement requires verified optimal status, a finite complete private vector,
and absolute row/bound violation at most 1e-7 on the private and original
models. Existing MILP acceptance separately checks integrality and recomputes
the original objective. Only the point and private heuristic basis advance;
the distance objective, bounds, certificate and infeasibility status do not
enter the global tree. A failed child preserves the staged parent basis for
its alternate. No reference result is used as a solver input.

These are cooperative time checks, not hard real-time/process containment.
Snapshot retention adds a model-sized allocation; it is not a hard memory cap.
Staging may change the fractional point and hence the later branch trajectory,
so it is not merely a performance-neutral cache optimization.

## Evidence and counters

JSON `distance_stage` counts consideration, eligibility, attempts, verified
stages, accepted incumbents and offers/verification of the first child basis.
Its `reopt` counters are separate from `distance_reopt` (branch LP work).
Global LP/work totals include both. An offer is not an accepted warm restart;
a verified private optimum is not an integer solution or global proof.

The first eight stage samples retain status, work and remaining slice. With
`--capture-feasibility`, the first stage and first child can each retain an
exact private model/input basis, bounded to 10000 variables, 20000 rows and
200000 original nonzeros. These snapshots support independent diagnostic
replay outside the measured solve, without feeding results back into search.
Capture is not a complete trace or a global memory cap.

See [iteration24](../reports/milp-iteration-24/REPORT.md), its predeclared plans
and complete paired model ledger for observed effects and limitations.
The 27 public models are reused development cases, not unseen holdouts or
evidence that every MILP is handled. Keep historical profiles available.
