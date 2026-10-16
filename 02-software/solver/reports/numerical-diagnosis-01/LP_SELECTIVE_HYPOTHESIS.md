# Apply the stable ratio rule only to a weak selected pivot

The full two-pass candidate completes all 18 declared LP observations with
independent original-model checks, including bandm default/refined. It also
changes the pivot trajectories of most already-successful LPs. Before choosing
a production change, test a narrower variant from the original source.

Keep the existing minimum ratio selection unless its selected positive pivot
is at most 1e-7 * (1 + ||direction||_inf). Only then, outside Bland fallback,
use the same two-pass stable selection from the preceding candidate. This
retains ordinary strong-pivot choices. No eta refresh, factorization change,
new tolerance or model-specific branch is combined with the policy.

Run the same 18 checked LP observations. If this completes bandm while retaining
existing strong-pivot paths, prefer this narrower correction for integration.
Require a focused numerical regression and the full correctness gate before
any final profile evaluation. Retain both earlier candidates and their outcomes.
