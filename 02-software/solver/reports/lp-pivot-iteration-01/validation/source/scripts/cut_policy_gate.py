"""Iteration15 regression/default-parity gate; not a performance measurement."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from milp_robustness import FLAGS,timed,reference
from validate_milp_frontier import semantic,verify
from check_milp_work import check as work_check
from check_cut_policy import check as policy_check
import test_milp
import test_mixed_v2

def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve();digest=sha(binary)
    def command(name,cmd,cwd=ROOT):
        p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
        (out/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,(name,p.stdout,p.stderr)
        print(name,'PASS',flush=True)
    command('ctest',['ctest','--test-dir',str(binary.parent),'--output-on-failure'])
    command('policy-cpp',[str(binary.parent/'solver_cut_policy_tests.exe')])
    command('python',[sys.executable,'-X','utf8','-m','unittest','test_milp_robustness','test_exact_binary_check','test_result_parser',
        'test_milp_diagnostics','test_lifted_cover_check','test_objective_lattice_check','test_milp_frontier_check','test_milp_work_check','test_cut_policy_check','-v'],ROOT/'scripts')
    command('marker-contract',[sys.executable,'-X','utf8',str(ROOT/'scripts/check_mps_marker_contract.py'),
        '--binary',str(binary),'--output',str(out/'marker-contract'),'--require-pass'])
    old=ROOT/'reports/milp-iteration-14/final_solver_cli.exe';assert sha(old)=='f31c1181bc6b775f197a47aee543c9f997955df4a9ff9cb7da61a9820a69df69'
    parity=[];traced=stops=0
    cases=[(n,False) for n in ('gt2','lseu','mod008','misc03')]+[(n,True) for n in ('binkar10_1','p0282','mod008')]
    for name,cuts in cases:
        signatures=[];model=ROOT/'datasets/milp-robustness-wave1'/(name+'.mps')
        # Binkar is in the older MIPLIB dataset; resolve through the manifest.
        specs=json.loads((ROOT/'datasets/milp-robustness-wave1/manifest.json').read_text())['instances']
        entry=next(s for s in specs if s['name']==name);model=ROOT/entry['model'];assert sha(model)==entry['model_sha256']
        flags=['--late-reduced-bound-lp','--restart-nodes','2'] if cuts else ['--no-cuts']
        for label,b,extra in [('old',old,[]),('off',binary,[]),('capture',binary,['--capture-cut-rounds'])]:
            key=f'{name}.{int(cuts)}.{label}'
            r=timed([str(b),str(model),'--milp','--json','--capture-work','--capture-frontier','--objective-lattice','--raw-lp-priority',
                '--no-heuristics','--node-limit',str(3 if cuts else 512),'--time-limit','120','--gap','0',*flags,*extra],150,out/key)
            save(out/(key+'.json'),r);assert r['status'] in ('node_limit','optimal','gap_limit','infeasible'),(key,r['status'])
            signatures.append(semantic(r));work_check(r)
            if label!='old':policy_check(r)
        assert len(set(signatures))==1,(name,cuts,'default/capture trajectory changed')
        parity.append({'model':name,'cuts_enabled':cuts,'semantic_identical':True});print(name,'cut' if cuts else 'node','parity PASS',flush=True)
    generated={};reused=[]
    if not args.quick:
        for profile,extra in [('baseline5',[]),('adaptive0',['--adaptive-cut-rounds','--root-cut-rounds','0']),
                              ('adaptive1',['--adaptive-cut-rounds','--root-cut-rounds','1']),('adaptive5',['--adaptive-cut-rounds'])]:
            flags=[*FLAGS,'--objective-lattice','--raw-lp-priority','--capture-work','--capture-frontier','--capture-cut-rounds','--restart-nodes','2',*extra]
            test_milp.main(out/(profile+'-binary'),True,binary,flags);test_mixed_v2.main(out/(profile+'-mixed'),binary,flags)
            for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
                rows=json.loads((out/(profile+'-'+kind)/file).read_text());assert len(rows)==40 and all(r['passed'] for r in rows)
                generated[profile+'-'+kind]=len(rows)
            paths=list((out/(profile+'-binary')).glob('*.result.json'))+list((out/(profile+'-mixed')).glob('case*.json'))
            for p in paths:
                r=json.loads(p.read_text());work_check(r);c=policy_check(r);traced+=c['rounds_checked'];stops+=c['stops_checked']
        source=ROOT/'reports/milp-iteration-12/generated-lattice'
        for s in json.loads((source/'results.json').read_text()):
            key=f"generated{s['case']:03d}";model=source/f"case{s['case']:03d}.mps";assert sha(model)==s['model_sha256']
            r=timed([str(binary),str(model),'--milp','--json','--time-limit','5','--objective-lattice','--raw-lp-priority',
                '--adaptive-cut-rounds','--capture-cut-rounds','--capture-work','--capture-frontier'],20,out/key)
            ref=reference(model,r,5);save(out/(key+'.ours.json'),r);save(out/(key+'.reference.json'),ref)
            category,errors,checks=verify(model,r,ref,out,key,1e-6);work_check(r);c=policy_check(r)
            assert not errors and category=='numerical_completion_checked' and abs(r['objective']-s['expected'])<=1e-7
            traced+=c['rounds_checked'];stops+=c['stops_checked'];reused.append({'key':key,'all_pass':True,'model_sha256':sha(model)})
        save(out/'reused-checks.json',reused)
    assert sha(binary)==digest
    summary={'all_pass':True,'quick':args.quick,'binary_sha256':digest,'runner_sha256':sha(Path(__file__)),
             'parity':parity,'generated':generated,'reused_models':len(reused),'generated_rounds_checked':traced,'generated_stops_checked':stops}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--quick',action='store_true');main(p.parse_args())
