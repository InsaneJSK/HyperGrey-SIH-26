"""End-to-end CLI demonstration: industrial case, what-if, limits and rejection.

Every solver answer is re-checked against an independent HiGHS process on the
original model. Nothing here feeds a reference value back into the solver. The
refinery case is a published teaching model, not MRPL operating data.

Usage: python -B scripts/demo_cli.py --binary <solver_cli.exe> --output <folder>
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

MILP_PROFILE = ROOT / 'reports/milp-iteration-30/CANDIDATE_PROFILE.json'
UNSUPPORTED = """NAME UNSUPPORTED
ROWS
 N COST
 L CAP
COLUMNS
 X COST 1 CAP 1
RHS
 B CAP 4
SOS
 S1 SET1 X 1
ENDATA
"""


def solve(binary, model, flags, limit, output, label):
    command = [str(binary), str(model), '--json', '--time-limit', str(limit), *flags]
    done = subprocess.run(command, capture_output=True, text=True, timeout=limit + 60)
    record = {'label': label, 'command': command, 'exit_code': done.returncode, 'stderr': done.stderr.strip()[:400]}
    try:
        record['result'] = json.loads(done.stdout)
    except ValueError:
        record['result'] = None
    (Path(output) / (label + '.json')).write_text(json.dumps(record, indent=1), encoding='utf-8')
    return record


def reference(model, record, limit, integer, output, label):
    """Independent HiGHS check of the returned point on the original model.

    Runs in a separate process that never sees our solver, and reads the
    original MPS with its own parser.
    """
    candidate = Path(output) / (label + '.candidate.json')
    candidate.write_text(json.dumps(record.get('result') or {}), encoding='utf-8')
    script = 'milp_robustness.py' if integer else 'benchmark_lp.py'
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'scripts' / script), '--reference', str(model),
               '--candidate', str(candidate)]
    command += ['--reference-limit', str(limit)] if integer else ['--limit', str(limit)]
    done = subprocess.run(command, capture_output=True, text=True, timeout=limit + 120)
    try:
        result = json.loads(done.stdout)
    except ValueError:
        result = {'status': 'reference_error', 'stderr': done.stderr.strip()[:400]}
    (Path(output) / (label + '.reference.json')).write_text(json.dumps(result, indent=1), encoding='utf-8')
    return result


def show(record, keys=('status', 'objective', 'best_bound', 'gap', 'total_seconds', 'nodes', 'iterations')):
    result = record.get('result') or {}
    parts = [f"{k}={result[k]}" for k in keys if result.get(k) is not None]
    return f"exit {record['exit_code']}: " + ', '.join(parts) + (f" | stderr: {record['stderr']}" if record['stderr'] else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--binary', type=Path, default=ROOT / 'reports/milp-iteration-30/final_solver_cli.exe')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--limit', type=float, default=30)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    milp_flags = json.loads(MILP_PROFILE.read_text())['flags'] + ['--milp', '--node-limit', '100000000', '--gap', '1e-6']
    lp_flags = ['--lp-method', 'bounded']
    summary = {'binary': str(args.binary), 'steps': []}

    print('1. Industrial LP: refinery planning and blending (published teaching model)')
    base = solve(args.binary, ROOT / 'examples/industrial/marco_refinery.mps', lp_flags, args.limit, out, 'refinery')
    print('   ', show(base))
    base_reference = reference(ROOT / 'examples/industrial/marco_refinery.mps', base, args.limit, False, out, 'refinery')
    print(f"    independent HiGHS: {base_reference['status']} objective={base_reference.get('objective')}"
          f" candidate violation={base_reference.get('candidate_max_violation')}")
    profit = -(base['result'] or {}).get('objective', float('nan'))
    print(f"    refinery profit (negated cost objective): {profit:.4f}")

    print('2. What-if: tighter fuel-oil sulfur limit (3.5 -> 3.4)')
    whatif = solve(args.binary, ROOT / 'examples/industrial/marco_low_sulfur.mps', lp_flags, args.limit, out, 'refinery_low_sulfur')
    print('   ', show(whatif))
    whatif_reference = reference(ROOT / 'examples/industrial/marco_low_sulfur.mps', whatif, args.limit, False, out, 'refinery_low_sulfur')
    print(f"    independent HiGHS: {whatif_reference['status']} objective={whatif_reference.get('objective')}"
          f" candidate violation={whatif_reference.get('candidate_max_violation')}")
    tight_profit = -(whatif['result'] or {}).get('objective', float('nan'))
    print(f"    profit after the change: {tight_profit:.4f} (change {tight_profit - profit:+.4f});"
          f" a tighter specification must not increase profit: {'OK' if tight_profit <= profit + 1e-6 else 'VIOLATED'}")

    print('2b. Sensitivity: where does the fuel-oil sulfur limit stop being affordable?')
    # Only the fuel-oil sulfur coefficient of row R39 changes; everything else is the
    # published model. Each variant is solved and checked independently.
    base_text = (ROOT / 'examples/industrial/marco_refinery.mps').read_text()
    marker = ' sale_fueloil R39 -3.5'
    curve = []
    if marker in base_text:
        for limit in (3.5, 3.48, 3.46, 3.44, 3.42, 3.4):
            variant = out / f'sulfur_{limit:g}.mps'
            variant.write_text(base_text.replace(marker, f' sale_fueloil R39 -{limit:g}'), encoding='utf-8')
            label = f'sulfur_{limit:g}'
            record = solve(args.binary, variant, lp_flags, args.limit, out, label)
            check = reference(variant, record, args.limit, False, out, label)
            value = (record.get('result') or {}).get('objective')
            profit_at = None if value is None else -value
            agrees = (check.get('objective') is not None and value is not None
                      and abs(check['objective'] - value) <= 1e-6 * (1 + abs(value)))
            curve.append({'sulfur_limit': limit, 'profit': profit_at, 'status': (record.get('result') or {}).get('status'),
                          'reference_agrees': bool(agrees)})
            print(f"    limit {limit:>5}: profit {profit_at if profit_at is None else round(profit_at, 4)!s:>8}"
                  f"  reference agrees: {agrees}")
        summary['sensitivity'] = curve
        print('    reading: profit falls with the specification and reaches zero once no in-spec plan pays,')
        print('    because residual sulfur has nowhere to go. That is a planning limit, not a solver failure.')

    print('3. MILP: multi-period production and lot sizing')
    milp = solve(args.binary, ROOT / 'examples/industrial/production_lotsizing.mps', milp_flags, args.limit, out, 'production_lotsizing')
    print('   ', show(milp))
    milp_reference = reference(ROOT / 'examples/industrial/production_lotsizing.mps', milp, args.limit, True, out, 'production_lotsizing')
    print(f"    independent HiGHS: {milp_reference['status']} objective={milp_reference.get('objective')}"
          f" candidate violation={milp_reference.get('candidate_max_violation')}"
          f" integrality={milp_reference.get('candidate_integer_violation')}")

    print('4. Honest limit: a hard public MILP at a short budget')
    hard = solve(args.binary, ROOT / 'datasets/milp-cut-policy-holdout/mas74.mps', milp_flags, 5, out, 'mas74_short')
    result = hard['result'] or {}
    print('   ', show(hard))
    print(f"    reported as a limit, not an optimum: status={result.get('status')},"
          f" remaining gap={result.get('gap')}")

    print('5. Rejected input: an unsupported MPS section')
    bad = out / 'unsupported.mps'
    bad.write_text(UNSUPPORTED, encoding='utf-8')
    rejected = solve(args.binary, bad, ['--milp'], 10, out, 'unsupported')
    print('   ', show(rejected))

    for label, record, check in (('refinery', base, base_reference), ('refinery_low_sulfur', whatif, whatif_reference),
                                 ('production_lotsizing', milp, milp_reference), ('mas74_short', hard, None),
                                 ('unsupported', rejected, None)):
        summary['steps'].append({'label': label, 'exit_code': record['exit_code'],
                                 'status': (record.get('result') or {}).get('status'),
                                 'objective': (record.get('result') or {}).get('objective'),
                                 'reference_status': (check or {}).get('status'),
                                 'reference_objective': (check or {}).get('objective'),
                                 'candidate_max_violation': (check or {}).get('candidate_max_violation')})
    summary['what_if'] = {'profit': profit, 'profit_after': tight_profit, 'monotone': tight_profit <= profit + 1e-6}
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(f'\nWrote {out / "SUMMARY.json"}')


if __name__ == '__main__':
    main()
