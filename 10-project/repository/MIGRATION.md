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

The numbered section order and `_CONTENTS.md` convention follow the hardware
repo. Hardware/firmware sections are omitted and research is deferred.

## Why the solver remains self-contained

The CMake tests, 144 existing scripts, notebook packaging and historical hashes
depend on `src/`, `include/`, `tests/`, `scripts/`, `datasets/`, `docs/` and
`reports/` sharing a project root. Keeping that unit intact preserves behavior
without introducing symlinks, duplicate datasets or path changes to executable
code. Sections 05, 06 and parts of 07 link to these canonical locations.
The sibling name `kaggle_delivery` is retained because existing scripts resolve
it via the solver's parent directory.

No solver, API, worker, test, notebook, dependency pin, Dockerfile, Compose file,
deployment script, frozen source, binary, report or paper content was changed.
Historical command lines and absolute paths in evidence remain historical;
their old project root maps to `04-software/solver/` for navigation.

## Adjusted imported files

Exactly **9** imported files changed, all for navigation or repository
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
Run `python 10-project/repository/verify_migration.py` to check the imported
files locally. Supply `--source PATH` to also compare the original source tree
and ensure every originally tracked non-research path is accounted for.

The verifier deliberately excludes newly authored navigation and validation
documents from the source hash manifest. Its hashes describe this migration
baseline, so later intentional source changes require interpreting differences
as changes since the import, not automatically as corruption.
