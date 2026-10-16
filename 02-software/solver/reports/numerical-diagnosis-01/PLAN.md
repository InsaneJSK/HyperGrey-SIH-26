# Retained LP rejection and QP accuracy diagnosis

Declared 17 September 2026 before these diagnostic measurements. Preserve
iteration 29 and the continuous-validation checkpoint unchanged. No reference
point, multiplier or bound enters our engine.

Use an isolated source copy with logging only. Trace failed LU factorization,
small pivot choices and primal-infeasibility rejection on the original `bandm`
fixture. Run default, refined-at-checks and compact/refined configurations, each
with 30 seconds, the existing 10000-pivot cap and a 45-second process watchdog.
Retain the exact basis matrix/RHS for any failure. Independently inspect rank,
residuals and numerical conditioning before proposing a recovery mechanism.

For original QPLIB 9002, trace the diagonal-equality specialist's Newton/PCG
progress, termination and dispatch to ADMM at tolerances 1e-7, 1e-10 and 1e-12.
Each dispatch has the unchanged 30-second shared budget and 45-second watchdog.
Retain any specialist point before fallback and independently check original
KKT and absolute feasibility afterward. Logging runs diagnose arithmetic/work;
they do not establish a speedup or substitute for the frozen measured results.

Run all own configurations serially and independent analysis afterward. The
source is unchanged apart from diagnostic output. After finding a cause,
declare one bounded corrective hypothesis and its tests before editing the
working engine. No default promotion, extra solve budget, relaxed acceptance,
GPU execution or universal robustness claim follows from this diagnosis.
