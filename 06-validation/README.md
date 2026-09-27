# Validation

Existing evidence is preserved at [solver/reports](../04-software/solver/reports/).
Frozen sources, binaries, manifests, archived streams and numerical records were
not rewritten. Historical absolute paths still describe their original runs.

- [C++ tests](../04-software/solver/tests/) and [Python harness](../04-software/solver/scripts/)
- [Backend tests](../04-software/backend/tests/test_api.py)
- [Full MIPLIB benchmark report](../04-software/solver/reports/miplib2017-benchmark/REPORT.md)
- [Iteration 37](../04-software/solver/reports/milp-iteration-37/REPORT.md)
- [GPU box-QP report](../04-software/solver/reports/kaggle-gpu-03/REPORT.md)
- [Restructure verification](restructure-checks.md)

From the repository root:

```sh
python -m pip install -r 04-software/backend/requirements-dev.txt
python -m pytest 04-software/backend/tests -q
python 10-project/repository/verify_migration.py
```

From `04-software/solver/` after building:

```sh
ctest --test-dir build-v2 -C Release --output-on-failure
python scripts/package_kaggle_source.py --check
python scripts/archive_run_records.py --verify
```

The package and archive checks verify frozen evidence; they do not run new
benchmarks or establish current solver performance.
