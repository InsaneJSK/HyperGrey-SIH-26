"""Verify imported files against the migration baseline and documented later changes."""
import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name('migration-manifest.csv')
CHANGES = Path(__file__).with_name('post-import-changes.json')
RENAMES = Path(__file__).with_name('layout-renames.json')


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


def layout_renames(problems):
    """Resolve original import sections without changing their manifest IDs."""
    try:
        layout = json.loads(RENAMES.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        problems.append(f'cannot read layout rename map: {error}')
        return {}
    if not isinstance(layout, dict) or layout.get('schema_version') != 1:
        problems.append('unsupported layout rename schema')
        return {}
    renames = layout.get('top_level_renames')
    if not isinstance(renames, dict):
        problems.append('top-level renames must be an object')
        return {}
    targets = set()
    valid = {}
    for old, new in renames.items():
        for name in (old, new):
            if (not isinstance(name, str) or not name or name in ('.', '..')
                    or PurePosixPath(name).parts != (name,)
                    or '\\' in name or ':' in name):
                problems.append(f'unsafe top-level rename: {old!r} -> {new!r}')
                break
        else:
            if new in targets:
                problems.append(f'duplicate layout destination: {new}')
            targets.add(new)
            valid[old] = new
    return valid


def current_destination(relative, renames):
    """Apply a section rename once, even when a target is also an old name."""
    parts = PurePosixPath(relative).parts
    if not parts:
        return relative
    return PurePosixPath(renames.get(parts[0], parts[0]), *parts[1:]).as_posix()


def later_changes(rows, problems):
    """Keep later edits explicit without rewriting the original import manifest."""
    baseline = {row['destination']: row['destination_sha256'] for row in rows}
    try:
        ledger = json.loads(CHANGES.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        problems.append(f'cannot read post-import ledger: {error}')
        return {}
    if not isinstance(ledger, dict) or ledger.get('schema_version') != 1:
        problems.append('unsupported post-import ledger schema')
        return {}
    entries = ledger.get('changes')
    if not isinstance(entries, list):
        problems.append('post-import changes must be a list')
        return {}
    approved = {}
    for entry in entries:
        if not isinstance(entry, dict):
            problems.append('invalid post-import change entry')
            continue
        name = entry.get('destination')
        expected = entry.get('current_sha256')
        if not isinstance(name, str) or name not in baseline:
            problems.append(f'post-import path not in migration manifest: {name}')
            continue
        if name in approved:
            problems.append(f'duplicate post-import path: {name}')
        if entry.get('baseline_sha256') != baseline[name]:
            problems.append(f'post-import baseline hash mismatch: {name}')
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            problems.append(f'invalid post-import current hash: {name}')
            continue
        if expected == baseline[name]:
            problems.append(f'post-import entry has no content change: {name}')
        if not isinstance(entry.get('reason'), str) or not entry['reason'].strip():
            problems.append(f'post-import reason missing: {name}')
        approved[name] = expected
    return approved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='optional original sih-backup-solver checkout')
    args = parser.parse_args()
    problems = []
    renames = layout_renames(problems)
    if problems:
        for problem in problems:
            print('FAIL: ' + problem)
        return 1
    with MANIFEST.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    approved = later_changes(rows, problems)
    source_names = set()
    destination_names = set()
    current_names = set()
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
        current = current_destination(new, renames)
        if current in current_names:
            problems.append(f'current destination collision: {current}')
        current_names.add(current)
        if any(part.lower() in ('research', '03-research', '01-research')
               for name in (new, current) for part in PurePosixPath(name).parts):
            problems.append(f'research unexpectedly imported: {new}')
        same = row['source_sha256'] == row['destination_sha256']
        unchanged += same
        if not same and new not in allowed_changes:
            problems.append(f'unexpected content change: {new}')
        expected_change = 'unchanged' if same else 'navigation/configuration only'
        if row['change'] != expected_change:
            problems.append(f'incorrect change label: {new}')
        target = contained(ROOT, current)
        if not target.is_file():
            problems.append(f'missing: {new} (current: {current})')
        elif sha256(target) != approved.get(new, row['destination_sha256']):
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
    for original in ('00-submission', '03-research', '04-software', '05-models', '06-validation',
                 '07-documentation', '08-media', '09-business', '10-project'):
        name = current_destination(original, renames)
        if not (ROOT / name / 'README.md').is_file():
            problems.append(f'missing section guide: {name}')
    print(f'{len(rows):,} imported files checked; import baseline records {unchanged:,} '
          f'byte-identical files and {len(rows) - unchanged} navigation/configuration changes.')
    print(f'{len(approved)} documented post-import change(s) checked against current hashes.')
    if args.source:
        print('Original checkout hashes and complete tracked-file coverage checked.')
    for problem in problems:
        print('FAIL: ' + problem)
    if problems:
        print(f'{len(problems)} problem(s).')
        return 1
    print('PASS: imported files match the baseline plus documented post-import changes.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
