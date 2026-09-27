# Iteration09: compact equality LPs and proof-gap work

User requests further progress toward proving Binkar, not a relabeled small gap.
Preserve iteration08 and test an opt-in compact equality representation in the
LP core: one equation with an unrestricted dual multiplier, instead of two
inequalities. Binkar has1016 equality rows. Do not remove constraints or relax
tolerances. Artificial variables belong only to Phase I and cannot enter Phase
II/warm bases. Equality rays must satisfy both signs. Rank/numerical rejection
can fall back to the original formulation within the same remaining budget.

First run analytical/adversarial/generated checks, then equal-budget local
comparisons and independent original-model/cut audits. Attempt a longer proof
run if the compact representation gives useful progress. Neither a timeout nor
a reference incumbent is called an optimum. CPU only; no Kaggle or user upload.
