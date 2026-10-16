# Validation and reproducibility

SolveForge retains regression tests, independent solution checks, numerical experiments and versioned benchmark campaigns.

| Review route | Open |
|---|---|
| Benchmark outcomes | [Reports, raw records and comparison entry points](benchmark-results/README.md) |
| Build and test | [Test and reproduction guide](test-plan/README.md) |
| Hosts and compute settings | [Execution environments](execution-environments/README.md) |
| Repository and API review | [Current adapter, navigation and integrity checks](repository-verification-2026-10-16.md) |
| Fresh local verification | [Mac build, examples and platform results](readme-verification-2026-10-16.md) |
| Repository verification | [Import/restructure checks](restructure-checks.md) |

From the repository root, after building the solver as described in the [quick start](../07-documentation/user-guide/quick-start.md):

```sh
ctest --test-dir 04-software/solver/build-local -C Release --output-on-failure
python -m pip install -r 04-software/backend/requirements-dev.txt
python -m pytest 04-software/backend/tests -q
python 10-project/repository/verify_migration.py
```

From `04-software/solver/`, the archive checks verify retained package and run-record identities:

```sh
python scripts/package_kaggle_source.py --check
python scripts/archive_run_records.py --verify
```

Frozen source, binaries and numerical records stay together in the [report archive](../04-software/solver/reports/README.md). Package/hash verification and new solver measurements serve different purposes; each report records its own run configuration.
