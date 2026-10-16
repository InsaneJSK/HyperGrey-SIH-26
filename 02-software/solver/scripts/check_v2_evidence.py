"""Verify that the CPU evidence still matches the current numerical source."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main(folder,build=None):
    metadata=json.loads((folder/'metadata.json').read_text());checked=0
    for name,expected in metadata['source_sha256'].items():
        if name.split('/')[0] in ('src','include','tests'):
            assert digest(ROOT/name)==expected,'Numerical source changed since validation: '+name
            checked+=1
    expected_core={name for name in metadata['source_sha256'] if name.split('/')[0] in ('src','include','tests')}
    actual_core={str(p.relative_to(ROOT)).replace('\\','/') for directory in ('src','include','tests') for p in (ROOT/directory).rglob('*') if p.suffix in ('.cpp','.hpp','.cu')}
    assert expected_core==actual_core,'Core inventory changed since validation'
    build=(build or ROOT/'build-v2').resolve()
    binary=build/('solver_cli.exe' if (build/'solver_cli.exe').exists() else 'solver_cli')
    assert digest(binary)==metadata['binary_sha256'],'Binary changed since validation'
    assert digest(ROOT/'CMakeLists.txt')==metadata['cmake_sha256'],'Build definition changed'
    summary=json.loads((folder/'summary.json').read_text());assert summary['all_generated_passed'],'A generated correctness gate failed'
    records=json.loads((folder/'benchmarks.json').read_text());incomplete=[r['family']+'/'+r['name'] for r in records if not r['passed']]
    result={'core_files_verified':checked,'binary_sha256':metadata['binary_sha256'],'groups':summary['groups'],'incomplete_public_cases':incomplete,'gpu_verified':summary['gpu_verified']}
    (folder/'evidence_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--build',type=Path)
    args=parser.parse_args();main(args.folder,args.build)
