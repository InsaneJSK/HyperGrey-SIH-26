"""Repeated root-only check of a known local regression, never a speedup benchmark."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT,run

def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(args):
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    binary=args.binary.resolve();model=ROOT/'datasets/miplib2017/markshare_4_0.mps'
    checks=[]
    for index in range(3):
        command=[str(binary),str(model),'--milp','--json','--binary-meet','--lp-recovery',
                 '--improve-incumbent','--repair-candidates','--time-limit','20','--node-limit','1','--gap','1e-6']
        ours=run(command,30);save(output/f'root-{index}.ours.json',ours)
        assert ours['binary_meet_eligible'] and ours['binary_meet_completed'] and ours['binary_meet_improved']
        assert ours['status']=='node_limit' and ours['nodes']==1 and ours['best_bound']<=0 and ours['gap']>.49
        assert abs(ours['objective']-1.)<=1e-7 and ours['binary_meet_left_states']==ours['binary_meet_right_states']==32768
        for label,point in [('final',ours['primal']),('meet',ours['binary_meet_primal'])]:
            path=output/f'root-{index}.{label}.candidate.json';save(path,{'primal':point})
            ref=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(path),'--limit','0'],20)
            save(output/f'root-{index}.{label}.reference.json',ref)
            assert ref.get('candidate_max_violation',math.inf)<=1e-7 and ref.get('candidate_integer_violation',math.inf)<=1e-7
            assert abs(ref['candidate_recomputed_objective']-1.)<=1e-7
            checks.append({'repeat':index,'sample':label,'objective':ref['candidate_recomputed_objective'],
                           'max_violation':ref['candidate_max_violation'],'integer_violation':ref['candidate_integer_violation'],
                           'root_search_seconds':ours['binary_meet_seconds'],'first_incumbent_seconds':ours['first_incumbent_seconds']})
    result={'binary_sha256':sha(binary),'model_sha256':sha(model),'script_sha256':sha(Path(__file__)),
            'checks':checks,'all_pass':True,'repeats':3,'global_limit_seconds':20,'node_limit':1,
            'limitation':'Root-only regression on one model; not repeated full-search timing, independent optimality certification or broad public-model coverage.'}
    save(output/'CHECKS.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--binary',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args())
