# Iteration17 — sparse basis accuracy, CPU only

Frozen control: iteration16, unchanged. Retained fixture:
`../milp-iteration-16/mas74-diagnosis/captured-relaxation.mps`, SHA256
`3de0d967366662e95d8918c68b5cca7b077459d386c9cdb27525faa1a1e81339`.

1. Diagnose the basis RHS and transpose residuals before and after correction
   and fresh factorization. Preserve diagnostic source and output.
2. Implement the smallest supported numerical correction, retaining all valid
   bounds, tolerances, pivot limits, fill limits and total recovery allowances.
   No cut/restart policy changes. Keep final primal/dual verification.
3. Retained cold and original warm-basis replay, transformed min/max LPs,
   deterministic degeneracy/singularity, infeasible/unbounded, resource and
   interruption tests. Existing CTest and Python suites, generated MILPs.
4. Local mas74 paired screen, then 24 development cases at 30s each. These are
   development models, not fresh holdouts. Preserve failures and independently
   check original-model points and proof bookkeeping. New holdouts are a
   separate gate before broad performance promotion.
5. Freeze source, binary, raw outputs, checks, and a candid submission report.

No claim to solve every public MILP or guarantee submission rank. A numerical
repair on this fixture is distinct from an optimality proof for full mas74.
