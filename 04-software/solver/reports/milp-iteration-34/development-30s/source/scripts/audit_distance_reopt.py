"""Recheck the private handoff and the full inherited saved-run validation chain."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_pump_reopt import main as prior_audit
from check_distance_reopt import check,COUNTS,SEED

def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text());totals=dict.fromkeys(COUNTS+SEED,0)
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text());c=check(r)
            assert c==json.loads((folder/(key+'.distance-reopt-check.json')).read_text())
            assert r['distance_reopt']['enabled']==('--pump-distance-reopt' in row['command'])
            save(a.output/folder.name/(key+'.distance-reopt-check.json'),c)
            for k in totals:totals[k]+=c[k]
        runs.append({'run':folder.name,'records':len(rows),**totals,'all_pass':True})
    save(a.output/'DISTANCE_REOPT_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(ROOT/'scripts/check_distance_reopt.py'),'pump_audit_sha256':sha(a.output/'PUMP_REOPT_AUDIT.json')})
    print(json.dumps(runs,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
