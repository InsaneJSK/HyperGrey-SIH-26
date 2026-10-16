# Problem statement 26119: requirement-to-evidence matrix

This is the preserved V1 matrix. Current development coverage is recorded in
[V2_REQUIREMENTS.md](V2_REQUIREMENTS.md).

Source: [original statement](../Problem%20Statement.txt). Statuses describe the
current V1, not the final ambition. Passing a small subset never completes a
large-scale or robustness requirement by itself.

The user confirms that the supplied dataset paragraph was already incomplete.
The [source verification record](PS_SOURCE_CHECK.md) documents the unsuccessful
attempt to recover a verified continuation; no omitted requirement is inferred.

| ID | PS expectation | V1 status / evidence | Work remaining |
| --- | --- | --- | --- |
| PS-01 | Solver core built from mathematical foundations; no existing solver core | Implemented in `src/solver.cpp`, `milp.cpp`, `qp.cpp`; CMake links only our library | Maintain dependency/provenance audit as implementation grows |
| PS-02 | LP support | Dense two-phase simplex; Netlib subset; generated primal/dual checks | Sparse revised simplex/IPM, stronger numerical recovery, broader benchmark coverage |
| PS-03 | MILP support | Best-bound branch-and-bound, integer/binary MPS metadata, incumbent/bound/gap reporting | Warm starts, presolve, cuts, heuristics, improved branching and harder MIPLIB coverage |
| PS-04 | QP support | Continuous convex subset; QPLIB input, sparse first-order algorithms, KKT residual checks | Broader PSD handling, reliable constrained-QP convergence, nonconvex scope clarification |
| PS-05 | Extensible toward MIQP/NLP/MINLP | Separate model/LP/MILP/QP modules | No MIQP, NLP or MINLP algorithms implemented; API abstraction needs further development |
| PS-06 | Sparse matrices and efficient numerical algebra | Sparse MPS input rows and sparse QP operations | LP standardization and tableau remain dense; no sparse factorization or basis updates |
| PS-07 | Multicore parallelization | Not implemented; solver runs single-threaded | Profile and introduce deterministic parallel work with equivalent-accuracy comparisons |
| PS-08 | GPU acceleration where benefits are measurable | Not implemented or measured | Confirm hardware, implement candidate kernels and compare end-to-end CPU/GPU runs |
| PS-09 | Numerical stability, degeneracy, ill-conditioning | Cycling regression, row scaling, generated extreme row-scaling tests, Netlib `degen2` | No comprehensive ill-conditioned basis suite or production-grade recovery; no exact arithmetic proofs |
| PS-10 | Thousands to millions of variables/constraints | Some 14k-15k-variable box QPs tested; LP/MILP limited to small models | General industrial-scale sparse LP/MILP/QP and million-variable demonstrations absent |
| PS-11 | Benchmark recognized datasets | Selected Netlib, historical MIPLIB 3.0, QPLIB runs with original-input hashes | Modern MIPLIB 2017 set and a declared Mittelmann set not yet tested; full libraries not covered |
| PS-12 | Compare with an established solver | HiGHS LP/MILP and OSQP QP comparisons in isolated reference processes | More repetitions, peak memory, matched configurations, performance profiles and representative selections |
| PS-13 | Industrial applications | Synthetic blending LP, production MILP and dispatch QP | Open-literature refinery scheduling / supply chain cases and domain-expert validation |
| PS-14 | Basic API or CLI sufficient | C++ headers, MPS/QPLIB/lpmini CLI, JSON outputs | Stable public API, richer diagnostics and packaging across environments |
| PS-15 | Transparent and sovereign foundation | Source, algorithms, phase reports, reproducible scripts and limitation register | Review numerical claims and keep provenance complete; no commercial replacement claim yet |

The PS names simplex, IPM, branch-and-cut, presolve and heuristics as possible
core techniques. V1 does not imply that every named technique is implemented.
Likewise the PS lists benchmark libraries as examples; our report explicitly
tracks which ones have actually been exercised.

See [phase history](PHASES.md), [limitations](LIMITATIONS.md), and
[V1 validation report](../reports/V1_REPORT.md) for the practical evidence.
