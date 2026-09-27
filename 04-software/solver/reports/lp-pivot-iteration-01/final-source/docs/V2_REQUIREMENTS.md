# SIH26119: V2 requirement coverage

The supplied `Problem Statement.txt` is the controlling source. Its final
dataset paragraph is truncated; no missing requirement is inferred. This matrix
distinguishes implemented capability from the PS's broader performance ambition.

| PS area | V2 capability/evidence | Remaining obligation |
| --- | --- | --- |
| Own solver core | CMake compiles our numerical and optimization code; references are separate processes | Preserve provenance and obtain organizer interpretation of permitted infrastructure |
| LP | Sparse revised primal/dual simplex, scaling, basis reuse, numerical checks and recession rays | Broader ill-conditioning coverage and production numerical recovery |
| MILP | Own branch-and-cut, propagation, cover/lifted cuts, heuristics, repair and gap tracking; restricted exact proof for Markshare; independently checked earlier Blend2 numerical completion | Binkar remains incomplete; stronger general bounds/search and broader repeated modern-MILP evidence |
| QP | Continuous convex box/general-linear paths; original QPLIB 9002 passes independent numerical KKT/dual-gap checks locally | 9002 reference comparison remains incomplete; absolute operational errors, broader QP coverage and nonconvex scope clarification |
| MIQP/NLP/MINLP extension | Separate model, sparse algebra and algorithm APIs | Algorithms for these future classes are not implemented |
| Sparse algebra | Sparse input/CSR products, LU and eta updates | Fill growth can still be expensive; no production sparse reordering package |
| Multicore | OpenMP QP products and iterations; repeated 1/4-thread measurements | Wider workloads; no parallel MILP tree or parallel simplex |
| GPU | P100 compiled/executed our CUDA box-QP kernels; all three planted CUDA scale cases passed through one million variables | Single timing pass only; repeated measurements, public box-QP GPU checks and reliable memory diagnostics |
| Numerical robustness | Analytical/cycling/scaling/PSD tests, original-model gates, independent checks; exact arithmetic only in the explicitly restricted binary-proof subset | General LP/MILP/QP use numerical, not exact/interval certificates; difficult public failures remain |
| Industrial scale | Synthetic million-variable sparse box QP with known optimum | General million-variable LP/MILP/constrained QP and real industrial scale unproven |
| Recognized benchmarks | Netlib, historical MIPLIB, QPLIB, additional MIPLIB 2017 selection | Broader sets and Mittelmann runs; no full-library coverage |
| Established reference | HiGHS/OSQP, independent model parsing and original-solution checks | Repeat larger public workloads on final hardware; preserve incomplete references |
| Industrial use cases | Literature refinery planning/blending and transportation; synthetic multi-period production | MRPL data or domain-expert validation; operational deployment unproven |
| API/CLI | C++ APIs, MPS/QPLIB/lpmini CLI and JSON diagnostics | Stable ABI, broader format support and additional platform validation |
| Transparency | Phase records, source/input/binary hashes, reproduction scripts, notebook snapshot and audited Kaggle return bundle | Final report after remaining robustness/performance work; keep limitations visible |

Detailed implementation: `V2_ARCHITECTURE.md`. The original V2 evidence is
preserved in `../reports/V2_REPORT.md`; later results are version-specific.
Read [current submission assessment](SUBMISSION_ASSESSMENT.md),
[MILP iteration09](../reports/milp-iteration-09/REPORT.md),
[MILP iteration10](../reports/milp-iteration-10/REPORT.md), and
[QP iteration01](../reports/qp-iteration-01/REPORT.md).
Outstanding inputs: `V2_REMAINING.md`.
First GPU return: `../reports/KAGGLE_GPU_REPORT.md`.
