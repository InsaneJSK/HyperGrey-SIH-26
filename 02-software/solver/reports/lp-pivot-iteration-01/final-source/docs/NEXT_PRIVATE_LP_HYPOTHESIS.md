# Evidence-selected follow-up after the rejected reserve policy

**Status: tested in [iteration 29](../reports/milp-iteration-29/REPORT.md).**
The diagnostic confirms the exact warm dual rejection. A guarded local
certificate avoids phase one on the retained fixtures and in both lotsize
screen runs, but neither produces an integer point. Keep the feature off;
see [next work](../reports/milp-iteration-29/NEXT_STEP.md). The text below
preserves the hypothesis as written before implementation and measurement.

Iteration26 identifies a more specific source of work than a generally slow
warm start. In its lotsize step7 fixture, adaptive replay uses one dual restart,
one preliminary pivot and1220 phase-one pivots. Cold replay uses1220 pivots.
Both establish local infeasibility. Exact fixtures and references are retained
under `reports/milp-iteration-26/private-replay/`.

In `src/sparse_lp.cpp`, a dual iteration with a negative basic value and no
eligible entering column returns `warm_start_rejected`. The caller accepts
only an optimal warm result (or returns its time/iteration limit); otherwise
it starts phase one. Thus the current implementation can repeat substantial
feasibility work to obtain its trusted infeasibility certificate. This is a
source-supported explanation consistent with the replay counts, not a trace
proving the precise rejection reason in every captured call. The existing
`reopt.rejected` counter counts initial primal/dual eligibility rejection and
does not cover every later optimizer rejection.

The next focused hypothesis should test whether a candidate infeasibility
certificate from that dual row can be independently verified before falling
back to phase one. It must check finite arithmetic, all canonical columns,
inequality signs and a scaled strict contradiction, and preserve the existing
fallback whenever verification fails. Add exact/perturbed/ill-conditioned
tests, invalid-basis and budget checks, and MIN/MAX/free-variable coverage.
Do not accept the absence of an entering column by itself as proof.

First reproduce and instrument the exact rejection, then evaluate on the saved
fixtures with references outside measured search. Any verified private
infeasibility remains local. No private certificate can prune the original
MILP globally, and faster private work is not automatically better MILP
coverage. A new repeated screen must establish that separately.

This is a proposed next hypothesis, not implemented code, a promised speedup,
an assigned new iteration count or a solved lotsize result.
