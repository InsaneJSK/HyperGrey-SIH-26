# Focused MILP delivery verification

Notebook size: **9,681 bytes**, below 1 MB. Two code cells.
Source input ZIP: 2,234,310 bytes; its data are not embedded in the notebook.
All 140 archive entries and 22 core-source hashes match the packaged CPU evidence.

Local checks: three CTest groups; 160 generated binary/mixed-integer cases across
both strategies; six equal-budget hard-case smoke runs. All four returned
incumbents independently passed original-model checks; no hard optimum is claimed.
Five tests of the actual notebook cells passed with external commands mocked,
including zipped/unpacked inputs, reruns, and diagnostic ZIP export on failure.
The initial Windows test-harness cleanup issue was corrected, not suppressed.

The longer Kaggle experiment has now been received and audited as
`reports/kaggle-milp-01`. All 160 generated checks pass and all four hard-case
incumbents pass fresh independent checks. No hard model was proved optimal;
both blend2 runs stopped early at an individual LP iteration limit. Reliability
is not an overall winner and remains opt-in. No unchanged rerun is needed.
This was CPU-only; it did not repeat the previous QP/GPU sweep.

Source SHA-256:
`a200a445026c9d27487fc69087b8765cd161aa22e9b4f95ee1e848d6ad3ee591`

Tested Windows CLI SHA-256:
`08e8022ba5d348f19b6b647aa255e3a50dd91d4c8a336f1250c71cb4b11700a5`

The established branching strategy remains the default. The notebook explicitly
compares it with the experimental strategy under equal limits before promotion.
Previous deliveries and their source ZIPs are unchanged.
