# MILP work attribution and bounded root cut rounds

Iteration14 adds optional `--capture-work`, `--root-cut-rounds N` (0 through5)
and `--restart-nodes N`. Defaults are unchanged: capture off, five rounds per
root, and the existing half-time restart trigger. No option names a benchmark.

## What the counters measure

The `work` JSON object contains exclusive wall seconds and MILP-visible LP
call/reported-iteration counts for17 phases. Scoped child work pauses its
parent's timer, so phase times sum to the instrumented interval. Reported LP
iterations sum to the existing result total. Neither sum is a proof certificate.

Root/tree/cut LP categories include their LP wrapper's model preparation,
canonicalization, factorization and internal numerical checks. Recovery calls
made explicitly by MILP are attributed separately. A wrapper's internal
fallbacks contribute its combined reported iteration count, not extra visible
LP calls. `validation` means the MILP candidate-acceptance check; `presolve`
means MILP domain propagation, not every operation performed inside an LP.
`cut_separation` includes cut-round bookkeeping outside its nested LP call.
`pump` includes setup and other pump work outside fixing/projection LP scopes.
`other` retains unattributed MILP overhead rather than silently dropping it.

The interval excludes MPS parsing, initial input validation/model copying and
output serialization. Wall time is NOT CPU time, pivot-equivalent work, a
factorization count, or a platform-neutral performance metric. Instrumentation
can affect clock-triggered search. Both compared profiles use the same capture
setting; no uninstrumented speedup is inferred.

## Root-round allowance

`--root-cut-rounds 1` permits at most one optional cut round at the initial
root and at most one after the existing full-original-domain restart. The
default5 preserves the previous loop. Zero skips optional root cut rounds.
A round may add several cuts, and may spend substantial work solving its LP.
This is a ROUND/CALL limit, not a hard LP-iteration, time, memory or FLOP cap.
Global time/node limits and LP safety checks remain separate.

No cut gains new validity from this option. Verified LP bounds still govern
proof/pruning, failed optional cut LPs still roll back model/trace/basis, and
heuristic-local bounds still cannot become global proof bounds. Less cut work
can leave more time for feasibility search but can also weaken bounds severely.
The predeclared p0282 screen demonstrates precisely that adverse outcome.
The one-round candidate therefore remains optional, not the new default.

## Counter-only restart tests

`--restart-nodes N` changes ONLY the trigger of an already enabled late restart:
it uses the explored-node counter instead of the half-time trigger. It does
not enable cuts/restarts by itself, add multiple restarts or reset consumed
global budgets. Zero requests an immediate restart when normal limits permit.
The original domain is retained and the inherited bound is still the minimum
over queued/deferred nodes. Independent frontier replay checks that boundary.

This makes the restart trigger deterministic, not every time-limited heuristic
or LP in a full run. Fixed-node tests with other timed heuristics disabled are
distinct from wall-clock performance comparisons.

## Evidence

The [iteration14 report](../reports/milp-iteration-14/REPORT.md) records the
diagnostic build, candidate, all failures, paired outcomes and repeat caveats.
Tests include exhaustive min/max mixed models, zero/tiny limits, default/capture
parity, nested phase restoration, invalid controls and counter restarts.
Independent checkers retain their original numerical/exact-scope boundaries.
The lattice checker now reads binding-backed sparse arrays once; its parsed
data is checked identical to frozen13 on all21 public models. That speeds
validation, not the optimization engine. Earlier archives are preserved.
