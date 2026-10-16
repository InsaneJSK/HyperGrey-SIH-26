"""Frozen19/new-disabled/new-disabled-traced fixed-node semantic comparisons."""
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import semantic
from milp_robustness import timed
from check_feasibility_trace import check


def main():
    out=ROOT/'reports/milp-iteration-20/control-parity';out.mkdir(parents=True,exist_ok=False)
    old=ROOT/'reports/milp-iteration-19/final_solver_cli.exe';binary=ROOT/'build-milp-iter20/solver_cli.exe'
    assert sha(old)=='bb14f6adeb88e869a618a185c0fd48d5666134812534d8c350d08166f6642b35'
    digest=sha(binary)
    models={s['name']:s for f in ('milp-robustness-wave1','milp-cut-policy-holdout') for s in json.loads((ROOT/f'datasets/{f}/manifest.json').read_text())['instances']}
    rows=[]
    for name in ('p0201','mas74','lseu','enigma'):
        model=ROOT/models[name]['model'];signatures=[]
        for label,b,flags in [('frozen19',old,[]),('off',binary,[]),('traced',binary,['--capture-feasibility'])]:
            key=name+'.'+label;cmd=[str(b),str(model),'--milp','--json','--node-limit','64','--time-limit','120',
                '--restart-nodes','1000000','--refine-basis','--refine-at-checks','--lp-recovery','--repair-candidates',
                '--repair-heuristic-candidates','--capture-work','--capture-frontier',*flags]
            r=timed(cmd,135,out/key);save(out/(key+'.json'),r);signatures.append(semantic(r))
            if label=='traced':save(out/(key+'.trace-check.json'),check(model,r))
            if label!='frozen19':assert not r['pump_guidance']['enabled'] and r['pump_guidance']['calls']==0
            rows.append({'key':key,'command':cmd,'binary_sha256':sha(b),'model_sha256':sha(model),'result_sha256':sha(out/(key+'.json')),'semantic':signatures[-1]})
        save(out/'results.json',rows);assert len(set(signatures))==1,(name,signatures);print(name,'three-way parity PASS',flush=True)
    assert sha(binary)==digest
    save(out/'SUMMARY.json',{'all_pass':True,'cases':4,'runs':12,'binary_sha256':digest,'frozen19_sha256':sha(old),
        'runner_sha256':sha(Path(__file__)),'results_sha256':sha(out/'results.json')})


if __name__=='__main__':main()
