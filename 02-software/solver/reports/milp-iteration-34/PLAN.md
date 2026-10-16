# Iteration 34 plan — let the root LP finish

Declared 19 September 2026, before any code change, timed comparison or holdout
solve.

## What the benchmark showed

Across the first 164 MIPLIB 2017 benchmark instances, **17 never left the root
LP** (`unresolved_relaxations` at node 1). A diagnosis on 12 of them
(`reports/root-lp-diagnosis/`) found one cause for all twelve:

- Every root relaxation stopped at **exactly 10,000 simplex iterations** — the
  default `--iteration-limit`, a per-LP count cap that no code path ever raises
  for the one LP that starts cold.
- The bounded engine had used only **11 to 59 seconds** of its 300-second budget
  when the cap stopped it. The rest went to fallback engines carrying the same
  cap, which cannot succeed where the faster engine was stopped by a count.

With the cap lifted, **8 of the 12 root LPs complete**, in 13.8 to 224.6 seconds
(`CMS750_4` needed 11,261 iterations — 1,261 past the cap). Four still reach the
time limit (`dano3_3`, `dano3_5`, `mzzv11`, `mzzv42z`); that is LP throughput and
is not addressed here.

## Mechanism

`--root-iteration-limit N`: the iteration cap for the root relaxation, including
its cut-round re-solves, becomes `max(--iteration-limit, N)`. Node LPs and
heuristic LPs keep `--iteration-limit` unchanged; they start warm and do not
approach it. Default `N = 0` means no change, so executable defaults are
unchanged. The candidate profile sets `N = 100000000`, the CLI's ceiling, which
leaves the root bounded by time alone.

Nothing about the LP engines changes. This is a budget allocation.

## Risks, stated in advance

1. A root LP that previously gave up at 10,000 iterations and fell back may now
   spend most of the budget and leave little for the search. That is the right
   trade when the alternative is no root at all, but on the development set it
   could cost time on models whose root previously failed fast and recovered.
2. A stalled root LP now runs until time instead of until 10,000 iterations.

## Correctness gate

CTest and the sparse accuracy gate with the full flag set, before any timed run.
The change cannot alter any LP's answer, only whether a root LP is allowed to
finish, so every existing check applies unchanged.

## Evidence

- **Profiles**: control is iteration 33's promoted profile; candidate adds
  `--root-iteration-limit 100000000`. Same executable, single-flag ablation.
- **Development**: the 27 reused models, two repeats per profile, 30 s. At this
  budget the root cap is not expected to bind on these small models, so the
  expected result is no change; the screen exists to catch a regression.
- **Mechanism set** (development data — they informed the design): the 12
  diagnosed instances at 300 s, control and candidate started together on the
  same host, as in the iteration 33 guard re-run.
- **Fresh holdout for this mechanism**: the five root-stuck instances that were
  **not** part of the diagnosis and have never been run with the cap lifted —
  `academictimetablesmall`, `brazil3`, `irish-electricity`, `k1mushroom`,
  `neos-3216931-puriri`. Their sweep outcome (stuck at the root) is known and is
  exactly why they were chosen; their response to this change is not. 300 s,
  paired, same protocol.

Every returned point checked by an independent HiGHS 1.12.0 reader; every
objective compared with MIPLIB's published solution file.

## Decision rule

Promote only if:

- zero validation failures and zero rejected points in every set, and no
  objective disagreeing with a published or independently proven optimum;
- development completions and checked-point coverage do not fall;
- the root LP completes on more mechanism-set instances than in the control;
- on the fresh five, the candidate completes the root on at least as many as
  the control, and introduces no new failure.

Report every instance where the uncapped root consumed the budget and the search
got less time than before.
