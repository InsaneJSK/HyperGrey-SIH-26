# Reference-output audit after the final CPU run

The numerical solver and original CPU evidence are unchanged. The HiGHS 1.12.0
worker for blend2 exited with code 0 and emitted one JSON result reporting
`Optimal`, objective `7.598985`, followed by two native diagnostic lines:

```text
HighsMipSolverData::transformNewIntegerFeasibleSolution tmpSolver.run();
HighsMipSolverData::transformNewIntegerFeasibleSolution tmpSolver.run();
```

The old whole-stdout JSON parser therefore recorded `process_error`. The
corrected `parse_json_output` in `scripts/benchmark_lp.py` accepts exactly one
JSON status object amid diagnostic lines, retaining those lines in
`stdout_diagnostics`. Missing or ambiguous multiple results still fail parsing.
`scripts/validate_v2.py` now uses the same parser.

`scripts/test_result_parser.py` exercises plain/pretty JSON, diagnostic text,
missing JSON and ambiguous multiple objects. The actual saved blend2 output was
also checked with the fixed parser. Its recovered status and objective match
the JSON above. Our own blend2 solve remains `time_limit` without an incumbent;
the public score remains 0/3 for the additional MIPLIB selection.

Original unmodified evidence: `../v2-final-cpu/miplib2017/blend2.reference.json`.
This audit is a reporting correction, not a new numerical run.
