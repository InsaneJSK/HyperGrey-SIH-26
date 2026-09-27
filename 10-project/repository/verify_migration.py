"""Verify the structure-only import using Python's standard library."""
import argparse
import csv
import hashlib
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name('migration-manifest.csv')


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def contained(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts or '\\' in relative or ':' in relative:
        raise ValueError(f'unsafe manifest path: {relative}')
    path = root.joinpath(*name.parts).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'path outside repository: {relative}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='optional original sih-backup-solver checkout')
    args = parser.parse_args()
    problems = []
    with MANIFEST.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    source_names = set()
    destination_names = set()
    unchanged = 0
    allowed_changes = {
        '.gitattributes', '.gitignore', '.vscode/settings.json',
        '04-software/solver/.gitignore', '04-software/backend/README.md',
        '04-software/backend/DEPLOY.md', '04-software/website/WEBSITE_PLAN.md',
        '07-documentation/PAPERS.md', '10-project/timeline/objective.md',
    }
    for row in rows:
        old, new = row['source'], row['destination']
        if old in source_names or new in destination_names:
            problems.append(f'duplicate mapping: {old} -> {new}')
        source_names.add(old)
        destination_names.add(new)
        if any(part.lower() in ('research', '03-research') for part in PurePosixPath(new).parts):
            problems.append(f'research unexpectedly imported: {new}')
        same = row['source_sha256'] == row['destination_sha256']
        unchanged += same
        if not same and new not in allowed_changes:
            problems.append(f'unexpected content change: {new}')
        expected_change = 'unchanged' if same else 'navigation/configuration only'
        if row['change'] != expected_change:
            problems.append(f'incorrect change label: {new}')
        target = contained(ROOT, new)
        if not target.is_file():
            problems.append(f'missing: {new}')
        elif sha256(target) != row['destination_sha256']:
            problems.append(f'destination hash mismatch: {new}')
        if args.source:
            original = contained(args.source, old)
            if not original.is_file():
                problems.append(f'source missing: {old}')
            elif original.stat().st_size != int(row['bytes']) or sha256(original) != row['source_sha256']:
                problems.append(f'source changed since import: {old}')
    if args.source:
        source = args.source.resolve()
        result = subprocess.run(
            ['git', '-c', f'safe.directory={source.as_posix()}', '-C', str(source), 'ls-files', '-z'],
            capture_output=True, check=True,
        )
        tracked = {name for name in result.stdout.decode('utf-8').split('\0') if name
                   and 'research' not in [part.lower() for part in PurePosixPath(name).parts]}
        for name in sorted(tracked - source_names):
            problems.append(f'tracked source omitted: {name}')
        for name in sorted(source_names - tracked):
            problems.append(f'manifest source not tracked: {name}')
    for name in ('00-submission', '04-software', '05-models', '06-validation',
                 '07-documentation', '08-media', '09-business', '10-project'):
        if not (ROOT / name / 'README.md').is_file():
            problems.append(f'missing section guide: {name}')
    print(f'{len(rows):,} imported files checked; {unchanged:,} byte-identical to source; '
          f'{len(rows) - unchanged} navigation/configuration changes.')
    if args.source:
        print('Original checkout hashes and complete tracked-file coverage checked.')
    for problem in problems:
        print('FAIL: ' + problem)
    if problems:
        print(f'{len(problems)} problem(s).')
        return 1
    print('PASS: imported files match the recorded migration baseline.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
