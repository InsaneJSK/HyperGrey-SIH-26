"""Recheck iteration16 saved outputs and the source of every cut incumbent."""
import argparse
from collections import Counter
import json
from pathlib import Path
from types import SimpleNamespace
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_milp_work import main as work_audit
from check_cut_policy import check as policy_check
from check_cut_incumbents import check as incumbent_check

def main(args):
    work_audit(SimpleNamespace(runs=args.runs,output=args.output,supplemental=None));summaries=[]
    for folder in args.runs:
        rows=json.loads((folder/'results.json').read_text());rounds=stops=points=0;reasons=Counter()
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text())
            c=policy_check(r);inc=incumbent_check(ROOT/row['model'],r)
            assert r['cut_policy']['version']==2
            assert r['cut_policy']['enabled']==('--adaptive-cut-rounds' in row['command'])
            assert r['cut_policy']['require_incumbent']==('--cut-after-incumbent' in row['command'])
            assert c==json.loads((folder/(key+'.policy-check.json')).read_text())
            assert inc==json.loads((folder/(key+'.cut-incumbent-check.json')).read_text())
            save(args.output/folder.name/(key+'.policy-check.json'),c);save(args.output/folder.name/(key+'.cut-incumbent-check.json'),inc)
            rounds+=c['rounds_checked'];stops+=c['stops_checked'];points+=inc['points_checked']
            reasons.update(e['decision'] for e in r['cut_policy']['rounds'])
        summaries.append({'run':folder.name,'records':len(rows),'rounds_checked':rounds,'stops_checked':stops,'incumbents_checked':points,'reasons':dict(reasons),'all_pass':True})
    save(args.output/'POLICY_AUDIT.json',{'all_pass':True,'runs':summaries,
        'checker_sha256':{name:sha(ROOT/'scripts'/name) for name in ('check_cut_policy.py','check_cut_incumbents.py','audit_incumbent_cuts.py')},
        'work_audit_sha256':sha(args.output/'AUDIT.json')})
    print(json.dumps(summaries,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
