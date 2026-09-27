# MILP iteration 01 delivery verification

- Notebook: 11,492 bytes, below the 1,000,000-byte limit; two code cells.
- Companion source ZIP: 2,213,886 bytes, attached as private Kaggle input,
  not embedded in notebook/kernel code.
- Notebook schema/code syntax, ZIP integrity and 128 file hashes verified.
- All 22 numerical source/test files match the retained CPU evidence.
- Retained C++ binary: 3/3 CTest; 230/230 generated tests; 12/12 Netlib,
  4/4 historical MILP, 2/3 QPLIB, 0/3 completed modern MILP, 4/4 application
  cases, and 6/6 CPU scale checks through one million variables.
- Actual notebook cells: 12/12 control-flow tests passed, including missing or
  wrong input, build/install failure ZIP export, CPU fallback and reruns.
  External commands were mocked: these are not CUDA execution tests.
- Result parser: 3/3 tests passed. GPU-memory sampler: 6/6 mocked tests passed.
- Previous V2 notebook/source ZIP still match the archived Kaggle baseline.

Source ZIP SHA-256:
`f9b8a366cbdf6d0cf216c21307d9439515e6f46c52d2ad22b612b94e5e29b1d8`

This snapshot has now run successfully on Kaggle/P100. The returned ZIP was
audited as reports/kaggle-gpu-02: all 230 generated and nine scale configurations
passed, including three CUDA cases. The binkar10_1 incumbent was independently
verified, found at 13.79 seconds with an 8.75% gap at the 30-second limit.
The same four hard problems remain incomplete. No unchanged rerun is needed.
The notebook/source ZIP files were not changed by this audit.

Improvement: the retained binary found a valid binkar10_1 incumbent in three
local runs, with gaps around 8.8%. It has not proved that optimum. blend2 still
has no incumbent, markshare_4_0 still has a large gap, and QPLIB 9002 is pending.
