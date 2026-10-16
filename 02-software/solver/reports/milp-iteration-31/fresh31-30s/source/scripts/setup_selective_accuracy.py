"""Predeclare iteration18 plans and fetch bounded public holdout inputs."""
import datetime
import gzip
import io
import json
import os
from pathlib import Path
import re
import ssl
import urllib.request
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    out=ROOT/'reports/milp-iteration-18';names=['danoint','rout','mas76'];prior=[]
    pattern=re.compile(r'\b(?:danoint|rout|mas76)\b')
    for root,dirs,files in os.walk(ROOT/'reports'):
        dirs[:]=[d for d in dirs if d not in ('source','final-source','milp-iteration-18','__pycache__')]
        for f in files:
            if f in ('results.json','manifest.json','summary.json','SUMMARY.json','metadata.json'):
                p=Path(root)/f
                if pattern.search(p.read_text(encoding='utf-8')):prior.append(str(p))
    for p in (ROOT/'datasets').rglob('*.mps'):
        if p.stem in names:prior.append(str(p))
    assert not prior,prior
    plan=json.loads((ROOT/'reports/milp-iteration-17/WAVE.json').read_text())
    plan['common'].append('--capture-refinement')
    plan['profiles']={'baseline':[],'selective':['--refine-basis','--refine-at-checks']}
    for file,models,repeats in [('WAVE.json',plan['models'],1),('SCREEN.json',['p0201','eil33-2','mas74'],2),('HOLDOUT.json',names,1)]:
        target=out/file;assert not target.exists()
        save(target,{**plan,'models':models,'repeats':repeats,'manifests':plan['manifests']+(['datasets/milp-accuracy-holdout/manifest.json'] if file=='HOLDOUT.json' else [])})
    dest=ROOT/'datasets/milp-accuracy-holdout';dest.mkdir(parents=True,exist_ok=False)
    import certifi
    context=ssl.create_default_context(cafile=certifi.where())
    manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':names,
        'prior_results_matches':prior,'plan_sha256':sha(out/'HOLDOUT_PLAN.md'),'script_sha256':sha(Path(__file__)),'instances':[]}
    for name in names:
        url=f'https://miplib.zib.de/WebData/instances/{name}.mps.gz'
        s={'name':name,'url':url,'metadata_url':f'https://miplib.zib.de/instance_details_{name}.html','new_case':True}
        try:
            with urllib.request.urlopen(url,context=context,timeout=30) as f:raw=f.read(16*1024*1024+1)
            assert len(raw)<=16*1024*1024
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:data=f.read(64*1024*1024+1)
            assert len(data)<=64*1024*1024 and b'ENDATA' in data
            packed=dest/(name+'.mps.gz');packed.write_bytes(raw);model=dest/(name+'.mps');model.write_bytes(data)
            s.update(status='ready',model=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),raw_sha256=sha(packed),bytes=len(data))
        except Exception as e:s.update(status='download_failed',error=repr(e))
        manifest['instances'].append(s);save(dest/'manifest.json',manifest);print(name,s['status'],flush=True)
    assert all(s['status']=='ready' for s in manifest['instances'])

if __name__=='__main__':main()
