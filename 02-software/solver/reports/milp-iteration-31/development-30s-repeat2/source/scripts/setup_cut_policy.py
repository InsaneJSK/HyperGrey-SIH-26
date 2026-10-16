"""Materialize the predeclared iteration15 protocols and untouched holdouts."""
import datetime
import gzip
import io
import json
import ssl
import urllib.request
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    report=ROOT/'reports/milp-iteration-15'
    base=json.loads((ROOT/'reports/milp-iteration-14/WAVE.json').read_text())
    base.update(profiles={'baseline':[],'adaptive':['--adaptive-cut-rounds']},reference_watchdog=150)
    base['common']+=['--capture-cut-rounds']
    for name,models,repeats in [('SCREEN',['binkar10_1','p0282','mod008'],1),('REPEATS',['binkar10_1','p0282','mod008'],2),
                                ('WAVE',base['models'],1),('HOLDOUT',['mas74','gen-ip054','neos859080'],1)]:
        plan={**base,'models':models,'repeats':repeats}
        if name=='HOLDOUT':plan['manifests']=['datasets/milp-cut-policy-holdout/manifest.json']
        path=report/(name+'.json');assert not path.exists();save(path,plan)
    out=ROOT/'datasets/milp-cut-policy-holdout';out.mkdir(parents=True,exist_ok=False)
    import certifi
    context=ssl.create_default_context(cafile=certifi.where())
    manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':['mas74','gen-ip054','neos859080'],
              'plan_sha256':sha(report/'PLAN.md'),'benchmark_index':'https://miplib.zib.de/tag_benchmark.html','instances':[]}
    save(out/'manifest.json',manifest)
    for name in manifest['selection']:
        url=f'https://miplib.zib.de/WebData/instances/{name}.mps.gz'
        r={'name':name,'url':url,'metadata_url':f'https://miplib.zib.de/instance_details_{name}.html','new_case':True}
        try:
            with urllib.request.urlopen(url,timeout=30,context=context) as response:data=response.read(16*1024*1024+1)
            if len(data)>16*1024*1024:raise ValueError('Compressed size cap')
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:raw=stream.read(64*1024*1024+1)
            if len(raw)>64*1024*1024 or b'ENDATA' not in raw:raise ValueError('Invalid/oversized MPS')
            packed=out/(name+'.mps.gz');packed.write_bytes(data);model=out/(name+'.mps');model.write_bytes(raw)
            r.update(status='ready',model=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),raw_sha256=sha(packed),bytes=len(raw))
        except Exception as e:r.update(status='download_failed',error=repr(e))
        manifest['instances'].append(r);save(out/'manifest.json',manifest);print(name,r['status'],flush=True)

if __name__=='__main__':main()
