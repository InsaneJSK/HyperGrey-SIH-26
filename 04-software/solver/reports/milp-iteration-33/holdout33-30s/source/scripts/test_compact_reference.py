"""Independent HiGHS cross-checks for tiny equality LPs; run after timings."""
import argparse
import json
import math
from pathlib import Path
import random
import sys
from benchmark_lp import ROOT, run
from industrial_cases import MpsModel
from validate_binary_proof import save, sha

if not __debug__:
    raise RuntimeError('Checks require assertions')


def main(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT / 'tools/reference/python'))
    import highspy
    rng = random.Random(26119091)
    records = []
    for case in range(90):
        model = MpsModel('EQUALITY_REFERENCE')
        maximize = case < 60 and case % 2 == 1
        if case < 60:
            kind = 'optimal'
            point = [rng.randint(-12, 16) / 4 for _ in range(6)]
            for j in range(6):
                model.var(f'x{j}', rng.randint(-9, 9) / 4, -4, 5)
            for i in range(4):
                row = {f'x{j}': rng.randint(-5, 5) / 8 for j in range(6)}
                rhs = sum(row[f'x{j}'] * point[j] for j in range(6))
                sense = 'E' if i < 2 else ('L' if i == 2 else 'G')
                model.row(row, sense, rhs + (2 if sense == 'L' else (-2 if sense == 'G' else 0)))
            if case % 4 == 0:
                row, _, rhs = model.rows[0]
                model.row({k: -2 * v for k, v in row.items()}, 'E', -2 * rhs)
        elif case < 75:
            kind = 'infeasible'
            for j in range(3):
                model.var(f'x{j}', rng.randint(-5, 5), None)
            row = {f'x{j}': rng.randint(1, 7) for j in range(3)}
            rhs = rng.randint(-9, 9)
            model.row(row, 'E', rhs)
            model.row({k: -2 * v for k, v in row.items()}, 'E', -2 * rhs + 1)
        else:
            kind = 'unbounded'
            model.var('x0', -1, None)
            model.var('x1', -1, None)
            model.row({'x0': rng.randint(1, 5), 'x1': -rng.randint(1, 5)}, 'E', rng.randint(-9, 9))
        path = output / f'case{case:02d}.mps'
        model.write(path)
        if maximize:
            path.write_text(path.read_text().replace('ROWS\n', 'OBJSENSE\n MAX\nROWS\n', 1))
        command = [str(args.binary.resolve()), str(path), '--json', '--compact-equalities', '--time-limit', '5']
        ours = run(command, 10)
        save(output / f'case{case:02d}.ours.json', ours)
        reference = highspy.Highs()
        for key, value in {'output_flag': False, 'threads': 1, 'presolve': 'off',
                           'time_limit': 5., 'primal_feasibility_tolerance': 1e-9,
                           'dual_feasibility_tolerance': 1e-9}.items():
            assert reference.setOptionValue(key, value) != highspy.HighsStatus.kError
        assert reference.readModel(str(path)) != highspy.HighsStatus.kError
        reference.run()
        status = reference.modelStatusToString(reference.getModelStatus()).lower()
        passed = ours['status'] == kind and status == kind
        if kind == 'optimal':
            passed = passed and len(ours.get('primal', [])) == len(model.vars) and all(math.isfinite(v) for v in ours['primal'])
        violation = value_error = None
        if kind == 'optimal' and ours.get('primal'):
            x = dict(zip(model.vars, ours['primal']))
            violation = max([0.] + [max(lo - x[n], x[n] - up) for n, (_, lo, up, _) in model.vars.items()])
            for row, sense, rhs in model.rows:
                delta = sum(v * x[n] for n, v in row.items()) - rhs
                violation = max(violation, abs(delta) if sense == 'E' else (delta if sense == 'L' else -delta))
            recomputed = sum(c * x[n] for n, (c, _, _, _) in model.vars.items())
            expected = reference.getObjectiveValue()
            value_error = abs(recomputed - expected)
            passed = passed and ours['optimality_verified'] and violation <= 1e-7
            passed = passed and value_error <= 1e-7 * (1 + abs(expected)) and abs(recomputed - ours['objective']) <= 1e-7
        elif kind == 'infeasible':
            passed = passed and ours['infeasibility_verified']
        elif kind == 'unbounded':
            ray = dict(zip(model.vars, ours.get('unbounded_ray', [])))
            passed = passed and ours['unboundedness_verified'] and len(ray) == 2
            if len(ray) == 2:
                passed = passed and all(math.isfinite(v) for v in ray.values())
                passed = passed and abs(sum(v * ray[n] for n, v in model.rows[0][0].items())) <= 1e-7
                passed = passed and sum(c * ray[n] for n, (c, _, _, _) in model.vars.items()) < -1e-9
        record = {'case': case, 'kind': kind, 'passed': bool(passed), 'reference_status': status,
                  'reference_version': reference.version(), 'max_violation': violation,
                  'objective_error': value_error, 'compact_fallback': ours.get('compact_fallback'),
                  'model_sha256': sha(path), 'result_sha256': sha(output / f'case{case:02d}.ours.json'), 'command': command}
        records.append(record)
        save(output / 'results.json', records)
        assert passed, record
    save(output / 'SUMMARY.json', {'all_pass': True, 'cases': len(records), 'optimal': 60,
         'infeasible': 15, 'unbounded': 15, 'fallbacks': sum(r['compact_fallback'] for r in records),
         'binary_sha256': sha(args.binary), 'script_sha256': sha(Path(__file__)),
         'limitation': 'Small independent numerical LP cross-checks, not general exact proofs or public timing evidence.'})
    print('Independent equality LP checks: 90/90', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    main(p.parse_args())
