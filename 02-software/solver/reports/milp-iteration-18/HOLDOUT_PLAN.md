# Predeclared new-instance checks, 16 September 2026

Before any solver runs on these inputs, select danoint, rout and mas76 from
the public MIPLIB collection. Check previous local manifests/results for prior
use, download bounded MPS files, and retain input hashes. Published solutions
are not downloaded or supplied to the solver. Metadata pages were inspected;
this is not a blinded-to-published-objective competition experiment.

- [danoint](https://miplib.zib.de/instance_details_danoint.html): 521 variables,
  664 constraints, 56 binary and 465 continuous variables; telecom flow model.
- [rout](https://miplib.zib.de/instance_details_rout.html): 556 variables,
  291 constraints, including 15 general integers and 241 continuous variables.
- [mas76](https://miplib.zib.de/instance_details_mas76.html): 151 variables,
  12 constraints. It is closely related to mas74, so it tests unseen-instance
  transfer, not an independent unseen-family claim.

These are moderate historical instances, catalogued as easy for mature solvers,
not a claim to tackle the hardest MIPLIB industrial-scale class. The three
selected cases do not alone establish degeneracy or ill-conditioning coverage.
Existing transformed LP regressions remain a separate numerical stress gate.

Use the fixed candidate, one alternating-order control/candidate pair per case,
30 seconds, 250000 nodes, gap1e-6 and unchanged recovery budgets. The full
development wave and holdouts are characterization after a passing correctness
gate and valid screen outputs, even if performance is mixed. No default
promotion solely from diagnostic timing; retain all failures and require
repeatability and first-feasible/completion regressions to be resolved first.

The attempted gesa2 metadata page was unavailable to the browsing tool; rout
was selected instead before downloading or running either model.
