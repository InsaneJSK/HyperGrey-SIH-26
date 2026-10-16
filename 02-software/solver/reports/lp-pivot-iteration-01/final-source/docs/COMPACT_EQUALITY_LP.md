# Compact equality LP experiment

`--compact-equalities` is an opt-in representation for the sparse LP engine.
It also applies to sparse LP relaxations inside the MILP engine. The default
keeps the earlier two-inequality representation. Dense LP and QP algorithms
are unchanged; requesting this flag does not accelerate those algorithms.

## Representation and safety

A row whose finite lower and upper bounds are exactly equal is stored once,
as an equation. Nearly equal ranged bounds remain two inequalities. Other row
sides and finite variable upper bounds use the existing representation.
No original variable, constraint or feasibility check is removed.

An equality's identity column is a Phase-I artificial variable, not a Phase-II
slack. Negative-right-hand-side rows use the existing negative artificial
column. Phase I minimizes all artificial values; every remaining basic
artificial must be pivoted out before Phase II. Artificial variables cannot
enter Phase II or a supplied warm basis. A dependent equality that prevents
safe purging rejects the attempt rather than silently dropping a row.

The dual multiplier of an equation is unrestricted in sign. In both the dual
optimality and infeasibility checks, only inequality multipliers are clamped.
An unbounded ray must satisfy an equality in both directions. The established
scaled primal/dual/gap checks and original-model primal checks remain active,
with unchanged tolerances. These are numerical certificates, not exact rational
proofs for arbitrary MPS data.

Two-phase artificial variables and equality/free-dual correspondence are
standard LP techniques; see [MIT's simplex reference](https://web.mit.edu/~r/current/lib/R/library/boot/html/simplex.html)
and [MIT duality notes](https://ocw.mit.edu/courses/6-854j-advanced-algorithms-fall-2005/d974aef980258f2a796171e96717d646_n11_lp.pdf).
This implementation is independent; no reference solver is called by the core.

## Fallback and diagnostics

On `numerical_error` or `numerical_stall`, the wrapper may retry the previous
representation cold, using only the remaining wall-clock allowance. A stopped
or unsupported compact attempt is not relabeled a proof. The iteration limit
is per formulation attempt; reported iterations include both completed
attempts. Time checks remain cooperative and can overrun their nominal slice.

`LpBasis::compact_equalities` prevents cross-formulation warm reuse. A basis
with the wrong mode, dimensions, repeated columns or an artificial column is
rejected. Captured failure JSON includes this mode alongside the basis columns.

LP JSON reports `canonical_rows`, `compact_equality_rows`, and
`compact_fallback`. After fallback, row counts describe the returned ordinary
formulation. MILP JSON reports `compact_lp_calls`, `compact_lp_fallbacks`,
`root_lp_rows`, and `root_compact_equalities`. Call/fallback counters cover the
initial calls through the main relaxation helper, not every direct pump,
strong-branch or recovery subcall. Root counts refer to the most recently
processed root, including a delayed-cut restart. They are not peak memory
measurements or a complete LP-call count.

## Verification and reproduction

The seventh CTest group includes analytical equality/dual/infeasibility/ray
cases, dependent-row fallback, warm-mode rejection, zero-time handling,
300 generated LP comparisons and 80 generated mixed-integer comparisons.
The local validation harness adds 40 binary-enumeration and 40 independent
mixed-integer checks per selected profile. These counts are repeated generated
cases, not a count of distinct public benchmark instances.

Use a new output directory; the harness will refuse to overwrite evidence:

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_compact_equalities.py --output reports/my-equality-screen --root-only --nodes 1 --limit 60 --models binkar10_1 p0033
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_compact_equalities.py --output reports/my-equality-comparison --limit 180 --models binkar10_1 p0033 --generated
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_compact_run.py reports/my-equality-comparison --binary build-milp-iter9b/solver_cli.exe --output reports/my-equality-audit
```

Timings are sequential with alternating profile order. Independent original-MPS
candidate and retained-cut checks run afterward. An independent original-literal
Markshare proof sentinel checks that the earlier restricted exact-proof path
still works. It does not establish Binkar optimality. The evidence audit checks
saved vectors, not all objective-only intermediate incumbents or every internal
LP dual bound. The source, binary, models, commands and limits are hashed.

This is local CPU work. No Kaggle notebook, GPU allocation or upload is needed.

## Delayed activation

The first full Binkar comparison found that compact LPs changed the incumbent
search path adversely, despite a faster root screen. That failed performance
attempt remains archived. `--late-compact-equalities` therefore tests a separate
schedule: preserve the ordinary LP formulation initially, then activate compact
equalities at the existing half-time, full-domain lifted-cover restart.

This option implies delayed lifted covers. `--no-cuts` prevents the restart and
therefore prevents delayed compact activation. When both immediate and delayed
compact flags are supplied, delayed activation takes precedence in MILP mode.
An early completed run need not use compact LPs at all. The exact-proof engine
remains separate. Global time, node counts, consumed heuristic budgets and the
same-run incumbent survive the restart; its inherited bound still covers the
entire original domain. The new root starts cold in the new representation.

JSON distinguishes `late_compact_equalities_enabled` (requested) from actual
`compact_lp_calls` and `cut_restarts`. Deterministic min/max tests force a restart
at a node threshold, check incumbent/bound retention, verify no compact calls
before activation, and cover no-cuts/zero-time behavior. The CLI uses only the
half-time trigger, not the deterministic test hook.

Reproduce this variant with `--build build-milp-iter9b --late-compact` on the
validation command, or `--late-compact-equalities` on the solver CLI. Use a fresh
output directory and match the auditor's `--binary` to `build-milp-iter9b`.
