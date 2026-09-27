# Same-slice alternate reserve, declared after exact diagnostic replay

Both lotsize diagnostic runs reach the same expensive primary at step 7:
1221 total pivots, 1220 phase-one pivots, and local infeasibility. It consumes
about 1.3 seconds of the shared two-second dive slice. Step 11 then times out
with only 0.32–0.38 seconds left. All twelve cold/dual/adaptive replays of the
four retained fixtures agree with independent HiGHS on local infeasibility.
This is expensive infeasibility/fallback work, not evidence of a false LP
answer. These local statuses never certify the original MILP infeasible.

Test one generic opt-in scheduling change: each primary private distance-LP
attempt receives half the remaining dive slice; an alternate can use the
remaining slice. Staging and the overall dive deadline are unchanged. A failed
primary leaves the parent basis and original alternate bounds untouched.
Ranking remains off. No changes to numerical/proof/acceptance tolerances.

Paired screen: lotsize and danoint, three alternating-order repeats/profile,
30 seconds, 250000 nodes, gap 1e-6. Control is retained staged profile; candidate
adds only `--pump-distance-alternate-reserve`. Capture is off during timings.
Own solves serial, references afterward. Full correctness gate first.

Require valid repeated improvement in first-feasible coverage/reliability;
preserve every failure. If neither model gains useful coverage, reject the
policy and stop the broad timing escalation. If it gains, broaden protection
before promotion. Danoint's prior miss occurred in pump fixing before the dive;
this policy does not claim to repair that separate deadline sensitivity.
