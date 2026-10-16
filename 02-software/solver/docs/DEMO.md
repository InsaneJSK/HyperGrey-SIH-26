# Command-line demonstration

`scripts/demo_cli.py` runs the five things a reviewer should see, in one pass,
and re-checks every answer with an independent HiGHS process that reads the
original file itself. No reference value is ever fed back into the solver.

```powershell
python -B scripts/demo_cli.py --binary reports/milp-iteration-31/final_solver_cli.exe --output reports/demo-<date>
```

Each step writes its own JSON (solver output, candidate point, reference
result), and `SUMMARY.json` collects the outcomes.

## What it shows

1. **Industrial LP — refinery planning and blending.** `marco_refinery.mps`, a
   published teaching model (GAMS library, after Kendrick/Meeraus/Suh and
   Aronofsky et al.) with two crudes, five processes, unit capacities,
   intermediate balances, blending compatibility and octane/vapour/density/
   sulfur specifications. The objective is cost minus revenue, so profit is the
   negated objective: **6.5884**, matching HiGHS to 1e-14 with a candidate
   violation of 1.1e-13 on the original rows.
2. **A what-if the operator would actually ask.** Tighten the fuel-oil sulfur
   maximum from 3.5 to 3.4 (`marco_low_sulfur.mps`, the source's own scenario).
   Profit falls to **0**: with the tighter specification no positive plan stays
   in spec, because residual sulfur has nowhere else to go. HiGHS agrees the
   optimum is 0. A tighter specification must never increase profit, and the
   demo asserts that.
3. **A sensitivity sweep instead of a single cliff.** The same model at 3.50,
   3.48, 3.46, 3.44, 3.42 and 3.40, changing only that one coefficient: profit
   6.5884, 2.5756, then 0 from 3.46 down. Every point is independently checked.
   That locates the economic break-even between 3.48 and 3.46 — the kind of
   answer a planner needs, and something a solver that only reported "infeasible"
   could not give.
4. **A MILP with integer decisions.** `production_lotsizing.mps` solves to
   proven optimality (762, gap 0, 7 nodes), with the point's feasibility and
   integrality confirmed independently.
5. **An honest limit and an honest rejection.** A hard public MILP (`mas74`) at
   a five-second budget returns `time_limit` with its incumbent and remaining
   gap, never an optimality claim. An MPS containing an unsupported `SOS`
   section is rejected with exit code 2 and the message
   `Unsupported MPS section: SOS`.

## What it does not show

The refinery case is a literature teaching model, not MRPL operating data, and
its quality equations are volumetric conventions from the source. Nothing here
demonstrates industrial scale: these models are small. The GPU path is not part
of this demo. See `docs/INDUSTRIAL_CASES.md` and `docs/LIMITATIONS.md`.
