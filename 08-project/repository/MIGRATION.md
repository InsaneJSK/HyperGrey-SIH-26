# Repository migration

Date: 2026-09-27. Source: `sih-backup-solver`, commit `72925040b5063c7785dabaece96cf62d9b4b35e3`.
Destination: **HyperGrey-SIH-26**, software PS 26119.
Organizational reference: **Hyper-Grey-SIH-26**, hardware PS 26058.

## Scope

Imported all **15,974 Git-tracked files** outside research, totaling
**467,128,349 original bytes**. Both source repositories
were read only. No source Git metadata, virtual environment, editor session,
untracked compiler, untracked downloads or untracked run records were copied.
The research folder was not read or imported. Existing tracked reference
packages, fixtures and historical binaries are retained, including files that
the source's newer ignore rules happened to match.

## Path map

| Source path | Destination path |
|---|---|
| `SIH-backup-solver/` | `04-software/solver/` |
| `backend/` | `04-software/backend/` |
| `kaggle_delivery/` | `04-software/kaggle_delivery/` |
| `papers/technical/` | `07-documentation/technical-report/` |
| `papers/cost/` | `09-business/market/` |
| `papers/README.md` | `07-documentation/PAPERS.md` |
| `objective.md` | `10-project/timeline/objective.md` |
| `WEBSITE_PLAN.md` | `04-software/website/WEBSITE_PLAN.md` |
| `.vscode/settings.json` | Same path, now workspace-relative |

At import, the numbered section order and `_CONTENTS.md` convention followed the
hardware repository. Hardware/firmware sections were omitted and research was
deferred to the subsequent separate curation.

## Why the solver remains self-contained

The CMake tests, 144 existing scripts, notebook packaging and historical hashes
depend on `src/`, `include/`, `tests/`, `scripts/`, `datasets/`, `docs/` and
`reports/` sharing a project root. Keeping that unit intact preserves behavior
without introducing symlinks, duplicate datasets or path changes to executable
code. The model, validation and documentation sections link to these canonical locations.
The sibling name `kaggle_delivery` is retained because existing scripts resolve
it via the solver's parent directory.

During that import, no solver, API, worker, test, notebook, dependency pin,
Dockerfile, Compose file, deployment script, frozen source, binary, report or
paper content was changed.
Historical command lines and absolute paths in evidence remain historical;
their old project root now maps to `02-software/solver/` for navigation.

## Adjusted imported files

At the import baseline, exactly **9** imported files changed, all for navigation or repository
configuration:

- `.gitattributes`
- `.gitignore`
- `.vscode/settings.json`
- `04-software/solver/.gitignore`
- `04-software/website/WEBSITE_PLAN.md`
- `04-software/backend/DEPLOY.md`
- `04-software/backend/README.md`
- `10-project/timeline/objective.md`
- `07-documentation/PAPERS.md`

The solver ignore file adds exceptions for previously tracked files so importing
into an empty Git repository does not silently drop them. The attributes file
protects imported source and evidence from line-ending conversion. Papers and
their compiled PDFs retain their original bytes; path interpretation is recorded
in PAPERS.md instead of modifying them.

## Verification

`migration-manifest.csv` records each old/new path and both SHA-256 values.
Run `python3 08-project/repository/verify_migration.py` to check the imported
files locally. Supply `--source PATH` to also compare the original source tree
and ensure every originally tracked non-research path is accounted for.

The verifier deliberately excludes newly authored navigation and validation
documents from the source hash manifest. Its hashes describe this migration
baseline. Later intentional edits are registered with exact current hashes in
the separate post-import ledger described below.


## Current repository organization

The [repository guide](README.md) records the current continuous **00–08** section
order. The original import table above and CSV retain their historical names;
[layout-renames.json](layout-renames.json) resolves each original top-level
section to its current directory exactly once.

Media is grouped by type, folder guides use GitHub-rendered `README.md` files,
and the separately curated research library is in
[01-research](../../01-research/README.md). Solver, backend and Kaggle components
now share `02-software/`; their internal source, dataset, package and frozen-report
relationships are preserved.

The original CSV remains unchanged. Intentional subsequent edits to imported
files are recorded in [post-import-changes.json](post-import-changes.json), each
with the exact import-baseline hash, current hash, date and reason. Manifest and
ledger destination identifiers stay in the original import namespace. The
verifier resolves the current location using the section map, then requires the
recorded content hash; it rejects unlisted changes and path collisions. Its
optional `--source` audit compares the untouched original source independently
of the later moves and edits.
