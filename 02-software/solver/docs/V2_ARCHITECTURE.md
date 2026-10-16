# V2 architecture and scope

The initial PS classes are LP, MILP and QP. This version solves continuous convex
QP; nonconvex QP, MIQP, NLP and MINLP remain extension work. Numerical PSD tests
are conservative and floating-point checks are not exact mathematical proofs.

## Implemented components

| Component | Implementation | Purpose |
| --- | --- | --- |
| Input/API | C++ headers, MPS, QPLIB, lpmini, JSON CLI | Common bounds, objective sense and integrality |
| LP | Sparse revised primal simplex and dual-simplex basis reuse | Solve LPs and MILP relaxations |
| Basis algebra | Own sparse LU, threshold row pivoting, eta updates | Avoid a dense tableau and explicit matrix inverse |
| Numerical recovery | Dense two-phase simplex retained for small MILP failures | Alternative solve path, followed by validation |
| MILP | Bound propagation, root binary cover cuts, L1 feasibility pump, two diving heuristics, best-bound search with depth tie-breaking | Find feasible incumbents and close bounds |
| Small-binary exact mode | Separate opt-in checked-integer split enumeration and original-model witness checks | Exact proof only within the explicitly guarded subset |
| Lifted-cover experiment | Opt-in exhaustive small binary-row separation, sequential lifting and full cut-validity checks | Strengthen root relaxations; global LP bounds remain numerical |
| QP | Sparse scaled ADMM, Jacobi-preconditioned CG, active-set KKT polishing | Continuous convex QPs with linear constraints |
| Structured QP | Magnitude-scaled dual Newton/CG for positive diagonal Hessians and equality rows, with bounded ADMM fallback | Separable equality QPs, including models above 512 variables |
| Box QP | Accelerated projected gradient (FISTA) | Sparse convex QPs with variable bounds |
| Multicore | OpenMP CSR matrix products and box iterations | Explicit CPU thread comparisons |
| CUDA | Resident CSR data and double-precision FISTA kernels | Box-QP acceleration on NVIDIA hardware |
| Verification | Original-model feasibility, dual/KKT checks, integer checks, independent reference readers | Reject unsupported or unchecked solutions |

Sparse LU retains fill; its memory budget may still stop difficult factorizations.
Eta updates are periodically refactored. Warm starts verify reduced costs and
fall back to a cold solve if dual feasibility is lost. Bound propagation derives
each row's updates simultaneously, using outward numerical margins. Nearly
integral candidates are repaired with fixed integers against the original model.

The root feasibility pump alternates integer rounding and sparse LP distance
projection, with deterministic cycle perturbations. Interior general-integer
targets use absolute-distance auxiliary variables; binary targets use a linear
distance objective. The pump is limited to 40 projections and at most the
smaller of five seconds or the remaining global time. Root cut processing
reserves up to five seconds for that search. An unfinished cut LP is optional:
its added rows are removed and the previous validated model/basis is restored.
Fixed-integer polishing and
all candidates pass the unchanged original-model acceptance check. Distance
objectives/bases never supply the tree's objective lower bounds. `--no-pump`
provides an ablation; `--no-heuristics` disables both pump and dives. Heuristic
sub-LPs share their heuristic deadline, including numerical recovery.

The separate [binary-proof mode](MILP_BINARY_PROOF.md) runs before floating
root processing and can return exact optimality/infeasibility only for its
strict small integer-data subset. The [lifted-cover separator](MILP_LIFTED_COVERS.md)
instead supplies exact-valid cuts for supported parsed binary64 knapsack rows;
it does not make the general floating-point MILP search an exact proof engine.
Both are opt-in, and no reference optimizer enters either core algorithm.

The GPU backend currently accepts **box-constrained convex QPs only**. Constrained
QP and LP/MILP run on the CPU. Selecting CUDA for unsupported input is an explicit
error. A CPU-only build never silently pretends to execute CUDA.

## Status and bound semantics

- `optimal`: numerical LP optimality or QP KKT checks passed at the requested
  tolerance. A QP KKT success is not a universal global objective-error bound.
  MILP may also finish its numerical search. Only a completed, verified
  `binary_proof` result denotes the restricted exact path; inspect its metadata.
- `gap_limit`: a feasible MILP incumbent and numerical bound meet the requested
  relative-gap threshold. Search bounds include a numerical safety margin.
- `infeasible`: an LP numerical Farkas check or completed MILP pruning supports
  infeasibility. General QP infeasibility certificates are not implemented.
- `unbounded`: the sparse LP path checks a recession ray. An unbounded MILP
  relaxation is reported separately as `unbounded_relaxation`.
- Limits, unsupported curvature and numerical failures remain failures. Candidate
  iterates must not be presented as optimal solutions.

QP row duals and `dual_bound_minimization_sense` use the normalized minimization
problem, including for maximization inputs. LP/MILP objectives are printed in
the original input sense. QP `relative_gap` is null when the tangent bound over
an unbounded variable box is not finite.
For strictly positive diagonal Hessians, an exact separable Lagrangian formula
now supplies the numerical dual bound and acceptance also requires its relative
gap to meet the requested tolerance. See [scaling and bound derivation](DIAGONAL_QP_METHOD.md).

## Mathematical sources and implementation provenance

All optimization and numerical source is implemented in this project. No source
from an existing optimizer is embedded in the core. Published mathematical
methods inform the implementation, including the operator-splitting formulation
described by [Stellato et al.](https://web.stanford.edu/~boyd/papers/pdf/osqp.pdf).
The reference solver's [algorithm documentation](https://osqp.org/docs/solver/)
also describes residual balancing and active-set polishing. Our implementation
uses its own sparse products, LU and conjugate-gradient routines.

The feasibility-pump mathematics follows
[Fischetti, Glover and Lodi, The Feasibility Pump](https://www.dei.unipd.it/~fisch/papers/feasibility_pump.pdf).
The implementation here uses our sparse simplex; it does not copy or call the
paper's commercial solver implementation. Heuristic success is not an
optimality certificate.

HiGHS and OSQP execute only in Python reference/test processes. OpenMP and the
optional CUDA runtime provide execution infrastructure, not optimization models
or solver algorithms. Whether organizers permit general numerical/GPU libraries
is still an external clarification; the current core does not use BLAS,
cuSPARSE, cuSOLVER, Eigen or another solver library.

The old `src/milp.cpp` remains as historical V1 code and is not compiled by V2.
The active implementation is `src/milp_v2.cpp`. CMake lists all compiled sources.
