# Industrial case evidence

`scripts/industrial_cases.py` independently builds four MPS models. Their hashes,
variable names and sources are in `examples/industrial/manifest.json`.

## Refinery planning and blending

`marco_refinery.mps` reformulates the numerical MARCO example from the
[GAMS model library](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html),
which cites Kendrick, Meeraus and Suh (1981) and Aronofsky, Dutton and
Tayyabkhan (1978). It includes two crude sources, five processes, unit capacities,
intermediate balances, blending compatibility, sales, crude and butane costs,
operating costs, octane, vapor-pressure, density and sulfur specifications.

The objective minimizes costs minus revenue, so a negative solver objective is
positive refinery profit. Volumetric yield/quality conventions are those of the
published teaching model; they are not a universal physical blending law.
`marco_low_sulfur.mps` applies the source's tighter fuel-oil sulfur scenario,
changing its maximum from 3.5 to 3.4. Profit should not increase under this change.

These are historical literature cases, not current MRPL operating data or a
domain-expert-approved refinery deployment. Quality equations and units need
engineering validation before operational use.

## Supply-chain transportation

`transport_dantzig.mps` uses the capacities, demands and distances from
[TRNSPORT](https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html),
which cites Dantzig (1963). It minimizes shipment costs from two plants to three
markets. The known optimum is 153.675 in the model's thousands-of-dollars units.

## Multi-period production

`production_lotsizing.mps` is a synthetic six-period fixed-charge production and
inventory model. Its binary setup decisions, capacity constraints, stock balances
and final empty-stock requirement demonstrate an integrated MILP application.
The numerical data is generated for this project and is not sourced factory data.

All four models are independently parsed and solved by HiGHS in the V2 harness.
This verifies the emitted MPS solutions, not every modeling assumption. Candidate
flows, objectives and independent violations are retained in the raw JSON files.
