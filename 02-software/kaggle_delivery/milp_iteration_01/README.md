# Simple Kaggle delivery

Import **SIH26119_V2_Kaggle.ipynb** (under 1 MB).
Upload the NEW **SIH26119_V2_source.zip** as a **private Kaggle dataset**, then
attach that dataset to the notebook using **Add Input**. Any dataset name works.
Select GPU + Internet, and Run All.
You can also use Save Version → Save & Run All.
Download **sih26119_kaggle_results.zip** from Output and send it back.

There are only two code cells: unpack, then run. No second virtual environment
or manual path changes. Uses the current Python and standard pip/subprocess.
The companion source ZIP is REQUIRED. It is input data, not notebook/kernel
code, so its approximately 2.2 MB size is kept outside the notebook size limit.
The notebook detects either the ZIP or its extracted files automatically.

This quick run uses one timing repetition per size/configuration. It keeps all
public results and tests sizes 1,000, 100,000 and 1,000,000. It does not establish
repeatable GPU speedups. Missing GPU/compiler is clearly labeled CPU-only.
Installation/build/check errors are captured in a diagnostic ZIP. Send that ZIP
too; don't spend time repairing the notebook yourself.

This source snapshot is separate from the local Windows project. It passed
the generated CPU regression gate linked in SNAPSHOT_INFO.json. Public hard
cases can remain incomplete; see the included evidence, not just the exit code.
This snapshot's Kaggle/P100 return is now audited in reports/kaggle-gpu-02.
The notebook and source ZIP remain unchanged. See VERIFICATION.md; no unchanged
rerun is needed. Hard-case completion and repeated timing studies remain pending.

Source SHA-256: f9b8a366cbdf6d0cf216c21307d9439515e6f46c52d2ad22b612b94e5e29b1d8
