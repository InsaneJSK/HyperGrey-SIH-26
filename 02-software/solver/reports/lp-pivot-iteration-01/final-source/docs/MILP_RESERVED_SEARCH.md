# Iteration06: reserved, coupled incumbent search

Experimental CPU-only mode: `--improve-incumbent --neighborhood reserved`.
Selecting a neighborhood alone does not enable it. Existing `guided` and
`diversified` behavior and the default remain available and unchanged.
Results and promotion decisions belong in `reports/milp-iteration-06/REPORT.md`;
adding a method is not evidence that it improves the hard cases.

## What changed

Iteration05 exhausted markshare's calls before its best incumbent appeared.
Its late diversified binkar attempt received only about 0.2 seconds. The new
mode reserves both calls and usable time, and stops treating tiny floating-point
objective differences as a reason to restart a productive search sequence.

Only scheduling uses a material-gain threshold: in normalized minimization
sense, before - after must exceed 1e-6 * (1 + abs(before)). Acceptance still uses
the original strict objective comparison, original absolute feasibility <=1e-7,
and integer tolerance <=1e-7 with rounding within that tolerance. A tiny accepted
improvement is still recorded, but does not reset this mode's stall counter.
A material improvement from the main tree resets that counter too.

## Reserved schedule

The total allowance is unchanged: min(30 seconds, 15% of the global time limit),
at most16 calls, and at least128 processed main-tree nodes between calls.
These are cooperative time limits; an individual numerical operation can overrun.

- Start with the original guided variable-selection rule, up to2 seconds and
  64 local nodes per call.
- Guided work can use at most12 calls and80% of the total local-search allowance.
  Four consecutive calls without material progress also trigger strong mode.
- Once strong mode starts, do not return to guided mode. Allow at most four
  strong calls: one before40% of the global time budget, three before65%, and
  all four afterward. Quotas are upper limits, not promises that a call will run;
  the main solve may terminate first.
- Space strong starts by10% of the global time limit unless the current incumbent
  materially improves on the center used at the previous strong start. Such an
  improvement bypasses spacing only, never the release quotas.
- Each strong call gets up to4 seconds and512 local nodes. Its time slice is also
  capped by remaining cumulative allowance / remaining strong calls. Thus one
  early strong call cannot consume all the reserved time.
- Every call remains capped by20% of remaining global time. An additional
  `--pace-neighborhood` gate, if explicitly supplied, still applies to all calls.

The implementation and clock-independent schedule tests are in
`include/milp_neighborhood.hpp` and `tests/test_v2.cpp`. No problem name, known
optimum, uploaded reference vector or external optimizer enters this policy.

## Coupled binary neighborhood

Strong mode releases every movable integer whose original integer domain is
exactly {0,1}, keeps other integers fixed to the current incumbent, and keeps
continuous variables free in their original domains. It adds the PRIVATE row

    sum(x[j] for center[j]=0) + sum(1-x[j] for center[j]=1) <= radius

Radii alternate4,8,4,8. This allows coupled flips anywhere in the binary model,
instead of requiring every useful variable to belong to a small LP-ranked set.
It is an independently coded, bounded heuristic use of the Hamming neighborhood
described by [Fischetti and Lodi's local-branching work](https://site.unibo.it/operations-research/en/research/library-of-codes-and-instances-1/mic2003-lb.pdf/@@download/file/mic2003-lb.pdf),
not an implementation of that paper's complete external search framework.

With no eligible binaries, strong mode falls back to the existing deterministic
diversified integer selection (up to96 released integers), retaining its stronger
local node allowance. It is not an unrestricted general-integer distance ball.
The added row requires a fresh root basis; child solves reuse compatible bases.

The private LP model, private DFS, local bounds, incomplete/failing relaxations
and exhausted local stack NEVER enter the main proof queue. Only independently
checked original-model feasible incumbents are exported. The main solver's
near-integer repair proof correction from iteration04 is unchanged.

## Evidence and reproduction

Diagnostics record the material-progress flag, strong/guided flag, radius, free
integer indices, and a strong binary call's center vector on models with at most
10000 variables. Improved vectors are captured as before. The independent audit
reconstructs the schedule, checks Hamming distance and fixed integer membership,
and re-evaluates captured centers, final candidates and available improved/repair
vectors against the original MPS using the separate reference reader.
Intermediate within-call improvements may still have objective-only traces.

Build into a NEW directory with CUDA disabled; never rebuild archived baselines.

```powershell
cmake -S . -B build-milp-iter6 -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DSOVEREIGN_ENABLE_CUDA=OFF -DCMAKE_CXX_COMPILER=C:/mingw64/bin/c++.exe
cmake --build build-milp-iter6 -j 4
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/test_milp_diagnostics.py
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/validate_milp_focus.py --build build-milp-iter6 --output reports/my-reserved-comparison --limit 180 --nodes 250000 --reference-limit 30 --experiment reserved
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/audit_local_milp.py reports/my-reserved-comparison --binary build-milp-iter6/solver_cli.exe --output reports/my-reserved-audit
```

Run benchmarks sequentially, without competing numerical work. The runner does
CTest and240 generated checks first, then alternates baseline/candidate order
across three models. Reference solves follow all timed runs. No Kaggle notebook,
GPU run, package installation or result upload is needed for this CPU experiment.
