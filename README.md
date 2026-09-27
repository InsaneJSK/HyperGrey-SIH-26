# Hyper Grey — SIH 2026 software

**PS 26119: Indigenous GPU-Accelerated Optimization Solver**  
**Mangalore Refinery and Petrochemicals Limited (MRPL)**

This is **`HyperGrey-SIH-26`**, the software repository. The separate
**`Hyper-Grey-SIH-26`** repository is the hardware project (PS 26058).
Software and retained evidence were imported from `sih-backup-solver`.

## Repository layout

The numbered sections and `_CONTENTS.md` guides follow the hardware repository.
Its hardware and firmware sections do not apply here. The `03-research` library
was curated separately for the software problem statement.

| Section | Contents |
|---|---|
| [00-submission](00-submission/README.md) | Problem statement, requirements and demo navigation; submission slots |
| [03-research](03-research/README.md) | 15 software research topics, 43 PDFs, 60 annotated sources and a priority reading map |
| [04-software](04-software/README.md) | C++/CUDA solver, FastAPI backend, existing Kaggle packages, website plan |
| [05-models](05-models/README.md) | Dataset, example-model and notebook navigation |
| [06-validation](06-validation/README.md) | Test commands and retained benchmark/evidence navigation |
| [07-documentation](07-documentation/README.md) | Technical paper, API, methods, user guide and migration notes |
| [08-media](08-media/README.md) | Slots for project video, screenshots and diagrams |
| [09-business](09-business/README.md) | Existing cost/market paper, roadmap and third-party notices |
| [10-project](10-project/README.md) | Objectives, timeline, team/risk slots and import verification |

Read a folder's `_CONTENTS.md` before adding a deliverable. Empty submission or
media slots are explicitly marked pending; no new claims or assets were invented.

## Build and run

The solver is a self-contained project at `04-software/solver/`. Its source,
scripts, datasets, test fixtures, reports and frozen binaries retain their
internal paths and bytes. Run its existing instructions from that directory.

```sh
cd 04-software/solver
cmake -S . -B build-v2 -DCMAKE_BUILD_TYPE=Release
cmake --build build-v2 --config Release
ctest --test-dir build-v2 -C Release --output-on-failure
```

The CTest suite needs `datasets/miplib2017/blend2.mps`; the imported repository
tracks that fixture. Optional CUDA remains off by default.

For the API, start from the repository root with Python 3.12:

```sh
python -m pip install -r 04-software/backend/requirements.txt
python -m uvicorn app:app --app-dir 04-software/backend --host 127.0.0.1 --port 8000 --workers 1
```

The backend still defaults to **HiGHS** (`SOLVER_ENGINE=reference`); its optional
Sovereign engine mode, flags and environment settings are unchanged. The C++
solver remains independently implemented. See the [backend guide](04-software/backend/README.md)
and [quick start](07-documentation/user-guide/quick-start.md).

## Verify the import

```sh
python 10-project/repository/verify_migration.py
```

Every imported file is listed with its old path, new path and SHA-256 in the
[migration manifest](10-project/repository/migration-manifest.csv).
See [migration scope and path map](10-project/repository/MIGRATION.md) and the
[validation record](06-validation/restructure-checks.md) for what was checked.
