# Implemented follow-up: space attempts across useful incumbents

Motivation from the current diagnostic run: markshare uses all16 calls by
0.9 seconds around objective73, yet its global tree improves substantially
after that. The diversified selector also exhausts its call cap before1 second.
Selection alone is therefore not enough to give later incumbents local search.

The full comparison and its independent audit finished before this change:
six checked final candidates and28 total vector checks passed. That source and binary are already
preserved in `four-stall-source/` and `four_stall_solver_cli.exe`.

The bounded experiment adds a separate opt-in time-spacing flag, retaining
the guided selector so that scheduling and diversification are not confounded.
Keep the original128-main-node gate,16 calls and cumulative time allowance.
Require successive call start times to be at least min(5 seconds,2% of the
MILP time budget) apart. Keep the first call immediate. This allows later
incumbents to be considered without increasing the total heuristic allowance.

Implemented as `--pace-neighborhood`. CTest3/3, generated240/240 and11 diagnostic
checker tests pass. The single-strategy hard screen is in `pacing-180s-screen/`;
it is complete with all three final candidates and12 total available vectors
independently checked. No final hard-instance objective improves. CLI SHA256:
`ef1856d074862aa754a81e5bff7bfc44c350c02eae4f0a6b43a309c4f4e53cd6`.

No-heuristics, zero time, node-limit proof preservation, maximization, generated
mixed/general-integer cases and emitted spacing diagnostics were checked.
The screen is explicitly distinct from a fresh paired/repeated timing comparison.
All available final and captured improvement vectors were audited afterward.
Defaults remain unchanged; final decision and further work are in `REPORT.md`.

Do not promote a worse result or interpret a node/time limit as completion.
No GPU work or user-uploaded notebook is required.
