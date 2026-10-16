# Iteration15 — predeclared selective root-cut continuation

CPU only. Preserve iteration14 and all older archives. No benchmark-name rules,
imported reference incumbents, tolerance changes, or general exact-proof claim.

## Candidate fixed before coding/timings

New opt-in `--adaptive-cut-rounds`, retaining the existing maximum five rounds
per root and the existing full-domain restart. Keep at least two SUCCESSFUL
rounds when cuts/time/the explicit round cap permit. Keep cheap rounds whose
MILP-visible LP work is less than 256 reported iterations. For other successful
rounds with nonzero root-LP work, use minimization-sense raw numerical LP bounds:

    scale = max(1, abs(before - signed_offset), abs(after - signed_offset))
    gain = max(0, after - before) / scale
    effort = max(1, round_iterations / root_iterations)
    stop if gain <= 0.001 * effort

Use binary64 arithmetic with finite guards; nonfinite/unavailable metrics mean
CONTINUE under the old round/time caps. Missing (zero) root work also continues.
This is an experimental allocation decision, not a new valid bound. Subtracting
the objective offset reduces translation sensitivity but cannot remove binary64
cancellation; scale floor 1 is explicitly not invariant under arbitrary scaling.
Reported LP iterations include visible recovery/fallback work. They are a proxy,
not a hard pivot/FLOP/memory or wall-time bound. Minimum-two and the 256 floor
are development-informed safeguards, not fitted universal constants.

Evaluate after successful verified LPs only. Failed optional cut LPs retain the
existing rollback and terminal handling. Do not change proof-bound publication,
frontier coverage, heuristic budgets, or node ranking. Capture each attempted
cut round and its reason; at most ten attempts under the existing one restart.
Default capture and adaptive policy are off; five rounds remain the default.

## Evidence sequence (one unchanged candidate)

1. Build in `build-milp-iter15`. Policy boundary/invalid-metric tests, exhaustive
   mixed min/max models, partial/zero-time outcomes, default/capture parity,
   parser domains and independent trace replay. Exercise stopping decisions
   directly; tiny cases need not reach the production 256-iteration floor.
2. Paired 30s screen on Binkar, p0282 and mod008, then two NEW rotated repeat
   pairs on each of these three targets. Keep adverse outcomes and no-points.
3. Same 30s pair on all 21 existing public development cases, no post-screen
   tuning, followed by the three predeclared fresh holdouts below. Own solves
   precede independent references; no concurrent builds/checks during timings.
4. Re-audit unchanged saved outputs, phase sums, cut decisions, cuts/lattice/
   frontier checks and exact-subset claims. Final regression gate and archive.

Common comparison flags retain iteration14's robust, raw/lattice/late-cut
profile plus `--capture-work --capture-cut-rounds`. Both policies have a five-
round maximum. Own limits: 30s, 250000 nodes, gap 1e-6, 45s external watchdog.
References: configured 5s with external 150s allowance, run separately; this is
not an equal-budget solver speed comparison. Keep reference timeouts explicit.
Optimize the reference sparse-array access only with frozen14 equivalence checks
before any timings; do not count checker speed as engine speed.

## Fresh holdouts selected by size/structure

Verified in the [official MIPLIB2017 benchmark index](https://miplib.zib.de/tag_benchmark.html)
before solver runs. Never place the site's objective answers inside the solver.

- `mas74`: 151 variables (150 binary, one continuous), 13 constraints.
- `gen-ip054`: 30 general integers, 27 constraints.
- `neos859080`: 160 variables (80 binary, 80 general integer), 164 constraints;
  the source labels it infeasible, testing negative-outcome handling.

Download the unchanged official compressed MPS files, retain provenance and
hashes, cap downloads at 16 MiB compressed / 64 MiB decompressed. Do not replace
failed downloads or difficult outcomes. These cases become development data
after this iteration. No claim of all-library or industrial-scale coverage.
