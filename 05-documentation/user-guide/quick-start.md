# Build and run SolveForge

Run the following commands from the **HyperGrey-SIH-26 repository root**. Use CMake 3.16 or newer and a C++11 compiler for the core; use Python 3.12 for the API.

## Build the independent core

```sh
cmake -S 02-software/solver -B 02-software/solver/build-local -DCMAKE_BUILD_TYPE=Release
cmake --build 02-software/solver/build-local --config Release --parallel 4
ctest --test-dir 02-software/solver/build-local -C Release --output-on-failure
```

Run the included LP, MILP and convex-QP examples:

```sh
./02-software/solver/build-local/solver_cli 02-software/solver/examples/industrial/marco_refinery.mps --lp-method bounded --json
./02-software/solver/build-local/solver_cli 02-software/solver/examples/industrial/production_lotsizing.mps --milp --bounded-lp --json
./02-software/solver/build-local/solver_cli 02-software/solver/examples/dispatch.qplib --json
```

On Windows, use the executable location produced by your CMake generator. Optional CUDA builds use `-DSOVEREIGN_ENABLE_CUDA=ON` on a supported NVIDIA host. The [solver guide](../../02-software/solver/README.md) explains build profiles and CLI options; the [Mac verification record](../../04-validation/readme-verification-2026-10-16.md) records an actual local build and test run.

## Run the API

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r 02-software/backend/requirements.txt
python -m uvicorn app:app --app-dir 02-software/backend --host 127.0.0.1 --port 8000 --workers 1
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell. Open [the local API documentation](http://127.0.0.1:8000/docs).

The default `reference` mode uses HiGHS. To select the built project engine:

```sh
SOLVER_ENGINE=sovereign SOVEREIGN_BINARY="$PWD/02-software/solver/build-local/solver_cli" \
  python -m uvicorn app:app --app-dir 02-software/backend --host 127.0.0.1 --port 8000 --workers 1
```

In another terminal, exercise the running API:

```sh
python 02-software/backend/smoke_test.py http://localhost:8000
```

The [backend guide](../../02-software/backend/README.md) documents engine selection, request fields and resource limits. Keep `backend/` as the Docker build context:

```sh
docker build -t refinery-api ./02-software/backend
```

See the [deployment guide](../../02-software/backend/DEPLOY.md) for container/EC2 configuration.

## Models, notebooks and evidence

- [Datasets and manifests](../../03-models/datasets/README.md).
- [Notebook packages](../../03-models/notebooks/README.md).
- [Benchmark results](../../04-validation/benchmark-results/README.md).
- [Tests and reproduction](../../04-validation/test-plan/README.md).

The solver's source, datasets, scripts, tests and reports remain together. `02-software/kaggle_delivery/` stays beside it for package compatibility. Use fresh output directories for new runs and the matching snapshot for a historical reproduction.
