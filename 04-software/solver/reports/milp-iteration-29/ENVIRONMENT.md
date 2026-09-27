# Execution and retained harness failures

Use the project-local x64 GCC14.2 toolchain documented in iteration25.
Fresh builds are `build-milp-iter29-diagnostic` and `build-milp-iter29`.
No GPU, global installation, upload or external message is involved.

The initial candidate build exposed a missing self-contained header include;
`candidate-build.log` retains the compiler failure. The corrected build and
focused checks are retained in subsequent numbered logs.

The first replay harness incorrectly asserted that every saved warm fixture
needed one preliminary pivot. The expensive capture needs one, while the
failed capture needs zero. The first output and assertion remain under
`candidate-checks`; `candidate_gate.initial.py` preserves the assumption.
The corrected harness checks against each frozen diagnostic event's actual
pivot count. No numerical implementation changed for that correction.

Two full-gate launches and a direct CTest launch failed during Windows DLL
loading (0xc0000022 / 0xc000007b), before the affected numerical tests ran.
An isolated direct launch of the same certificate executable succeeded from
both source and build directories. Copying the five matching runtime DLLs
beside all candidate executables resolved the CTest failures. Their hashes
are in `RUNTIME_DEPENDENCIES.json`. No frozen historical binary was changed.
The resulting CTest run passes all26 groups; `gate-local-runtime` contains
the complete successful correctness gate, including176 Python tests,
320 generated runs,100 retained exhaustive cases and disabled parity.

The diagnostic timing includes logging, so its pivot counts are evidence of
work avoided; no elapsed-time speed ratio is inferred. The repeated screen
runs serially with the iteration28 Windows watchdog,45-second outer timeout,
1536MiB sampled commit threshold and20ms memory sampling. It retains wrapper
records separately from native solver results. These limits are cooperative
or sampled; this is not a hard allocation or real-time guarantee.
