# 12-benchmarks-formats

Benchmark libraries and input formats

## What this folder supports

MIPLIB, Netlib, QPLIB and Mittelmann provenance; precise MPS/QPLIB semantics and problem-class filtering.

**Problem-statement mapping:** PS-11, PS-12, PS-14 (IDs follow the preserved PS_REQUIREMENTS matrix).

## Where it is used in our work

- [src/mps.cpp](../../02-software/solver/src/mps.cpp)
- [docs/MPS_DOMAIN_CONTRACT.md](../../02-software/solver/docs/MPS_DOMAIN_CONTRACT.md)
- [docs/MPS_DUPLICATE_OBJECTIVES.md](../../02-software/solver/docs/MPS_DUPLICATE_OBJECTIVES.md)
- [datasets/README.md](../../02-software/solver/datasets/README.md)

## Scope note

Library membership does not mean a model is supported or has been solved. Preserve input and reference-solution versions.

## Sources (7; 2 PDFs held)

| Year | Title | Venue / source | Local copy and note | Original |
|---|---|---|---|---|
| 2021 | MIPLIB 2017: Data-Driven Compilation of the 6th Mixed-Integer Programming Library | Mathematical Programming Computation 13, 443-490 | [PDF](2021-miplib-2017-data-driven-compilation-of-the-6th-mixed-integer-programming-library.pdf) / [note](2021-miplib-2017-data-driven-compilation-of-the-6th-mixed-integer-programming-library.source.md) | [source](https://doi.org/10.1007/s12532-020-00194-3) |
| 2026 | MIPLIB 2017: Downloads and solution files | Official benchmark documentation | [note](2026-miplib-2017-downloads-and-solution-files.source.md) / reference only | [source](https://miplib.zib.de/download.html) |
| 2026 | QPLIB Documentation: Problem Types and File Format | Official QPLIB documentation | [note](2026-qplib-documentation-problem-types-and-file-format.source.md) / reference only | [source](https://qplib.zib.de/doc.html) |
| 2026 | Netlib LP test problems | Official benchmark archive | [note](2026-netlib-lp-test-problems.source.md) / reference only | [source](https://www.netlib.org/lp/data/) |
| 2026 | Model File Formats: MPS Format | Gurobi Optimizer Reference Manual | [note](2026-model-file-formats-mps-format.source.md) / reference only | [source](https://docs.gurobi.com/projects/optimizer/en/current/reference/fileformats/modelformats.html) |
| 2026 | Decision Tree for Optimization Software: Benchmarks | Arizona State University benchmark service | [note](2026-decision-tree-for-optimization-software-benchmarks.source.md) / reference only | [source](https://plato.asu.edu/sub/benchm.html) |
| 2018 | QPLIB: A Library of Quadratic Programming Instances | Mathematical Programming Computation; author manuscript | [PDF](2018-qplib-a-library-of-quadratic-programming-instances.pdf) / [note](2018-qplib-a-library-of-quadratic-programming-instances.source.md) | [source](https://optimization-online.org/2017/02/5846/) |

## Reading notes

- **miplib-paper:** Explains benchmark selection, instance diversity, solution checking and reference-version provenance.
- **miplib-downloads:** Use versioned instance sets, reference solutions and the independent checker for reproducible MILP evaluation.
- **qplib:** Defines QPLIB type codes and coefficient conventions needed to select the supported convex continuous subset.
- **netlib-lp:** Historical sparse LP benchmark source, including degenerate models and compressed MPS input.
- **mps-format:** Reference for row types, integer markers, variable bounds and objective conventions in MPS parsing.
- **mittelmann:** Find declared benchmark sets and comparison protocols for future solver evaluation.
- **qplib-paper:** Explains QP taxonomy and dataset construction for representative convex-QP selection.

[Back to the research index](../README.md)
