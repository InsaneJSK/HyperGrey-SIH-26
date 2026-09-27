"""Preselected additional Netlib LPs; data decoding only, no optimizer."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert (ROOT/'reports/milp-iteration-29/screen-30s/SUMMARY.json').is_file()
    out=BASE/'additional-lp-verified';out.mkdir(exist_ok=True)
    original=json.loads((ROOT/'datasets/netlib/manifest.json').read_text())
    working_utility=ROOT/'tools/data/emps.c';data=working_utility.read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(data).hexdigest()==original['utility_sha256']
    utility=out/'emps.c';utility.write_bytes(data)
    os.environ['PATH']=str(ROOT/'tools/local-toolchain/mingw64/bin')+os.pathsep+os.environ['PATH']
    command=[str(ROOT/'tools/local-toolchain/mingw64/bin/gcc.exe'),'-O2',str(utility),'-o',str(out/'emps.exe')]
    if not (out/'emps.exe').exists():
        cp=subprocess.run(command,capture_output=True,text=True,timeout=45)
        (out/'build.log').write_text(cp.stdout+cp.stderr);assert cp.returncode==0
    manifest={'selected_before_solves':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'utility_source_sha256':sha(utility),'working_utility_sha256':sha(working_utility),
              'utility_lf_restored_in_copy_only':sha(utility)!=sha(working_utility),
              'decoder_sha256':sha(out/'emps.exe'),'build_command':command,'instances':[]}
    for name in ('readme','agg','bandm','israel','scagr7'):
        url='https://netlib.org/lp/data/'+name
        raw=out/(name+'.raw')
        if raw.exists():data=raw.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
        assert data and not data.lstrip().lower().startswith((b'<!doctype html',b'<html')),url
        if not raw.exists():raw.write_bytes(data)
        if name=='readme':manifest['readme_sha256']=sha(raw);continue
        cp=subprocess.run([str(out/'emps.exe'),str(raw)],capture_output=True,timeout=10)
        (out/(name+'.decode.stderr')).write_bytes(cp.stderr)
        assert cp.returncode==0 and b'ENDATA' in cp.stdout
        model=out/(name+'.mps');model.write_bytes(cp.stdout)
        manifest['instances'].append({'name':name,'url':url,'raw_sha256':sha(raw),'mps_sha256':sha(model)})
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print('Prepared additional LP',name,len(cp.stdout),flush=True)

if __name__=='__main__':main()
