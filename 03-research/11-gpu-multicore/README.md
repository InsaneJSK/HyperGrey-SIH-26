# 11-gpu-multicore

GPU and multicore optimization

## What this folder supports

GPU-friendly sparse operations, transfer overhead, parallel algorithm structure and CPU/GPU comparisons.

**Problem-statement mapping:** PS-07, PS-08, PS-10 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/cuda_box.cu](../../04-software/solver/src/cuda_box.cu)
- [src/accelerated_qp.cpp](../../04-software/solver/src/accelerated_qp.cpp)
- [src/scale_benchmark.cpp](../../04-software/solver/src/scale_benchmark.cpp)

## Scope note

Existing GPU measurements cover box-constrained convex QP. They do not establish accelerated general LP or MILP.

## Sources (4; 3 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2020 | GPU Acceleration of ADMM for Large-Scale Quadratic Programming | Journal of Parallel and Distributed Computing 144, 55-67 | [PDF](2020-gpu-acceleration-of-admm-for-large-scale-quadratic-programming.pdf) / [note](2020-gpu-acceleration-of-admm-for-large-scale-quadratic-programming.source.md) | [source](https://arxiv.org/abs/1912.04263) |
| 2025 | cuPDLP.jl: A GPU Implementation of Restarted Primal-Dual Hybrid Gradient for Linear Programming in Julia | Operations Research 73(6), 3440-3452; arXiv author version | [PDF](2025-cupdlp-jl-a-gpu-implementation-of-restarted-primal-dual-hybrid-gradient-for-linear-programming-in-julia.pdf) / [note](2025-cupdlp-jl-a-gpu-implementation-of-restarted-primal-dual-hybrid-gradient-for-linear-programming-in-julia.source.md) | [source](https://arxiv.org/abs/2311.12180) |
| 2023 | cuPDLP-C: A Strengthened Implementation of cuPDLP for Linear Programming by C language | arXiv technical report | [PDF](2023-cupdlp-c-a-strengthened-implementation-of-cupdlp-for-linear-programming-by-c-language.pdf) / [note](2023-cupdlp-c-a-strengthened-implementation-of-cupdlp-for-linear-programming-by-c-language.source.md) | [source](https://arxiv.org/abs/2312.14832) |
| 2026 | CUDA C++ Best Practices Guide | Official developer documentation | [note](2026-cuda-c-best-practices-guide.source.md) / reference only | [source](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html) |

## Reading notes

- **gpu-admm:** Direct research comparator for GPU sparse ADMM kernels and end-to-end large-QP performance.
- **cupdlp-julia:** Demonstrates a GPU-friendly LP algorithm direction based on matrix-vector products and restarts.
- **cupdlp-c:** Implementation-level GPU LP comparison: hardware, language overhead and matched end-to-end evaluation.
- **cuda-best-practices:** Supports coalesced access, minimizing host/device transfers, profiling and measuring whole-program speedup.

[Back to the research index](../README.md)
