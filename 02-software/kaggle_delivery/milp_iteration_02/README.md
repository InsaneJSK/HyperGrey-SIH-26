# SIH26119 — focused hard-MILP experiment

1. Import this small notebook (under 1 MB).
2. Upload the matching **SIH26119_V2_source.zip** as a **private Kaggle dataset**
   and attach it using **Add Input**. Any dataset name works; zipped/unpacked
   layouts are detected automatically.
3. Enable **Internet**. **GPU is not needed**: this MILP implementation runs on CPU.
4. **Run All**, or **Save Version → Save & Run All**. Allow about **20-25 minutes**.
5. Download **sih26119_milp_results.zip** from Output and send it back.

Compares current fractionality branching and experimental reliability branching
on blend2, binkar10_1, and markshare_4_0. Each gets the SAME 180-second and
250,000-node limits. All failures remain visible, and candidates are independently
checked. A shorter local smoke run passed the generated correctness gate; hard
case performance at these longer limits is not yet established.

There are only two code cells. No manual path edits or second environment.
This is separate from the previous QP/MILP notebooks and does not run the GPU
scale sweep. The companion ZIP is input data, outside the notebook size limit.

Source SHA-256: a200a445026c9d27487fc69087b8765cd161aa22e9b4f95ee1e848d6ad3ee591
