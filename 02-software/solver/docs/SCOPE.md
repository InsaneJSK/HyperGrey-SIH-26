# Scope and development workflow

> Historical planning document from the initial LP prototype. The two-day V1
> scope and current completion status are maintained in `DECISIONS.md`,
> `PHASES.md`, and `PS_REQUIREMENTS.md`; do not treat the checklist below as a
> current implementation inventory.

## Assumptions and open decisions

- Target a research prototype first; measure scale rather than claim millions
  of variables from the outset.
- Implement solver algorithms ourselves. Existing solvers may only be separate
  comparison tools, never dependencies of the solver core.
- Confirm with MRPL whether general numerical libraries (BLAS, sparse
  factorization, CUDA libraries) are permitted before adopting them.
- Propose convex QP as the initial QP subset; confirm this interpretation.
- Record team skills, deadline, CPU/RAM, and GPU model before scheduling GPU work.

## Ordered backlog and acceptance gates

1. **LP correctness baseline (implemented):** small CLI, blending model, two-phase
   simplex, independent primal checks, analytical tests for status and objective.
2. **Verification harness:** run an external reference solver in a separate
   process; generate bounded LPs with known primal/dual optima, add cycling and
   ill-conditioning cases, and persist failing inputs. Verify primal/dual
   residuals and objective gap; add certificates before trusting difficult
   infeasibility/unboundedness classifications.
3. **Production model layer:** row/column bounds, objective offset and sense,
   integrality metadata, CSR/CSC storage, documented MPS subset and parser tests.
4. **Numerical LP core:** sparse revised simplex, stable basis solves and updates,
   refactorization, scaling, anti-cycling safeguards, reversible presolve and
   postsolve. Pass baseline tests and an explicitly selected Netlib subset.
5. **MILP:** branch-and-bound, reusable LP basis, valid node bounds, incumbent
   validation, gap/time limits. Match enumeration on tiny bounded integer models
   before selected MIPLIB cases; add heuristics and cuts incrementally.
6. **Convex QP:** implement a dedicated method; test PSD objective matrices,
   singular/redundant cases, feasibility and KKT conditions. Reject unsupported
   nonconvex input rather than claiming global optimality.
7. **GPU:** profile first. Evaluate a from-scratch first-order LP path when sparse
   matrix-vector products dominate. Compare CPU/GPU versions at equal accuracy,
   including setup, transfers, memory, and total runtime.
8. **Industrial demo:** keep the blending LP; add a documented production-planning
   MILP and a convex quadratic dispatch example, with transparent assumptions.

## Benchmark protocol

Record instance source/hash, rows, columns, nonzeros, solver revision, compiler,
hardware, thread count, seed, tolerances, limits, status, objective, residuals,
time, and memory. For MILP record incumbent, best bound, and gap. Include failures
and timeouts; distinguish no feasible solution found from proven infeasibility.
Compare end-to-end runs under disclosed configurations. Keep reference tools
isolated from the core executable.

Dataset entry points: https://netlib.org/lp/data/ and
https://miplib.zib.de/download.html . Reference solver: https://highs.dev/ .
