"""Fetch the predeclared first breadth wave without modifying old datasets."""
import concurrent.futures
import datetime
import gzip
import json
from pathlib import Path
import ssl
import urllib.request
from benchmark_lp import ROOT
from validate_binary_proof import sha, save

NEW = ['egout', 'gt2', 'lseu', 'mod008', 'p0201', 'p0282', 'misc03', 'misc07', 'pk1', 'rgn']
OLD = {'miplib': ['p0033', 'enigma', 'flugpl', 'stein27'],
       'miplib2017': ['markshare_4_0', 'blend2', 'binkar10_1']}


def main():
    output = ROOT / 'datasets/milp-robustness-wave1'
    output.mkdir(parents=True, exist_ok=False)
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    index = (ROOT / 'datasets/miplib/index.html').read_text()
    assert all('miplib3/' + name + '.mps.gz' in index for name in NEW)
    records = []
    for family, names in OLD.items():
        manifest = json.loads((ROOT / 'datasets' / family / 'manifest.json').read_text())
        for name in names:
            spec = next(s for s in manifest['instances'] if s['name'] == name)
            model = ROOT / 'datasets' / family / (name + '.mps')
            assert sha(model) == spec['model_sha256']
            records.append({'name': name, 'status': 'ready', 'new_case': False,
                            'model': model.relative_to(ROOT).as_posix(), 'model_sha256': sha(model),
                            'url': spec['url'], 'family': family})
    metadata = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'new_selection': NEW, 'existing_selection': OLD,
                'policy': 'Predeclared historical/modern breadth subset, not the full MIPLIB benchmark.',
                'script_sha256': sha(Path(__file__)), 'instances': records}
    save(output / 'manifest.json', metadata)

    def fetch(name):
        url = f'https://miplib2010.zib.de/miplib3/miplib3/{name}.mps.gz'
        record = {'name': name, 'new_case': True, 'url': url, 'family': 'historical_miplib3'}
        try:
            with urllib.request.urlopen(url, timeout=30, context=context) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
            if len(raw) > 16 * 1024 * 1024:
                raise ValueError('Download exceeds first-wave size cap')
            raw_path = output / (name + '.mps.gz'); raw_path.write_bytes(raw)
            data = gzip.decompress(raw)
            if len(data) > 32 * 1024 * 1024 or b'ENDATA' not in data:
                raise ValueError('Invalid/oversized first-wave MPS')
            model = output / (name + '.mps'); model.write_bytes(data)
            record.update(status='ready', model=model.relative_to(ROOT).as_posix(),
                          model_sha256=sha(model), raw_sha256=sha(raw_path), bytes=len(data))
        except Exception as error:
            record.update(status='download_failed', error=str(error))
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(fetch, NEW):
            records.append(record); save(output / 'manifest.json', metadata)
            print(record['name'], record['status'], flush=True)
    print(json.dumps({'selected': len(records), 'ready': sum(r['status'] == 'ready' for r in records)}))


if __name__ == '__main__':
    main()
