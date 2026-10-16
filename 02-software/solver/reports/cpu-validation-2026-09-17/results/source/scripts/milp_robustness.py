"""Failure-preserving breadth ledger. Reference work never feeds the solver."""
import argparse
from collections import Counter
import datetime
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from benchmark_lp import ROOT, parse_json_output
from validate_binary_proof import sha, save

FLAGS = ['--lp-recovery', '--improve-incumbent', '--repair-candidates',
         '--capture-lp-failure', '--capture-rejected-candidates',
         '--late-lifted-covers', '--late-compact-equalities',
         '--late-reduced-bound-lp', '--binary-proof']
LIMITS = {'time_limit', 'node_limit', 'iteration_limit', 'external_timeout'}


def timed(command, timeout, prefix):
    start = time.perf_counter()
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        stdout, stderr, code = p.stdout, p.stderr, p.returncode
        try:
            result = parse_json_output(stdout)
        except ValueError:
            result = {'status': 'process_error'}
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
        stdout, stderr, code = decode(error.stdout), decode(error.stderr), None
        result = {'status': 'external_timeout'}
    prefix.with_suffix(prefix.suffix + '.stdout.log').write_text(stdout, encoding='utf-8')
    prefix.with_suffix(prefix.suffix + '.stderr.log').write_text(stderr, encoding='utf-8')
    result.update(process_seconds=time.perf_counter()-start, exit_code=code)
    if stderr: result['stderr'] = stderr
    return result


def reference(model, candidate, limit):
    sys.path.insert(0, str(ROOT / 'tools/reference/python'))
    import highspy
    import numpy as np
    h = highspy.Highs()
    for key, value in {'output_flag': False, 'threads': 1, 'random_seed': 0,
                       'time_limit': limit, 'mip_rel_gap': 1e-9, 'mip_abs_gap': 1e-9,
                       'primal_feasibility_tolerance': 1e-8,
                       'dual_feasibility_tolerance': 1e-8, 'mip_feasibility_tolerance': 1e-8}.items():
        if h.setOptionValue(key, value) == highspy.HighsStatus.kError:
            raise RuntimeError('Reference option rejected: ' + key)
    if h.readModel(str(model)) == highspy.HighsStatus.kError:
        raise RuntimeError('Independent MPS read failed')
    h.run(); h.ensureColwise(); lp, info = h.getLp(), h.getInfo()
    valid = h.getSolution().value_valid and info.primal_solution_status == 2
    finite = lambda v: float(v) if math.isfinite(v) else None
    result = {'status': h.modelStatusToString(h.getModelStatus()), 'version': h.version(),
              'rows': lp.num_row_, 'columns': lp.num_col_, 'maximize': lp.sense_ == highspy.ObjSense.kMaximize,
              'objective': finite(h.getObjectiveValue()) if valid else None,
              'best_bound': finite(info.mip_dual_bound), 'gap': finite(info.mip_gap),
              'solve_seconds': h.getRunTime(),
              'integers': sum(t != highspy.HighsVarType.kContinuous for t in lp.integrality_),
              'candidate_checked': False}
    x = np.asarray(candidate.get('primal', []), dtype=float)
    if len(x) == 0:
        return result
    if len(x) != lp.num_col_ or not np.all(np.isfinite(x)):
        result['candidate_error'] = 'Wrong dimensions or nonfinite vector'; return result
    names = candidate.get('variable_names')
    if names is not None:
        if len(names) != len(x) or len(set(names)) != len(x) or set(names) != set(lp.col_names_):
            result['candidate_error'] = 'Variable name mismatch'; return result
        by_name = dict(zip(names, x)); x = np.asarray([by_name[n] for n in lp.col_names_])
    matrix = lp.a_matrix_; activity = np.zeros(lp.num_row_)
    starts, indices, values = matrix.start_, matrix.index_, matrix.value_
    for j in range(lp.num_col_):
        for k in range(starts[j], starts[j+1]):
            activity[indices[k]] += values[k] * x[j]
    violation = 0.0
    for values, lower, upper in ((x, lp.col_lower_, lp.col_upper_), (activity, lp.row_lower_, lp.row_upper_)):
        for value, lo, up in zip(values, lower, upper):
            violation = max(violation, lo-value, value-up)
    integer_error = max((abs(x[j]-round(x[j])) for j, kind in enumerate(lp.integrality_)
                         if kind != highspy.HighsVarType.kContinuous), default=0.0)
    result.update(candidate_checked=True, candidate_max_violation=float(violation),
                  candidate_integer_violation=float(integer_error),
                  candidate_objective=float(np.dot(lp.col_cost_, x)+lp.offset_))
    return result


def classify(ours, ref, requested_gap, exact=False):
    errors = []
    status, obj, bound = ours.get('status'), ours.get('objective'), ours.get('best_bound')
    point = bool(ours.get('primal'))
    ref_ok = isinstance(ref.get('columns'), int)
    reference_obj = ref.get('objective')
    sign = -1 if ref.get('maximize') else 1
    close = lambda a, b: a is not None and b is not None and abs(a-b) <= 1e-7*(1+abs(b))
    if point and ref_ok:
        if not ref.get('candidate_checked') or ref.get('candidate_max_violation', math.inf) > 1e-7 or ref.get('candidate_integer_violation', math.inf) > 1e-7:
            errors.append('original_model_infeasible_candidate')
        if not close(obj, ref.get('candidate_objective')): errors.append('objective_mismatch')
    if ref_ok and ours.get('columns') is not None and (ours['columns'] != ref['columns'] or ours['rows'] != ref['rows']):
        errors.append('parsed_model_dimensions_mismatch')
    if bound is not None and reference_obj is not None and sign*(bound-reference_obj) > 1e-7*(1+abs(reference_obj)):
        errors.append('bound_excludes_independent_feasible_point')
    if point and bound is not None:
        if sign*(bound-obj) > 1e-7*(1+abs(obj)): errors.append('bound_excludes_own_point')
        expected = max(0, sign*(obj-bound))/(1+abs(obj))
        if not close(ours.get('gap'), expected): errors.append('reported_gap_mismatch')
    if status in ('optimal', 'gap_limit'):
        if not point or bound is None or ours.get('gap') is None or ours['gap'] > requested_gap+1e-10:
            errors.append('completion_without_point_and_closed_gap')
        # gap_limit promises the requested tolerance, not exact objective equality.
        objective_tolerance = max(1e-7, requested_gap if status == 'gap_limit' else 0.)
        objective_matches = obj is not None and reference_obj is not None and abs(obj-reference_obj) <= objective_tolerance*(1+abs(obj))
        if ref['status'] == 'Optimal' and not objective_matches: errors.append('false_completion_vs_reference')
    if status in ('infeasible', 'unbounded') and reference_obj is not None:
        if status == 'infeasible' or ref['status'] == 'Optimal': errors.append('false_terminal_status')
    if errors: return 'validation_failure', errors
    if exact: return 'exact_proof_checked', []
    if status in ('optimal', 'gap_limit'):
        return ('numerical_completion_checked' if ref['status'] == 'Optimal' and ref.get('gap', math.inf) is not None and ref['gap'] <= 1e-8 else 'completion_reference_pending'), []
    if status in LIMITS:
        if point and not ref_ok: return 'incumbent_reference_pending', []
        return ('feasible_limit' if point else 'no_incumbent_limit'), []
    if status in ('infeasible', 'unbounded'):
        return ('terminal_status_crosschecked' if ref['status'].lower() == status else 'terminal_reference_pending'), []
    if status == 'process_error':
        return ('input_rejected' if 'MPS line' in ours.get('stderr', '') else 'process_failure'), []
    return 'numerical_or_unresolved', []


def main(args):
    if not __debug__: raise RuntimeError('Validation requires assertions')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    manifest_path = ROOT / 'datasets/milp-robustness-wave1/manifest.json'
    manifest = json.loads(manifest_path.read_text()); source = args.source.resolve()
    binary = args.binary.resolve(); records = []
    metadata = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'binary': str(binary), 'binary_sha256': sha(binary), 'source': str(source),
                'source_sha256': {p.relative_to(source).as_posix(): sha(p) for folder in ('src', 'include') for p in (source/folder).glob('*') if p.is_file()},
                'cmake_sha256': sha(source/'CMakeLists.txt'), 'manifest_sha256': sha(manifest_path),
                'runner_sha256': sha(Path(__file__)), 'limit': args.limit, 'watchdog': args.limit+15,
                'checker_sha256': {name:sha(ROOT/'scripts'/name) for name in ('benchmark_lp.py','validate_binary_proof.py','exact_binary_check.py','check_lifted_covers.py')},
                'reference_limit': args.reference_limit, 'node_limit': 250000, 'gap': 1e-6,
                'flags': FLAGS, 'platform': platform.platform(),
                'protocol': 'Fixed profile; sequential own runs, then references. No external incumbents. All selected outcomes retained.'}
    save(output/'metadata.json', metadata)
    for spec in manifest['instances']:
        if args.models and spec['name'] not in args.models: continue
        name = spec['name']; record = {**spec}
        if spec['status'] != 'ready':
            record['category'] = 'download_failed'; records.append(record); continue
        model = ROOT / spec['model']; assert sha(model) == spec['model_sha256']
        command = [str(binary), str(model), '--milp', '--json', *FLAGS,
                   '--time-limit', str(args.limit), '--node-limit', '250000', '--gap', '1e-6']
        ours = timed(command, args.limit+15, output/(name+'.ours'))
        save(output/(name+'.ours.json'), ours)
        record.update(command=command, ours_status=ours['status'], objective=ours.get('objective'),
                      best_bound=ours.get('best_bound'), gap=ours.get('gap'), seconds=ours.get('total_seconds'),
                      nodes=ours.get('nodes'), ours_sha256=sha(output/(name+'.ours.json')))
        records.append(record); save(output/'results.json', records)
        print(name, {k: record[k] for k in ('ours_status','objective','best_bound','gap','seconds')}, flush=True)
    for record in records:
        if record['status'] != 'ready': continue
        name = record['name']; model = ROOT / record['model']
        ours = json.loads((output/(name+'.ours.json')).read_text())
        command = [sys.executable, str(Path(__file__).resolve()), '--reference', str(model),
                   '--candidate', str(output/(name+'.ours.json')), '--reference-limit', str(args.reference_limit)]
        ref = timed(command, args.reference_limit+20, output/(name+'.reference'))
        save(output/(name+'.reference.json'), ref)
        exact = False; check_errors = []
        if ours.get('binary_proof', {}).get('status') in ('optimal', 'infeasible'):
            try:
                from exact_binary_check import check, parse_mps
                proof = check(parse_mps(model.read_text()), ours)
                save(output/(name+'.exact-check.json'), proof); exact = proof['all_checks_pass']
            except Exception as error: check_errors.append('exact_check: '+str(error))
        try:
            from check_lifted_covers import check
            cuts = check(model, ours); save(output/(name+'.cut-check.json'), cuts)
        except Exception as error: check_errors.append('cut_check: '+str(error))
        category, errors = classify(ours, ref, 1e-6, exact)
        if check_errors: category = 'validation_failure'
        record.update(category=category, validation_errors=errors+check_errors,
                      reference_status=ref['status'], reference_objective=ref.get('objective'),
                      reference_bound=ref.get('best_bound'), reference_gap=ref.get('gap'),
                      candidate_violation=ref.get('candidate_max_violation'),
                      reference_sha256=sha(output/(name+'.reference.json')))
        save(output/'results.json', records); print(name, category, errors+check_errors, flush=True)
    assert sha(binary) == metadata['binary_sha256']
    for name, digest in metadata['source_sha256'].items(): assert sha(source/name) == digest
    assert sha(Path(__file__)) == metadata['runner_sha256']
    for name, digest in metadata['checker_sha256'].items(): assert sha(ROOT/'scripts'/name) == digest
    summary = {'runs': len(records), 'categories': dict(Counter(r['category'] for r in records)),
               'all_selected_solved': all(r['category'] in ('exact_proof_checked','numerical_completion_checked','terminal_status_crosschecked') for r in records),
               'validation_failures': sum(r['category']=='validation_failure' for r in records),
               'limitation': 'Numerical completions are not exact rational proofs. Unfinished and reference-pending cases stay on the ledger.'}
    save(output/'SUMMARY.json', summary); print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path)
    p.add_argument('--binary', type=Path); p.add_argument('--source', type=Path)
    p.add_argument('--limit', type=float, default=30); p.add_argument('--reference-limit', type=float, default=5)
    p.add_argument('--models', nargs='+'); p.add_argument('--reference', type=Path); p.add_argument('--candidate', type=Path)
    args = p.parse_args()
    if args.reference:
        print(json.dumps(reference(args.reference, json.loads(args.candidate.read_text()), args.reference_limit), allow_nan=False))
    else:
        if not args.output or not args.binary or not args.source: p.error('Provide output, binary and matching source')
        main(args)
