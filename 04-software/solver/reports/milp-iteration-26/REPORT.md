# MILP iteration26 — exact diagnosis, alternate reserve rejected

17 September 2026. Keep `--pump-distance-alternate-reserve` off. It changes
private work but gains no feasible coverage in the declared repeated screen.
Retain the staged control for iteration27. No larger timing wave is justified.

| Two models, three runs/profile, 30 seconds each | Stage | Reserve |
|---|---:|---:|
| Checked feasible points | 3 / 6 | 3 / 6 |
| Completions | 0 | 0 |
| No point | 3 | 3 |
| Validation failures | 0 | 0 |

All lotsize runs fail to find an integer point. Every danoint run returns
69.5 with about a 9.664% gap; first-point times span 4.949–5.435 seconds.
Danoint has zero reserve calls: its checked point is found before the private
distance dive. These repetitions do not erase its retained earlier fixing
timeout or prove general first-feasible reliability.

See [the full model ledger](MODEL_LEDGER.md) for each objective, bound, gap,
status, first-point time, total time, nodes and pivots; `FACTS.json` retains
phase work. Own runs were serial, alternating profile order. Separate five-second
HiGHS validation follows all own runs. This is not a matched performance race.

## Exact bottleneck

Two root-only diagnostics per model preceded the policy. On lotsize, step7's
primary branch uses 1221 pivots (1220 phase-one), returns local infeasibility
and consumes about 1.3 seconds. Step11 then times out with just 0.318–0.380
seconds left. The bounded diagnostic captures exact coefficients, private
objective and auxiliaries, branch bounds, tagged input basis, node/step,
status, total/final LP pivots and elapsed/available time.

Four saved fixtures replay in cold, dual-only and adaptive modes: all twelve
results are infeasible and independently corroborated by HiGHS. Step11 needs
1222 pivots in the replay. The private subproblems are genuinely infeasible;
no false LP certificate or invalid point is demonstrated. Compatible basis
metadata alone does not remove expensive phase-one work. These private
infeasibility results never establish infeasibility of the original MILP.

The two danoint diagnostics return 69.5 without entering a distance-guided
private child. Iteration25 separately retained its failed pump fixing target:
the same target finishes at1876 pivots in successful runs but times out at1862
in the failed run, before staging/ranking. This experiment does not alter that
fixing deadline. No replay point or bound enters any measured solve.

## The tested policy

Only a primary distance-guided child LP gets half of the remaining shared
dive slice. Its alternate may use what remains. Staging and the existing total
dive deadline are unchanged; no extra slice, tolerance change or global bound
rule. Failed primary attempts retain the parent basis and alternate bounds.
The ranking experiment from25 stays off.

In the three lotsize candidate runs the cap executes47 times and alternates
are attempted16 times. The policy is active but does not find a point. Total
dive phase time across repeated heuristic invocations is roughly9.7–10.2
seconds per whole solve; this does not mean one dive receives that allowance.
Internal deadlines are cooperative and can slightly overshoot.

## Validation and retained failures

The exact candidate binary passes25 CTest groups,176 Python checks,320
generated runs,100 retained exhaustive cases, independent LP fixtures, MPS
contracts and disabled arithmetic parity. Five further fixed-work parity
pairs pass against frozen25 or inactive features. Prerequisite errors and
zero-time/node/LP-iteration behavior pass. Existing staged-basis tests cover
failed-primary/alternate ownership, invalid bases and exhausted LP budgets.

The first local check incorrectly expected a top-level iteration-limit status
for zero LP pivots. The documented solver contract is `unresolved_relaxations`
with zero LP work, no point and no finite bound. The original test/log/result
remain; the corrected check passes without changing the binary. No timing
comparison ran before these checks passed.

All12 comparison records and6 final vectors pass the saved-run audit, source
and model hashes, original-model feasibility/integrality/objective checks,
frontier/cut/lattice and heuristic accounting checks. Root diagnostics have
zero validation failures. Earlier frozen25 remains unchanged. Diagnostic
and candidate executables are both retained because instrumentation preceded
the budget policy.

Candidate CLI SHA256:
`f74d9fe31411ec2c94452eb302b1967ad8bf85be44df3d6d4d177e93a162cf2c`.
Same project-local GCC14.2 x64 toolchain and Windows host as iteration25.
Shared desktop timing remains a limitation; no process-memory measurement
was collected in these comparisons. CPU only.

## Next

Iteration27 tests one existing restart scheduling policy against the staged
control, protecting completed cases and measuring binkar10_1/mas74 quality.
Iteration28 will separately recheck all27 development cases, untouched public
cases, artificial transformations, resources and the final profile decision.
Neither remaining slot guarantees a successful release promotion.
