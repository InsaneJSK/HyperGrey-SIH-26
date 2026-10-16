# Iteration 37 plan — should `--gomory-cuts` stay in the recommended profile?

Declared 21 September 2026, before the comparison is run.

## Why this is being asked

Iteration 32 promoted `--gomory-cuts` on a **bound** criterion: the root bound
improved on 26 of 28 changed development observations and 4 of 4 unseen ones.
That report stated plainly that no end-to-end gain was demonstrated — the
30-second gap was a wash, better on 15 records and worse on 13 — and that
`p0282` regressed.

The MIPLIB 2017 re-run now supplies evidence the development set could not. On
the 60 instances of part a, the current profile finds **fewer** answers than the
old one: proven 3 → 2, validated solutions 21 → 18, even though the failure
modes iterations 33, 34 and 36 targeted are nearly gone (memory-guard stops
8 → 1, unresolved roots 5 → 0, resource-limit exits 1 → 0).

A four-instance ablation isolates the cause, and it is not telemetry (node
counts are identical with the `--capture-*` flags removed):

| Instance | Recommended | Without `--gomory-cuts` |
|---|---|---|
| `decomp2` | nothing, 4,278 nodes | **proven -160 at the root, 1 node** |
| `cost266-UUE` | nothing, 2,295 nodes | **solution 26,627,506**, 7,735 nodes |
| `cvs16r128-89` | nothing, 229 nodes | nothing, 371 nodes |
| `glass-sc` | nothing, 404 nodes | nothing, 402 nodes |

Four instances are not enough to reverse a promotion. This iteration measures it
on a set large enough to decide.

## What is run

- **All 60 instances of benchmark part a** (positions 0–59), the slice whose
  re-run exposed the regression. Every instance, not a selection — choosing
  instances by their outcome would bias the result.
- Control: the iteration 36 recommended profile. Candidate: the same profile
  **minus `--gomory-cuts`**. Single-flag ablation, same frozen executable
  (`e379b12c…1dad`).
- 300 seconds, node limit 100,000,000, gap 1e-6 — the benchmark budget.
- Paired and simultaneous on this host, so machine load hits both together.
- Every returned point checked by an independent HiGHS 1.12.0 reader; every
  objective compared with MIPLIB's published solution file.

These 60 instances are development data for this question: part a's result is
what raised it. The decision here is about what to recommend, and it is made on
the same public instances the recommendation will be judged on.

## Decision rule

`--gomory-cuts` **stays** in the recommended profile only if, against the
control:

- proven optimal answers do not fall, and
- validated solutions do not fall.

If either falls, it is **removed from the recommended profile** and kept as an
opt-in flag, with iteration 32's bound evidence left standing as what it was:
a demonstrated improvement in root bound that does not convert into answers at
this budget.

Either way, report the per-instance differences in both directions, and state
whether the cut separator should be retained at all for the submission.
