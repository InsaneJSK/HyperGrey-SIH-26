# Reserved-search experiment: retained, not promoted

Binary: `reserved_solver_cli.exe`, SHA256
`8bcdf69bb0e5b14645615ff738e0970324aac5920df8efe5b13cf61eae1c8e55`.
Source: `reserved-source/`. Build: `build-milp-iter6` (do not rebuild).
Raw evidence: `local-180s/`; independent audit: `local-180s-audit/AUDIT.json`.

One sequential180s/250000-node run per mode/model, alternating order;30s
reference solves afterward. No GPU or reference solutions in the core.

| Model | Guided | Reserved coupled search |
| --- | --- | --- |
| markshare_4_0 | objective~5, node_limit,117.51s | objective~5, node_limit,121.41s |
| blend2 | objective8.015188, time_limit180.07s | objective7.598985, gap_limit135.01s |
| binkar10_1 | no incumbent, time_limit180.20s | objective6810.690026, time_limit180.17s |

All five returned final candidates pass independent original-model checks. The
audit verifies28 available final/center/neighborhood/repair vectors, original
feasibility/integrality, accounting, scheduling and source/model/binary identity.
CTest3/3, generated240/240 and15 diagnostic tests passed. Eighty generated guided
outputs exactly match iteration05, excluding timing and additional diagnostics.

The markshare reservation works: coupled calls at approximately0.28,72.00,74.81
and117.00s. The first improves73 to46; the later calls work around8 and5, but
the final objective remains5. All four hit512 local nodes in0.14–0.31s, using
little of their allowed time. This exposed search depth/structure as a further
limit rather than call availability.

On binkar, each strong call explored only one LP before its time slice expired.
The new neighborhood did not improve6810.69. This is worse than the best earlier
guided result6747.31 and does not justify changing defaults.

Performance caveat: the fresh guided blend2 and binkar runs did not reproduce
their best earlier results. A short read-only CPU sample during the run showed
other applications consuming substantial CPU (including Chrome and Node).
Applications and power settings were not changed. This is evidence of concurrent
activity, not a quantitative attribution of the slowdown. The timing pass is
not an isolated/repeated speedup benchmark. Preserve both failures and results.

The following structural meet-in-the-middle experiment has separate source,
binary and output identity; do not attribute its improvement to reserved search.
