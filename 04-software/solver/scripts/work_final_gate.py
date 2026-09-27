"""Post-comparison regression gate for iteration14 (not a performance run)."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from benchmark_lp import ROOT
from milp_robustness import timed,reference,FLAGS
from validate_binary_proof import sha,save
from validate_milp_frontier import verify,semantic
from check_milp_work import check
import test_milp
import test_mixed_v2

def main(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve()
    def command(name,cmd,cwd=ROOT):
        p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True);(out/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
        assert p.returncode==0,(name,p.stdout,p.stderr);print(name,'PASS',flush=True)
    command('ctest',['ctest','--test-dir',str(binary.parent),'--output-on-failure'])
    command('work-cpp',[str(binary.parent/'solver_work_tests.exe')])
    command('python',[sys.executable,'-X','utf8','-m','unittest','test_milp_robustness','test_exact_binary_check','test_result_parser',
                      'test_milp_diagnostics','test_lifted_cover_check','test_objective_lattice_check','test_milp_frontier_check','test_milp_work_check','-v'],ROOT/'scripts')
    command('marker-contract',[sys.executable,'-X','utf8',str(ROOT/'scripts/check_mps_marker_contract.py'),'--binary',str(binary),
                               '--output',str(out/'marker-contract'),'--require-pass'])
    generated={}
    for n in (0,1,5):
        flags=[*FLAGS,'--objective-lattice','--raw-lp-priority','--capture-work','--capture-frontier','--root-cut-rounds',str(n),'--restart-nodes','2']
        test_milp.main(out/f'round{n}-binary',True,binary,flags);test_mixed_v2.main(out/f'round{n}-mixed',binary,flags)
        for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
            rows=json.loads((out/f'round{n}-{kind}'/file).read_text());assert len(rows)==40 and all(r['passed'] for r in rows)
            generated[f'{n}-{kind}']=len(rows)
        for p in (out/f'round{n}-binary').glob('*.result.json'):check(json.loads(p.read_text()))
        for p in (out/f'round{n}-mixed').glob('case*.json'):check(json.loads(p.read_text()))
    source=ROOT/'reports/milp-iteration-12/generated-lattice';specs=json.loads((source/'results.json').read_text());checks=[]
    for s in specs:
        key=f"generated{s['case']:03d}";model=source/f"case{s['case']:03d}.mps";assert sha(model)==s['model_sha256']
        r=timed([str(binary),str(model),'--milp','--json','--time-limit','5','--objective-lattice','--raw-lp-priority',
                 '--root-cut-rounds','1','--capture-work','--capture-frontier'],20,out/key)
        ref=reference(model,r,5);save(out/(key+'.ours.json'),r);save(out/(key+'.reference.json'),ref)
        category,errors,audits=verify(model,r,ref,out,key,1e-6);check(r)
        assert not errors and category=='numerical_completion_checked' and abs(r['objective']-s['expected'])<=1e-7,(key,errors)
        checks.append({'key':key,'all_pass':True,'model_sha256':sha(model)})
    save(out/'generated-checks.json',checks)
    parity=[];old=ROOT/'reports/milp-iteration-13/final_solver_cli.exe'
    for name in ('gt2','lseu','mod008','misc03'):
        signatures=[]
        for label,b,flags in [('old',old,[]),('off',binary,[]),('on',binary,['--capture-work'])]:
            key=name+'.'+label;r=timed([str(b),str(ROOT/'datasets/milp-robustness-wave1'/(name+'.mps')),'--milp','--json',
                '--objective-lattice','--raw-lp-priority','--capture-frontier','--no-heuristics','--no-cuts','--node-limit','512','--time-limit','120','--gap','0',*flags],135,out/key)
            save(out/(key+'.json'),r);assert r['status']=='node_limit';signatures.append(semantic(r))
            if label!='old':check(r)
        assert len(set(signatures))==1;parity.append(name)
    for flags in (['--root-cut-rounds','6'],['--root-cut-rounds','-1'],['--restart-nodes','0.5']):
        p=subprocess.run([str(binary),str(ROOT/'examples/production.mps'),'--milp','--json',*flags],text=True,capture_output=True)
        assert p.returncode==2 and not p.stdout
    for nodes in (0,2):
        key=f'restart{nodes}';model=ROOT/'datasets/milp-robustness-wave1/gt2.mps'
        r=timed([str(binary),str(model),'--milp','--json','--time-limit','5','--node-limit','32','--no-heuristics',
                 '--late-lifted-covers','--root-cut-rounds','0','--restart-nodes',str(nodes),'--capture-frontier','--capture-work'],20,out/key)
        ref=reference(model,r,5);save(out/(key+'.ours.json'),r);save(out/(key+'.reference.json'),ref)
        category,errors,audits=verify(model,r,ref,out,key,1e-6);check(r)
        assert not errors and r['cut_restarts']==1 and audits['frontier']['resets_checked']==1
    summary={'all_pass':True,'generated':generated,'reused_exhaustive_models':len(checks),'default_parity_models':parity,
             'binary_sha256':sha(binary),'runner_sha256':sha(Path(__file__)),'invalid_cli_cases':3,'counter_restart_cases':2}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
