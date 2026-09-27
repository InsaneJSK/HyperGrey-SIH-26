"""Recheck iteration22 private reoptimization and every inherited saved-run check."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_pump_distance import main as prior_audit
from check_pump_reopt import check,COUNTS

def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text());totals=dict.fromkeys(COUNTS,0)
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text());c=check(r)
            assert c==json.loads((folder/(key+'.pump-reopt-check.json')).read_text())
            assert r['pump_reopt']['enabled']==('--pump-primal-reopt' in row['command'])
            save(a.output/folder.name/(key+'.pump-reopt-check.json'),c)
            for k in totals:totals[k]+=c[k]
        runs.append({'run':folder.name,'records':len(rows),**totals,'all_pass':True})
    save(a.output/'PUMP_REOPT_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(ROOT/'scripts/check_pump_reopt.py'),'distance_audit_sha256':sha(a.output/'PUMP_DISTANCE_AUDIT.json')})
    print(json.dumps(runs,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
