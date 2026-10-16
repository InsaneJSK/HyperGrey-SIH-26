# 01-research - SIH26119 research library

Sources are organized by the mathematical technique, engineering decision or industrial use case they support, following the numbered topic-folder structure of the Hyper-Grey-SIH-26 reference repository.

**60 sources across 15 topics: 43 PDFs held locally and 17 reference-only entries.** Every entry has an original source note with its citation, relevance, scope and retrieval status. Curated on 2026-09-27.

## Index

| Folder | Sources | PDFs held | Supports |
|---|---:|---:|---|
| [01-foundations-duality](01-foundations-duality/README.md) | 3 | 2 | LP/QP formulations, weak and strong duality, KKT conditions and the distinction between a feasible point and a proof of optimality. |
| [02-revised-simplex](02-revised-simplex/README.md) | 3 | 3 | Primal/dual revised simplex, bounded variables, hyper-sparse pivots and reusable basis representations. |
| [03-sparse-linear-algebra](03-sparse-linear-algebra/README.md) | 3 | 2 | Sparse products, LU fill, triangular solves, Krylov methods and preconditioners for the LP and QP engines. |
| [04-numerics-certificates](04-numerics-certificates/README.md) | 5 | 4 | Scaling, residual checks, iterative refinement, safe pruning and exact-versus-tolerance-based verification. |
| [05-presolve-propagation](05-presolve-propagation/README.md) | 3 | 2 | Bound tightening, substitution, formulation strengthening, postsolve reconstruction and safe parallel reductions. |
| [06-branch-bound-search](06-branch-bound-search/README.md) | 3 | 3 | Relaxation bounds, reliability branching, node selection, conflict reasoning and modular solver architecture. |
| [07-cutting-planes](07-cutting-planes/README.md) | 4 | 3 | Gomory/MIR, cover inequalities, cut validity, numerical safety and the tradeoff between stronger bounds and harder LPs. |
| [08-primal-heuristics](08-primal-heuristics/README.md) | 4 | 4 | Feasibility pumps, diving, rounding, repair and budgeted neighborhood searches for early feasible incumbents. |
| [09-convex-quadratic-programming](09-convex-quadratic-programming/README.md) | 4 | 3 | ADMM, projected/proximal methods, semidefinite Hessians and primal/dual stopping conditions. |
| [10-large-scale-continuous](10-large-scale-continuous/README.md) | 4 | 4 | PDHG restarts, interior-point systems and infeasibility detection for large sparse continuous models. |
| [11-gpu-multicore](11-gpu-multicore/README.md) | 4 | 3 | GPU-friendly sparse operations, transfer overhead, parallel algorithm structure and CPU/GPU comparisons. |
| [12-benchmarks-formats](12-benchmarks-formats/README.md) | 7 | 2 | MIPLIB, Netlib, QPLIB and Mittelmann provenance; precise MPS/QPLIB semantics and problem-class filtering. |
| [13-evaluation-reproducibility](13-evaluation-reproducibility/README.md) | 4 | 3 | Performance profiles, full failure accounting, fair stopping criteria, repeated runs and progress over time. |
| [14-refinery-blending](14-refinery-blending/README.md) | 4 | 3 | MRPL context, refinery material/quality balances, time-dependent scheduling and boundaries between LP/MILP and MINLP. |
| [15-production-logistics-power](15-production-logistics-power/README.md) | 5 | 2 | Transportation, lot sizing, supply-chain scheduling, economic dispatch and unit commitment as solver use cases. |

## Start here

Read [RESEARCH_MAP.md](RESEARCH_MAP.md) for priority reading and open research questions. [_CONTENTS.md](_CONTENTS.md) lists every entry. [references.bib](references.bib) provides portable citations. [CURATION.md](CURATION.md) records the collection checks and access limitations.

## Relation to the software problem statement

The controlling requirement is SIH26119, the MRPL from-scratch GPU-accelerated optimization solver problem. Its supplied dataset paragraph is truncated; no missing requirement has been invented. The local solver and its dated experiment reports remain the authority on what is implemented and measured.

External libraries appear here as papers, documentation, benchmark sources or independent comparison systems. Collecting their literature does not add a solver dependency or claim their algorithms are already implemented.

## Sourcing, versions and rights

Downloads come from arXiv, author/institutional repositories, publishers and official documentation/report hosts. Public accessibility does not imply a blanket redistribution license. Source notices remain in the unmodified PDFs, and source notes distinguish preprints, technical reports, final publications and living documentation. Books or publisher items selected as citation-only are not mirrored.

Filenames use `YYYY-lower-case-hyphenated-title.pdf`; the year is the catalog citation year. For living documentation, it is the access year and the note says so. A preprint may have an earlier date than its final journal citation. Retrieval timestamps, resolved URLs, byte counts, page counts and SHA-256 hashes are in [retrieval.json](retrieval.json).

## How to add or maintain a source

1. Add one entry to `catalog.json`, under the single topic it primarily supports. Write a concrete relevance sentence and scope/version note.
2. Set `pdf_url` only to a legitimate public full-text location; otherwise retain a reference note. Do not substitute an unrelated PDF when retrieval fails.
3. From `01-research`, run `python tools/library.py fetch --ids SOURCE_ID` to collect it (requires network and `pypdf`). Existing PDFs are never overwritten.
4. Run `python tools/library.py build`, then `python tools/library.py verify` to update and audit the indexes. `verify` is offline.

Counts are generated from actual successful PDF retrievals, not planned downloads. The collection is deliberately selected for relevance rather than a fixed number of papers per folder.
