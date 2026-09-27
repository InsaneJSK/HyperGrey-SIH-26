# Opt-in weak-pivot ratio safeguard: integration and validation

Declared after the isolated diagnostic/candidate studies, before measuring
the integrated executable. The selected policy is the selective two-pass
ratio choice documented in `../numerical-diagnosis-01/LP_SELECTIVE_HYPOTHESIS.md`.
The working engine adds `--stable-primal-ratio`, default off, without diagnostic
logging. No basis-refresh candidate, QP change or other numerical policy is
combined. The option can reach MILP relaxations but is not yet a recommended
MILP profile or a demonstrated search-performance improvement.

1. Build the complete current tree in a fresh directory with the matching
   local GCC 14.2 toolchain. Copy verified runtime DLLs beside the executables.
2. Test ratio choices at weak/strong/sole pivots, ties, absent leaving rows,
   nonfinite directions and Bland fallback; check 512 generated step-feasibility
   cases. Recheck the retained LP in default, refined, MAX and compact modes,
   including zero deadline/iteration budget. Do not import reference answers
   into measured solves; the recorded optimum is a test assertion only.
3. Run the full gate: CTest, Python checks, original-model fixture references,
   feature-off frozen parity, all generated/exhaustive MILP checks. Add a
   stable-only generated profile and enable the safeguard in the three refined
   profiles. Assert the output option marker matches every invocation.
4. On the final binary, run all 16 public LPs with the stable option alone and
   with refinement, plus default control calls on bandm and an unchanged compact
   call. Use 30 seconds, 10000 pivots, a 45-second watchdog and the existing
   original-model validation contract. Own solves run serially, then references.
5. QP numerical sources must remain byte-identical to frozen 29. Recheck the
   three original default QPs on this exact binary with original-model KKT/
   applicable diagonal checks, preserving QP 9002's relative/absolute limits.
   Do not rerun OSQP 9002 merely to generate another timeout or claim a speedup.

Only if these pass, freeze the opt-in LP profile, source, binary, dependencies,
raw evidence and limitations. Defaults remain unchanged. A broad MILP timing
study and a larger independent LP set are required before wider promotion;
the small LP improvement is not a new 27-model MILP score.
