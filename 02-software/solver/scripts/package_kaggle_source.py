"""Build the Kaggle source dataset for one frozen iteration.

What goes to Kaggle is the source that produced a frozen binary, not whatever
happens to be in the working tree.  Each iteration's `SOURCE_IDENTITY.json`
lists every source file with its SHA-256 and the SHA-256 of the executable
those files built; this script copies exactly those files out of that
iteration's `final-source/`, checks every hash on the way, and refuses to
write a bundle if one disagrees.

    python scripts/package_kaggle_source.py                  # newest iteration
    python scripts/package_kaggle_source.py --iteration 36
    python scripts/package_kaggle_source.py --check          # verify, write nothing

Then, with the token in ~/.kaggle/ and never in this tree:

    kaggle datasets create -p <bundle> --dir-mode zip
    kaggle datasets version -p <bundle> -m "<message>" --dir-mode zip
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
# `scripts/` is 142 files of measurement harness that a Kaggle build never
# compiles; the notebook carries its own runner.
BUILD_INPUTS = ('src/', 'include/', 'tests/', 'CMakeLists.txt')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def newest_iteration():
    found = [(int(re.search(r'(\d+)$', p.parent.name).group(1)), p.parent)
             for p in REPORTS.glob('milp-iteration-*/SOURCE_IDENTITY.json')]
    if not found:
        raise SystemExit('no iteration carries a SOURCE_IDENTITY.json')
    return max(found)


def wanted(identity):
    return {name: digest for name, digest in identity['source_sha256'].items()
            if name.startswith(BUILD_INPUTS)}


def check(folder, identity):
    """Every file this bundle would contain, verified against the ledger."""
    source = folder / 'final-source'
    problems = []
    for name, digest in sorted(wanted(identity).items()):
        path = source / name
        if not path.is_file():
            problems.append(f'missing: {name}')
        elif sha256(path) != digest:
            problems.append(f'SHA-256 disagrees with SOURCE_IDENTITY.json: {name}')
    binary = folder / identity['binary']
    if binary.is_file() and sha256(binary) != identity['binary_sha256']:
        problems.append(f'frozen binary does not match its recorded hash: {binary.name}')
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--iteration', type=int, help='iteration number (default: the newest frozen one)')
    parser.add_argument('--out', type=Path, help='bundle folder (default: build-kaggle/it<N>, ignored by git)')
    parser.add_argument('--user', default='prakhar1803', help='Kaggle username that owns the dataset')
    parser.add_argument('--check', action='store_true', help='verify the frozen source and write nothing')
    args = parser.parse_args()

    if args.iteration is None:
        number, folder = newest_iteration()
    else:
        number, folder = args.iteration, REPORTS / f'milp-iteration-{args.iteration}'
    identity = json.loads((folder / 'SOURCE_IDENTITY.json').read_text(encoding='utf-8'))

    problems = check(folder, identity)
    if problems:
        for line in problems:
            print('FAIL ' + line)
        raise SystemExit(f'iteration {number} is not intact; nothing written')
    files = wanted(identity)
    print(f'iteration {number}: {len(files)} build inputs verified against SOURCE_IDENTITY.json')
    print(f'  binary {identity["binary_sha256"][:16]}...  compiler {identity.get("compiler", "unrecorded")}')
    if args.check:
        return

    out = (args.out or ROOT / 'build-kaggle' / f'it{number}').resolve()
    if out.exists():
        shutil.rmtree(out)
    for name in files:
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(folder / 'final-source' / name, target)

    slug = f'sih26119-solver-source-it{number}'
    (out / 'dataset-metadata.json').write_text(json.dumps({
        'title': f'SIH26119 solver source (iteration {number})',
        'id': f'{args.user}/{slug}',
        'licenses': [{'name': 'other'}]}, indent=2), encoding='utf-8')
    (out / 'MANIFEST.json').write_text(json.dumps({
        'iteration': number,
        'binary_sha256': identity['binary_sha256'],
        'compiler': identity.get('compiler'),
        'build_type': identity.get('build_type'),
        'source': (folder / 'final-source').relative_to(ROOT).as_posix(),
        'files': {name: sha256(out / name) for name in sorted(files)}},
        indent=1), encoding='utf-8')

    total = sum((out / name).stat().st_size for name in files)
    print(f'wrote {out}  ({len(files)} files, {total/1024:.0f} KiB)')
    print(f'  kaggle datasets create  -p "{out}" --dir-mode zip')
    print(f'  kaggle datasets version -p "{out}" --dir-mode zip -m "iteration {number}"')


if __name__ == '__main__':
    main()
