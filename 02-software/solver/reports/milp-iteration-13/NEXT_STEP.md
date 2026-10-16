# Next local cycle — feasibility progress and controlled work budgets

Keep iteration13, all 21 public inputs and every observed failure/limit. Do not
promote raw priority or lattice bounds as a universally better default. The
raw policy restores gt2's better incumbent in the repeated comparison, but
the 17-case wave has no completion-count gain and several worse partial gaps.

## Highest-value diagnosis before another algorithm change

Short-budget progress is now a concrete weakness. Both wave policies leave
Blend2, Binkar and misc07 without an incumbent. On Binkar both stop after one
main node, three heuristic solves and two pump projections, with no late
restart. These counters do not isolate where all the elapsed time went.
The desktop also showed large timing changes at identical egout work counts.

Add low-overhead phase/work attribution: root LP, feasibility pump, dives,
candidate repair, branching LPs, restart, validation, and unaccounted overhead.
Use bounded diagnostic captures outside performance measurements. Check how
time limits propagate into each nested routine, including expensive setup and
factorization. Test immediate interruption and truthful no-incumbent/partial
results. Do not solve timing noise by loosening accuracy or extending only the
candidate's budget.

Then predeclare a work-budget-controlled feasibility experiment. Reserve main
tree work by limiting heuristic effort using work counters as well as time;
retain the existing strategy as control. Distinguish a better feasible point
from a stronger global bound. Clock-triggered restarts should have a separate
deterministic test mode exposed safely for repeatable ablations. No case-name
dispatch or external solutions. The new holdouts add lotsize and eil33-2
no-incumbent outcomes and open gaps of about 3% on gen-ip002 and 18% on
assign1-5-8. Those outcomes must inform this
diagnosis, but those four cases become development cases after this iteration;
they cannot be relabeled as untouched in a later tuned test.

## Proof and robustness work still required

- Strengthen weak mixed-integer relaxations with independently validated cuts
  or branching changes only after isolating the bottleneck. Lattice rounding
  alone leaves large gaps on gt2, misc03, pk1 and other cases.
- Extend beyond saved frontier bookkeeping toward independently checkable LP
  bounds, infeasibility and branching coverage. Current general certificates
  are numerical; the exact binary engine remains a restricted class.
- Add process memory instrumentation/limits and failure-preserving larger waves.
  The existing dense-fallback cell guard is not a total memory cap.
- Keep parser, min/max, objective-offset, free/negative domain, malformed-input,
  numerical stress and metamorphic regressions. Preserve every counterexample.
- After freezing a new candidate, choose additional untouched public models by
  structure/size before results, with a declared resource envelope. Report
  completion, checked-point, no-point, numerical, parser and resource outcomes
  separately. Do not extrapolate 21 tested models to all 240 benchmark members.

For submission, a checked near-optimal industrial example, domain review,
repeated applicable final GPU evidence and a reproducible CLI demonstration
remain necessary. None of those justify claiming arbitrary MILP exact proof
or a top-0.1% rank. CPU investigation continues locally; no Kaggle upload or
new user result ZIP is required for this next cycle.
