# Next bounded work — first feasibility and honest proof progress

Keep selective and always-check refinement optional. Preserve the repaired
cold/warm LP, both modes' transformed equivalents, the unrefined control, and
every public failure. P0201 completes in the repeated screen and the wave.
Eil33-2 returns points in all four screen runs but in neither wave run: its
first-feasible outcome is not reliable yet. None of this establishes a universal
default choice or an optimal full mas74 solve.

## First-feasible experiment

Prioritize the retained 30s no-point cases, with blend2, lotsize and eil33-2 as
explicit development targets. Their selective wave runs report zero numerical recovery and
zero unresolved nodes, so do not assume more residual correction is the fix.
Blend2 spends about 12.37s in dives, 11.56s in tree LPs and 4.62s in pump
projection. Lotsize spends about 10.00s in pump projection, 6.51s in dives,
5.92s in tree LPs and 4.85s in root LPs. These are phase measurements, not a
diagnosis of the exact search mechanism. Eil33-2 spends 10.01s in pump projection
in the no-point wave run versus 5.00s in its first successful screen run. The
same configuration follows different time-limited heuristic paths; this is an
observed allocation/path difference, not yet a proved root cause.

1. Capture bounded pump/dive diagnostic traces on the saved inputs: integer
   distance, repeated rounded/fixed assignments, LP outcomes, progress before
   budget exhaustion and original-model rejection reasons. Distinguish cycling,
   infeasible fixings, slow LPs and weak branching before changing a heuristic.
   Freeze a failing trajectory and exercise the relevant branch in a regression.
2. Implement only the general mechanism supported by that evidence, without
   model-name switches, published solutions, tolerance loosening or hidden
   extra recovery/time budgets. If no reproducible mechanism is established,
   report that result rather than stacking unrelated heuristics.
3. Repeat matched 30s controls on the targets and on the existing regression
   sentinels p0201, eil33-2, binkar10_1 and mas74. Keep the candidate binary and
   budget fixed, rotate order, and separate all references from own timings.
   Measure checked first-point rate/time, final objective, bound/gap and status;
   do not select only the best repeat.
4. Keep the new danoint/rout no-point cases in the same diagnostic ledger.
   Danoint's selective run spends 12.62s on six tree LP calls and 9.12s in pump
   projection; rout spends 12.03s in tree LPs and 9.45s in dives. Both use some
   recovery, unlike the first three targets. Diagnose those paths separately;
   do not assume one heuristic change solves every no-point mechanism.
5. Run the complete 27-model development ledger, then predeclare additional
   genuinely untouched inputs by structure and size before any candidate runs.
   Danoint/rout/mas76 are no longer fresh after iteration18; mas76 is not an
   unseen family. Preserve every timeout, no-point and numerical failure.

## Proof and submission work remain separate

Large gaps on models such as gt2, pk1 and mas74 need stronger valid bounds and
search, not merely earlier incumbents. Diagnose bound weakness separately from
the first-feasible change. General LP/MILP numerical completion is not an exact
rational certificate; restricted binary exact proofs must remain labeled.

The full 240-instance MIPLIB2017 benchmark is a coverage target, not a guarantee
that any finite iteration count will prove every public or arbitrary MILP.
Before a large batch, enforce and test explicit per-process memory/time limits,
keep resource exits honest, and size the batch for this local machine. Existing
in-process budgets do not constitute hard operating-system containment.

For submission, real MRPL/domain-expert case validation, an end-to-end CLI/API
demo with reproducible evidence, installation/resource hardening, and repeated
final GPU-specific measurements remain outstanding. Historical synthetic QP
GPU results do not prove GPU MILP acceleration or this final snapshot's speed.
CPU development stays local. No user input or Kaggle upload is needed for the
next solver experiment; use Kaggle only when actual CUDA/GPU work is ready.
