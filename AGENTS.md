# Repository identity and scope

- `HyperGrey-SIH-26` (this repository, no hyphen after Hyper) is the **software** PS 26119 repository.
- `Hyper-Grey-SIH-26` is the separate **hardware** PS 26058 repository. It supplies the organizational pattern only.
- The imported software comes from `sih-backup-solver`; do not edit either source repository when working here.
- Research was excluded from the initial migration and curated separately in `03-research/`; its README and RESEARCH_MAP.md describe the software-specific collection.
- Application code lives in `04-software/solver/` and `04-software/backend/`.
- The solver's internal paths and sibling `04-software/kaggle_delivery/` are intentional: packaging, validation and historical hashes depend on them.
- Read `10-project/repository/MIGRATION.md` before moving retained evidence or changing this layout.
