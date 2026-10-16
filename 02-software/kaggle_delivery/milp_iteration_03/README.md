# SIH26119 — MILP iteration 03: recovery + incumbent improvement

1. Import this small notebook (under 1 MB).
2. Upload the matching **SIH26119_V2_source.zip** as a **private Kaggle dataset**
   and attach it using **Add Input**. Any dataset name works; zipped/unpacked
   layouts are detected automatically.
3. Enable **Internet**. **GPU is not needed**: this MILP implementation runs on CPU.
4. **Run All**, or **Save Version → Save & Run All**. Allow about **20-25 minutes**.
5. Download **sih26119_milp_results.zip** from Output and send it back.

Compares the current control against opt-in LP recovery + neighbourhood search
(both retain fractionality branching)
on blend2, binkar10_1, and markshare_4_0. Each gets the SAME 180-second and
250,000-node limits. All failures remain visible, and candidates are independently
checked. A shorter local smoke run passed the generated correctness gate; hard
case performance at these longer limits is not yet established.

There are only two code cells. No manual path edits or second environment.
This is separate from the previous QP/MILP notebooks and does not run the GPU
scale sweep. The companion ZIP is input data, outside the notebook size limit.

240 generated correctness checks cover control, recovery-only, and the combined
mode. The six hard runs compare control against the combined mode. Failed tree
LP snapshots, recovery counts, checked incumbent history and unresolved-node
bounds are included in the result ZIP. Incomplete results remain incomplete;
this experiment does not promise a hard-case optimum or an overall speedup.

Source SHA-256: 1ba3309e1cb62c7508af66698dc53defa1f229a8bd4ec8de77f2dde9a0aba889
