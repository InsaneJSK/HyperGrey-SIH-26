"""Local reduced-bound LP experiment; sequential timings, then verification.

Root-only screens use one node and no heuristics. Full runs compare the same
late-cut strategy with/without compact equalities; neither receives a reference
solution. Outputs must be fresh directories. All numerical inputs are hashed.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from benchmark_lp import ROOT, run
from validate_binary_proof import sha, save
from check_lifted_covers import check as check_cuts
from exact_binary_check import check as check_exact, parse_mps

if not __debug__:
    raise RuntimeError('Validation requires assertions')


def main(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    build = (ROOT / args.build).resolve()
    binary = build / ('solver_cli.exe' if os.name == 'nt' else 'solver_cli')
    common = ['--lp-recovery', '--improve-incumbent', '--repair-candidates',
              '--capture-neighborhood', '--capture-lp-failure', '--capture-rejected-candidates']
    delayed = not args.root_only and not args.no_late
    common += ['--late-lifted-covers', '--late-compact-equalities'] if delayed else ['--compact-equalities']
    profiles = {'control': common, 'reduced': common + ['--late-reduced-bound-lp' if delayed else '--reduced-bound-lp']}
    profiles = {k: profiles[k] for k in args.profiles}
    metadata = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'binary_sha256': sha(binary), 'cmake_sha256': sha(ROOT / 'CMakeLists.txt'),
        'cmake_cache_sha256': sha(build / 'CMakeCache.txt'), 'profiles': profiles,
        'limit': args.limit, 'nodes': args.nodes, 'root_only': args.root_only,
        'repeats': args.repeats,
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p)
                          for folder in ('src', 'include', 'tests', 'scripts')
                          for p in (ROOT / folder).glob('*')
                          if p.suffix in ('.cpp', '.hpp', '.cu', '.py')},
        'protocol': 'Sequential equal-budget runs, alternating order; references after timings. CPU only.'}
    save(output / 'metadata.json', metadata)
    shutil.copy2(build / 'CMakeCache.txt', output / 'CMakeCache.txt')
    test = subprocess.run(['ctest', '--test-dir', str(build), '--output-on-failure'],
                          capture_output=True, text=True)
    (output / 'ctest.log').write_text(test.stdout + test.stderr)
    assert test.returncode == 0
    generated = {}
    if args.generated:
        import test_milp
        import test_mixed_v2
        for profile, flags in {**profiles, 'reduced_proof': common + ['--reduced-bound-lp', '--binary-proof']}.items():
            test_milp.main(output / (profile + '-binary'), True, binary, flags)
            test_mixed_v2.main(output / (profile + '-mixed'), binary, flags)
            for kind, name in [('binary', 'enumeration.json'), ('mixed', 'summary.json')]:
                data = json.loads((output / (profile + '-' + kind) / name).read_text())
                assert len(data) == 40 and all(r['passed'] for r in data)
                generated[profile + '-' + kind] = 40
    records = []
    for index, name in enumerate(args.models):
        model = ROOT / 'datasets' / ('miplib' if name == 'p0033' else 'miplib2017') / (name + '.mps')
        spec = next(s for s in json.loads((model.parent / 'manifest.json').read_text())['instances'] if s['name'] == name)
        assert sha(model) == spec.get('mps_sha256', spec.get('model_sha256'))
        for repeat in range(args.repeats):
            order = list(profiles) if (index + repeat) % 2 == 0 else list(profiles)[::-1]
            for profile in order:
                command = [str(binary), str(model), '--milp', '--json', *profiles[profile],
                           *(['--no-heuristics'] if args.root_only else []),
                           '--time-limit', str(args.limit), '--node-limit', str(args.nodes), '--gap', '1e-6']
                ours = run(command, args.limit + 30)
                key = f'{name}.{profile}.{repeat}'
                save(output / (key + '.ours.json'), ours)
                fields = ('status', 'objective', 'best_bound', 'gap', 'nodes', 'lp_iterations',
                          'total_seconds', 'root_bound_before_cuts', 'root_bound_after_cuts',
                          'lifted_cover_seconds', 'compact_lp_calls', 'compact_lp_fallbacks',
                          'root_lp_rows', 'root_compact_equalities', 'reduced_bound_lp_calls',
                          'reduced_bound_lp_fallbacks', 'reduced_bound_lp_accepted',
                          'reduced_upper_candidates', 'root_reduced_upper_bounds')
                records.append({'key': key, 'model': str(model), 'model_sha256': sha(model),
                                'profile': profile, 'repeat': repeat, 'command': command,
                                **{field: ours.get(field) for field in fields}})
                save(output / 'results.json', records)
                print(key, {k: ours.get(k) for k in ('status', 'objective', 'best_bound', 'gap',
                      'nodes', 'total_seconds', 'reduced_bound_lp_fallbacks', 'root_lp_rows', 'root_reduced_upper_bounds')}, flush=True)
    cuts = points = 0
    for record in records:
        path = output / (record['key'] + '.ours.json')
        ours = json.loads(path.read_text())
        assert ours['status'] in ('optimal', 'gap_limit', 'time_limit', 'node_limit', 'unresolved_relaxations')
        checked = check_cuts(Path(record['model']), ours)
        save(output / (record['key'] + '.cut-check.json'), checked)
        cuts += checked['cuts_checked']
        ref = run([sys.executable, str(ROOT / 'scripts/benchmark_lp.py'), '--reference',
                   record['model'], '--candidate', str(path), '--limit', '0'], 25)
        save(output / (record['key'] + '.reference.json'), ref)
        if ours['primal']:
            assert ref['candidate_max_violation'] <= 1e-7 and ref['candidate_integer_violation'] <= 1e-7
            assert abs(ref['candidate_recomputed_objective'] - ours['objective']) <= 1e-7 * (1 + abs(ours['objective']))
            points += 1
    model = ROOT / 'datasets/miplib2017/markshare_4_0.mps'
    sentinel = run([str(binary), str(model), '--milp', '--json', '--compact-equalities',
                    '--lifted-covers', '--binary-proof', '--time-limit', '30'], 45)
    save(output / 'markshare-proof-sentinel.json', sentinel)
    exact = check_exact(parse_mps(model.read_text()), sentinel)
    save(output / 'markshare-independent-proof.json', exact)
    assert exact['all_checks_pass']
    assert sha(binary) == metadata['binary_sha256']
    for name, digest in metadata['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    summary = {'all_pass': True, 'generated': generated, 'timed_runs': len(records),
               'public_cuts_checked': cuts, 'final_points_checked': points,
               'markshare_exact_sentinel_pass': True,
               'limitation': 'General MILP bounds are numerical, not exact rational certificates. Root-only screens are not full solves.'}
    save(output / 'summary.json', summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--build', default='build-milp-iter10')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--limit', type=float, default=180)
    p.add_argument('--nodes', type=int, default=250000)
    p.add_argument('--repeats', type=int, default=1)
    p.add_argument('--models', nargs='+', default=['binkar10_1'], choices=['binkar10_1', 'blend2', 'p0033'])
    p.add_argument('--profiles', nargs='+', default=['control', 'reduced'], choices=['control', 'reduced'])
    p.add_argument('--root-only', action='store_true')
    p.add_argument('--no-late', action='store_true')
    p.add_argument('--generated', action='store_true')
    args = p.parse_args()
    if args.root_only and args.nodes != 1:
        p.error('Root-only screens require --nodes 1')
    main(args)
