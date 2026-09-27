"""Audit and preserve a returned Kaggle ZIP against its exact source snapshot."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import shutil
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def known_objective(n):
    state, optimum = 26119, []
    for _ in range(n):
        state = (1664525*state+1013904223) & 0xffffffff
        optimum.append(.5+(state % 10001)/10000)
    return math.fsum(-.5*x*(2.02*x-(optimum[j-1] if j else 0)
                          -(optimum[j+1] if j+1 < n else 0)) for j, x in enumerate(optimum))


def main(returned, source, output):
    returned, source, output = returned.resolve(), source.resolve(), output.resolve()
    with zipfile.ZipFile(returned) as z, zipfile.ZipFile(source) as s:
        assert z.testzip() is None and s.testzip() is None, 'ZIP integrity failure'
        assert len(z.namelist()) == len(set(z.namelist())), 'Duplicate output paths'
        for entry in z.infolist():
            p = PurePosixPath(entry.filename)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in entry.filename
            assert entry.file_size < 100_000_000, 'Unexpectedly large output entry'
            assert not ((entry.external_attr >> 16) & 0o170000) == 0o120000, 'ZIP symlinks rejected'
        assert sum(i.file_size for i in z.infolist()) < 500_000_000, 'Unexpected output size'
        read = lambda name: json.loads(z.read(name))
        prefix = 'reports/kaggle_validation/'
        snapshot = read('SNAPSHOT.json')['snapshot_sha256']
        assert sha(source.read_bytes()) == snapshot, 'Wrong companion source ZIP'
        assert z.read('SOURCE_MANIFEST.json') == s.read('SOURCE_MANIFEST.json'), 'Manifest mismatch'
        manifest = read('SOURCE_MANIFEST.json')
        for name, digest in manifest.items():
            assert sha(s.read(name)) == digest, 'Source archive changed: '+name
        meta = read(prefix+'metadata.json')
        for name, digest in meta['source_sha256'].items():
            assert manifest.get(name) == digest, 'Runtime source mismatch: '+name
        assert meta['cmake_sha256'] == manifest['CMakeLists.txt']
        assert sha(z.read(prefix+'CMakeCache.txt')) == meta['cmake_cache_sha256']
        groups = {}
        for family, path in [('generated_lp', 'generated-lp/summary.json'),
                             ('generated_milp', 'generated-milp/enumeration.json'),
                             ('generated_qp', 'generated-qp/generated.json'),
                             ('generated_mixed', 'generated-mixed/summary.json')]:
            records = read(prefix+path)
            groups[family] = {'passed': sum(r['passed'] is True for r in records), 'total': len(records)}
        if prefix+'generated-qp-equalities/summary.json' in z.namelist():
            records=read(prefix+'generated-qp-equalities/summary.json')
            groups['generated_qp_equalities']={'passed':sum(r['passed'] is True for r in records),'total':len(records)}
        public = read(prefix+'benchmarks.json')
        kkt_count=0
        for record in public:
            family, name = record['family'], record['name']
            model = ('examples/industrial/' if family == 'industrial' else 'datasets/'+family+'/')+name
            model += '.qplib' if family == 'qplib' else '.mps'
            assert record['source_sha256'] == manifest[model], model
            ours, reference = read(prefix+family+'/'+name+'.ours.json'), read(prefix+family+'/'+name+'.reference.json')
            actual, expected = ours.get('objective'), reference.get('objective')
            recomputed = reference.get('candidate_recomputed_objective')
            qp = family == 'qplib'
            integer = family in ('miplib', 'miplib2017') or (family == 'industrial' and name == 'production_lotsizing')
            passed = (ours.get('status') in ('optimal', 'gap_limit') and reference.get('status') == 'Optimal'
                      and actual is not None and expected is not None and recomputed is not None
                      and abs(actual-expected)/(1+abs(expected)) <= 1e-6
                      and abs(actual-recomputed)/(1+abs(actual)) <= 1e-7
                      and reference.get('candidate_scaled_violation', math.inf) <= (1e-7 if qp else 1e-8)
                      and reference.get('candidate_integer_violation', 0) <= 1e-7
                      and (integer or ours.get('optimality_verified') is True))
            assert passed == record['passed'], 'Public score mismatch: '+name
            if qp and 'independent_kkt_passed' in record:
                certificate=reference.get('candidate_certificate',{})
                assert record['independent_kkt_passed']==certificate.get('independent_kkt_passed',False)
                assert record['independent_diagonal_certificate_passed']==certificate.get('diagonal_certificate_passed',False)
                assert record['independent_relative_dual_gap']==certificate.get('relative_dual_gap')
                kkt_count+=int(certificate.get('independent_kkt_passed',False))
            group = groups.setdefault(family, {'passed': 0, 'total': 0})
            group['passed'] += int(passed)
            group['total'] += 1
        if 'qplib_independent_kkt' in read(prefix+'summary.json')['groups']:
            groups['qplib_independent_kkt']={'passed':kkt_count,'total':sum(r['family']=='qplib' for r in public)}
        scale = read(prefix+'scale.json')
        comparisons, known = [], {}
        for row in scale:
            n = row['requested_columns']
            assert row['columns'] == n and row['backend'] == row['requested_backend']
            if n not in known:
                known[n] = known_objective(n)
            expected = known[n]
            assert abs(row['known_objective']-expected)/(1+abs(expected)) < 1e-12
            passed = (row['status'] == 'optimal' and row['exit_code'] == 0
                      and abs(row['objective']-expected)/(1+abs(expected)) <= 1e-8
                      and row['max_solution_error'] < 1e-4 and row['stationarity_residual'] <= 1e-7)
            assert bool(row['passed']) == passed, 'Scale score mismatch'
        for n in sorted(known):
            selected = [r for r in scale if r['requested_columns'] == n]
            assert len(selected) == 3 and all(r['repetition'] == 0 for r in selected), 'Expected single-pass run'
            cpu = next(r for r in selected if r['backend'] == 'cpu' and r['threads'] == 1)
            multi = next(r for r in selected if r['backend'] == 'cpu' and r['threads'] > 1)
            gpu = next(r for r in selected if r['backend'] == 'cuda')
            assert abs(cpu['objective']-gpu['objective'])/(1+abs(cpu['objective'])) <= 1e-8
            comparisons.append({'variables': n, 'cpu1_seconds': cpu['solve_seconds'],
                                'cpu_multicore_seconds': multi['solve_seconds'], 'cpu_threads': multi['threads'],
                                'gpu_seconds': gpu['solve_seconds'], 'cpu1_over_gpu': cpu['solve_seconds']/gpu['solve_seconds'],
                                'multicore_over_gpu': multi['solve_seconds']/gpu['solve_seconds'],
                                'process_cpu1_over_gpu': cpu['process_seconds']/gpu['process_seconds'],
                                'repetitions': 1})
        groups['scale'] = {'passed': sum(r['passed'] is True for r in scale), 'total': len(scale)}
        assert groups == read(prefix+'summary.json')['groups'], 'Summary counts mismatch'
        assert read('run_logs/RUN_STATUS.json')['completed'] is True
        assert b'100% tests passed' in z.read(prefix+'ctest.log')
        result = {'returned_zip_sha256': sha(returned.read_bytes()), 'snapshot_sha256': snapshot,
                  'source_files_verified': len(manifest), 'runtime_source_files_verified': len(meta['source_sha256']),
                  'groups_recounted': groups, 'comparisons': comparisons,
                  'incomplete_public_cases': [r['family']+'/'+r['name'] for r in public if not r['passed']],
                  'cuda_scale_cases_passed': sum(r['passed'] and r['backend'] == 'cuda' for r in scale),
                  'gpu_memory_measured': any(r.get('peak_gpu_memory_sampled_bytes') is not None for r in scale),
                  'interpretation': 'Single-pass synthetic box-QP evidence, not repeatable or general industrial speedup'}
        output.mkdir(parents=True, exist_ok=False)
        shutil.copy2(returned, output/'returned_results.zip')
        shutil.copy2(source, output/'submitted_source.zip')
        notebook = source.with_name('SIH26119_V2_Kaggle.ipynb')
        if notebook.is_file():
            shutil.copy2(notebook, output/'submitted_notebook.ipynb')
        z.extractall(output/'raw')
        (output/'AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('returned', type=Path)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    main(args.returned, args.source, args.output)
