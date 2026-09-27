# Structure-only migration checks

Validation date: 2026-09-27. Source commit:
`72925040b5063c7785dabaece96cf62d9b4b35e3` in `sih-backup-solver`.

## Scope

This check concerns relocation and preservation, not a new solver benchmark or
submission-readiness assessment. Research was excluded. The hardware project
provided the numbered organizational pattern; none of its application code or
hardware deliverables was imported.

## Checks performed

| Check | Result |
|---|---|
| File inventory | All 15,974 Git-tracked non-research source files imported |
| Content preservation | 15,965 files unchanged; 9 navigation/configuration files adjusted |
| Source/destination hash verification | Passed for all 15,974 files, with complete original tracked-file coverage |
| Git ignore coverage | Every imported file remains addable in the destination repository |
| Navigation | 130 local links checked across 47 new or adjusted Markdown guides; zero broken links |
| C++ Release build | Passed, CMake 3.30.4, WinLibs GCC 14.2.0, OpenMP enabled, CUDA disabled |
| CTest | All 29 tests passed after supplying the compiler's runtime DLLs locally |
| Solver Python regression suite | 206 passed, plus 70 subtests passed |
| Backend regression suite | 35 passed; one existing Starlette/httpx deprecation warning |
| Frozen-source packaging check | Iteration 36: 71 build inputs verified against SOURCE_IDENTITY.json |
| Archived evidence | 16,223 archived files verified, zero problems |

The import manifest records both the original and destination SHA-256 for every
file. The [verification script](../10-project/repository/verify_migration.py)
checks destination hashes and, with `--source`, compares the original checkout's
hashes and complete tracked-file inventory. See the
[migration notes](../10-project/repository/MIGRATION.md) for the path map and
the nine adjusted files.

## Reproduction

From the repository root, with the original pinned backend dependencies installed:

```sh
python 10-project/repository/verify_migration.py --source /path/to/sih-backup-solver
python -m pytest 04-software/backend/tests -p no:cacheprovider -q
```

From `04-software/solver/`:

```sh
python -m pytest scripts --ignore=scripts/test_kaggle_notebook.py --ignore=scripts/test_milp_kaggle_notebook.py --ignore=scripts/test_lattice_reader_equivalence.py -p no:cacheprovider -q
python scripts/package_kaggle_source.py --check
python scripts/archive_run_records.py --verify
```

A fresh C++ Release build was created in the ignored local validation directory
`.migration-work/solver-build/`. No historical executable was overwritten.
Its CTest suite ran with the matching compiler runtime libraries copied beside
the executables: `libgcc_s_seh-1.dll`, `libstdc++-6.dll`,
`libwinpthread-1.dll`, `libgomp-1.dll`, and `libdl.dll`.
Initial Windows DLL-loading failures were resolved by that local test setup;
no build configuration or C++ source edits were needed. Twenty-six cases passed
after the first runtime correction, and the remaining three passed after adding
the OpenMP library's `libdl.dll` dependency.

## Existing limitations and exclusions

- The two notebook-flow test modules require `nbformat`, which was not available
  in the local test environment. Their notebooks, cells, companion ZIPs and
  package records were preserved and included in the hash manifest. No GPU or
  hosted Kaggle execution was attempted.
- `test_lattice_reader_equivalence.py` is a historical replay script, executed
  at import time. It expects
  `reports/milp-iteration-13/final-source/scripts/check_objective_lattice.py`,
  which is absent in the original source checkout as well. A broad first test
  collection exposed this existing missing input; the executable source was
  left unchanged and this script was excluded from the regression run.
- The newest available `SOURCE_IDENTITY.json` selected by the existing packaging
  check is iteration 36. The imported iteration 37 report remains historical;
  it was not relabeled or given fabricated source/binary identity records.
- Locally untracked model downloads, run output, virtual environments and
  toolchains were not imported. Historical ledgers may reference those original
  local assets. No historical run was rerun or its outcome changed.
- The API keeps its original HiGHS default and optional Sovereign adapter. No
  network deployment, CUDA run, or new performance comparison was performed.
