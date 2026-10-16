# SolveForge media

[Project overview](../README.md) · [Architecture](diagrams/README.md) · [Screenshots](screenshots/README.md) · [Benchmarks](benchmarks/README.md) · [Demo playlist](videos/README.md)

Selected visuals for the SolveForge software project, PS 26119. Each asset is linked to its source below; benchmark graphics are generated from retained run records.

| Asset | Source | Description |
|---|---|---|
| [Presentation system design](diagrams/solveforge-system-design.png) | Architecture region rendered from page 3 of supplied `Hyper-Grey-software-5.pdf` | Presentation overview; use the implementation diagram and component guides for current API and backend selection |
| [Core and service architecture](diagrams/solveforge-architecture.svg) | Editable SVG drawn from the [core architecture](../02-software/solver/docs/V2_ARCHITECTURE.md), [CLI guide](../02-software/solver/docs/CLI_API.md), and [backend implementation](../02-software/backend/README.md) | Independent numerical core, eligible CUDA box-QP backend, original-model checks, and explicitly configured API modes |
| [Public workbench](screenshots/solveforge-web-workbench.jpg) | Browser capture of the [public solve page](https://sovereign-solver-gilt.vercel.app/solve), 16 October 2026 | Actual model-entry interface, captured at 1280 px width |
| [Refinery results](screenshots/solveforge-refinery-live.jpg) | Browser capture of the [refinery demo](https://sovereign-solver-gilt.vercel.app/refinery), 16 October 2026 | Returned six-point sulfur/profit sweep; base profit 6.5884, profit 2.5756 at 3.48, and zero at the sampled 3.46 limit |
| [Android overview](screenshots/solveforge-app-overview.jpg) | Original embedded JPEG from page 3 of supplied `Hyper-Grey-software-5.pdf` | Offline Android overview |
| [Android model entry](screenshots/solveforge-app-solve.jpg) | Original embedded JPEG from the same slide | LP/MILP/QP model-entry screen |
| [Android refinery case](screenshots/solveforge-app-refinery.jpg) | Original embedded JPEG from the same slide | Refinery planning workflow |
| [Android sensitivity](screenshots/solveforge-app-sensitivity.jpg) | Original embedded JPEG from the same slide | Sulfur/profit curve and returned results |
| [CPU/GPU timings](benchmarks/box-qp-cpu-gpu-t4-medians.svg) | Retained T4 box-QP run records | Five sizes, three configurations, three repeats; median reported solve times |
| [MIPLIB outcomes](benchmarks/miplib2017-historical-outcomes.svg) | Complete historical 240-instance campaign | Mutually exclusive outcomes under the recorded 300-second per-instance budget |

The four Android images retain their original 216 × 483 pixel resolution and JPEG bytes. They document the supplied application demonstration. The web captures show the public interface and returned teaching-model results; engine configuration and the independent-core benchmarks are described in their respective guides.

The [benchmark chart guide](benchmarks/benchmark-charts.md) provides exact input files, aggregation, timing definitions, and a reproducible generator. The architecture SVG remains directly editable in a vector editor or as XML.

## Demonstration links

- [Software demo playlist](https://www.youtube.com/playlist?list=PLRNv4l1yWhLs): offline/online Android, website, architecture, approach, and CPU/GPU routing walkthroughs.
- [Supplied project collection](https://drive.google.com/drive/folders/1nRVg4Sxxy0ztX5gHeZVvTwpCjPGWnLbT).
- [Android download collection](https://drive.google.com/drive/folders/1qeA-JjZ5pdWwm-EGbLhcT_W3obh-BZ51): `SolveForge-Offline.apk` and `SolveForge.apk`.

Further reading: [solver technical paper](../05-documentation/technical-report/solver_research.pdf) and [India cost/market study](../07-business/market/india_cost_analysis.pdf).
