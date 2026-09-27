# Follow-up hypothesis: small binary models with separable continuous recourse

The first iteration06 comparison showed that reserved Hamming searches reach
late markshare incumbents, but hit their512-node cap with little local time used.
No final markshare improvement was obtained. Inspecting the model also identifies
30 binary variables and four distinct continuous slack columns, each belonging
to its own equality. This is a mathematical structure, not an instance identifier.

Evaluate a separately versioned meet-in-the-middle incumbent heuristic for at
most36 movable binary variables and8 rows, optionally eliminating a single
continuous variable from each equality when that column appears nowhere else.
Reject unsupported structures cheaply and retain the existing general solver.
Keep the reduced row intervals and objective coefficients, enumerate half states,
and use a bounded spatial range search to combine compatible halves. Every
candidate must be reconstructed and checked against the original model. No
reference optimizer or known answer enters this search.

The split-enumeration principle is established by
[Horowitz and Sahni](https://www.cise.ufl.edu/~sahni/papers/computingPartitions.pdf).
This implementation's multi-row range-search and separable-recourse adaptation
is independently written. It is a bounded incumbent heuristic; completing its
floating-point query loop is NOT exported as an optimality/infeasibility proof.

First run the standalone prototype only after all earlier timed/reference work
finishes. If it produces a useful independently checked point, integrate it as a
separate opt-in root heuristic. Require exhaustive small-model tests, original
feasibility checks, zero/no-heuristics controls, minimization/maximization and
unsupported-structure fallback tests. Then run a focused equal-budget local
control/candidate comparison with new source/binary hashes and output directory.

The first comparison also experienced visible competing application CPU activity
and substantial baseline variation. Preserve that limitation; do not promote
single-pass wall-time differences to a speedup claim. Do not terminate or change
the user's applications or machine power settings.
