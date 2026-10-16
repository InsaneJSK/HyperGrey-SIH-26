# Delivery verification — MILP iteration 03

- Notebook: 10,356 bytes (10.4 kB), below the 1,000,000-byte limit; two code cells.
- Matching external input ZIP: 2,353,620 bytes. This is Kaggle input data, not kernel code.
- Source SHA-256: `1ba3309e1cb62c7508af66698dc53defa1f229a8bd4ec8de77f2dde9a0aba889`.
- Notebook schema and both Python cells parse; archive CRC, paths, manifest and all 176 source entries pass. All 22 numerical/test source files match final CPU evidence.
- Five actual-cell mocked flow tests pass: zipped input, unpacked input, rerun, build-failure diagnostic ZIP, and validation-failure diagnostic ZIP. These are not claimed as actual Kaggle execution.
- Result parser: 3/3 tests pass. CTest: 3/3 groups pass.
- Final-source generated correctness: 240/240 checks across control, recovery-only and combined modes, repeated successfully for the extended check.
- Final 15-second hard pairs: four independently verified candidates; no unsafe/error run. binkar control7297.320029 versus combined6810.690026. No hard optimum completion.
- Final 90-second blend2 pair: control exits at its LP cap; combined continues to global time limit, recovers3/3 LPs, retains2 unresolved nodes, but still has no valid incumbent.
- CUDA is intentionally disabled. No GPU quota or `nvidia-smi` is required.
- Update 15 September 2026: this exact source has now run on Kaggle and is audited in `reports/kaggle-milp-02`. CTest3/3, generated240/240 and four fresh independent candidate checks pass. binkar improves7297.320029 to6747.310015, gap8.6623% to1.2257%; blend2 recovers5/5 LPs but still has no incumbent; markshare final objective is unchanged. No rerun of this unchanged notebook is needed.

Earlier local builds, Kaggle deliveries, and returned result archives remain separate.
The source ZIP includes the detailed report, final-source checks and distinctly
labeled initial experiment, including its numerical-error result. Experimental
options remain opt-in; no general speedup or industrial-completeness claim is made.
