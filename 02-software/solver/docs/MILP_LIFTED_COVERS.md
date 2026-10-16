# Checked lifted-cover experiment

`--lifted-covers` is an opt-in CPU root separator. It strengthens small binary
capacity constraints, not a new general MILP solver. `--no-cuts` disables it;
`--no-heuristics` does not disable valid cutting planes. The earlier exact
small-binary proof engine and floating incumbent helper remain separate.

## Method and validity boundary

A binary knapsack row can imply a cover inequality: if a set of items exceeds
capacity, not all of those items can be selected. Sequential up-lifting can
strengthen its coefficients for other binary variables. This established family
is described in the [SCIP knapsack documentation](https://www.scipopt.org/doc-8.0.0/html/cons__knapsack_8c.php).
Our bounded enumeration implementation is independent; SCIP is neither linked
nor called, and reference solutions do not enter search.

The separator considers each finite side of ORIGINAL rows containing2–20
distinct binary variables, whose global domains lie within[0,1]. Mixed rows,
general-integer domains, duplicate columns and unsupported arithmetic are
declined. Signed coefficients are converted with binary complements. Each
parsed binary64 coefficient and bound is converted exactly to an integer at
a common power-of-two scale, with an absolute-sum envelope no larger than2^60.
This uses int64 without rounding or overflow. Extreme dynamic range is rejected.

Enumerate the full binary cube and identify every assignment satisfying that
source row. Rank minimal covers by fractional violation, try at most eight,
and sequentially lift their outside variables. For a current valid cut with
RHS b, the new coefficient for variable j is b minus the maximum current cut
activity among all row-feasible assignments having j=1. Other zero-coefficient
variables remain unrestricted. Thus the lifted inequality stays valid globally
for the source row; it does not depend on local branch bounds or an incumbent.

After lifting, recompute every feasible assignment's activity FROM SCRATCH.
Only completely checked, nonduplicate, violated cuts are exported. At most two
per source side and16 per pass are added. A stopped candidate contributes no
unchecked cut; fully verified earlier cuts may remain available. Memory failure
in the optional separator is caught before model mutation. The ordinary cover
separator is used when the new method exports none.

The existing five-pass root cut loop re-solves each strengthened LP with its
normal numerical gates. If a cut-LP attempt fails, both the model rows and
retained-cut trace are rolled back. No incumbent check or LP tolerance is relaxed.
These are exact-valid cuts for the PARSED binary64 row. General MILP LP bounds
are still floating-point numerical bounds, NOT exact optimality certificates
or arbitrary-precision statements about the original decimal text.

## Budgets and diagnostics

Each separation call gets at most2s and the remaining root-cut allowance. Total
separator time is capped at min(5s,5% global limit). Root reoptimization uses the
existing global budget; it is not included in `lifted_cover_seconds`.
Arrays scale as2^row_width (at most2^20 assignments); the principal weight/loss/
mask/activity arrays total roughly24MiB at this limit, plus candidates/overhead.
Time checks are cooperative and a scan/allocation/sort can overrun its slice.

JSON reports `lifted_cover_states`, `lifted_cover_checked`,
`lifted_cover_seconds`, `root_bound_before_cuts`, `root_bound_after_cuts` and
`lifted_cover_trace`. Each retained cut records its original source row/side,
integer coefficients/RHS and count of checked row-feasible assignments.
Generated-but-not-retained checks can exceed trace length. The general `cuts`
count also includes ordinary covers. Exact-proof early returns do not solve a
root LP, so these LP-bound diagnostic fields remain null there.

## Delayed full-domain restart

The first direct-cut Binkar experiment strengthened the bound but worsened its
180s incumbent, so it was not promoted. `--late-lifted-covers` tests a separate
schedule: run the ordinary guided search first, then restart once at half the
global time budget if a live frontier remains. The option enables lifted covers
only at that restart. It does NOT import a saved or reference solution.

The new root covers the ENTIRE original variable domain, including all live and
deferred old nodes. Only the valid global minimum of the old frontier/deferred
bounds (capped by the incumbent) is inherited. The same-run original-checked
incumbent and global valid cuts are retained. Total node count, elapsed time and
spent heuristic budgets are NOT reset. Re-exploration costs time; improvement is
not guaranteed. Zero node/time limits and `--no-cuts` prevent a restart.

JSON records the restart count/time/node count, inherited global bound, incumbent
objective and its vector (models up to10000 columns). The independent audit
checks the carried vector and its pre-restart incumbent trace. Final root-bound
diagnostics describe the most recent root processing, not necessarily the first
root. A non-CLI node-count hook makes the C++ min/max restart tests deterministic;
normal CLI behavior uses the half-time threshold alone.

## Independent verification and reproduction

`scripts/check_lifted_covers.py` loads MPS with an independent HiGHS reader but
does not run that optimizer. Python unbounded integers represent the reader's
binary64 values exactly; an independent subset recurrence in ORIGINAL variable
coordinates checks every row-feasible assignment and every retained inequality.
This validates parsed coefficients, not arbitrary rational MPS literal semantics.
Unit tests include invalid/tampered cuts, complemented rows and lower row sides.
C++ tests check400 signed/dyadic10-variable rows exhaustively, plus max/min
integration, boundary, domain and budget controls.

Use a fresh build/output directory and preserve earlier evidence:

```powershell
cmake -S . -B build-current-local -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF
cmake --build build-current-local -j 4
ctest --test-dir build-current-local --output-on-failure
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_lifted_cover_check.py
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_lifted_covers.py --build build-current-local --output reports/my-cut-comparison --limit 180 --models binkar10_1 p0033
```

`--root-only --nodes 1 --limit 30` is a diagnostic screen, not a full solve.
Normal runs include240 generated checks, public comparisons with alternating
profile order, independent candidate/cut checks AFTER all timed runs, and a
markshare exact-proof sentinel. `--repeats N` repeats the public run grid.
The option remains experimental; stronger root bounds alone do not establish
better end-to-end performance. No GPU/Kaggle run is required.
Use `--late` on the validation runner to test the delayed schedule against the
same guided control, instead of direct root cuts. Preserve these as distinct runs.
