"""Fixed-node frozen18/new-off/new-traced semantic parity on fast public cases."""
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import semantic
from milp_robustness import timed
from check_feasibility_trace import check

def main():
    out=ROOT/'reports/milp-iteration-19/control-parity';out.mkdir(parents=True,exist_ok=False)
    old=ROOT/'reports/milp-iteration-18/final_solver_cli.exe';binary=ROOT/'build-milp-iter19/solver_cli.exe'
    models={s['name']:s for f in ('milp-robustness-wave1','milp-cut-policy-holdout') for s in json.loads((ROOT/f'datasets/{f}/manifest.json').read_text())['instances']}
    rows=[]
    for name in ('p0201','mas74','lseu','enigma'):
        model=ROOT/models[name]['model'];signatures=[]
        for label,b,flags in [('frozen18',old,[]),('off',binary,[]),('traced',binary,['--capture-feasibility'])]:
            key=name+'.'+label;cmd=[str(b),str(model),'--milp','--json','--node-limit','64','--time-limit','120',
                '--restart-nodes','1000000','--refine-basis','--refine-at-checks','--lp-recovery','--repair-candidates','--capture-work','--capture-frontier',*flags]
            r=timed(cmd,135,out/key);save(out/(key+'.json'),r);signatures.append(semantic(r))
            if label=='traced':save(out/(key+'.trace-check.json'),check(model,r))
            rows.append({'key':key,'command':cmd,'binary_sha256':sha(b),'model_sha256':sha(model),'result_sha256':sha(out/(key+'.json')),'semantic':signatures[-1]})
        save(out/'results.json',rows);assert len(set(signatures))==1,(name,signatures);print(name,'three-way parity PASS',flush=True)
    save(out/'SUMMARY.json',{'all_pass':True,'cases':4,'runs':12,'binary_sha256':sha(binary),'frozen18_sha256':sha(old),
        'runner_sha256':sha(Path(__file__)),'results_sha256':sha(out/'results.json')})

if __name__=='__main__':main()
