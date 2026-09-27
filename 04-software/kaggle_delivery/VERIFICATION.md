# Small-notebook delivery verification

Notebook: 11,492 bytes (about 11.5 KB), below the user's 1,000,000-byte limit.
Required companion input ZIP: 2,186,469 bytes (about 2.2 MB).
Source snapshot SHA-256:
6df478b347011bddb81af6950fbfec1a7c2557954c2fc4ccc0cea42a18f2bb6b

The source/data payload is no longer embedded in the notebook. Upload the
companion ZIP as a private Kaggle dataset and attach it using Add Input.
Use the updated notebook and ZIP together; an older ZIP will not match.

Verified in this revision:

- Notebook schema, both code cells and the under-1-MB size gate pass.
- Archive integrity and all 115 source/data/evidence hashes pass.
- All 22 numerical source/test files and CMake match the final CPU evidence.
- Twelve notebook tests pass: size, zipped input, unpacked nested input,
  missing/wrong input, changed-source rejection, CPU-only execution flow,
  cell rerun, GPU command selection, optional capability failure and
  installation/compiler/build/validation diagnostic-ZIP handling.
- Input extraction and hashes are actually checked; external build/validation
  commands in the control-flow tests are mocked, not GPU-validated.

The earlier embedded revision completed a real Linux CPU smoke run (230/230
generated checks and ZIP export). This exact small-notebook snapshot subsequently
completed on Kaggle/P100: 230/230 generated checks and 9/9 CPU/CUDA scale checks.
The returned source/runtime hashes match. The local project's
reports/kaggle-gpu-01/AUDIT.json and reports/KAGGLE_GPU_REPORT.md record the audit.
Only one timing pass was run; four hard public cases remain incomplete and
GPU-memory values were unavailable. The numerical core is unchanged.

Download the results ZIP from notebook output and send it back. Missing GPU
is clearly labeled CPU-only and never counts as GPU validation.
