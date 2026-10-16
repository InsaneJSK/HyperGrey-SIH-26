# Selective stability safeguard for weak primal pivots

`--stable-primal-ratio` enables an experimental sparse-simplex ratio safeguard.
It is off by default. Use it alone for the recorded 16-LP profile, or with
`--refine-basis --refine-at-checks` for its separately checked refined profile.
It does not require compact equalities. Dense simplex and QP methods are outside
this option's scope; broad MILP performance has not been measured for it.

The ordinary minimum ratio test can select a numerically unreliable small
pivot in a degenerate basis. The retained bandm trace captures an apparently
positive 2.72e-8 pivot followed by an exactly singular basis. Its paired
canonical rows have an exact nonzero left null vector. Refactorization
correctly rejects that basis; making singular-factor acceptance weaker would
not repair the problem.

Our safeguard keeps the ordinary choice unless its pivot is at most
`1e-7 * (1 + ||direction||_inf)`. Outside Bland's cycle fallback, it then bounds
the step by `min((max(0, x_i) + tolerance) / d_i)` over the existing eligible
positive directions. Among rows with unrelaxed step inside that bound, it
prefers the largest pivot, breaking equal-pivot ties by basic column index.
The threshold asks for more stable selection; it is not a condition-number
proof. The two-pass principle follows established Harris ratio-test practice;
see [Huangfu and Hall, section 2.2.2 and reference 12](https://www.maths.ed.ac.uk/hall/HuHa13/ERGO-14-011.pdf).
The implementation is our own code in `include/primal_ratio.hpp`.

The existing feasibility tolerance is used during selection. Intermediate
rejection, model coefficients, bounds, pivot eligibility, original-model
optimality checks and all MILP incumbent/proof checks remain unchanged. A
genuine sole small pivot is not automatically dropped. No factorization
refresh policy, imported answer or instance-specific rule is included.

The [diagnostic report](../reports/numerical-diagnosis-01/REPORT.md) retains the
failed refresh-only attempt and the broader two-pass candidate. The selective
candidate activates only on the two standard bandm calls in the 18-observation
diagnostic study, preserving other LP pivot counts. The
[integrated report](../reports/lp-pivot-iteration-01/REPORT.md) records the exact
final binary, full correctness gate, both 16-LP profiles and remaining limits.
These small public sets do not establish arbitrary-scale robustness, a speed
ranking or an improvement in integer search. Defaults remain unchanged.
