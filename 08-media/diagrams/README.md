# Architecture diagrams

- [Presentation system design](solveforge-system-design.png): architecture region rendered from page 3 of the supplied submission slides; featured in the main README.
- [Core and service implementation](solveforge-architecture.svg): editable SVG derived from the repository's C++ core, CLI and FastAPI adapter.

The presentation shows the system design. The API selects its engine through `SOLVER_ENGINE`; the C++ CLI selects CUDA explicitly for eligible box-constrained QPs. See the [backend guide](../../04-software/backend/README.md) and [CLI guide](../../04-software/solver/docs/CLI_API.md) for configuration.

[Media sources](../README.md) · [Benchmark figures](../benchmarks/README.md) · [Project architecture](../../README.md#architecture)
