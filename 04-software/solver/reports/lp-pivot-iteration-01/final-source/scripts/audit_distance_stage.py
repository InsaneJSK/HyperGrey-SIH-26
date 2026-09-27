"""Recheck staged private LP accounting and all inherited saved-run checks."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_distance_reopt import main as prior_audit
from check_distance_stage import check,FIELDS,COUNTS

def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text());totals=dict.fromkeys(FIELDS,0);reopt=dict.fromkeys(COUNTS,0)
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text());c=check(r)
            assert c==json.loads((folder/(key+'.distance-stage-check.json')).read_text())
            assert r['distance_stage']['enabled']==('--pump-distance-stage' in row['command'])
            save(a.output/folder.name/(key+'.distance-stage-check.json'),c)
            for k in totals:totals[k]+=c[k]
            for k in reopt:reopt[k]+=c['reopt'][k]
        runs.append({'run':folder.name,'records':len(rows),**totals,'reopt':reopt,'all_pass':True})
    save(a.output/'DISTANCE_STAGE_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(ROOT/'scripts/check_distance_stage.py'),'handoff_audit_sha256':sha(a.output/'DISTANCE_REOPT_AUDIT.json')})
    print(json.dumps(runs,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
