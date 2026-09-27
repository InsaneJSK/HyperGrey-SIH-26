# Iteration 36 plan — a resource limit is a failed LP, not a dead solve

Declared 20 September 2026, before any code change or timed comparison.

## What is wrong

`neos8` (46,324 × 23,228) is one of the seven instances the MIPLIB 2017
benchmark proves optimal, at -3719 in 71 seconds. Under the **currently
recommended profile it aborts** with `resource_limit: sparse LU fill budget`
and exit 2. Iteration 35 isolated it: the abort needs `--lifted-covers` and
`--gomory-cuts` together, and removing either proves the instance.

The factorization budget in `include/sparse_lu.hpp` throws, and nothing between
there and `main` catches it, so a limit hit while solving *one strengthened cut
round* destroys the whole solve — including the valid pre-cut relaxation and any
incumbent already found.

The same throw is why `buildingenergy` and `supportcase10` exit 2 in the
benchmark. Those two are genuinely too large for the factorization, but exit 2
is the code for a rejected input, so an honest resource limit is reported as if
the model were malformed.

## Mechanism

A relaxation that raises `resource_limit:` returns a **failed relaxation with
status `resource_limit`** instead of propagating the exception. One catch point,
in `relax_model`, restricted to messages beginning `resource_limit:` so real
faults still propagate. Everything downstream already handles a failed
relaxation:

- inside a root cut round, the existing rollback path restores the pre-cut model
  and basis and stops cutting — which is exactly the right response to "this
  strengthened model is too big to factorize";
- at a tree node, the existing defer path retains the node in the bound;
- at the root with nothing to fall back to, the solve ends with a reported
  status and a JSON result rather than exit 2.

New counter `lp_resource_limits`, reported in the JSON, and the end-of-search
message says a factorization budget was hit when one was.

## Risks, stated in advance

1. Rolling back a cut round leaves a weaker relaxation than intended, so an
   instance may end with a worse bound than if the cuts had fitted. That is
   still strictly better than aborting.
2. A model that genuinely cannot be factorized now spends its full budget
   discovering that at several nodes instead of failing immediately.

## Correctness gate

CTest and the sparse accuracy gate with the full flag set. The change cannot
alter any LP's answer; it only converts an exception into a failed status.

## Evidence

Control is the iteration 35 frozen executable, candidate the iteration 36 one,
on identical flags — iteration 35's promoted profile. Paired and simultaneous at
300 s, as in previous iterations.

1. **Mechanism set** (development data — these three motivated the change):
   `neos8`, `buildingenergy`, `supportcase10`. Required: `neos8` no longer
   aborts and is proven optimal at -3719; the other two report a status with a
   JSON result instead of exit 2.
2. **Development**: 27 models, two repeats, 30 s. Expected unchanged — no model
   in that set approaches the factorization budget.
3. **Fresh set**, declared here before any run: the eight largest benchmark
   instances by rows + columns that no iteration set has used —
   `neos-3402454-bohle`, `neos-5114902-kasavu`, `supportcase19`,
   `supportcase12`, `neos-5104907-jarama`, `gfd-schedulen180f7d50m30k18`,
   `ns1760995`, `savsched1`. Size is the property under test, so the largest
   unused instances are the right fresh set. All eight returned `time_limit` in
   the benchmark under the older profile; their behaviour under the current
   profile, and under this change, is unknown.

Every returned point checked by an independent HiGHS 1.12.0 reader; every
objective compared with MIPLIB's published solution file.

## Decision rule

Promote only if:

- zero validation failures and zero rejected points in every set, and no
  objective disagreeing with a published or independently proven optimum;
- **`neos8` is proven optimal at -3719 under the full recommended profile**;
- no instance in any set exits 2 on a resource limit; each reports a status;
- development completions and checked-point coverage do not fall;
- on the fresh set, no instance ends worse than its control: no new abort, and
  no loss of a checked point.

Report every instance where a cut round was rolled back for a resource limit,
and every instance whose bound is worse than the control's as a result.

## Amendment, declared 20 September before any further measurement

The mechanism above was implemented and tested on `neos8` alone. It works as far
as it goes — the abort is gone, exit 1 with a JSON result, and the optimum
-3719 is found — but the instance ends `unresolved_relaxations` and is **not
proven**, so the declared rule is not met.

The reason is visible in the record: `cut_rollbacks=0`, `cuts=91`. The budget is
not hit inside a cut round, so the rollback path never runs. It is hit at a node
*after* 91 separator rows are already in the model. Tableau cuts may carry up to
5,000 nonzeros each under the support cap set in iteration 32, and that density
is what the factorization cannot take, on a model whose own rows factorize
fine.

**Second mechanism, added now:** when a relaxation returns `resource_limit` and
separator rows are present, remove every separator row, invalidate the bases and
retry that node once. The rows added during the search are optional by
construction — the model without them is the one that proved this instance in
153 nodes — so discarding them all is the correct response to "the strengthened
model does not fit". If the retry also hits the limit, the node is deferred as
before.

This is recovery, not prevention. The support cap that lets a cut carry 5,000
nonzeros is the underlying cause and is left alone here: changing it would alter
cut selection on every model and belongs in its own iteration with its own
measurement.

The decision rule is unchanged, including the requirement that `neos8` be proven
optimal at -3719. One line is added to what must be reported: **every instance
where separator rows were discarded for a resource limit, and the bound it
reached compared with its control.**
