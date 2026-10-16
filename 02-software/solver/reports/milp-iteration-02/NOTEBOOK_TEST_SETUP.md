# Notebook-flow test cleanup issue

The first five mocked notebook-flow tests reached Windows temporary-directory
cleanup while their process was still inside that directory. Windows rejected
removing the active working directory. The test harness now restores its old
working directory before cleanup, including assertion-failure paths.

This was a test-harness cleanup error, not a solver or notebook execution error.
No optimization logic, limits or notebook cells changed to fix it. The delivery
was rebuilt after the harness correction; the final test result is recorded in
the delivery verification file.
