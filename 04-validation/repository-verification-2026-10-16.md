# Repository and API verification

Verified on macOS on **16 October 2026** after the navigation/media reorganization, continuous section numbering and focused backend corrections.

| Check | Result |
|---|---|
| Backend regression suite | **41/41 passed**, including six sovereign-adapter contract checks |
| Sovereign MILP smoke | Production lotsizing returned **optimal**, objective **762**, using the retained iteration-37 recommended algorithm profile |
| Explicit LP relaxation | The same model with `integer=false` returned **optimal**, objective **742** |
| Rejected input | Malformed MPS returned **input_rejected** |
| Section layout | Continuous **00–08** numbering; solver, backend and Kaggle sibling relationships preserved |
| Navigation | **761** local links and **16** Markdown anchors resolved; all three SVGs parsed successfully |
| Import integrity | All **15,974** imported files matched the immutable baseline or one of **ten** exact documented post-import changes |
| Frozen source package | **71** build inputs matched the retained iteration-36 source identity |
| Archived evidence | **16,223** files verified, **zero** problems |
| Benchmark charts | Regenerated from **45** CPU/GPU run records and the complete **240-instance** historical MIPLIB outcome summary |
| Moved media | All **11** assets preserved; the chart guide's reproduction command points to its new folder |
| Ledger and section-map checks | **15** section-map fixtures passed, including one-time mapping, path collisions and unrecorded edits; the earlier **10** ledger fixtures also passed |
| Current-path build | Fresh CMake Release CLI build succeeded; LP, MILP and QP examples returned their expected optimal objectives |
| Research library | **60** sources, **15** topics and **43** local PDFs verified offline; all **78** generated files reproduced |

The backend suite emitted one upstream Starlette/httpx deprecation warning. No C++ numerical algorithm or frozen experiment input was changed. The [Mac build record](readme-verification-2026-10-16.md) records the existing core build, numerical smoke results and platform-specific CTest results.

## Reproduce the checks

With the backend development dependencies installed, from the repository root:

```sh
python -m pytest 02-software/backend/tests -q
python3 08-project/repository/verify_migration.py
python3 06-media/benchmarks/build_benchmark_charts.py
```

From `02-software/solver/`:

```sh
python3 scripts/package_kaggle_source.py --check
python3 scripts/archive_run_records.py --verify
```

[Current structure and integrity ledger](../08-project/repository/README.md) · [Adapter contract tests](../02-software/backend/tests/test_sovereign_adapter.py)
