"""Recheck iteration20 saved guidance, final points and inherited proof accounting."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_heuristic_repair import main as prior_audit
from check_pump_guidance import check


def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text());calls=dives=steps=points=0
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text());c=check(ROOT/row['model'],r)
            assert c==json.loads((folder/(key+'.pump-guidance-check.json')).read_text())
            assert r['pump_guidance']['enabled']==('--pump-guided-diving' in row['command'])
            save(a.output/folder.name/(key+'.pump-guidance-check.json'),c)
            calls+=c['calls'];dives+=c['guided_dives'];steps+=c['guided_steps'];points+=c['seed_points_checked']
        runs.append({'run':folder.name,'records':len(rows),'calls':calls,'guided_dives':dives,
                     'guided_steps':steps,'seed_points_checked':points,'all_pass':True})
    save(a.output/'PUMP_GUIDANCE_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(ROOT/'scripts/check_pump_guidance.py'),'heuristic_audit_sha256':sha(a.output/'HEURISTIC_AUDIT.json')})
    print(json.dumps(runs,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
