# SolveForge software

| Project | Contents |
|---|---|
| [solver](solver/README.md) | Independent C++/CUDA LP, MILP and convex-QP engine, numerical methods, CLI, tests and benchmark evidence |
| [backend](backend/README.md) | FastAPI model-solving and refinery service, isolated workers, tests, Docker and EC2 deployment configuration |
| [kaggle_delivery](kaggle_delivery/README.md) | Reproducible notebooks, matching source ZIPs and package checks |
| [website](website/README.md) | Public web demonstration, integration guide and retained product plan |
| [releases](releases/README.md) | Android download links, notebook packages and versioned solver artifacts |

Start with the [repository quick start](../05-documentation/user-guide/quick-start.md). The solver keeps source, tests, scripts, datasets and reports together so its build and reproduction paths remain stable. `kaggle_delivery` stays beside it for notebook/package compatibility.

The backend guide runs commands from this `02-software/` directory. Its Docker build context is `backend/`.
