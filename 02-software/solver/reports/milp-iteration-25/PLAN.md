# Iteration25: deterministic near-tie ranking in private distance dives

Resumed by the user on 17 September 2026. Preserve frozen24 and all its results.
CPU work stays local. Environment recovery precedes measurements: the old build
cache points to another checkout and its 64-bit compiler/runtime is absent.

Hypothesis: roundoff near equal fractionality need not change the selected
private branch. Candidate finds the actual maximum fractionality, then chooses
the first original column within an absolute 1e-12 of it, excluding scores at or
below the unchanged integer acceptance tolerance. This is a two-pass anchored
set, not a non-transitive pairwise comparator. It acts only in private distance
dives. No model names, favored column constants, reference answers, new budget,
or changes to acceptance, LP checks, cuts, bounds or proof state.

Stability contract: fixed layout and eligibility, and perturbations that leave
membership in the anchored maximum's tie set unchanged, preserve the winner.
There is no universal continuity claim at the tie/eligibility boundary. Ties
follow column order; permuting tied columns can change the winner, while the
chosen variable must remain in the maximum's tie set. Integer translations and
MIN/MAX do not alter the mathematical fractionality score (subject to floating
representation). Nonfinite points are rejected at the helper boundary.

Before timed screening: replay saved seed/stage vectors through strict and
candidate ranking; diagnostic actual strict-original, staged-strict and
staged-stable paths; CTest, existing full Python/generated/retained correctness
gate with candidate enabled, frozen24 off parity, inactive-option parity,
MIN/MAX/domain and budget checks. Save failures and hashes. Diagnose any gate
failure before timings; do not quietly alter the threshold after results.

Screen: misc07, lotsize, danoint, blend2, eil33-2, rout, p0201, mod008, mas74,
binkar10_1, gt2, pk1; two repeats each, alternating profile order. Control is
frozen24's staged settings in the new binary. Candidate adds only
--pump-distance-stable-ranking. Both: 30 seconds, 250000 nodes, 1e-6 gap and
identical accuracy. Timed own solves serial; independent five-second validation
references afterward (not a matched performance contest). Retain captures.

Promotion gate: correctness and stability contract pass, preserve misc07's
checked result and protected completions, and report every coverage/quality/gap
tradeoff. Only run a 27-model wave if screen evidence supports broader testing;
same source/settings, one repeat/profile, no captures. Reject promotion on lost
protected coverage/completion or unexplained validation failure. Keep option
off by default unless broader repeated evidence warrants a documented decision.
No best-of-profile union, no claim these reused cases are unseen holdouts.

Iterations26–28 remain conditional on this evidence. A failed gate takes priority
over spending the next slot on another heuristic.
