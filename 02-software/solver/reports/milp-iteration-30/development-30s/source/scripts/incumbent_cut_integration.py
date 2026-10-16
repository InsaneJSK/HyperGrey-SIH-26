"""Analytic MIN/MAX CLI checks for guarded cuts, including source vectors."""
import argparse
import json
from pathlib import Path
from milp_robustness import timed,reference
from validate_binary_proof import sha,save
from validate_milp_frontier import verify
from check_cut_policy import check as policy_check
from check_cut_incumbents import check as incumbent_check
from check_milp_work import check as work_check

def main(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve();digest=sha(binary);records=[]
    for sense,sign in [('MIN',1),('MAX',-1)]:
        for pairs in (40,100):
            lines=['NAME INCUMBENT_CUT','OBJSENSE',' '+sense,'ROWS',' N OBJ']
            lines += [f' L K{i}' for i in range(pairs)]+[f' E C{i}' for i in range(320)]+['COLUMNS']
            for i in range(pairs):
                for prefix in ('X','Y'):lines += [f' {prefix}{i} OBJ {-100*sign}',f' {prefix}{i} K{i} 2']
            for i in range(320):
                lines += [f' U{i} OBJ {1000*sign}',f' U{i} C{i} 1']
                if i<319:lines += [f' U{i} C{i+1} -1']
            lines += ['RHS']+[f' B K{i} 3' for i in range(pairs)]+[f' B C{i} 1' for i in range(320)]+['BOUNDS']
            lines += [f' BV B {prefix}{i}' for i in range(pairs) for prefix in ('X','Y')]+['ENDATA']
            model=out/f'{sense}{pairs}.mps';model.write_text('\n'.join(lines)+'\n',encoding='utf-8');expected=51360000-100*pairs
            for profile,extra in [('baseline',[]),('ungated',['--adaptive-cut-rounds']),('guarded',['--adaptive-cut-rounds','--cut-after-incumbent'])]:
                key=f'{sense}{pairs}.{profile}'
                flags=['--no-heuristics'] if pairs==40 else ['--late-lifted-covers','--restart-nodes','1']
                r=timed([str(binary),str(model),'--milp','--json','--no-presolve','--time-limit','30','--node-limit',str(1 if pairs==40 else 2),
                    '--gap','0','--capture-work','--capture-frontier','--capture-cut-rounds',*flags,*extra],45,out/key)
                save(out/(key+'.ours.json'),r);ref=reference(model,r,5);save(out/(key+'.reference.json'),ref)
                category,errors,checks=verify(model,r,ref,out,key,0);p=policy_check(r);inc=incumbent_check(model,r);work_check(r)
                save(out/(key+'.policy-check.json'),p);save(out/(key+'.incumbent-check.json'),inc)
                assert not errors and r['best_bound'] is not None and sign*r['best_bound']<=expected+1e-6,(key,errors)
                if r.get('primal'):assert sign*r['objective']>=expected-1e-6
                if profile=='guarded':
                    assert category=='numerical_completion_checked' and abs(sign*r['objective']-expected)<=1e-6,(key,r)
                    assert any(e['decision']=='no_incumbent' for e in r['cut_policy']['rounds'])
                    if pairs==100:assert p['stops_checked']>0 and inc['points_checked']==1
                    else:assert p['stops_checked']==0
                if pairs==40 and profile=='ungated':assert r['status']=='node_limit' and not r['primal'] and p['stops_checked']==1
                records.append({'key':key,'all_pass':True,'expected_objective':sign*expected,'status':r['status'],'category':category,
                    'model_sha256':sha(model),'ours_sha256':sha(out/(key+'.ours.json')),'reference_sha256':sha(out/(key+'.reference.json')),
                    'rounds_checked':p['rounds_checked'],'stops_checked':p['stops_checked'],'cut_incumbents_checked':inc['points_checked']})
                save(out/'results.json',records);print(key,category,'PASS',flush=True)
    assert sha(binary)==digest
    save(out/'SUMMARY.json',{'all_pass':True,'models':4,'runs':len(records),'binary_sha256':digest,'runner_sha256':sha(Path(__file__)),
        'results_sha256':sha(out/'results.json'),'stops_checked':sum(r['stops_checked'] for r in records),
        'cut_incumbents_checked':sum(r['cut_incumbents_checked'] for r in records),'scope':__doc__})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
