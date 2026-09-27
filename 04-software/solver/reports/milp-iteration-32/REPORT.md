# Iteration 32 — tableau Gomory mixed-integer cuts

18 September 2026. Plan and holdout selection were declared before any timed
run (`PLAN.md`, `HOLDOUT_SELECTION.md`). Binary SHA-256
`6e073229a08065b6d2fccd7669fb75f99dd89090be39c3ccbcf1d43ca90351a4`, 213 frozen
source files (`SOURCE_IDENTITY.json`). Executable defaults unchanged.

## What was added

`--gomory-cuts`: a root separator that reads Gomory mixed-integer cuts off the
tableau of the bounded dual simplex. Requires `--bounded-lp`; rejected together
with `--no-cuts`. Mechanism and validity argument in `docs/GOMORY_CUTS.md`.

## Correctness first

A wrong cut removes the optimum and returns a confident wrong answer, so
validity was gated before any benchmark ran.

- `gomory_cut_validity` (CTest): **3,000 random all-integer models with every
  integer point enumerated** — 2,706 cuts checked against 64,430 feasible
  points, zero violations. The strengthened relaxation was re-solved on 1,491
  of them and never passed the enumerated integer optimum.
- **400 mixed models**: each cut was *maximized* over the continuous variables
  with the integers fixed, one LP per assignment — an exact test over the whole
  mixed region. 1,059 feasible completions checked, zero violations.
- CTest 28/28. `sparse_accuracy_gate.py --gomory-cuts`: `all_pass`, 14 generated
  profiles at 40/40, 400 reused lattice models.
- Every benchmark record independently checked against HiGHS 1.12.0 reading the
  original file: **zero validation failures in 128 records.**

## Development set: 27 models, two repeats, 108 records

| | Control | Candidate |
|---|---:|---:|
| Completions | 22 | 22 |
| Checked points | 50 | 50 |
| Validation failures | 0 | 0 |
| Peak commit MiB | 1138.7 | **762.8** |
| Separator seconds, all 54 records | — | 0.114 |
| Cuts applied / later purged | — | 1102 / 796 |

**A correction against our own summary.** The category counts show the
candidate at 23 completions, and that is not a solver gain. All four
`neos859080` records return `infeasible` from this engine in both profiles; the
category differs only because the five-second HiGHS reference finished on one
run and timed out on the other three. The honest count is 22 against 22.

### The root bound, which is what the mechanism targets

Candidate better on **26** paired observations, worse on **2**, unchanged on 22.

| Model | Root bound, control → candidate | Share of root gap closed | Cuts retained |
|---|---|---:|---:|
| `egout` | 367.08 → 528.55 | **80.3%** | 21 |
| `gt2` | 13461 → 18344 | **63.4%** | 8 |
| `p0201` | 7125 → 7265 | 33.8% → **52.7%** | 5 |
| `rgn` | 48.80 → 52.76 | 11.9% | 8 |
| `misc03` | 1910 → 1995 | 5.9% | 3 |
| `lotsize` | 348385 → 407728 | 5.2% | 42 |
| `p0282` | 226637 → **213581** | **regression** | 11 |

Also improved: `binkar10_1`, `blend2`, `flugpl`, `gen-ip002`, `gen-ip054`,
`lseu`, `rout`.

`gt2.control.0` stopped on the **open-node memory guard** at 1139 MiB — the only
memory-guard stop in the set. No candidate run hit it; the smaller tree stayed
under the threshold.

### End to end at 30 seconds it is a wash

Relative gap better on **15** records, worse on **13**, unchanged on 22.
Checked incumbents better on 9 observations, worse on 11. A tighter root did
not convert into completions at this budget, and this report does not claim it
did.

### The `p0282` regression, diagnosed

The candidate applied 80 tableau cuts and the cover separator then produced
**27 cuts where the control produced 35**. Tableau rows change the LP point, and
the cover separator is point-driven, so strong covers were crowded out. Net root
bound 213581 against the control's 226637, and the final gap degrades from
0.0475 to 0.126 and 0.174 across the two repeats.

The ordering that caused this — tableau cuts separated first in every round —
was declared in advance and is not being re-tuned now. Re-ordering and
re-measuring on the set that exposed the problem would be fitting to it. It is
iteration 33's first candidate, to be validated on a set that has not been used.

## Fresh holdout: 10 untouched MIPLIB 3 models

Declared before download in `HOLDOUT_SELECTION.md`, and deliberately the hard
end of MIPLIB 3.

| | Control | Candidate |
|---|---:|---:|
| Completions | 1 (`gen`) | 1 (`gen`) |
| Checked points | 6 | 6 |
| No incumbent at all | 4 | 4 |
| Validation failures | 0 | 0 |
| Peak commit MiB | 441.9 | **326.0** |
| Root bound | — | **better on 4, worse on 0**, same on 5 |

Root bound improvements: `swath` 334.50 → 373.37, `mkc` -611.36 → -603.86,
`seymour` 404 → 406, `gen` 112312.6 → 112313.4 (the published optimum is
112313.36, so the strengthened root is essentially integral there).

Incumbents split evenly as on development: better on `markshare1` (44 → 32) and
`swath` (685.60 → 633.90), worse on `markshare2` (61 → 85) and `mkc`
(-478.83 → -431.27), unchanged on `air04` and `gen`.

`arki001`, `dano3mip`, `rentacar` and `seymour` return no point in either
profile. Both profiles fail them equally; the cuts neither helped nor hurt.

## Decision

Against the rule declared in `PLAN.md`:

| Declared criterion | Result |
|---|---|
| Zero validation failures in either set | ✅ 0 and 0 |
| No objective disagreeing with a proven HiGHS optimum | ✅ none |
| Development completions do not fall | ✅ 22 → 22 |
| Development checked-point coverage does not fall | ✅ 50 → 50 |
| Root bound improves on more models than it worsens | ✅ 26–2 and 4–0 |
| Holdout: no new failure, crash, guard stop or rejected point | ✅ none, and one fewer guard stop |

**Promoted into the recommended profile.** The rule was written before the runs
precisely because a single 30-second budget over 27 models cannot resolve
completion differences, and the data confirms that (gap better on 15, worse on
13). What the evidence does establish is that the separator is cheap (0.1–0.2 s
per set), safe (zero failures across 128 checked records, zero holdout
regressions), reduces memory materially, and tightens the root bound almost
everywhere it acts.

Executable defaults remain unchanged. `--gomory-cuts` stays opt-in and requires
`--bounded-lp`.

## What this does not show

- **No end-to-end speed or completion gain is demonstrated at 30 seconds.** The
  bound improvement is the demonstrated result.
- The cuts are derived in floating point and are not certified in the
  directed-rounding sense (`docs/LIMITATIONS.md` L-11). Enumeration, the
  unit-violation rebuild, incumbent rejection and the independent reference are
  what stand behind the answers.
- Root only. Nothing is separated in the tree.
- One host, two repeats. Node counts on this machine vary about 40 percent
  between identical runs, so single-repeat differences are not evidence.

## Iteration 33 candidates, in order

1. **Separate cover cuts before tableau cuts**, or only fall back to tableau
   cuts when covers add nothing. `p0282` says the current order costs more than
   it gains where covers are strong. Validate on an unused set.
2. Presolve strengthening — coefficient tightening, probing, dominated columns.
   The largest remaining structural gap against established solvers.
3. Reliability branching; the option exists and has never been measured.
4. A lock-based first-point heuristic for `arki001`, `dano3mip`, `rentacar`,
   `seymour`, `lotsize`, `mitre`, `p2756`, which return no point at all.

## Artifacts

`PLAN.md`, `HOLDOUT_SELECTION.md`, `SOURCE_IDENTITY.json`, `gate/` and
`gate.log`, `development-30s/` (108 records), `holdout32-30s/` (20 records),
`MODEL_LEDGER.md`, `COMPARISON.md`, `SUMMARY.json`, `CANDIDATE_PROFILE.json`,
`FINAL_STATE.json`, and the frozen binary with its runtime DLLs and
`final-source/`.
