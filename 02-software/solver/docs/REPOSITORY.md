# What is in this repository, and how to ship it

## The rule

Commit what cannot be regenerated, and commit the ledger that identifies what
is left out. Every rule in `.gitignore` follows from that, and every rule is a
pattern rather than a list, so starting an iteration never requires editing it.

The previous version of that file listed one exception per iteration, and the
list stopped at 35 — which is how **iterations 36 and 37 came to have their
frozen binaries silently ignored by git**. Patterns do not fail that way.

## What is tracked

| | Why |
|---|---|
| `src/`, `include/`, `tests/`, `CMakeLists.txt` | the engine |
| `docs/`, `scripts/` | the method and the measurement harness |
| `reports/**/*.md`, `PLAN.md`, `REPORT.md`, `FINAL_STATE.json` | the declared plan and the result |
| `reports/**/results.json`, `SUMMARY.json`, `SOURCE_IDENTITY.json` | the ledger: every record's SHA-256, the model's, the binary's, the exact command |
| `reports/**/final_solver_cli.exe` and its runtime DLLs | the frozen binary is the evidence; its SHA-256 is in `FINAL_STATE.json` |
| `reports/**/final-source/` | the source that built that binary |
| `reports/**/checks.zip`, `streams.zip`, `ARCHIVE.json` | validator outputs and captured streams (below) |
| `datasets/*-holdout/*.mps`, `*-fresh/*.mps`, `*-guard*/*.mps` | the exact bytes a declared holdout was measured on |

About 6,900 files and 146 MiB.

## What is not tracked, and what stands in for it

**Paired-run records.** A solve writes `<model>.<profile>[.<repeat>].json` — the
captured monitor record, up to 31 MiB of solution vector and traces — plus
`.ours.json` and `.reference.json`. Across iterations 30–37 that is about
3 GiB, with single files above GitHub's 50 MiB warning threshold. They stay on
the machine that produced them. `results.json` in the same folder records each
one's SHA-256, its model's SHA-256, the binary's SHA-256 and the command that
produced it, and `SUMMARY.json` records `results.json`'s own SHA-256. A
two-dot filename is a run record; ledgers, plans and manifests have one dot.

**Downloaded models.** Public MIPLIB, Netlib and QPLIB instances are
downloaded, not authored — `datasets/miplib2017-parta/` alone is 728 MiB. Each
dataset folder keeps `manifest.json` with the source URL and SHA-256 of every
file (`datasets/README.md`).

**Build trees, local toolchains, reference builds.** `tools/reference/` holds
the independent HiGHS 1.12.0 and OSQP readers used for checking; it is
reinstalled from `tools/reference-requirements.txt`.

## The per-record archives

A paired run also writes eight or more accounting-check files and the captured
stdout/stderr per solve. Those are evidence — `scripts/audit_*.py` re-derive
them from `.ours.json` and assert equality — but as loose files they were
16,223 of them.

`scripts/archive_run_records.py` packs them per folder into `checks.zip` and
`streams.zip`. Every member is read back and compared byte for byte before the
original is removed, and `ARCHIVE.json` records each member's size and SHA-256,
so an archive can be checked without unpacking it.

```
python scripts/archive_run_records.py --verify
python scripts/archive_run_records.py --restore reports/milp-iteration-34/development-30s
python scripts/archive_run_records.py --apply          # pack a newly finished run
```

An audit script needs the loose files, so restore the folder first.

## Packaging for Kaggle

What goes to Kaggle is the source that produced a frozen binary, never whatever
is in the working tree. `scripts/package_kaggle_source.py` copies exactly the
files listed in an iteration's `SOURCE_IDENTITY.json` out of its
`final-source/`, checks every SHA-256 on the way, and refuses to write a bundle
if one disagrees.

```
python scripts/package_kaggle_source.py --check        # verify, write nothing
python scripts/package_kaggle_source.py                # newest frozen iteration
python scripts/package_kaggle_source.py --iteration 36
```

It writes `build-kaggle/it<N>/` (ignored by git) containing the 71 build inputs
— `src/`, `include/`, `tests/`, `CMakeLists.txt` — plus `dataset-metadata.json`
and a `MANIFEST.json` naming the binary those files built. The 142 harness
scripts are left out: a Kaggle build never compiles them, and the notebook
carries its own runner.

```
kaggle datasets create  -p build-kaggle/it36 --dir-mode zip
kaggle datasets version -p build-kaggle/it36 --dir-mode zip -m "iteration 36"
```

The API token lives in `~/.kaggle/`, outside this tree. `kaggle.json` and
`*.token` are ignored at the repository root so it cannot be committed by
accident.

`scripts/package_kaggle.py` is a different, older thing: the self-contained V1/V2
notebook packager, kept for the deliverables under `kaggle_delivery/`.

## Line endings

`.gitattributes` marks `*.mps`, `*.qplib`, `*.lp` and everything under
`reports/` and `datasets/` as `-text`. Evidence is compared by SHA-256 against
a value recorded when it was produced, so any line-ending conversion would
break the check.
