# Local iteration08: stronger checked binary capacity cuts

Baseline: preserved iteration07 CLI3e623c0c... . Binkar iteration05 guided run
has zero failed/recovered/deferred global LPs but a final lower bound6664.91
versus incumbent6747.31. This is weak/slow bound progress, not a demonstrated
numerical-recovery blocker. Original Binkar has2298 columns,170 binaries,
1026 rows and ten pure-binary17-variable capacity rows.

Test an opt-in --lifted-covers root separator on small binary knapsacks. Exact
dyadic arithmetic enumerates feasible assignments of each parsed source row;
sequential up-lifting strengthens promising minimal covers. Independently
recompute all row-feasible assignment activities before exporting each cut.
No model names, published answers or reference incumbents enter the algorithm.
Unsupported arithmetic/domains and interrupted checks export no unverified cut.
Keep existing root LP validation/rollback and original-model candidate gates.

Validate exhaustive/adversarial cuts, generated mixed/binary models, independent
cut verification, root bound screens and equal-budget Binkar runs locally.
Retain markshare exact-proof tests. No Kaggle/GPU work is needed. Preserve all
neutral/regressive experiments and do not promote based on a single timing pass.
