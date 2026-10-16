"""Recheck saved iteration17 public outputs, options and proof accounting."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_incumbent_cuts import main as prior_audit

def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text())
        for row in rows:
            r=json.loads((folder/(row['key']+'.ours.json')).read_text())
            assert r['basis_refinement_enabled']==('--refine-basis' in row['command'])
        runs.append({'run':folder.name,'records':len(rows),'refined_runs':sum('--refine-basis' in r['command'] for r in rows),'all_pass':True})
    save(a.output/'ACCURACY_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'work_audit_sha256':sha(a.output/'AUDIT.json'),'policy_audit_sha256':sha(a.output/'POLICY_AUDIT.json'),
        'scope':'Numerical final points, saved structural/proof checks and option identity; not an exact general-MILP proof.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
