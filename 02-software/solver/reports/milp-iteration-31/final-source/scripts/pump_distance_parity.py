"""Frozen20/new distance-disabled semantics and inactive-option checks; not timing evidence."""
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import semantic
from milp_robustness import timed
from check_pump_distance import check

def main():
    out=ROOT/'reports/milp-iteration-21/control-parity';out.mkdir(parents=True,exist_ok=False)
    old=ROOT/'reports/milp-iteration-20/final_solver_cli.exe';binary=ROOT/'build-milp-iter21/solver_cli.exe'
    assert sha(old)=='0da07acbe45aaf097162c93eb8c33ef41321d692337e31dfbb5bab3612ef53d4'
    digest=sha(binary);rows=[];cases=0
    models={s['name']:s for f in ('milp-robustness-wave1','milp-cut-policy-holdout') for s in json.loads((ROOT/f'datasets/{f}/manifest.json').read_text())['instances']}
    for name in ('p0201','lseu','enigma'):
        for guidance in (False,True):
            signatures=[]
            for label,b in [('frozen20',old),('off',binary)]:
                key=f'{name}.{int(guidance)}.{label}';model=ROOT/models[name]['model']
                cmd=[str(b),str(model),'--milp','--json','--node-limit','64','--time-limit','120',
                     '--restart-nodes','1000000','--refine-basis','--refine-at-checks','--lp-recovery','--repair-candidates',
                     '--repair-heuristic-candidates','--capture-work','--capture-frontier']+(['--pump-guided-diving'] if guidance else [])
                r=timed(cmd,135,out/key);save(out/(key+'.json'),r);signatures.append(semantic(r))
                if label=='off':assert not r['pump_distance']['enabled'];check(model,r)
                rows.append({'key':key,'command':cmd,'binary_sha256':sha(b),'model_sha256':sha(model),'result_sha256':sha(out/(key+'.json'))})
            save(out/'results.json',rows);assert signatures[0]==signatures[1],(name,guidance,signatures);cases+=1
            print(name,guidance,'frozen20 parity PASS',flush=True)
    for inactive in ('--no-pump','--no-heuristics'):
        signatures=[];model=ROOT/models['p0201']['model']
        for enabled in (False,True):
            key=f'inactive.{inactive[2:]}.{enabled}'
            cmd=[str(binary),str(model),'--milp','--json','--node-limit','64','--time-limit','120',
                 '--capture-frontier','--pump-guided-diving',inactive]+(['--pump-distance-diving'] if enabled else [])
            r=timed(cmd,135,out/key);save(out/(key+'.json'),r);signatures.append(semantic(r));check(model,r)
            assert r['pump_distance']['dives']==0
            rows.append({'key':key,'command':cmd,'binary_sha256':sha(binary),'model_sha256':sha(model),'result_sha256':sha(out/(key+'.json'))})
        assert signatures[0]==signatures[1];cases+=1;save(out/'results.json',rows)
    assert sha(binary)==digest
    save(out/'SUMMARY.json',{'all_pass':True,'cases':cases,'runs':len(rows),'binary_sha256':digest,'frozen20_sha256':sha(old),
        'runner_sha256':sha(Path(__file__)),'results_sha256':sha(out/'results.json')})

if __name__=='__main__':main()
