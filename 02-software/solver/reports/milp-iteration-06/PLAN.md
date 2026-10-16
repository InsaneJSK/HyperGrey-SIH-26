# Local MILP iteration06 protocol

User authorized continuation locally. GPU/Kaggle remains out of scope.

Hypothesis: reserving late attempts and using a coupled binary Hamming
neighborhood can improve final incumbents without changing feasibility criteria
or importing local bounds into the global proof queue.

Control: iteration05 guided search, unchanged defaults. Preserved binary:
`../milp-iteration-05/final_solver_cli.exe`, SHA256
`ef1856d074862aa754a81e5bff7bfc44c350c02eae4f0a6b43a309c4f4e53cd6`.

Candidate: `--neighborhood reserved`, documented in
`../../docs/MILP_RESERVED_SEARCH.md`. Both compared profiles enable the same
LP recovery, incumbent search and candidate repair. Neither receives reference
solutions or known objective values.

Gate: CTest, diagnostic tests,40 binary enumeration and40 mixed MILP models
under each of guided/reserved/legacy settings (240 checks,80 unique models).
Timing: one sequential run for each profile/model on markshare_4_0, blend2,
binkar10_1;180-second /250000-node /1e-6-gap limits; alternating strategy order.
Reference solves:30 seconds per distinct model, after all timed runs. Fresh
independent candidate/center/neighborhood checks follow timing.

Keep unsuccessful results. Do not promote defaults from a single exploratory
pass or confuse a valid incumbent with a proven optimum. Record any follow-up
experiment separately, with its own binary/source identity and protocol.
