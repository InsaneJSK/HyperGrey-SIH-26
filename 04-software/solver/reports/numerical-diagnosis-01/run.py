"""Run the six declared diagnostics serially; analyze only after all finish."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_binary_proof import sha, save


def main():
    out = BASE / 'results'
    out.mkdir(exist_ok=False)
    binary = ROOT / 'build-numerical-diagnostic-01/solver_cli.exe'
    runtime = json.loads((ROOT / 'reports/milp-iteration-29/RUNTIME_DEPENDENCIES.json').read_text())
    for name, digest in runtime.items():
        source = ROOT / 'reports/milp-iteration-29' / name
        assert sha(source) == digest
        shutil.copy2(source, binary.parent / name)
    os.environ['PATH'] = str(binary.parent) + os.pathsep + os.environ['PATH']
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    source = ROOT / 'reports/milp-iteration-29/run_contained.py'
    spec = importlib.util.spec_from_file_location('diagnostic_monitor', source)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    inputs = ROOT / 'reports/cpu-validation-2026-09-17/results/inputs'
    jobs = [('bandm.default', inputs / 'additional-lp/bandm.mps', []),
            ('bandm.refined', inputs / 'additional-lp/bandm.mps', ['--refine-basis', '--refine-at-checks']),
            ('bandm.compact', inputs / 'additional-lp/bandm.mps', ['--compact-equalities', '--refine-basis', '--refine-at-checks'])]
    jobs += [('9002.' + tol, inputs / 'qplib/9002.qplib', ['--tolerance', tol]) for tol in ('1e-7', '1e-10', '1e-12')]
    save(out / 'metadata.json', {'binary_sha256': sha(binary), 'source_identity_sha256': sha(BASE / 'SOURCE_IDENTITY.json'),
         'runner_sha256': sha(Path(__file__)), 'wrapper_sha256': sha(source), 'runtime': runtime,
         'models': {str(model.relative_to(ROOT)): sha(model) for _, model, _ in jobs},
         'scope': 'Logging-only diagnostics; no timing ranking.'})
    records = []
    for name, model, flags in jobs:
        result = monitor.monitor([str(binary), str(model), '--json', '--time-limit', '30', *flags], out / name, 45, 1536)
        records.append(dict(name=name, status=result['status'], iterations=(result['native_result'] or {}).get('iterations')))
        save(out / 'SUMMARY.json', records)
        print(name, result['status'], records[-1]['iterations'], flush=True)
    shutil.copy2(binary, BASE / 'diagnostic_cli.exe')
    print('All declared diagnostic solves finished.', flush=True)


if __name__ == '__main__':
    main()
