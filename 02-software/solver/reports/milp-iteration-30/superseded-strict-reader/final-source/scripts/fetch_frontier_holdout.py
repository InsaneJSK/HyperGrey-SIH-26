"""Fetch the four predeclared untouched iteration13 benchmark models."""
import datetime
import gzip
import io
from pathlib import Path
import ssl
import urllib.request
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

NAMES=['gen-ip002','assign1-5-8','lotsize','eil33-2']


def main():
    out=ROOT/'datasets/milp-frontier-holdout';out.mkdir(parents=True,exist_ok=False)
    try:
        import certifi
        context=ssl.create_default_context(cafile=certifi.where())
    except ImportError:context=ssl.create_default_context()
    manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':NAMES,
              'selection_plan_sha256':sha(ROOT/'reports/milp-iteration-13/HOLDOUT_PLAN.md'),
              'script_sha256':sha(Path(__file__)),'benchmark_index':'https://miplib.zib.de/tag_benchmark.html','instances':[]}
    save(out/'manifest.json',manifest)
    for name in NAMES:
        url=f'https://miplib.zib.de/WebData/instances/{name}.mps.gz'
        r={'name':name,'url':url,'metadata_url':f'https://miplib.zib.de/instance_details_{name}.html','family':'miplib2017_benchmark_holdout','new_case':True}
        try:
            with urllib.request.urlopen(url,timeout=30,context=context) as response:raw=response.read(16*1024*1024+1)
            if len(raw)>16*1024*1024:raise ValueError('Compressed download limit')
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:data=stream.read(64*1024*1024+1)
            if len(data)>64*1024*1024 or b'ENDATA' not in data:raise ValueError('Invalid/oversized MPS')
            packed=out/(name+'.mps.gz');packed.write_bytes(raw);model=out/(name+'.mps');model.write_bytes(data)
            r.update(status='ready',model=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),raw_sha256=sha(packed),bytes=len(data))
        except Exception as e:r.update(status='download_failed',error=repr(e))
        manifest['instances'].append(r);save(out/'manifest.json',manifest);print(name,r['status'],flush=True)


if __name__=='__main__':main()
