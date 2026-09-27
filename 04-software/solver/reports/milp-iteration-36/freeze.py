"""Freeze the iteration 36 executable, runtime DLLs and source identity."""
import hashlib
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
BUILD = ROOT / 'build-milp-iter33'
DLLS = ['libgcc_s_seh-1.dll', 'libstdc++-6.dll', 'libgomp-1.dll', 'libwinpthread-1.dll', 'libdl.dll']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    target = BASE / 'final_solver_cli.exe'
    if target.exists():
        raise SystemExit('Already frozen; refusing to overwrite evidence')
    shutil.copy2(BUILD / 'solver_cli.exe', target)
    runtime = {}
    for name in DLLS:
        shutil.copy2(BUILD / name, BASE / name)
        runtime[name] = sha(BASE / name)
    source = {}
    for folder in ('src', 'include', 'tests', 'scripts'):
        for p in sorted((ROOT / folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                rel = p.relative_to(ROOT)
                dest = BASE / 'final-source' / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
                source[rel.as_posix()] = sha(p)
    for extra in ('CMakeLists.txt',):
        shutil.copy2(ROOT / extra, BASE / 'final-source' / extra)
        source[extra] = sha(ROOT / extra)
    state = {'binary': 'final_solver_cli.exe', 'binary_sha256': sha(target),
             'build_binary_sha256': sha(BUILD / 'solver_cli.exe'), 'runtime_dlls': runtime,
             'compiler': 'WinLibs GCC 14.2.0 x64 UCRT POSIX SEH r2 (C:/mingw64)', 'build_type': 'Release',
             'source_sha256': source}
    (BASE / 'SOURCE_IDENTITY.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(state['binary_sha256'], len(source), 'source files')


if __name__ == '__main__':
    main()
