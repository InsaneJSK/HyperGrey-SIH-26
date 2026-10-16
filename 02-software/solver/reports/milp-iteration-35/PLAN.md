# Iteration 35 plan — keep the basis through the cut purge

Declared 19 September 2026, before any code change or timed comparison.

## What iteration 34 exposed

With the root LP now allowed to finish, several large MIPLIB instances solved
their root and then ended `unresolved_relaxations` after two or three nodes. The
split was clean across the eleven instances whose root newly solved:

- **tableau cuts purged after the root** (`CMS750_4`, `neos-3656078-kumeu`,
  `neos-662469`, `neos-957323`, `academictimetablesmall`, `neos-3216931-puriri`):
  one or two bounded-engine fallbacks in every one;
- **no purge** (`neos-827175`, `neos-933966`, `ns1208400`, `k1mushroom`): zero
  fallbacks in every one.

Iteration 32's purge discards the basis (`lp.basis = LpBasis(); node.basis =
LpBasis()`), so the root's children cold start, and a cold start on a model this
size needs more than the 10,000 iterations node LPs are given.

## Mechanism

When slack tableau cuts are purged, keep the bounded basis and delete only the
purged rows' logical entries from its status vector.

Why that is valid: a row is purged precisely because its logical is basic.
Deleting that row together with its own basic logical removes one unit column
and the row it sits in, so the basis stays square and — expanding the
determinant along that unit column — nonsingular. The purged rows carried zero
duals, so the reduced basis is still optimal for the reduced LP. If anything
were wrong with it, the bounded engine's existing warm-start checks reject it
and cold start, which is exactly today's behaviour; the change cannot make a
node worse than it is now.

This is not flag-gated: like iteration 33 it changes how state is carried, not
what is solved, and it applies wherever the purge runs (`--gomory-cuts`).

## Evidence

Executables compared, flags identical: control is the iteration 34 frozen
executable, candidate the iteration 35 executable, both on iteration 34's
promoted profile.

1. **Development**: 27 models, two repeats, 30 s. The purge fires often here
   (796 of 1,102 applied cuts were purged in iteration 32), so this set
   exercises the mechanism on many models, not only large ones.
2. **Mechanism set** (development data — it informed the design): the six purge
   instances above, 300 s, paired and simultaneous.
3. **Fresh set**: the seven batch 3 sweep instances that returned a validated
   point under the old sweep binary — `neos-4954672-berkel`, `neos-860300`,
   `neos-911970`, `neos17`, `neos5`, `neos8`, `nu25-pr12`. Chosen by that rule
   alone, before running, because a model that returns a point branches, and
   branching is where a kept basis can matter. None has been run with the
   current profile or with this change. 300 s, paired.

## Decision rule

Promote only if:

- zero validation failures and zero rejected points in every set, and no
  objective disagreeing with a published or independently proven optimum;
- on the mechanism set, bounded-engine fallbacks and unresolved nodes fall;
- development completions and checked-point coverage do not fall;
- on the fresh set, no new failure, and checked points do not fall.

Report every instance where the kept basis was rejected by the warm-start checks.
