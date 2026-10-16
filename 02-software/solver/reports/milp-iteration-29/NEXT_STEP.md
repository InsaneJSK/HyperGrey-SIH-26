# Evidence-selected next work

The verified-row hypothesis is implemented and its narrow arithmetic contract
passes. The two repeated lotsize runs avoid private phase one and produce 37
and 34 checked private LP points, versus 11 and 7, but neither finds an integer
solution. The candidate does not merit a default change or another broad
MILP batch merely because it reduces local LP work.

1. Current-source validation is complete: 12 retained LPs pass both profiles,
   three of four additional LPs pass, and all three default QPs pass relative
   KKT checks. A separate compact/refined profile completes 16/16 LPs.
   See [the LP/QP report](../cpu-validation-2026-09-17/REPORT.md) and
   [LP profile study](../lp-bandm-01/REPORT.md).
2. Trace the retained default `bandm` numerical failure and QP 9002 accuracy
   floor/fallback as the next continuous numerical work. Both tighter QP
   probes time out and fail independent checks. Keep small-sample results
   separate from scale or operational claims; obtain domain tolerances before
   claiming 9002's absolute residual is acceptable.
3. Before another MILP timing cycle, capture the remaining lotsize private
   trajectory under fixed work: accepted steps, rejected directions, remaining
   fractional variables, parent ownership and why the slice ends. Determine
   whether time, the 64-step cap, or ineffective integer decisions bind. More
   steps alone do not justify a larger slice.
4. If a budget hypothesis follows, redistribute the SAME total budget and
   compare repeated outcomes on protected feasibility/completion/quality cases.
   Do not infer a certificate-caused binkar regression: that path is unused
   there. Its time-dependent search quality needs its own controlled diagnosis.
5. Advance industrial what-if demonstration, final package/API instructions,
   matched-accuracy performance work and a CPU-validated GPU-only notebook as
   separate tracks. GPU execution requires NVIDIA Kaggle; no CPU upload is
   pending. Domain data/feedback and organizer deliverables/cutoff remain inputs.

No additional iteration count, universal MILP coverage or competition result
is promised. Keep the new feature off until a future declared experiment
establishes its practical value with acceptable counterpart behavior.
