"""Analytically known MILPs that exercise production early-stop work thresholds."""
import argparse
import json
import math
from pathlib import Path
from benchmark_lp import ROOT
from milp_robustness import timed,reference
from validate_binary_proof import sha,save
from validate_milp_frontier import verify
from check_cut_policy import check as policy_check
from check_milp_work import check as work_check

def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve();digest=sha(binary)
    pairs,chain,cost,profit=40,320,1000,100
    # Each independent binary pair has x+y<=1 since 2x+2y<=3. The continuous
    # chain has u[i]=i+1 exactly. Its cost is a fixed, analytically known term.
    minimum=cost*chain*(chain+1)//2-pairs*profit
    records=[]
    for sense,sign in [('MIN',1),('MAX',-1)]:
        lines=['NAME CUT_STOP_'+sense,'OBJSENSE',' '+sense,'ROWS',' N OBJ']
        lines += [f' L K{i}' for i in range(pairs)]+[f' E C{i}' for i in range(chain)]+['COLUMNS']
        for i in range(pairs):
            for prefix in ('X','Y'):lines += [f' {prefix}{i} OBJ {-sign*profit}',f' {prefix}{i} K{i} 2']
        for i in range(chain):
            lines += [f' U{i} OBJ {sign*cost}',f' U{i} C{i} 1']
            if i+1<chain:lines += [f' U{i} C{i+1} -1']
        lines += ['RHS']+[f' B K{i} 3' for i in range(pairs)]+[f' B C{i} 1' for i in range(chain)]+['BOUNDS']
        lines += [f' BV B {prefix}{i}' for i in range(pairs) for prefix in ('X','Y')]+['ENDATA']
        model=out/(sense+'.mps');model.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        for profile,extra in [('baseline',[]),('adaptive',['--adaptive-cut-rounds'])]:
            key=sense+'.'+profile
            r=timed([str(binary),str(model),'--milp','--json','--no-presolve','--no-heuristics','--time-limit','30','--node-limit','1',
                     '--gap','0','--capture-work','--capture-frontier','--capture-cut-rounds',*extra],45,out/key)
            save(out/(key+'.ours.json'),r);ref=reference(model,r,5);save(out/(key+'.reference.json'),ref)
            category,errors,audits=verify(model,r,ref,out,key,0);p=policy_check(r);w=work_check(r)
            tolerance=max(1e-7,4*math.ulp(float(minimum)))
            assert not errors and r['best_bound'] is not None and sign*r['best_bound']<=minimum+tolerance,(key,errors,r)
            if r.get('primal'):assert sign*r['objective']>=minimum-tolerance
            if profile=='adaptive':
                assert p['stops_checked']>=1 and r['status']=='node_limit' and r['gap'] is None,(key,r)
            else:
                assert category=='numerical_completion_checked' and abs(sign*r['objective']-minimum)<=tolerance,(key,r)
            records.append({'key':key,'all_pass':True,'model_sha256':sha(model),'ours_sha256':sha(out/(key+'.ours.json')),
                'reference_sha256':sha(out/(key+'.reference.json')),'expected_objective':sign*minimum,'status':r['status'],
                'category':category,'rounds_checked':p['rounds_checked'],'stops_checked':p['stops_checked'],'best_bound':r['best_bound']})
            save(out/'results.json',records);print(key,'analytic bound/stop check PASS',flush=True)
    assert sha(binary)==digest
    save(out/'SUMMARY.json',{'all_pass':True,'models':2,'runs':len(records),'production_stops':sum(r['stops_checked'] for r in records),
         'binary_sha256':digest,'runner_sha256':sha(Path(__file__)),'results_sha256':sha(out/'results.json'),
         'scope':'Exact analytically known optimum of separable pairs plus fixed continuous chain. Observed general solver bounds are still numerical; no imported incumbents.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
