# Decisions and open questions

## Updated user decisions for V2

- Submission deadline: **30 September 2026**, confirmed in this task.
- GPU testing will use Kaggle. Deliver a separate upload-and-run notebook;
  preserve the local project as its own working version.
- The Kaggle notebook must contain the same source snapshot and return logs,
  correctness checks, CPU/GPU timings, hardware and hashes for final V2 evidence.
- Continue the solver, benchmark and documentation work already planned.

The older two-day assumption below applies only to V1 and is superseded.

## User decisions

- 2026-09-13: implement LP, MILP and QP in phases, test public datasets, report
  each phase, and continuously document remaining PS obligations and limitations.
- Downloads and separate established reference solvers are authorized.
- Treat the first submission as due in two days. The exact submission timestamp
  remains unknown; the planning target is approximately 2026-09-15, not a confirmed date.
- Hardware targets: 8-16 modern CPU cores, 32-64 GB RAM, optional NVIDIA GPU with
  8-16 GB VRAM, 20-50 GB storage. These are planning targets, not measurements of
  the machine used in the committed reports.
- No organizer clarification exists yet for general numerical-library use or
  a convex-only interpretation of the initial QP requirement.

## Implementation choices for the two-day V1

- C++11 core, no existing solver or numerical library linked into it.
- PowerShell build; Python orchestrates datasets, subprocesses and reports.
- Dense two-phase simplex is the LP/MILP baseline. Sparse revised simplex is
  postponed so LP, MILP and a declared QP subset can be demonstrated now.
- Sparse first-order QP: accelerated projected gradient for box-only problems;
  projected primal-dual iterations for linear constraints.
- LP/MILP reference: HiGHS 1.12.0, isolated subprocess.
- QP reference: OSQP 1.0.5, isolated subprocess; an independent Python reader
  preserves original QPLIB coefficients. HiGHS audits the official LP export;
  its default small-coefficient filtering changes the `9002` Hessian, so this
  export is not used as the final reference model. Earlier attempts are retained.
- Dataset selections are explicit smoke/stress subsets. Do not describe them as
  full-library coverage or representative performance benchmarks.
- No GPU or multicore speedup is claimed. No live industrial deployment is claimed.

## Questions still requiring outside information

1. Confirm the actual submission date/time and judging expectations.
2. Ask MRPL whether BLAS, sparse factorization packages, CUDA and cuSPARSE are
   permitted as general numerical infrastructure. We have not contacted MRPL.
3. Confirm whether convex QP is acceptable for the first demonstration. V1 does
   not implement global nonconvex QP optimization.
4. Identify actual final benchmark hardware and access arrangements.
5. Obtain an open-literature or MRPL-approved industrial case with meaningful
   operational constraints. Current demos are explicitly synthetic illustrations.
6. The user confirms that the supplied PS itself ends its dataset paragraph at
   "Where industrial da"; this is not a missing user attachment. A 2026-09-14
   web search found no verified continuation. Any omitted requirement remains
   unknown; see [source verification](PS_SOURCE_CHECK.md).
