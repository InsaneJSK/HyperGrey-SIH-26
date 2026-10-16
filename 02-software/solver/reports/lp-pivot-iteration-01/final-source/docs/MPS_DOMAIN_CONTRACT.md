# MPS integer-domain contract and iteration11 correction

The reader must solve the intended MPS model, not a looser model whose solution
then passes checks against the same incorrectly parsed bounds.

## Reproduced correctness defect

Before iteration11, every new column started at [0,+infinity], even integer
columns introduced between INTORG/INTEND markers with no bound record. The
documented marker convention is [0,1] when that variable has no bound record.
[IBM's integer-MPS documentation](https://www.ibm.com/docs/en/icos/22.1.1?topic=extensions-integer-variables-in-mps-files)
and the independent HiGHS 1.12.0 reader support this distinction.

With a marked X, no bound record for X, row X <= 7, and objective minimize -X,
the old build returned X=7/objective -7 and `optimal`. The correct default
domain permits X=1/objective -1. Adding a bound only for another column still
leaves X binary. This is a model-interpretation correctness bug, not a slow solve.
The [baseline reproductions](../reports/milp-iteration-11/marker-baseline/results.json)
retain all 28 tests: four fail, including both objective senses.

## Correction

Track whether each variable has any explicit BOUNDS entry. At the end of MPS
reading, integer columns with no such entry receive upper bound 1. Existing
explicit-bound handling is unchanged: for example, an explicit LO-only entry
uses the ordinary unspecified upper bound of +infinity. A BOUNDS section or
record for another variable must not affect X's defaults. Continuous columns
retain [0,+infinity]. Programmatic C++ model domains are not changed.

The independently implemented original-literal proof reader applies the same
documented convention. Its tests independently exercise marker-only exact
proofs, column-local bound records and explicit-LO semantics. HiGHS comparisons
avoid relying only on two implementations sharing an interpretation.

## Permanent gates and limits

The ninth CTest group covers all 14 domain configurations in min/max mode,
both normal and proof-enabled solves, and direct parsed-bound assertions.
It also covers a marker-domain infeasible case, a no-row bounded case and
rejection of unsupported/nonfinite/unknown-column input. The standalone
independent reference suite improves from 24/28 to 28/28 passing tests.

This fix is always active in iteration11; it is not an optional heuristic.
Older binaries remain immutable historical evidence and must not be advertised
as correct for this affected syntax. It does not automatically invalidate
previous results on explicitly bounded inputs, nor establish correctness on
all MPS dialects. Multiple objective/RHS/bound sets, semi-continuous/SOS/
indicator extensions and ambiguous negative-upper-only cases remain outside
the supported reader subset and are rejected, not silently interpreted.

Reproduce against a fresh output directory:

```powershell
C:/Users/Admin/anaconda3/python.exe -X utf8 scripts/check_mps_marker_contract.py --binary build-milp-iter11/solver_cli.exe --output reports/my-marker-check --require-pass
ctest --test-dir build-milp-iter11 --output-on-failure
```
