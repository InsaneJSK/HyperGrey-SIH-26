# Merge verification — does the weak-pivot safeguard change the shipping profile?

23 September 2026. The merge of the continuous LP/QP track into the MILP track
brings `--stable-primal-ratio` into the tree. The flag is opt-in and off by
default, so the claim to test was that the merged build answers exactly as
iteration 36's frozen executable does.

**It does. 16 of 16 models identical, 0 mismatches.** But the first three
attempts to establish that were wrong, and why they were wrong is the more
useful result.

## The recommended profile is not deterministic

The same frozen executable, the same model, the same flags, three consecutive
runs:

| Model | Run 1 | Run 2 | Run 3 |
|---|---:|---:|---:|
| `gen-ip002` | -4676.020982 | -4676.020982 | **-4718.794708** |
| `mas74` | 13422.837279 | 13422.837279 | **13320.466410** |
| `misc03` (LP iterations) | 8,562 | 9,408 | 9,414 |

Objectives, LP iterations and bound tightenings all vary. The cause is the
profile's heuristics, which take a wall-clock slice: at a fixed node limit the
*search* is fixed but the *heuristic effort inside it* is not, so a different
incumbent is found. Adding `--no-heuristics` makes all three deterministic.

This is a property of the shipping profile, not of this merge, and it has a
consequence for every comparison this project makes: **two binaries compared
under the recommended profile cannot be distinguished from one binary compared
with itself.** Iteration 33's equivalence harness already ran with
`--no-heuristics` for this reason. That is the right method and this report
follows it.

## What the wrong method produced

Three successive comparisons, each reported before the variance was understood,
each an artifact:

| Comparison | Apparent result | What it actually measured |
|---|---|---|
| frozen vs merged, full profile | 6 of 16 mismatched | run-to-run variance |
| frozen vs control, full profile | 8 of 16 drifted | variance plus a non-reproducible rebuild |
| control vs merged, full profile | 1 answer differed | variance; the model that "differed" swapped between runs |

The `gen-ip002` and `mas74` objective differences reported from those runs were
not caused by the merge. Repeating either comparison reshuffles which models
appear to differ.

## The controlled result

Control is iteration 36's frozen `final-source/`, rebuilt on this machine;
candidate is that source plus the safeguard, its flag off. Same compiler
(WinLibs GCC 14.2.0 x64 UCRT POSIX SEH r2), same CMake command, same machine.
Fixed 2,000-node limit, `--no-heuristics`, gap 0.

**16 models, 0 mismatches**, comparing `status`, `objective`, `best_bound`,
`gap`, `nodes`, `cuts`, `unresolved_nodes`, `lp_iterations`, `warm_starts` and
`bound_tightenings` — `p0033`, `flugpl`, `stein27`, `egout`, `lseu`, `mod008`,
`p0201`, `misc03`, `pk1`, `rgn`, `gen-ip002`, `blend2`, `gt2`, `mas74`,
`p0282`, `binkar10_1`.

`--stable-primal-ratio` is accepted by the merged build and returns the same
objective as the flag-off run, so the flag is wired through rather than inert.

CTest on the merged build: **29 of 29 passed**, including both sides' new
tests — `primal_ratio_stability` and `gomory_cut_validity`.

## A reproducibility gap, found on the way

Rebuilding iteration 36's frozen source, on the compiler its own
`SOURCE_IDENTITY.json` records, does **not** reproduce the frozen binary:

```
recorded  e379b12cb5136cdf04ae22539d00073730dd94672b1b2075c7e8e5012bf11dad
frozen    e379b12c...  (matches)
rebuilt   3d6220772abafd25b07e5864e11564e557db1878bee98ecb178c9f73ac0a7b69
```

The source is hash-bound and the binary is hash-bound, but the link between
them is not reproducible on this machine — the build directory path and link
order are baked into the image. Every measurement remains valid, because each
was made with the frozen binary that is stored and hashed. What is not
currently possible is regenerating that binary from its recorded source. This
predates today's work and is recorded here rather than fixed, because fixing it
means a reproducible-build flag set and its own measurement.

## Artifacts

`equivalence.py` and `EQUIVALENCE.json` (the controlled comparison),
`determinism.py` (the three-repeat test), `ATTRIBUTION.json` and
`CONTROLLED.json` (the superseded full-profile comparisons, retained because
they are what exposed the variance).
