# Simple Kaggle delivery

This exact source snapshot has now completed an audited P100 run. All three
synthetic CUDA scale cases passed. See the local project's
`reports/KAGGLE_GPU_REPORT.md`. No need to repeat this unchanged run solely to
return evidence; the original ZIP has been imported and preserved.

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

The solver source is unchanged and separate from the local Windows project.
Selected CUDA execution is verified by the first returned Kaggle run. Repeated
performance, broader GPU coverage and GPU-memory diagnostics remain follow-up work.

Source SHA-256: 6df478b347011bddb81af6950fbfec1a7c2557954c2fc4ccc0cea42a18f2bb6b
