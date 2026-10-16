"""Re-audit final iteration19 outcomes, trace metrics and repair accounting."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from audit_selective_accuracy import main as prior_audit
from check_feasibility_trace import check as trace_check
from check_heuristic_repair import check as repair_check

def main(a):
    prior_audit(a);runs=[]
    for folder in a.runs:
        rows=json.loads((folder/'results.json').read_text());attempts=successes=0
        for row in rows:
            key=row['key'];r=json.loads((folder/(key+'.ours.json')).read_text())
            t=trace_check(ROOT/row['model'],r);h=repair_check(r)
            assert t==json.loads((folder/(key+'.feasibility-check.json')).read_text())
            assert h==json.loads((folder/(key+'.heuristic-check.json')).read_text())
            assert r['heuristic_repair']['enabled']==('--repair-heuristic-candidates' in row['command'])
            assert r['feasibility']['enabled']==('--capture-feasibility' in row['command'])
            save(a.output/folder.name/(key+'.feasibility-check.json'),t);save(a.output/folder.name/(key+'.heuristic-check.json'),h)
            attempts+=h['attempts'];successes+=h['successes']
        runs.append({'run':folder.name,'records':len(rows),'attempts':attempts,'successes':successes,'all_pass':True})
    save(a.output/'HEURISTIC_AUDIT.json',{'all_pass':True,'runs':runs,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':{n:sha(ROOT/'scripts'/n) for n in ('check_feasibility_trace.py','check_heuristic_repair.py')},
        'selective_audit_sha256':sha(a.output/'SELECTIVE_AUDIT.json')})
    print(json.dumps(runs,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
