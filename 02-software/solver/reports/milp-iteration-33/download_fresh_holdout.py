"""Fetch the fresh holdout declared in HOLDOUT_SELECTION.md; keep bytes and failures."""
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
SELECTION = ['rail507', 'ran14x18-disj-8', 'reblock115', 'rmatr100-p10', 'rocI-4-11',
             'roll3000', 's250r10', 'sct2', 'sorrell3', 'sp150x300d']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    out = ROOT / 'datasets/milp-iteration-33-holdout'
    out.mkdir(exist_ok=False)
    manifest = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'selection': SELECTION,
                'selection_sha256': digest((BASE / 'HOLDOUT_SELECTION.md').read_bytes()), 'instances': []}
    for name in SELECTION:
        url = f'https://miplib.zib.de/WebData/instances/{name}.mps.gz'
        row = {'name': name, 'url': url, 'new_case': True}
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                raw = response.read(30_000_001)
                row['response_url'] = response.url
            assert len(raw) <= 30_000_000, 'Archive exceeds declared 30 MB limit'
            (out / (name + '.mps.gz')).write_bytes(raw)
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                data = stream.read(300_000_001)
            assert len(data) <= 300_000_000, 'Model exceeds declared 300 MB limit'
            assert b'ROWS' in data[:4000] and b'ENDATA' in data[-4000:], 'Not an MPS model'
            model = out / (name + '.mps')
            model.write_bytes(data)
            row.update(status='ready', model=model.relative_to(ROOT).as_posix(),
                       model_sha256=digest(data), raw_sha256=digest(raw), bytes=len(data))
        except Exception as error:  # retained, never hidden
            row.update(status='download_failed', error=repr(error))
        manifest['instances'].append(row)
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(name, row['status'], row.get('bytes'), flush=True)
    if any(row['status'] != 'ready' for row in manifest['instances']):
        raise RuntimeError('Retained holdout download failure')


if __name__ == '__main__':
    main()
