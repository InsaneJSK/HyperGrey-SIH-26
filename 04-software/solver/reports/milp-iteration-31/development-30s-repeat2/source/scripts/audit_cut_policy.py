"""Re-audit iteration15 saved outcomes, including cut-policy decisions."""
import argparse
from collections import Counter
import json
from pathlib import Path
from types import SimpleNamespace
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_milp_work import main as audit_work
from check_cut_policy import check

def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    equivalence=ROOT/'reports/milp-iteration-15/reference-equivalence/SUMMARY.json'
    eq=json.loads(equivalence.read_text());assert eq['all_pass'] and eq['models']==21
    assert eq['new_helper_sha256']==sha(ROOT/'scripts/milp_robustness.py')
    audit_work(SimpleNamespace(runs=args.runs,output=args.output,supplemental=None))
    summaries=[]
    for folder in args.runs:
        rows=json.loads((folder/'results.json').read_text());rounds=stops=0;reasons=Counter()
        for r in rows:
            own=json.loads((folder/(r['key']+'.ours.json')).read_text());c=check(own)
            assert c==json.loads((folder/(r['key']+'.policy-check.json')).read_text())
            save(args.output/folder.name/(r['key']+'.policy-check.json'),c)
            rounds+=c['rounds_checked'];stops+=c['stops_checked'];reasons.update(e['decision'] for e in own['cut_policy']['rounds'])
            assert own['cut_policy']['enabled']==('--adaptive-cut-rounds' in r['command'])
            assert own['cut_policy']['capture_enabled']
        summaries.append({'run':folder.name,'records':len(rows),'rounds_checked':rounds,'stops_checked':stops,'reasons':dict(reasons),'all_pass':True})
    save(args.output/'POLICY_AUDIT.json',{'all_pass':True,'runs':summaries,'checker_sha256':sha(ROOT/'scripts/check_cut_policy.py'),
         'audit_sha256':sha(Path(__file__)),'work_audit_sha256':sha(args.output/'AUDIT.json'),'reference_equivalence_sha256':sha(equivalence)})
    print(json.dumps(summaries,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
