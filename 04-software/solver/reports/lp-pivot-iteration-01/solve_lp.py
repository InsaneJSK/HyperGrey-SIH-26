"""Run one frozen opt-in continuous MPS LP profile with process containment."""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='Fresh output prefix; existing records are never replaced')
    parser.add_argument('--refined', action='store_true')
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error('--seconds must be finite and nonnegative')
    if args.model.suffix.lower() != '.mps':
        parser.error('This continuous LP profile expects an MPS file')
    profile = json.loads((BASE / ('REFINED_LP_PROFILE.json' if args.refined else 'LP_PROFILE.json')).read_text())
    binary = BASE / 'final_solver_cli.exe'
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == profile['binary_sha256'], 'Frozen executable changed'
    os.environ['PATH'] = str(BASE) + os.pathsep + os.environ['PATH']
    spec = importlib.util.spec_from_file_location('lp_containment', BASE / 'run_contained.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    command = [str(binary), str(args.model.resolve()), '--json', '--time-limit', str(args.seconds),
               '--iteration-limit', '10000', *profile['flags']]
    result = monitor.monitor(command, args.output, args.seconds + 15, 1536)
    print(json.dumps({key: value for key, value in result.items() if key != 'native_result'}, indent=2))


if __name__ == '__main__':
    main()
