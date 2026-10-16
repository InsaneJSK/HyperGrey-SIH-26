# Engineering controls and numerical assurance

SolveForge records the checks used to manage numerical, compute-resource and reproducibility risks.

| Control | Implementation or record |
|---|---|
| Original-model solution checks | [Numerical architecture](../../04-software/solver/docs/V2_ARCHITECTURE.md) and [validation guide](../../06-validation/README.md) |
| Reproducible source/input identities | [Benchmark reports and manifests](../../04-software/solver/reports/README.md) |
| API admission and resource controls | [Backend contract and limits](../../04-software/backend/README.md) |
| Explicit engine selection | [API configuration](../../04-software/backend/README.md) |
| Numerical profile evaluation | [LP safeguard report](../../04-software/solver/reports/lp-pivot-iteration-01/REPORT.md) and [MILP profile ablation](../../04-software/solver/reports/milp-iteration-37/REPORT.md) |
| Separate new runs and frozen evidence | [Execution policy](../../04-software/solver/docs/EXECUTION_POLICY.md) and [repository provenance](../repository/MIGRATION.md) |

The source-adjacent [technical scope record](../../04-software/solver/docs/V2_LIMITATIONS.md) provides detailed numerical and workload boundaries for implementation review.
