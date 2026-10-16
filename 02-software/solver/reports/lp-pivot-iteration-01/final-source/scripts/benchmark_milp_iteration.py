"""Sequential, paired MILP experiments; never feed reference solutions to our core."""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import sys

from benchmark_lp import ROOT, run


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--variant', nargs=2, action='append', required=True, metavar=('LABEL', 'BINARY'))
    parser.add_argument('--models', nargs='+', default=['p0033', 'enigma', 'flugpl', 'stein27', 'markshare_4_0', 'blend2', 'binkar10_1'])
    parser.add_argument('--limit', type=float, default=30)
    parser.add_argument('--reference-limit', type=float, default=30)
    parser.add_argument('--repeats', type=int, default=1)
    parser.add_argument('--ablation', action='store_true', help='Add --no-pump variant of the last binary')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    variants = [(label, Path(binary).resolve(), []) for label, binary in args.variant]
    if args.ablation:
        label, binary, _ = variants[-1]
        variants.append((label + '_no_pump', binary, ['--no-pump']))
    if len(set(label for label, _, _ in variants)) != len(variants):
        raise ValueError('Variant labels must be unique')
    sources = [ROOT / 'CMakeLists.txt']
    for folder in ('src', 'include', 'tests'):
        sources += sorted(p for p in (ROOT / folder).rglob('*') if p.is_file())
    sources.append(Path(__file__).resolve())
    snapshot = args.output / 'source'
    for p in sources:
        dest = snapshot / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    models = {}
    for name in args.models:
        found = [p for folder in ('miplib', 'miplib2017') for p in (ROOT / 'datasets' / folder).glob(name + '.mps')]
        if len(found) != 1:
            raise ValueError(f'Expected exactly one input for {name}')
        models[name] = found[0]
    metadata = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'platform': platform.platform(), 'time_limit': args.limit, 'node_limit': 10000,
                'repeats': args.repeats, 'reference_limit': args.reference_limit,
                'binary_sha256': {label: hashlib.sha256(binary.read_bytes()).hexdigest() for label, binary, _ in variants},
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                'input_sha256': {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in models.items()},
                'note': 'Sequential same-machine experiment; references run after all timed solver runs. Single repeats are exploratory.'}
    save(args.output / 'metadata.json', metadata)
    records = []
    for repeat in range(args.repeats):
        # Alternate order on paired repeats to reduce systematic thermal/order bias.
        order = variants if repeat % 2 == 0 else variants[::-1]
        for name, path in models.items():
            for label, binary, flags in order:
                command = [str(binary), str(path), '--milp', '--json', '--time-limit', str(args.limit), *flags]
                ours = run(command, args.limit + 15)
                key = f'{name}.{label}.{repeat + 1}'
                save(args.output / (key + '.ours.json'), ours)
                record = {'name': name, 'variant': label, 'repeat': repeat + 1, 'key': key,
                          'status': ours.get('status'), 'objective': ours.get('objective'), 'gap': ours.get('gap'),
                          'nodes': ours.get('nodes'), 'seconds': ours.get('total_seconds'),
                          'first_incumbent_seconds': ours.get('first_incumbent_seconds'),
                          'pump_projections': ours.get('pump_projections'), 'pump_incumbents': ours.get('pump_incumbents'),
                          'command': command}
                records.append(record)
                save(args.output / 'results.json', records)
                print(name, label, record['status'], record['objective'], 'pump', record['pump_incumbents'], flush=True)
    references = {}
    for record in records:
        name, key = record['name'], record['key']
        # One full independent solve per model; later workers only read/check candidates.
        limit = 0 if name in references else args.reference_limit
        reference = run([sys.executable, str(ROOT / 'scripts/benchmark_lp.py'), '--reference', str(models[name]),
                         '--candidate', str(args.output / (key + '.ours.json')), '--limit', str(limit)], limit + 20)
        save(args.output / (key + '.reference.json'), reference)
        references.setdefault(name, reference)
        obj, recomputed = record['objective'], reference.get('candidate_recomputed_objective')
        consistent = obj is not None and recomputed is not None and math.isfinite(obj) and abs(obj - recomputed) <= 1e-7 * (1 + abs(obj))
        record['candidate_verified'] = bool(consistent and reference.get('candidate_max_violation', math.inf) <= 1e-7
                                            and reference.get('candidate_integer_violation', math.inf) <= 1e-7)
        ref = references[name]
        record['reference_status'] = ref.get('status')
        record['reference_objective'] = ref.get('objective')
        record['completed_verified'] = bool(record['candidate_verified'] and record['status'] in ('optimal', 'gap_limit')
            and ref.get('status') == 'Optimal' and ref.get('objective') is not None
            and abs(obj - ref['objective']) <= 1e-6 * (1 + abs(ref['objective'])))
        record['independent_max_violation'] = reference.get('candidate_max_violation')
        save(args.output / 'results.json', records)
    for record in records:
        print(record['name'], record['variant'], 'feasible=', record['candidate_verified'],
              'completed=', record['completed_verified'], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
