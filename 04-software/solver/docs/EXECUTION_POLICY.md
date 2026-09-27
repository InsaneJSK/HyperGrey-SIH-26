# Execution policy — user instruction, 15 September 2026

CPU-only work runs locally. The assistant should build, run, inspect results,
and iterate without asking the user to upload/download a Kaggle notebook.
This includes current LP/MILP algorithms and the CPU constrained-QP solver.

Use Kaggle only when the experiment actually requires an NVIDIA GPU/CUDA.
The local machine has Intel integrated graphics; the optional CUDA box-QP
backend is an example of work that does require the separate GPU environment.
Do not use Kaggle merely to obtain Linux, longer CPU runs or another notebook
iteration. If a new local resource limitation arises, explain it before changing
the agreed workflow.

Preserve previous binaries, source snapshots, results and notebooks as versioned
evidence. Existing CPU-only Kaggle notebooks are historical/optional artifacts,
not pending work for the user. Any future required GPU notebook must still be
separate, use standard code, remain below1MB and save a single diagnostic/result ZIP.

Use bounded local experiments and sequential timed configurations for fair
comparisons. Save raw candidates, model/source/binary hashes, true failure/limit
statuses and independent checks. Do not loosen correctness gates or present
an incomplete solve as complete. A local result is not evidence of GPU execution.
