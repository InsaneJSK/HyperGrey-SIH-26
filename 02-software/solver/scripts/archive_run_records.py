"""Fold per-record validator and stdout files into one verified ZIP per run folder.

A paired run writes ten or more small files per solve: the monitor record, the
solver's own JSON, one file per accounting check, and the captured streams.  The
checks and streams are what `scripts/audit_*.py` re-derive and assert against,
so they are evidence and are never deleted -- they are packed into `checks.zip`
and `streams.zip` beside the records they belong to.

Every member is read back and compared byte for byte before the original is
removed, and `ARCHIVE.json` records each member's size and SHA-256, so the
archive can be checked without unpacking it.  `--restore` puts a folder back
exactly as it was, which is what an audit script needs.

    python scripts/archive_run_records.py --apply
    python scripts/archive_run_records.py --verify
    python scripts/archive_run_records.py --restore reports/milp-iteration-34/development-30s
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# A frozen source snapshot is read directly by the audit scripts (`ctest.log`,
# `CMakeCache.txt`); nothing inside one is ever archived.
SKIP_DIRS = {'final-source', 'generated-lattice', '.git'}
GROUPS = {
    'checks': lambda n: n.endswith('-check.json') or n.endswith('.check.json'),
    'streams': lambda n: n.endswith('.stdout.log') or n.endswith('.stderr.log'),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def folders(base):
    for path in sorted(base.rglob('*')):
        if path.is_dir() and not SKIP_DIRS & set(path.parts):
            yield path


def members(folder, match):
    return sorted(p for p in folder.iterdir() if p.is_file() and match(p.name))


def pack(folder, group, match, apply_changes):
    names = members(folder, match)
    if not names:
        return 0, 0
    archive = folder / (group + '.zip')
    if archive.exists():
        raise SystemExit(f'{archive} already exists; restore or remove it first')
    total = sum(p.stat().st_size for p in names)
    if not apply_changes:
        return len(names), total

    entries = {}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in names:
            raw = path.read_bytes()
            zf.writestr(path.name, raw)
            entries[path.name] = {'bytes': len(raw), 'sha256': sha256(raw)}

    # Read the archive back before anything is deleted.
    with zipfile.ZipFile(archive) as zf:
        for name, want in entries.items():
            got = zf.read(name)
            if len(got) != want['bytes'] or sha256(got) != want['sha256']:
                archive.unlink()
                raise SystemExit(f'{archive}: {name} did not survive the round trip')
    for path in names:
        path.unlink()

    ledger = folder / 'ARCHIVE.json'
    record = json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {}
    record[group] = {'files': len(entries), 'bytes': total,
                     'archive_bytes': archive.stat().st_size,
                     'archive_sha256': sha256(archive.read_bytes()),
                     'members': entries}
    ledger.write_text(json.dumps(record, indent=1, sort_keys=True), encoding='utf-8')
    return len(entries), total


def verify(base):
    bad = kept = 0
    for ledger in sorted(base.rglob('ARCHIVE.json')):
        record = json.loads(ledger.read_text(encoding='utf-8'))
        for group, block in record.items():
            archive = ledger.parent / (group + '.zip')
            if not archive.exists():
                print(f'MISSING {archive}')
                bad += 1
                continue
            if sha256(archive.read_bytes()) != block['archive_sha256']:
                print(f'CHANGED {archive}')
                bad += 1
                continue
            with zipfile.ZipFile(archive) as zf:
                held = set(zf.namelist())
                for name, want in block['members'].items():
                    if name not in held or sha256(zf.read(name)) != want['sha256']:
                        print(f'CORRUPT {archive}::{name}')
                        bad += 1
            kept += len(block['members'])
    print(f'{kept} archived files verified, {bad} problems')
    return bad


def restore(folder):
    ledger = folder / 'ARCHIVE.json'
    record = json.loads(ledger.read_text(encoding='utf-8'))
    written = 0
    for group, block in record.items():
        with zipfile.ZipFile(folder / (group + '.zip')) as zf:
            for name, want in block['members'].items():
                raw = zf.read(name)
                if sha256(raw) != want['sha256']:
                    raise SystemExit(f'{name}: SHA-256 does not match the ledger')
                (folder / name).write_bytes(raw)
                written += 1
    print(f'restored {written} files into {folder}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='reports', help='tree to walk')
    parser.add_argument('--apply', action='store_true', help='write archives and remove the originals')
    parser.add_argument('--verify', action='store_true', help='check every ARCHIVE.json against its ZIP')
    parser.add_argument('--restore', metavar='FOLDER', help='unpack one folder back to individual files')
    args = parser.parse_args()
    base = (ROOT / args.base).resolve()

    if args.restore:
        return restore(Path(args.restore).resolve())
    if args.verify:
        raise SystemExit(1 if verify(base) else 0)

    files = byte_total = 0
    for folder in folders(base):
        for group, match in GROUPS.items():
            count, size = pack(folder, group, match, args.apply)
            if count:
                files += count
                byte_total += size
                print(f'{"packed" if args.apply else "would pack"} {count:5d} {group:8s} {folder.relative_to(ROOT).as_posix()}')
    verb = 'Packed' if args.apply else 'Would pack'
    print(f'{verb} {files} files ({byte_total/2**20:.1f} MiB) into per-folder archives')


if __name__ == '__main__':
    main()
