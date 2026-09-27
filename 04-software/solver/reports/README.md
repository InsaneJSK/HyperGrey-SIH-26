# Reports

## What is current

- `miplib2017-benchmark/` — all 240 MIPLIB 2017 benchmark instances, the full
  table with failures.
- `milp-iteration-30/` to `milp-iteration-35/` — the complete evidence behind
  the current recommended profile: plans, frozen binaries, source snapshots,
  every run record.
- `kaggle-gpu-03/` — the repeated GPU box-QP validation.
- `kaggle-miplib2017-02/` to `-05/` — the individual benchmark sessions.
- `root-lp-diagnosis/` — the diagnosis behind iteration 34.
- `demo-2026-09-18/` — the command-line demonstration output.
- `cpu-validation-2026-09-17/`, `lp-bandm-01/` — the LP and QP validation.

## Older evidence was thinned on 19 September 2026

For iterations 1–29 and the early `phase*`, `v1-*`, `v2-*`, `qp-iteration-01`,
`kaggle-gpu-01/02`, `kaggle-milp-01/02` and `kaggle-package-*` folders, only the
notes were kept: every top-level `.md` and `.json` (reports, plans, ledgers,
comparisons, final states). The bulk — run outputs, frozen binaries, source
snapshots, logs, 83,591 files and 2.6 GiB — was removed from the working tree.

**Nothing was lost.** All of it is in git at commit
`2ca98ea20431e8ebe6c7f3a04fc2c030c31977e1`. To bring any folder back:

```
git checkout 2ca98ea20431e8ebe6c7f3a04fc2c030c31977e1 -- reports/milp-iteration-14
```

Some older documents link into those removed subfolders (for example
`reports/phase1/run01`); the command above restores them.

Two pieces of the old evidence were kept in full because the current toolchain
loads them:

- `milp-iteration-12/generated-lattice/` — 400 retained test models checked by
  `scripts/sparse_accuracy_gate.py` on every iteration.
- `milp-iteration-16/final_solver_cli.exe` and its runtime DLLs — the gate's
  SHA-checked baseline for "disabling a feature reproduces the old arithmetic
  exactly".

## Second cleanup, 21 September 2026

Regenerable bulk was removed from the current iteration folders as well —
**33,179 files, 1.92 GiB** — with every result and every note kept:

| Removed | Files | Why it is safe |
|---|---:|---|
| `gate/` working files in iterations 30–36 | 21,606 | The correctness gate reruns in minutes; each `gate/SUMMARY.json` is kept and records the pass |
| Downloaded `.mps` models | 152 | Public MIPLIB instances; every `manifest.json` with its URLs and SHA-256 is kept (see `datasets/README.md`) |
| Empty `.log` files | 4,308 | No content |
| Bytecode caches | 3,381 | Regenerated on import |
| A vendored virtualenv under `kaggle-simple-linux` | 3,732 | An old smoke test's Python environment |

Untouched: every run record, report, plan, frozen binary, source snapshot and
manifest, and the models in use by the iteration 37 ablation that was running at
the time.

## Third pass, 23 September 2026 — folded, not deleted

Nothing was removed this time. The per-solve accounting checks and captured
streams — **16,223 files, 509 MiB** — were packed into one `checks.zip` and one
`streams.zip` per run folder by `scripts/archive_run_records.py`, which reads
every member back and compares it byte for byte before removing the original,
and writes an `ARCHIVE.json` recording each member's size and SHA-256.

They are evidence: `scripts/audit_*.py` re-derive each check from the
`.ours.json` beside it and assert equality. That still works — restore the
folder first:

```
python scripts/archive_run_records.py --restore reports/milp-iteration-34/development-30s
python scripts/archive_run_records.py --verify
```

Also removed, both regenerable: the `build-milp-iter33/` CMake tree (532 files;
no frozen state records anything from it) and three bytecode caches.

The working tree went from 32,847 files to 16,166. `docs/REPOSITORY.md` says
what is tracked, what is not, and what stands in for what is not.
