"""Validate the small notebook, companion archive and CPU source identity."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
import nbformat


def check(folder):
    notebook = nbformat.read(folder/'SIH26119_V2_Kaggle.ipynb', as_version=4)
    nbformat.validate(notebook)
    notebook_bytes = (folder/'SIH26119_V2_Kaggle.ipynb').stat().st_size
    assert notebook_bytes < 1_000_000, 'Notebook exceeds the 1 MB limit'
    claimed_hash, claimed_manifest_hash, code_cells = None, None, 0
    for cell in notebook.cells:
        if cell.cell_type != 'code':
            continue
        code_cells += 1
        tree = ast.parse(cell.source)
        for statement in tree.body:
            if not isinstance(statement, ast.Assign):
                continue
            names = [target.id for target in statement.targets if isinstance(target, ast.Name)]
            if 'SNAPSHOT_SHA256' in names:
                claimed_hash = ast.literal_eval(statement.value)
            if 'MANIFEST_SHA256' in names:
                claimed_manifest_hash = ast.literal_eval(statement.value)
    payload = (folder/'SIH26119_V2_source.zip').read_bytes()
    assert claimed_hash is not None and claimed_manifest_hash is not None
    assert hashlib.sha256(payload).hexdigest() == claimed_hash
    with zipfile.ZipFile(folder/'SIH26119_V2_source.zip') as archive:
        assert archive.testzip() is None, 'Corrupt archive entry'
        assert len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate archive entry'
        for name in archive.namelist():
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
        manifest = json.loads(archive.read('SOURCE_MANIFEST.json'))
        assert hashlib.sha256(archive.read('SOURCE_MANIFEST.json')).hexdigest() == claimed_manifest_hash
        assert set(archive.namelist()) == set(manifest) | {'SOURCE_MANIFEST.json'}
        for name, digest in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
        evidence = (json.loads(archive.read('SNAPSHOT_INFO.json'))['cpu_evidence']
                    if 'SNAPSHOT_INFO.json' in manifest else 'reports/v2-final-cpu')
        metadata = json.loads(archive.read(evidence+'/metadata.json'))
        core = {name: digest for name, digest in metadata['source_sha256'].items()
                if name.split('/')[0] in ('src', 'include', 'tests')}
        assert set(core) == {name for name in manifest if name.split('/')[0] in ('src', 'include', 'tests')}
        for name, digest in core.items():
            assert manifest[name] == digest, 'CPU evidence source mismatch: '+name
        assert manifest['CMakeLists.txt'] == metadata['cmake_sha256']
    cuda_evidence = 'not yet evidenced for this snapshot'
    matched_audit = None
    report_root = Path(__file__).resolve().parents[1]/'reports'
    for audit_path in sorted(report_root.glob('kaggle-gpu-*/AUDIT.json')):
        audit = json.loads(audit_path.read_text(encoding='utf-8'))
        if audit['snapshot_sha256'] == claimed_hash and audit['cuda_scale_cases_passed'] > 0:
            cuda_evidence = 'selected synthetic CUDA cases passed in audited Kaggle return; single timing pass'
            matched_audit = audit_path.relative_to(report_root.parent).as_posix()
            break
    result = {'notebook_schema': 'passed', 'notebook_bytes': notebook_bytes,
              'under_1_mb': True, 'external_source_zip': True, 'code_cells_parsed': code_cells,
              'source_files_verified': len(manifest), 'cpu_core_files_matched': len(core),
              'cpu_evidence': evidence,
              'snapshot_sha256': claimed_hash, 'cuda_execution': cuda_evidence,
              'cuda_evidence_audit': matched_audit}
    (folder/'PACKAGE_CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    check(parser.parse_args().folder)
