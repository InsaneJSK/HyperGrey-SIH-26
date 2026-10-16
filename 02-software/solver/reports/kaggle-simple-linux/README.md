# Simplified notebook: actual Linux smoke run

The delivered two-cell notebook was executed on Ubuntu in WSL using a temporary
local test Python environment. This test environment is not part of the Kaggle
notebook: the notebook itself uses its current Python and does not create a venv.

Source snapshot: 847b82ddf16e2b36519c417b85f216c8a7978844e81618022be388ba4bc0f17b.
Python 3.12.3; GCC 13.3.0; CMake 3.28.3; CPU-only (no NVIDIA hardware).

Only two notebook settings were reduced for the local smoke test:
PUBLIC_TIME_LIMIT = 1 and SIZES = [1000]. The actual setup, pip installation,
build, validation and ZIP-export code was executed without command mocks.

Results: CTest 3/3; generated checks 230/230; Netlib 12/12; historical MIPLIB
2/4 under the reduced limit; QPLIB 2/3; additional MIPLIB 0/3; application
models 4/4; scale checks 2/2. All public failures remain recorded. This is
workflow/CPU verification, not GPU or general speedup evidence.

The exported artifact is LINUX_SMOKE_RESULTS.zip. It contains the notebook's
run logs, source manifest, snapshot hash, full validation evidence and status.
The delivered notebook has 30-second public limits and sizes 1,000, 100,000,
1,000,000, with one timing repetition for quick user feedback.
