# Iteration 30 plan — bounded dual-simplex node relaxations

Declared 17 September 2026, before any timed comparison or fresh-holdout solve.

## Hypothesis

Iteration 28/29 work data show that MILP time is dominated by node LPs, not by
search decisions. On misc07 the old sparse simplex spends about 2,300 pivots and
361 ms per tree LP; pk1 needs about 1,400 pivots per node; danoint about 6,800.
The old engine turns every finite variable bound into an extra row, recomputes
all primal/dual values each pivot, and restarts from a cold phase one whenever
its warm dual simplex stalls or meets an infeasible child.

Replacing only the relaxation engine should raise node throughput by an order
of magnitude and produce more completions, stronger bounds and better checked
incumbents at the same 30-second budget, with no validation failure.

## Mechanism (single change)

`--bounded-lp` routes root, cut, tree, dive, neighborhood and strong-branching
relaxations through a new, independently written bounded revised dual simplex
(`src/bounded_simplex.cpp`):

- rows are ranged logicals and bounds stay on variables, so branching changes no
  matrix and reuses the parent basis;
- Gilbert-Peierls sparse LU with product-form updates, dual steepest-edge
  pricing, Harris bound-flipping ratio test, primal cleanup phase;
- infeasible nodes end with a Farkas ray that is re-checked on the ORIGINAL rows
  and bounds; unverified rays are never used;
- nodes stop early only when a Lagrangian bound, recomputed from the original
  rows in extended precision, reaches the incumbent plus the existing margin;
- every optimal result passes the same original-model primal, dual and gap
  checks as `solve_sparse_lp`; anything unverified falls back to the existing
  engine unchanged.

Private pump/distance LPs, candidate repair and all proof/acceptance rules are
unchanged. With the flag off, the executable must reproduce the old semantics.
An open-node memory guard (960 MiB estimate, reported as `node_limit` with a
message) is active only with the flag, because faster nodes grow the frontier.

## Profiles

- Control: iteration 28 staged profile flags (`reports/milp-iteration-28/DEVELOPMENT.json`)
  on the new iteration 30 executable, feature off.
- Candidate: the identical flags plus `--bounded-lp`.

Same executable, serial runs, rotating profile order, 30 s, relative gap 1e-6,
45 s external watchdog, 1536 MiB sampled commit threshold. The node limit is
100,000,000 for both profiles: the historical 250,000 cap never binds the
control but binds the candidate on gt2 inside 30 s, which would hide the tested
effect. The earlier 250,000-node results remain comparable only to the control.

## Model sets

1. Development: the 27 reused iteration 28 models. Two repeats per profile.
2. Previous holdout: the six iteration 28 untouched models (vpm1, vpm2, bell3a,
   bell5, gesa2, noswot). Not solved or tuned since iteration 28. One repeat.
3. Fresh holdout: 15 public MIPLIB 3 models never downloaded or solved by this
   project, declared in `HOLDOUT_SELECTION.md` before download. One repeat.
4. LP track: the 16 LPs of `reports/cpu-validation-2026-09-17` with
   `--lp-method bounded` and the default method, independent HiGHS checks.

Development-screen observations already made while building the engine (27
models, parallel, not retained as evidence) informed only engine correctness
fixes; no model-specific rule exists. Sets 2 and 3 were not run at all.

## Validation

Original-model feasibility, objective and status checks against HiGHS 1.12.0
for every record (5 s references for development, 30 s for holdouts at the
tighter declared accuracy), plus the existing work/frontier/cut/pump checks and
the new `check_bounded_lp.py` accounting check. The correctness gate
(`sparse_accuracy_gate.py --bounded-lp`) runs before timed comparisons: CTest
including the new randomized engine test, Python tests, disabled parity against
frozen 16, generated binary/mixed suites for five profiles, and the 100 retained
lattice cases under both engines.

## Decision rule

Promote the candidate to the recommended MILP evaluation profile only if:

- zero validation failures in every set;
- candidate completions (numerical, exact or corroborated terminal) are at least
  the control's in the development set and in the fresh holdout;
- any control completion the candidate loses is explained and retained;
- checked-point coverage does not fall.

Report objectives, bounds, gaps, first-point times, nodes and memory for every
record. Report timing only as fixed-budget outcomes, not speedup ratios. The
executable default stays unchanged in this iteration; any default change is a
separate decision after the evidence is reviewed.

## Amendment before the formal runs (reader conformance)

The first fresh-holdout launch (retained in `fresh-30s-attempt1-reader`) stopped
at input rejections in BOTH profiles: `dcmulti` has text after `ENDATA`,
`dsbmip` has a second `N` row, and a later parse check found `qiu` writes
`BV` bounds with a value. These are standard MPS conventions that HiGHS and
other readers accept. That attempt was stopped after the fiber and fixnet6
comparisons had printed to its log (and a khb05250 control run was killed by
the stop). Those two visible outcomes did not influence any change: the only
change concerns input parsing. All attempt records are retained as history and
the fresh set is rerun in full on the rebuilt executable.

The C++ reader and the independent Python exact checker now drop later `N`
rows with their entries, ignore text after `ENDATA`, and ignore an optional
numeric value on `BV`/`MI`/`PL`/`FR` bounds. Parsed row/column counts match
HiGHS on the affected models. All previously accepted inputs parse unchanged.
`tests/test_mps_contract.cpp` covers the new cases and duplicate-name errors.
This is a separate input-contract fix, reported separately from the relaxation
engine. The first frozen executable and its passing gate are retained in
`superseded-strict-reader`; the executable is rebuilt, re-frozen and re-gated,
and every declared set is then run on that single executable.
