"""Re-audit iteration18 records and nested refinement accounting."""
import argparse
import json
from pathlib import Path
from validate_binary_proof import sha,save
from check_refinement_work import check
from audit_sparse_accuracy import main as prior_audit

def main(a):
    prior_audit(a);summaries=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text())
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text());checked=check(r)
            assert checked==json.loads((folder/(key+'.refinement-check.json')).read_text())
            assert r['basis_refinement_at_checks']==('--refine-at-checks' in row['command'])
            assert r['work']['refinement_enabled']==('--capture-refinement' in row['command'])
            save(a.output/folder.name/(key+'.refinement-check.json'),checked)
        summaries.append({'run':folder.name,'records':len(rows),'all_pass':True})
    save(a.output/'SELECTIVE_AUDIT.json',{'all_pass':True,'runs':summaries,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(Path(__file__).with_name('check_refinement_work.py')),'accuracy_audit_sha256':sha(a.output/'ACCURACY_AUDIT.json')})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
