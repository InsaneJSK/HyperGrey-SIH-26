# SIH26119 — MILP iteration 04: checked candidate repair

**Policy update:** no user run is needed for this CPU-only notebook. CPU
validation and iteration now run locally; Kaggle is used only for actual GPU
requirements. The original optional notebook instructions below are preserved.
The full local180-second comparison is now complete: blend2 reaches the
independently checked7.598985 optimum within numerical gap tolerance. See the
project's `reports/milp-iteration-04/LOCAL_VALIDATION.md`. This does not claim
that the optional notebook has run on Kaggle.

1. Import this small notebook (under 1 MB).
2. Upload the matching **SIH26119_V2_source.zip** as a **private Kaggle dataset**
   and attach it using **Add Input**. Any dataset name works; zipped/unpacked
   layouts are detected automatically.
3. Enable **Internet**. **GPU is not needed**: this MILP implementation runs on CPU.
4. **Run All**, or **Save Version → Save & Run All**. Allow about **20-25 minutes**.
5. Download **sih26119_milp_results.zip** from Output and send it back.

Compares the recovery + neighbourhood baseline against the same solver
with an opt-in dense candidate-repair fallback
on blend2, binkar10_1, and markshare_4_0. Each gets the SAME 180-second and
250,000-node limits. All failures remain visible, and candidates are independently
checked. A shorter local smoke run passed the generated correctness gate; hard
case results at these longer limits are now recorded separately from this
historical delivery in the local validation report.

There are only two code cells. No manual path edits or second environment.
This is separate from the previous QP/MILP notebooks and does not run the GPU
scale sweep. The companion ZIP is input data, outside the notebook size limit.

240 generated checks cover the baseline, repair mode and legacy control.
Both hard-run modes include the shared proof-safety fix: repairing a nearly
integer point does not prove that the entire node is solved. Rejected points,
fixed-integer LP results, fallback counts and checked incumbent traces are
saved in the output ZIP. Feasibility/integrality tolerances are unchanged.

Source SHA-256: 402e0c51b9684140cc7f7d41fc2cd44aea197c2f54b4e17b9829c225765dfab2
