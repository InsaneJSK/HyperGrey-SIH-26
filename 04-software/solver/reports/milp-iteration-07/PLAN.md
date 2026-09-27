# Local iteration07: guarded exact proof completion

Baseline is the immutable iteration06 build-milp-iter6b, CLI SHA256
65686ab54dd8e073989f9a93f9e75bbb8d06ba4143b1ca6d639307360f7d007a.
Its floating-point binary-meet search is an incumbent heuristic only.

Implement a SEPARATE opt-in --binary-proof path using checked signed integer
arithmetic on a strict subset of the parsed model. Do not reuse a tolerance-
feasible incumbent as an exact cutoff. Require complete bounded enumeration,
exact witness reconstruction and original-model checks before publishing a
global optimality/infeasibility conclusion. Interrupted, out-of-range or
unsupported cases contribute no proof bound. Preserve existing default behavior.

Validate by exhaustive small models, adversarial arithmetic/domain/deadline
tests, independent literal-MPS/integer checks and local public models. Include
markshare_4_0 and the existing historical p0033 model if structurally eligible.
Do not claim arbitrary-precision input parsing or general MILP certification.
Run all CPU work locally; no GPU/Kaggle changes or user upload are required.
