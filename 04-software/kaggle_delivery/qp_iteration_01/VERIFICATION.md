# QP iteration 01 delivery checks

- Notebook: 11,492 bytes, two code cells, below the 1,000,000-byte limit.
- Matching external source ZIP: 2,361,456 bytes; upload as private Kaggle input.
- Notebook schema/code parsed; all 140 source entries and 22 CPU core hashes verified.
- All 12 notebook flow tests passed, including zipped/unpacked input, reruns,
  CPU-only behavior and diagnostic ZIP paths. External commands are mocked in
  these tests: they do not establish a successful real Kaggle/CUDA execution.
- Retained local core passed 251 generated cases, 3 CTest groups, 7 independent
  certificate tests and all six CPU scale checks through one million variables.
- Original QPLIB 9002 independently passes relative KKT and diagonal-gap checks
  in three retained-binary repeats (4.19-4.81 s). Absolute violation is 2.3810;
  relative feasibility is 8.5718e-8. This is numerical, not exact, certification.
- Public reference-comparison QP score stays 2/3 because OSQP still times out
  on 9002; independently recomputed QP KKT score is separately 3/3.
- Modern MILP completed score remains 0/3. The binkar10_1 incumbent is retained.
- Earlier notebook/source/result bundles were not replaced.

Source SHA-256:
`f840453501c39a975d78cec449adb120690a3a9d0ff7d8df6d6a010f1327bf8e`

This NEW snapshot has no Kaggle/CUDA return yet. Enable GPU + Internet, attach
the matching ZIP, Run All, and send back `sih26119_kaggle_results.zip`.
