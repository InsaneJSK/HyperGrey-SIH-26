# Command-line and API reference

One model per invocation. Exit code 0 means a completed optimization —
`optimal`, or `gap_limit` on the MILP path — 1 an honest non-optimal outcome (a
limit, a proven terminal status, or a numerical failure), and 2 a rejected input
or invalid option. Use `--milp` to enforce integer variables. Without it, the
default sparse and dense LP methods reject integer declarations. Explicitly
selecting `--lp-method bounded` solves the continuous LP relaxation instead;
the API uses this path for `integer=false` requests. Its fractional solution
is an LP result, not a MILP solution.

```
solver_cli MODEL.{mps,qplib,lpmini} [options]
```

## Input

| Format | Use | Notes |
|---|---|---|
| `.mps` | LP and MILP | Free/fixed MPS. `OBJSENSE`, `RANGES`, `BOUNDS`, integer markers. The first `N` row is the objective and later `N` rows are dropped as free rows; text after `ENDATA` is ignored; `BV`/`MI`/`PL`/`FR` accept an ignored value. Rejected with a message naming the line: unsupported sections (`SOS`, quadratic), unsupported bound types (`SC`), and multiple RHS/range or bound sets. Sparse/dense LP methods reject integer declarations without `--milp`; bounded LP accepts their continuous relaxation. |
| `.qplib` | convex continuous QP | Quadratic objective with linear or box constraints. Nonconvex input is rejected rather than answered. |
| `.lpmini` | toy LP | Dense whitespace format, capped at 1000 rows/columns. |

## Core options

| Option | Default | Meaning |
|---|---|---|
| `--json` | off | Machine-readable result on stdout (the format below). |
| `--milp` | off | Solve integer variables rather than the relaxation. |
| `--time-limit S` | 30 | Wall-clock budget for the solve. Cooperative, not a hard kill. |
| `--gap G` | 1e-6 | Relative MILP gap that counts as completion (`gap_limit`). |
| `--node-limit N` | 10000 | MILP node cap. |
| `--iteration-limit N` | 10000 | Simplex iteration cap per LP. |
| `--tolerance T` | 1e-9 | Numerical tolerance for LP checks. |
| `--lp-method M` | `sparse` | `sparse` (original engine), `bounded` (iteration 30 engine, recommended for LP), `dense`. |
| `--no-scaling`, `--no-presolve`, `--no-heuristics`, `--no-pump`, `--no-cuts` | on | Disable a component, for diagnosis. |
| `--open-node-memory-mib M` | 960 | MILP frontier guard, active with `--bounded-lp`. When the estimated open-node memory passes this, the solve stops with `node_limit` and the message `Open-node memory guard`. |
| `--threads N`, `--backend cpu\|cuda` | 1, cpu | QP only. CUDA covers box-QP; other models are rejected for the CUDA backend. |

## Recommended MILP profile

The evaluation profile is a documented flag list, not a default. Use
`reports/milp-iteration-37/CANDIDATE_PROFILE.json` (`recommended_flags`), which
combines the iteration 28 staged flags with `--bounded-lp --tree-dives
--fix-propagate --lifted-covers` and `--root-iteration-limit`.
`--gomory-cuts` is deliberately **not** in it: iteration 37 measured it costing
answers on 60 public instances. Defaults remain conservative so that
disabling every option reproduces the older, simpler behaviour.

Feature flags worth knowing individually: `--bounded-lp` (bounded dual simplex
for node relaxations, `docs/BOUNDED_SIMPLEX.md`), `--tree-dives` and
`--fix-propagate` (primal heuristics, `docs/SEARCH_HEURISTICS.md`),
`--gomory-cuts` (root tableau cuts, `docs/GOMORY_CUTS.md`; requires
`--bounded-lp`, rejected with `--no-cuts`),
`--lifted-covers` / `--late-lifted-covers` (cut timing), `--binary-proof`
(restricted exact proof for small pure-binary models), `--improve-incumbent`
(neighbourhood search), `--lp-recovery` (dense recovery for failed node LPs).
The `--capture-*` flags only add telemetry to the JSON.

## Status values

| Status | Exit | Meaning |
|---|---|---|
| `optimal` | 0 | Solved; for MILP the gap is closed or an exact proof completed. |
| `gap_limit` | 0 | Completed to the requested relative gap. |
| `time_limit`, `node_limit`, `iteration_limit` | 1 | Budget reached. Any incumbent and the bound are reported. |
| `infeasible` | 1 | No feasible point exists; for LP backed by a checked Farkas certificate. |
| `unbounded`, `unbounded_relaxation` | 1 | Objective unbounded, with a checked ray where available. |
| `unresolved_relaxations` | 1 | Some node relaxations failed their checks; the bound retains them. |
| `numerical_error`, `numerical_stall` | 1 | A check failed; no answer is claimed. |
| `resource_limit` | 1 | A relaxation exceeded a factorization or dimension budget and no fallback succeeded. Any incumbent and bound are still reported. |

A completion is numerical unless `binary_proof.verified` is true: `optimal`
means the checks passed at the stated tolerances, not an exact rational proof.
If a MILP's root relaxation itself does not solve, its LP status is reported
unchanged rather than being translated (for example `warm_start_rejected`).

## JSON output

Both paths report `status`, `rows`, `columns`, `objective`, `total_seconds` and
`primal` (the solution vector in original variable order).

LP adds `algorithm`, `nonzeros`, `iterations`, `solve_seconds`,
`max_primal_violation`, `scaled_primal_violation`, `scaled_dual_violation`,
`relative_gap`, `optimality_verified`, `infeasibility_verified`,
`unboundedness_verified`, `unbounded_ray`, `canonical_primal`,
`canonical_dual`. There is no `gap` or `best_bound` on the LP path.

MILP adds `message`, `best_bound`, `gap`, `nodes`, `lp_iterations`,
`warm_starts`, `heuristic_solves`, `cuts`, `bound_tightenings`,
`first_incumbent_seconds`, `unresolved_nodes`, `lp_resource_limits`,
`separator_rows_discarded`, the arrays `incumbent_trace`,
`neighborhood_trace` and `rejected_candidates`, and one object per subsystem:
`bounded_lp`, `tree_dives`, `fix_propagate`, `gomory_cuts`, `work` (per-phase
seconds and LP counts), `frontier`, `cut_policy`, `objective_lattice`, `binary_proof`,
`pump_guidance`, `pump_distance`, `distance_stage`, `heuristic_repair`,
`feasibility`. A subsystem that is switched off still emits its object, with
`enabled: false` (`capture_enabled` for the capture-only ones) and zero
counters, so consumers can read the same shape every run; `scripts/check_*.py`
validate their internal consistency.

QP adds `algorithm`, `threads`, `iterations`, `optimality_verified`,
`primal_residual`, `stationarity_residual`, `complementarity_residual`,
`dual_bound_minimization_sense`, `relative_gap` and `row_dual`.

Objective sense and offset follow the model: `objective` is in the model's own
sense, while `best_bound` and any bound field named `*_minimization_sense` are
in minimization sense.

## C++ API

Link the `solver` target and include from `include/`:

```cpp
#include "mps.hpp"     // read_mps, LinearProblem, original_violation
#include "milp.hpp"    // MilpOptions, MilpResult, solve_milp
#include "sparse_lp.hpp"      // solve_sparse_lp
#include "bounded_simplex.hpp"// solve_bounded_lp
#include "qp.hpp"      // read_qplib, solve_qp_admm

std::ifstream input("model.mps");
auto problem = sovereign::read_mps(input);
sovereign::MilpOptions options;          // same defaults as the CLI
options.lp.time_limit_seconds = 30;
options.bounded_lp = options.tree_dives = options.fix_propagate = true;
auto result = sovereign::solve_milp(problem, options);
```

`MilpOptions` mirrors the CLI flags (`MilpOptions::lp` is the `Options` struct
from `solver.hpp`, with `tolerance` 1e-9, `iteration_limit` 10000 and
`time_limit_seconds` 30); `MilpResult` carries the fields above plus the traces.
Invalid options throw `std::invalid_argument`; a model too large for the
engine's fixed limits throws `std::runtime_error` with a `resource_limit:`
prefix; the CLI turns both into exit 2 with the message on stderr. No API call
writes files or starts processes.

## Errors and limits

Malformed or unsupported input is rejected on stderr with exit 2 and a message
naming the line. Internal limits (time, nodes, iterations) are cooperative: they
are checked between operations, so a single very large factorization can
overrun a deadline. Memory is bounded by a fill budget in the factorization and,
with `--bounded-lp`, by an open-node guard that stops with `node_limit` and the
message `Open-node memory guard`. For hard containment, run the solver under an
external watchdog; `reports/milp-iteration-31/run_contained.py` is the one used
for the project's own measurements.
