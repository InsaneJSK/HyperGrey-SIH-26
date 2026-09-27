# MILP iteration14 — measured root-cut work allocation

CPU only. Separate diagnostic build `build-milp-iter14-diag` and candidate
`build-milp-iter14`; iteration13 and earlier archives are preserved.

Decision: keep the new instrumentation and controls, but do NOT promote the
one-round candidate. In the matched 21-case wave it completes 9 cases versus
10 for the five-round baseline. Binkar's median gap improves in the repeats,
but one repeat and the broader p0282/mod008 results regress. Five rounds remain
the default. All final checks pass within their explicitly limited scope.

## What changed

Added optional exclusive phase-time/LP-work attribution and a configurable
root cut-round allowance. The tested candidate permits one round per root;
the default remains five. Added a separate counter-only restart trigger for
reproducibility tests. Pump/diving/neighborhood algorithms, bound/pruning logic,
feasibility/gap tolerances and the restricted exact-proof engine are unchanged.
No reference incumbent or benchmark-specific rule is used.

The [method document](../../docs/MILP_WORK_BUDGETS.md) explains accounting scope,
nesting, rollback safety and the difference between a round cap and hard work/
time/memory limits. The latter are NOT newly established by this option.

## Diagnosis before changing the policy

The diagnostic-only build passes all 11 prior CTest groups and reproduces
frozen13's semantic results on four 512-node cases with capture off AND on.
Nine checker mutation tests pass. These fixed-node tests disable heuristics
and cuts; they do not establish identical full clock-driven trajectories.

Five predeclared 30s diagnostics use the same previous raw/lattice/late-cut
profile. Own solves precede references. All result/phase checks pass.

| Case | Major exclusive phase observations | Own outcome |
|---|---|---|
| binkar10_1 | Cut LP 13.80s, root LP 5.03s, tree LP 4.28s | Point 6810.690026; gap 2.2682% |
| blend2 | Tree LP 11.22s, dives 8.61s, pump projections 7.71s | No point |
| misc07 | Tree LP 15.49s, pump projections 10.01s | No point |
| lotsize | Pump projections 10.02s, root LP 6.13s, tree LP 5.97s | No point |
| eil33-2 | Tree LP 16.62s, pump projections 10.03s | No point |

These are different bottlenecks. A global reduction in cut rounds cannot fix
all of them. Binkar found a point in this diagnostic, unlike its earlier busy-
desktop run; no-point outcomes are not universal characteristics of the model.
Phase times are wall time and exclude parsing/initial validation/output work.

## Predeclared target screen

The [candidate plan](CANDIDATE.md) fixes one versus five rounds, with all other
settings shared. Both profiles capture phase totals; this is an instrumented,
shared-desktop comparison. Each gets 30s, 250000 nodes and gap 1e-6. References
get 5s independently after own runs, not an equal-budget speed comparison.

| Model | Baseline five rounds | Candidate one round |
|---|---|---|
| Binkar | Point 6806.650018; bound 6678.594982; gap 1.8810% | Point 6762.080017; bound 6669.424182; gap 1.3700% |
| mod008 | Numerical completion 307 in 27.91s | Numerical completion 307 in 29.97s |
| p0282 | Point 266462; bound 257125; gap 3.5041% | Point 286548; bound 205296; gap 28.3554% |

All six outcomes validate. Binkar cut-LP time drops 9.71 to 2.47s (eight versus
two LP calls), with more tree nodes and a better incumbent, but a weaker bound.
P0282 is a serious regression in both point and bound. Mod008 completes in
both policies; candidate uses more nodes. No universal speedup or default
promotion is justified. The adverse screen is retained, not hidden or retuned.

## All 21 retained public models

The candidate core is unchanged from the screen. Each profile gets 30s,
250000 nodes, gap 1e-6 and an external 45s watchdog. Profile order rotates by
model/repetition. All own runs finish before reference work; no builds, heavy
diagnostics or reference solves run concurrently with these measured own solves.
All 21 cases are now development data, including iteration13's four holdouts.
There is no genuinely new holdout or full-library expansion in this iteration.

After the two separately retained reference retries described below:

| Policy | Restricted exact proofs | Numerical completions | Checked feasible limits | No-point limits |
|---|---:|---:|---:|---:|
| Five rounds, baseline | 2 | 8 | 9 | 2 |
| One round, candidate | 2 | 7 | 10 | 2 |

Both profiles independently reproduce the restricted exact results for p0033
(3089) and markshare_4_0 (1). Both numerically complete enigma (0), flugpl
(1201500), stein27 (18), egout (568.1007), lseu (1120), p0201 (7615), and rgn
(approximately 82.19999923). Numerical completions are checked against optimal
reference results at the declared tolerance, not general exact certificates.
Baseline also completes mod008 (307) in 29.07s; candidate still has a 0.3247%
gap at 30s. In the earlier target screen both completed mod008, demonstrating
its sensitivity to the clock boundary.

The complete unfinished-case ledger follows. Each cell is objective / reported
gap in percent, rounded for display; saved JSON retains full precision.

| Model | Baseline five rounds | Candidate one round |
|---|---|---|
| blend2 | No point | No point |
| binkar10_1 | 6810.690026 / 1.9402% | 6765.220016 / 1.4163% |
| gt2 | 42649 / 67.3107% | 42649 / 67.3107% |
| mod008 | 307 / numerical completion | 307 / 0.3247% |
| p0282 | 266462 / 3.5116% | 286548 / 28.4004% |
| misc03 | 3360 / 4.4630% | 3360 / 4.6117% |
| misc07 | 2920 / 46.9017% | 2920 / 47.0729% |
| pk1 | 36 / 97.2973% | 31 / 96.8750% |
| gen-ip002 | -4681.758266 / 2.8952% | -4681.758266 / 2.8967% |
| assign1-5-8 | 227.999999746 / 17.7214% | 227.999999746 / 17.7312% |
| lotsize | No point | No point |
| eil33-2 | 1204.099899 / 31.6187% | 1204.099899 / 31.6187% |

The p0282 regression repeats: its candidate bound is about 205167 versus
257105, as well as a worse incumbent. More tree nodes or less cut work is not
by itself a better solve. The candidate is NOT promoted. Comparisons with old
iterations are not controlled speed experiments: this is a shared i5-10210U
desktop, and wall-clock-triggered search varies with load. Prior long-budget
Blend2 completions remain valid historical evidence; this short profile does
not reproduce them. The solver's gap denominator is 1 + absolute objective.

## Three new Binkar repeat pairs

All six saved final points pass independent original-model checks. None closes
the gap. The one-round policy wins two pairs and loses the third:

| Pair | Baseline objective / gap | Candidate objective / gap |
|---|---|---|
| 1 | 6784.220013 / 1.5551% | 6765.220016 / 1.4165% |
| 2 | 6795.210015 / 1.7160% | 6765.220016 / 1.4182% |
| 3 | 6754.170019 / 1.1213% | 6762.080017 / 1.3726% |

Median reported gap is 1.5551% versus 1.4165%. Median explored nodes are 793
versus 1444. Candidate has a weaker bound in every repeat. The best baseline
run beats every candidate repeat, so the median improvement is limited evidence
of a budget trade-off, not a uniform Binkar win or global solver speedup.
Median exclusive cut-LP time drops from 9.94s to 2.53s, while tree-LP time
increases from 9.21s to 16.20s. These are per-phase medians, not an additive
single-run decomposition. Both profiles still consume their 30s solve budget.

## Two reference-process timeouts, separately resolved

The original wave keeps `incumbent_reference_pending` for both eil33-2 records.
The independent process hit its 25s watchdog before returning point validation;
this is not erased or relabeled in the original results/SUMMARY files.

`supplemental-references` retries only those checks using the unchanged helper
and unchanged saved own outputs. The configured HiGHS solve limit stays 5s;
only its external process watchdog increases to 150s. The two reference
processes take 58.15s and 61.58s, versus reported optimization times of 6.58s
and 6.69s. A solver's configured time limit is not a hard process wall limit;
large-vector validation adds substantial overhead here.

Both own vectors have zero reported original-row/bound and integer violation,
with recomputed objective 1204.099899. Both reference optimizations still time
out, so these are independently checked FEASIBLE LIMITS, not optimum claims.
No own solve is rerun and no reference point is fed into the solver. The final
auditor counts a point only when its original or linked supplemental check
actually validates it; a nonempty vector alone is insufficient.

## Final regression gate

- 12 CTest groups and 88 Python unit tests pass.
- New C++ coverage: 120 tiny exhaustive min/max mixed-integer models, 360 full
  solves across round caps 0/1/5, 720 partial/zero-time checks, and 237 observed
  counter-triggered restarts. Phase totals and iteration sums reconcile.
- 80 established generated cases across three round caps: 240 passing runs.
  Binary cases use enumeration; mixed cases include independent point/reference
  checks. These are 80 distinct models, not 240 new models.
- 100 reused iteration12 exhaustive MPS cases pass fresh reference, objective,
  saved lattice/frontier/cut and work-accounting checks.
- All 28 independent MPS marker-domain cases pass. Three invalid CLI controls
  are rejected. Two short public integrations replay restarts at node 0 and 2.
- Frozen13 versus current capture OFF/ON matches the semantic frontier/result
  signature on four 512-node cases with heuristics/cuts disabled. This tests
  default-preserving bookkeeping, not full clock-driven trajectory equality.
- The optimized lattice reader returns identical complete parsed data to the
  frozen13 reader on all 21 public models. Caching binding-backed arrays speeds
  the checker, not the optimization engine. The old archive remains untouched.

## Saved-result audit and archive

The final re-audit passes all 59 public experiment records on 21 distinct
models: 5 diagnostics, 6 screen runs, 42 broad-wave runs and 6 repeats. This
includes 51 saved final-point checks (two through linked supplemental retries),
4 restricted exact-proof recomputations on 2 models, 202 retained lifted-cover
checks and 82258 SAVED lattice events. Twenty lattice traces reach their
4096-event cap; truncation is explicit. These counts do not include unseen
events or assert exact validity of every underlying LP bound. Timed runs do
not capture full frontier traces; the separate regression/parity tests do.

All 59 phase/iteration accounting checks pass. There are zero observed result
validation failures, with the two initial reference-process timeouts retained
and separately resolved. The archived JSON summaries keep their original
pending categories; this report's combined counts explicitly incorporate the
linked rechecks. Failure to finish remains failure to finish, not validation
failure or proof of infeasibility.

The final state, source manifest, executable and CMake cache are saved beside
this report. The final audit hashes source snapshots and saved outcomes; the
freezer verifies the matching candidate core, the frozen iteration13 binary,
all its source/evidence hashes, and the iteration12/11/10 binaries before
writing a new archive. Earlier versions are not overwritten. The supplemental
runner and stricter point-count auditing were added after timings; the candidate
optimization core and benchmark outputs were not retuned or changed.

## Reproducibility and remaining scope

Candidate: `build-milp-iter14/solver_cli.exe`, 752437 bytes, SHA256
`f31c1181bc6b775f197a47aee543c9f997955df4a9ff9cb7da61a9820a69df69`.
Diagnostic-only binary SHA256
`987c09f805b26e38c4d32c3c867658ca3698699705bf3dd7620140b2fd06a00f`.
The diagnostic source differs from the candidate and is pinned separately.
Each experiment saves the exact plan, command, input/binary/source identities,
own output, references and checks. Read [reproduction instructions](../../docs/V2_REPRODUCE.md).

This is a better-instrumented, extensively checked research prototype, not a
general exact MILP solver, production replacement or evidence of a competition
percentile. General LP/proof bounds remain numerical, and phase accounting
cannot establish their exact validity. The tested option caps cut rounds,
not pivots, process memory or hard elapsed time. No new full QP/GPU or industrial
validation is claimed. The source remains an independent C++ optimization core;
HiGHS is used only as an external reference/checker.

The [next bounded experiment](NEXT_STEP.md) targets selective cut continuation
without sacrificing p0282/mod008, then separate feasibility failures and stronger
general bounds. Five root cut rounds remain the default; the one-round policy,
raw-LP ranking and lattice strengthening remain opt-in. CPU work stays local.
No Kaggle notebook, GPU experiment or user upload is needed for this iteration.
