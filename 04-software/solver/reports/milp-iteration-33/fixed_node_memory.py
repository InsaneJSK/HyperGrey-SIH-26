"""Peak process memory at a FIXED node count, old representation against new.

Same models, same flags, same number of nodes explored, so the only difference
measured is what an open node costs. Uses the iteration harness's own resource
monitor for the peak commit sample.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path('D:/sih-2026/SIH-backup-solver/SIH-backup-solver')
SCRATCH = Path('C:/Users/Admin/AppData/Local/Temp/claude/d--sih-2026-SIH-backup-solver/'
               '43a8b26f-0158-4c32-94e9-3eca7f17ed08/scratchpad/mem33')
spec = importlib.util.spec_from_file_location('contained', ROOT / 'reports/milp-iteration-32/run_contained.py')
contained = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contained)

OLD = ROOT / 'reports/milp-iteration-32/final_solver_cli.exe'
NEW = ROOT / 'build-milp-iter32/solver_cli.exe'
FLAGS = json.loads((ROOT / 'reports/milp-iteration-32/CANDIDATE_PROFILE.json').read_text())['recommended_flags']
MODELS = ['gen-ip054', 'mas74', 'markshare2', 'swath', 'lotsize', 'gt2']
NODES = sys.argv[1] if len(sys.argv) > 1 else '120000'
SCRATCH.mkdir(parents=True, exist_ok=True)


def find(name):
    for folder in sorted((ROOT / 'datasets').iterdir()):
        if (folder / (name + '.mps')).exists():
            return folder / (name + '.mps')
    raise SystemExit('not found: ' + name)


print(f"{'model':12s} {'cols':>6s} {'old MiB':>9s} {'new MiB':>9s} {'ratio':>7s} "
      f"{'old nodes':>10s} {'new nodes':>10s}")
for name in MODELS:
    model = find(name)
    row = {}
    for label, binary in (('old', OLD), ('new', NEW)):
        command = [str(binary), str(model), '--json', '--milp', '--time-limit', '300',
                   '--node-limit', NODES, '--gap', '1e-6', *FLAGS]
        record = contained.monitor(command, SCRATCH / f'{name}.{label}', 420, 4096)
        result = record['native_result'] or {}
        row[label] = (record.get('peak_commit_bytes', 0) / 2 ** 20, result.get('nodes'), result.get('columns'))
    (om, on, cols), (nm, nn, _) = row['old'], row['new']
    ratio = f'{om / nm:.2f}x' if nm else '-'
    print(f"{name:12s} {str(cols):>6s} {om:>9.1f} {nm:>9.1f} {ratio:>7s} {str(on):>10s} {str(nn):>10s}", flush=True)
