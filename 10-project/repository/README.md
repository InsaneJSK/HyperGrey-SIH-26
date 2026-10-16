# Repository structure and provenance

[Project overview](../../README.md) · [Project documentation](../README.md)

The numbered sections provide a review route through the submission, research, implementation, evidence and supporting material. Component guides render automatically as `README.md` on GitHub.

## Current layout

| Section | Canonical content |
|---|---|
| [Submission](../../00-submission/README.md) | Problem statement, requirements, project summary and demonstration routes |
| [Research](../../03-research/README.md) | Curated references, topic guides and generated source catalog |
| [Software](../../04-software/README.md) | Self-contained C++ solver, FastAPI backend and reproducible Kaggle packages |
| [Models](../../05-models/README.md) | Dataset, notebook and evaluation guides linked to canonical solver artifacts |
| [Validation](../../06-validation/README.md) | Benchmark results, execution environments, test commands and verification records |
| [Documentation](../../07-documentation/README.md) | Technical paper, numerical methods, API and user guides |
| [Media](../../08-media/README.md) | Diagrams, screenshots, sourced benchmark charts and demonstration links |
| [Business](../../09-business/README.md) | Cost/market paper and deployment economics |
| [Project](../README.md) | Objectives, project references and repository provenance |

## Folder naming

| Earlier navigation path | Current path |
|---|---|
| `05-models/dataset/` | [05-models/datasets/](../../05-models/datasets/README.md) |
| `05-models/notebook/` | [05-models/notebooks/](../../05-models/notebooks/README.md) |
| `06-validation/bench-results/` | [06-validation/benchmark-results/](../../06-validation/benchmark-results/README.md) |
| `06-validation/instruments/` | [06-validation/execution-environments/](../../06-validation/execution-environments/README.md) |
| `08-media/video/` | [08-media/videos/](../../08-media/videos/README.md) |

The former `08-media/readme/` assets are organized into `diagrams/`, `screenshots/` and `benchmarks/`; the media landing page holds their source table. Standalone `_CONTENTS.md` guides are promoted to `README.md`, and redundant component wrappers are removed. The generated [research catalog](../../03-research/_CONTENTS.md) keeps its established name because the research-library tool owns it.

The solver's internal `src/`, `include/`, `tests/`, `datasets/`, `scripts/`, `docs/` and `reports/` paths stay together under `04-software/solver/`. Its sibling `04-software/kaggle_delivery/` and the backend path also stay stable, preserving build, packaging and retained-evidence references.

## Import and subsequent changes

- [Migration record](MIGRATION.md): original import scope and source-to-destination path map.
- [Original SHA-256 manifest](migration-manifest.csv): immutable baseline for all 15,974 imported non-research files.
- [Post-import change ledger](post-import-changes.json): exact baseline/current hashes and reasons for intentional later edits to imported files.
- [Verifier](verify_migration.py): checks every imported file against the baseline or its explicit ledger entry; rejects unrecorded changes.

From the repository root:

```sh
python3 10-project/repository/verify_migration.py
```

Add `--source /path/to/sih-backup-solver` to independently compare the original checkout and its tracked-file coverage. Newly authored navigation, media and test files are reviewed through Git and their linked source/verification guides; they are outside the original import manifest.
