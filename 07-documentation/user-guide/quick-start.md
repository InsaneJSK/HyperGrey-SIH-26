# Quick start

All paths below start at the **HyperGrey-SIH-26** software repository root.

## Solver

Use CMake 3.16 or newer and a C++11 compiler. Follow the unchanged
[solver instructions](../../04-software/solver/README.md) from `04-software/solver/`.

```sh
cd 04-software/solver
cmake -S . -B build-v2 -DCMAKE_BUILD_TYPE=Release
cmake --build build-v2 --config Release
ctest --test-dir build-v2 -C Release --output-on-failure
```

On Windows the existing `scripts/build.ps1` selects MinGW and copies the built
CLI to `build/solver_cli.exe`. Make CMake and your chosen compiler available on
PATH first. Imported `build/` binaries are historical source artifacts; rebuild
before using a binary as the current version. CUDA is optional and unchanged.

## Backend

With Python 3.12, from the repository root:

```sh
python -m pip install -r 04-software/backend/requirements.txt
python -m uvicorn app:app --app-dir 04-software/backend --host 127.0.0.1 --port 8000 --workers 1
```

In another terminal:

```sh
python 04-software/backend/smoke_test.py http://localhost:8000
```

HiGHS remains the default engine. To select the existing Sovereign adapter, set
`SOLVER_ENGINE=sovereign` and `SOVEREIGN_BINARY` to an absolute path to your newly
built solver executable. No default solver settings were changed in this move.

For a container, keep the backend as the build context:

```sh
docker build -t refinery-api ./04-software/backend
```

See [DEPLOY.md](../../04-software/backend/DEPLOY.md) for the existing deployment
procedure. This migration does not deploy anything.

## Data, notebooks and evidence

The solver's `datasets/`, `reports/`, `scripts/`, `tests/` and `docs/` stay in
their original relative positions. `04-software/kaggle_delivery/` stays beside
the solver for notebook/package compatibility. Git-untracked local model
downloads, run output, virtual environments and compiler installations were
not imported; use the existing dataset manifests and setup instructions when
reproducing experiments that need them.
