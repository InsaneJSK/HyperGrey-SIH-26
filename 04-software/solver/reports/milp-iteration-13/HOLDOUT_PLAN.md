# Untouched holdout selection — declared before solving

Selected15 September2026 by published size/structure, before any own or reference
solve of these models in this project. Four members of the official MIPLIB2017
benchmark, not four newly invented2026 problems or a representative full-library
sample. The selection deliberately includes unsupported lattice structures.

| Model | Published variables / rows | Reason |
|---|---:|---|
| gen-ip002 | 41 / 24 | Dense general-integer generated problem |
| assign1-5-8 | 156 / 161 | Binary assignment with continuous variables |
| lotsize | 2985 / 1920 | Mixed lot-sizing / service-level structure |
| eil33-2 | 4516 / 32 | Many-column binary set partitioning / routing approximation |

Official membership: https://miplib.zib.de/tag_benchmark.html
Model metadata and download links:
- https://miplib.zib.de/instance_details_gen-ip002.html
- https://miplib.zib.de/instance_details_assign1-5-8.html
- https://miplib.zib.de/instance_details_lotsize.html
- https://miplib.zib.de/instance_details_eil33-2.html

Use unmodified official .mps.gz files and retain both compressed/model hashes.
No solution files or published objectives are imported into the solver.
Freeze selection regardless of eligibility, parse failure, timeout or outcome.

After the first-wave correctness comparisons: one30s pair per model, lattice
versus raw-LP ranking, same profile and gap1e-6 as the first wave. Node cap250000,
external watchdog45s, default16M-cell dense-fallback guard. This is NOT a total
process-memory cap; no measured RSS or full memory-limit claim. References5s,
one thread, only after all own timings. CPU only. No post-holdout tuning of the
candidate in this iteration. Retain every failure instead of swapping cases.
