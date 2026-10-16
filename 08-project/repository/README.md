# Repository structure and provenance

[Project overview](../../README.md) · [Project documentation](../README.md)

The top-level sections run continuously from **00 to 08**, following the project review order. Component guides render automatically as `README.md` on GitHub.

## Current layout

| Section | Contents |
|---|---|
| [00-submission](../../00-submission/README.md) | Problem statement, requirements, project summary and demonstrations |
| [01-research](../../01-research/README.md) | Curated references, topic guides and generated source catalog |
| [02-software](../../02-software/README.md) | Self-contained C++ solver, FastAPI backend and Kaggle packages |
| [03-models](../../03-models/README.md) | Dataset, notebook and evaluation guides |
| [04-validation](../../04-validation/README.md) | Benchmark results, test commands, environments and verification records |
| [05-documentation](../../05-documentation/README.md) | Technical paper, numerical methods, API and user guides |
| [06-media](../../06-media/README.md) | Diagrams, screenshots, sourced charts and demonstration links |
| [07-business](../../07-business/README.md) | Cost/market paper and deployment economics |
| [08-project](../README.md) | Objectives, development records and repository provenance |

Media is grouped into `diagrams/`, `screenshots/`, `benchmarks/` and `videos/`. Model and validation guides use descriptive plural names. The generated [research catalog](../../01-research/_CONTENTS.md) keeps its established filename because the research-library tool owns it.

## Component paths

The solver's internal `src/`, `include/`, `tests/`, `datasets/`, `scripts/`, `docs/` and `reports/` paths stay together under `02-software/solver/`. Its `02-software/kaggle_delivery/` and `02-software/backend/` siblings preserve build, packaging and retained-evidence relationships.

## Import integrity

- [Migration record](MIGRATION.md): original import scope and source-to-destination path map.
- [Original SHA-256 manifest](migration-manifest.csv): immutable baseline for all 15,974 imported non-research files.
- [Section rename map](layout-renames.json): resolves original manifest section names to the current continuous numbering.
- [Post-import change ledger](post-import-changes.json): exact baseline/current hashes and reasons for intentional content changes.
- [Verifier](verify_migration.py): checks every imported file at its current path against the baseline or its explicit ledger entry.

The manifest and ledger retain their original destination identifiers. A section move changes their resolved filesystem location; it does not change a recorded content hash. Frozen source, binaries, reports, datasets and research PDFs retain their bytes.

From the repository root:

```sh
python3 08-project/repository/verify_migration.py
```

Add `--source /path/to/sih-backup-solver` to independently compare the original checkout and tracked-file coverage. Newly authored navigation, media and test files are reviewed through Git and their linked source/verification guides; they are outside the original import manifest.
