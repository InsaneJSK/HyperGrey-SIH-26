"""Freeze the checked opt-in profile and all diagnostic evidence exactly once."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_binary_proof import sha, save


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def manifest(folder, scope, extra):
    records = {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*'))
               if p.is_file() and '__pycache__' not in p.parts and p.name not in ('SNAPSHOT_MANIFEST.json', 'FINAL_STATE.json')}
    target = folder / 'SNAPSHOT_MANIFEST.json'
    assert not target.exists() and not (folder / 'FINAL_STATE.json').exists()
    save(target, records)
    save(folder / 'FINAL_STATE.json', {'manifest_sha256': sha(target), 'files': len(records), 'scope': scope, **extra})
    return len(records)


def main():
    binary = ROOT / 'build-lp-pivot-01/solver_cli.exe'
    digest = sha(binary)
    gate = read(BASE / 'gate/SUMMARY.json')
    result = read(BASE / 'validation/REVIEWED_SUMMARY.json')
    metadata = read(BASE / 'validation/metadata.json')
    assert gate['all_pass'] and not gate['quick'] and gate['stable_ratio']
    assert digest == gate['binary_sha256'] == result['binary_sha256'] == metadata['binary_sha256']
    assert result['unvalidated_completions'] == 0
    assert result['profiles']['stable']['checked_completions'] == result['profiles']['stable_refined']['checked_completions'] == 16
    assert result['profiles']['default']['checked_completions'] == 3
    assert sha(BASE / 'validate.initial.py') == metadata['runner_sha256']
    assert sha(BASE / 'review_qp_applicability.py') == result['review_script_sha256']
    assert sha(ROOT / 'scripts/sparse_accuracy_gate.py') == gate['runner_sha256']
    for rel, expected in metadata['source_sha256'].items():
        assert sha(ROOT / rel) == expected, rel
        assert sha(BASE / 'validation/source' / rel) == expected, rel
    for folder in [ROOT / 'scripts', BASE, ROOT / 'reports/numerical-diagnosis-01']:
        for path in folder.glob('*.py'):
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    snapshot = BASE / 'final-source'
    snapshot.mkdir(exist_ok=False)
    for folder in ('src', 'include', 'scripts', 'tests', 'docs'):
        for path in sorted((ROOT / folder).iterdir()):
            if path.is_file():
                target = snapshot / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
    for name in ('CMakeLists.txt', 'README.md'):
        shutil.copy2(ROOT / name, snapshot / name)
    prior = ROOT / 'reports/cpu-validation-2026-09-17/results'
    for rel, expected in metadata['inputs'].items():
        assert sha(prior / rel) == expected
        target = snapshot / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(prior / rel, target)
    shutil.copy2(binary, BASE / 'final_solver_cli.exe')
    shutil.copy2(binary.with_name('solver_primal_ratio_tests.exe'), BASE / 'ratio_tests.exe')
    shutil.copy2(ROOT / 'reports/milp-iteration-29/run_contained.py', BASE / 'run_contained.py')
    shutil.copy2(prior / 'DEPENDENCIES.json', BASE / 'DEPENDENCIES.json')
    runtime = read(ROOT / 'reports/milp-iteration-29/RUNTIME_DEPENDENCIES.json')
    diagnostic = ROOT / 'reports/numerical-diagnosis-01'
    for name, expected in runtime.items():
        source = binary.parent / name
        assert sha(source) == expected
        shutil.copy2(source, BASE / name)
        shutil.copy2(source, diagnostic / name)
    save(BASE / 'RUNTIME_DEPENDENCIES.json', runtime)
    for refined in (False, True):
        save(BASE / ('REFINED_LP_PROFILE.json' if refined else 'LP_PROFILE.json'),
             {'name': 'Stable primal ratio LP' + (' with refinement' if refined else ''), 'binary_sha256': digest,
              'flags': ['--stable-primal-ratio'] + (['--refine-basis', '--refine-at-checks'] if refined else []),
              'checked_completions': 16, 'models': 16, 'default_changed': False,
              'scope': 'Explicit continuous LP evaluation profile; no broad MILP, speed or scale claim.'})
    smoke = BASE / 'package-smoke'
    smoke.mkdir(exist_ok=False)
    model = snapshot / 'tests/lp_ratio_bandm.mps'
    command = [sys.executable, '-B', str(BASE / 'solve_lp.py'), str(model), '--output', str(smoke / 'bandm')]
    executed = subprocess.run(command, env=dict(os.environ, PATH=r'C:\Windows\System32', PYTHONDONTWRITEBYTECODE='1'),
                              capture_output=True, text=True, timeout=60)
    (smoke / 'launcher.stdout.log').write_text(executed.stdout)
    (smoke / 'launcher.stderr.log').write_text(executed.stderr)
    assert executed.returncode == 0, executed.stderr
    wrapped = read(smoke / 'bandm.json')
    candidate = dict(wrapped['native_result'])
    candidate['variable_names'] = read(prior / 'bandm.default.reference-candidate.json')['variable_names']
    save(smoke / 'candidate.json', candidate)
    reference = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/benchmark_lp.py'), '--reference', str(model),
                                '--candidate', str(smoke / 'candidate.json'), '--limit', '30'], capture_output=True, text=True, timeout=45)
    (smoke / 'reference.stdout.log').write_text(reference.stdout)
    (smoke / 'reference.stderr.log').write_text(reference.stderr)
    assert reference.returncode == 0, reference.stderr
    ref = json.loads(reference.stdout)
    assert wrapped['status'] == 'optimal' and candidate['optimality_verified'] and ref['status'] == 'Optimal'
    assert ref['candidate_scaled_violation'] <= 1e-8 and abs(candidate['objective'] - ref['objective']) < 1e-6
    save(smoke / 'SUMMARY.json', {'all_pass': True, 'binary_sha256': digest, 'objective': candidate['objective'],
         'scaled_violation': ref['candidate_scaled_violation'], 'scope': 'Same-host restricted-PATH launcher and original-model check; not a fresh OS.'})
    cases = [('results', 'diagnostic_cli.exe'), ('lp-candidate-results', 'lp_candidate_cli.exe'),
             ('ratio-candidate-results', 'ratio_candidate_cli.exe'), ('selective-candidate-results', 'selective_candidate_cli.exe')]
    for folder, executable in cases:
        assert sha(diagnostic / executable) == read(diagnostic / folder / 'metadata.json')['binary_sha256']
    diagnostics_count = manifest(diagnostic, 'Exact LP basis diagnosis, retained candidate failures and QP traces; no QP fix.', {})
    count = manifest(BASE, 'Frozen opt-in LP safeguard; defaults unchanged; no broad MILP or operational QP accuracy claim.',
                     {'binary_sha256': digest, 'default_changed': False, 'stable_lp_checked': 16,
                      'stable_refined_lp_checked': 16, 'qp_relative_kkt_checked': 3, 'unvalidated_completions': 0})
    print(json.dumps({'all_pass': True, 'binary_sha256': digest, 'frozen_files': count, 'diagnostic_files': diagnostics_count,
                      'source_files_verified': len(metadata['source_sha256']), 'packaged_lp_smoke_passed': True}, indent=2))


if __name__ == '__main__':
    main()
