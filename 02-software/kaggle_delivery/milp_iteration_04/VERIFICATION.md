# Verification — MILP iteration04

User policy update15 September2026: this CPU-only notebook does NOT need to be
run. Longer CPU validation/iteration runs locally; Kaggle is reserved for actual
GPU requirements. The files below are preserved optional/historical artifacts.

- Notebook:10,335 bytes, two code cells, below1,000,000 bytes.
- Separate private-input source ZIP:2,669,023 bytes; not counted as notebook/kernel code.
- Source SHA-256:`402e0c51b9684140cc7f7d41fc2cd44aea197c2f54b4e17b9829c225765dfab2`.
- Notebook schema/AST, ZIP CRC/path checks and all653 archive-manifest entries pass. All22 numerical/test files match selected final CPU evidence.
- Five actual-cell mocked flow tests pass: zipped input, unpacked input, rerun, build-failure ZIP, validation-failure ZIP. These do not claim an actual Kaggle run.
- Result parser tests3/3; CTest groups3/3; generated MILP checks240/240 across baseline, repair and legacy control.
- New proof regression reproduces a false-optimality edge case in the preserved previous binary and verifies its correction in both current comparison modes.
- Final90s blend2 pair: baseline no incumbent; repair finds8.015188 at58.43s, with5.0051% gap. Independent original-MPS violation2.2737e-13, integrality violation0. No optimum completion.
- Final15s all-model pairs: same markshare~21 and binkar6810.690026 in both modes; blend2none at this short limit. Four checked candidates, no unsafe/error run.
- CPU-only; Internet required; no GPU, `nvidia-smi`, second environment or manual path edits.
- No Kaggle execution of this snapshot is claimed or requested. The longer local CPU validation is complete; see the project's reports/milp-iteration-04/LOCAL_VALIDATION.md. Notebook/source ZIP contents are unchanged.

Previous builds, notebooks, source ZIPs and audited returns remain preserved.
The new comparison baseline shares the proof-correctness fix and diagnostics;
only optional dense candidate repair differs. No generalized speedup,
industrial completeness, or submission ranking is claimed.
