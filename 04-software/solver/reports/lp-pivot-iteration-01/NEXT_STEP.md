# Next bounded work

1. Keep `--stable-primal-ratio` off by default. The two 16-LP profiles pass;
   default bandm remains a recorded failure and no new broad MILP score exists.
2. Before promoting the option, select a further LP set covering additional
   sparse, scaled, equality/ranged and degenerate structures. Test transformations
   and both primal/warm paths. Declare MILP controls and budgets separately if
   evaluating integer search; do not assume an LP gain improves MILP outcomes.
3. QP 9002's tight specialist runs show many tiny accepted steps and oscillating
   feasibility, not zero inner solves. Capture actual objective increments,
   slope, Armijo allowance, PCG convergence and active-set changes. First test
   whether the line-search allowance contributes; keep the model, shared time
   slice, fallback and final acceptance unchanged. Do not combine several fixes.
4. Preserve 9002's current relative certificate, absolute residual and OSQP
   timeouts. Tighter solver tolerances have not established operational accuracy;
   get domain units/requirements before making that claim.
5. Continue the independently checked industrial what-if and concise CLI/API
   demo, then prepare the supported box-QP GPU package for Kaggle. Broader
   completion, matched-accuracy performance and final package rehearsal remain.

No new guaranteed iteration count, universal solver coverage, speedup or
submission-ready claim is made. Preserve failed refresh and original ratio
candidates, initial validation classification and all raw evidence.
