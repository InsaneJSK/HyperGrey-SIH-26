# Kaggle MILP iteration 03 return — audited 15 September 2026

Saved and checked `sih26119_milp_results (1).zip` from Downloads. The submitted
notebook and source ZIP are preserved alongside the original return and extracted
raw output in this folder. The return matches the intended recovery/neighbourhood
experiment, not the previous branching comparison.

## Identity and correctness

- Return SHA-256: `711867e10aba5bc0cb0192faed038a0a86e20c94b03826c1473123b24eabb7fa`.
- Submitted source SHA-256: `1ba3309e1cb62c7508af66698dc53defa1f229a8bd4ec8de77f2dde9a0aba889`.
- Reported Linux binary: `e3ac5b4e239def54f7158c245aafc8f0a568c9b9c01897a2ce774ebbb8ee5593`.
- Verified archive CRC, 176 source entries, 74 runtime source hashes, dataset
  identities, CMake configuration, command limits and aggregate/raw agreement.
- CTest 3/3 groups and generated MILP checks 240/240 pass on Kaggle.
- All four returned incumbents pass fresh independent checks against the original
  MPS models locally. No invalid candidate was accepted. All current numerical
  and test source files also match this returned snapshot.
- CPU-only Linux, Python 3.12.13, GCC 11.4, two physical/four logical cores,
  33,659,379,712 bytes RAM. This is not a new GPU performance result.

## Equal-budget results

Each run used 180 seconds, 250,000 main-tree nodes and requested gap 1e-6. Both
modes use fractionality branching. The combined mode adds LP recovery and
neighbourhood improvement. References run separately after timed solver runs.

| Model | Control | Recovery + neighbourhood | Meaning |
| --- | --- | --- | --- |
| markshare_4_0 | Objective ~5, bound -1e-7, gap 83.33%; 250k nodes, 166.32 s | Same objective/bound/gap; 250k nodes, 166.82 s | No final-solution or proof improvement |
| blend2 | No incumbent; bound 7.468466152; LP iteration limit at 45.18 s, 3,762 nodes | No incumbent; bound 7.591048200; global time limit at 180.02 s, 10,285 nodes | Recovery allows continued search, but feasibility remains unresolved |
| binkar10_1 | 7297.320029; bound 6665.118071; gap 8.6623% | 6747.310015; bound 6664.595512; gap 1.2257% | Much better checked incumbent; proof still open |

### binkar: the incumbent gain reproduces on Kaggle

The new mode improves its first incumbent five times:

| Time (s) | Objective |
| ---: | ---: |
| 15.66 | 7297.320029 |
| 18.41 | 6810.690026 |
| 29.39 | 6789.670035 |
| 47.49 | 6757.190021 |
| 59.33 | 6752.000011 |
| 77.60 | 6747.310015 |

There is no further improvement before 180 seconds. Neighbourhood search makes
14 calls, explores 632 local nodes, and uses 27.0054 seconds; five calls improve
the incumbent. Total main-tree nodes decrease from 5,268 to 4,417. The new bound
is slightly weaker, so this is an incumbent improvement, not faster proof closure.
Independent final maximum absolute violation is 6.000000052e-9, integer violation
zero. Objective falls 7.5372% against the control at the same limits.

The 30-second reference times out with incumbent 6746.760023. Our candidate is
about 0.55 objective units above that reference incumbent, but the latter is NOT
a proven optimum. Do not substitute closeness to it for our reported 1.2257% gap.

### blend2: recovery succeeds, but no candidate yet

All five recovery attempts succeed in 0.4086 seconds of recovery time. Two nodes
remain unresolved, with their bounds retained. No finite MILP gap is claimed
without an incumbent. The reference proves optimum 7.598985; our lower bound
7.591048200 stays below it but is not itself a feasible solution.

The first failing relaxation (node4615, depth19, 10,000 iterations) and its input
basis are exactly equal to the final local 90-second control snapshot already
diagnosed in `../milp-iteration-03/lp-diagnostic-checked/`. Repeating that same
cold diagnostic would add little evidence. The return does NOT capture the two
rejected near-integer points or their fixing-LP outputs. Therefore the precise
reason they cannot be repaired remains unestablished from this archive alone.

### markshare: improvement counts need context

The new mode reports three neighbourhood improvement calls, but some recorded
objective changes are tiny numerical changes near the same integer objective.
Both modes reach the same final incumbent ~5 around101 seconds and exhaust
250,000 nodes. The reference times out with incumbent~4 (not an optimum).
Do not claim a markshare improvement from the counter alone.

## Next bounded iteration

1. Preserve this combined solver as the comparison baseline, without changing
   the default flags solely from one hard-case pass.
2. Capture the original/rounded near-integer point, original residuals, integer
   fixings and repair-LP outcome at the first rejected tree candidates. Reproduce
   the blend2 failures locally; use independent references only for diagnosis,
   never to inject a solution into our solver.
3. Determine whether each integer assignment is genuinely infeasible or whether
   continuous-variable repair/numerical accuracy is the issue. Implement the
   appropriate checked repair or continued branching while retaining unresolved
   bounds. Do not loosen the 1e-7 absolute feasibility or integrality gates.
4. Verify adversarial tiny-fraction/scaled-row cases, general integers,
   maximization, proof-bound preservation and all generated regressions, then
   compare against this combined baseline on hard models with equal budgets.
   Keep the next Kaggle notebook separate, two-cell and below1MB.

Target: an independently checked blend2 incumbent without regressions, not a
promise that one repair will solve it. After that, prioritize proof-bound strength
and repeated/broader testing. No hard optimum is completed in this return, no
industrial-completeness or top-percentile submission claim is justified, and
unchanged notebooks need not be rerun now. No solver-core changes were made
during this import/cleanup turn.

## Downloads cleanup

Four SIH result ZIPs were compared byte-for-byte by SHA-256 and length against
preserved project copies, then moved from Downloads to the Windows Recycle Bin.
Nothing was permanently deleted, and no unrelated download was touched. See
`DOWNLOADS_CLEANUP.json` for exact paths, hashes and backup locations.
