# GPU box-QP validation, repeated measurements (Kaggle T4)

18 September 2026. The first repeated CPU/GPU comparison for this project, on
the current source. Earlier GPU evidence was a single timing pass; this run has
three repeats for every size and backend, all checked against a planted optimum.

Device: **Tesla T4, 15360 MiB, driver 580.159.04, compute capability 7.5**,
host CPU Intel Xeon @ 2.00 GHz with 4 cores. Session run from this machine
through the Kaggle API; the local development machine has no NVIDIA GPU.

## Result

45 of 45 runs returned `optimal` and passed their own accuracy check
(`relative objective error <= 1e-8`, `max solution error < 1e-4`). Median solve
seconds, three repeats each, same accuracy contract everywhere:

| Variables | CPU 1 thread | CPU 4 threads | GPU (T4) | GPU vs 1 thread |
|---:|---:|---:|---:|---:|
| 10,000 | 0.116 | 0.084 | 0.382 | 0.30x (slower) |
| 50,000 | 0.573 | 0.396 | 0.514 | 1.11x |
| 200,000 | 2.551 | 1.616 | 0.980 | 2.60x |
| 500,000 | 7.314 | 4.086 | 1.900 | 3.85x |
| 1,000,000 | 15.923 | 8.342 | 3.501 | 4.55x |

The crossover is the useful part: **below about 50,000 variables the GPU path
is slower than one CPU thread**, because transfers and kernel setup dominate.
It becomes worthwhile from roughly 200,000 variables and reaches 4.55x against
one thread, or 2.38x against four threads, at one million variables.

## Independent checks

- The planted family's optimum was recomputed here in Python from the generator
  definition for n = 10,000 and 50,000 and matches the values the session
  reported (-947.124889445 and -4710.360537563).
- Worst relative objective error across all 45 runs: **8.2e-14**. Worst maximum
  solution error: **6.0e-6**, within the declared 1e-4 contract.
- CPU and GPU objectives agree per size to 9.1e-13 or exactly.

## Scope and limits

- Box-constrained convex QP only. This is not a GPU MILP result and not a
  general constrained-QP GPU claim; the CUDA path covers the box-QP kernel.
- One planted tridiagonal family, one session, one device. The spread across
  three repeats is not a statistical study of cloud timing variation.
- Timings are end-to-end process measurements including transfers and setup,
  taken on a shared cloud machine. They support the crossover statement above,
  not a general performance ranking against other solvers.
- Process versus device memory attribution is still not resolved here; no VRAM
  figure is claimed.

Artifacts: `kernel/gpu_validation.py` (the submitted script),
`returned/results.json` (all 45 records), `returned/SUMMARY.json`, and the
session log. The source came from the `sih26119-solver-source` dataset built
from this repository's `src`, `include` and `tests`.
