"""Post-timing regression and original-model/trace integration checks."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from milp_robustness import timed,reference,FLAGS
from validate_milp_frontier import verify,EXTRA
import test_milp
import test_mixed_v2


def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve()
    commands={'ctest':['ctest','--test-dir',str(binary.parent),'--output-on-failure'],
              'frontier-cpp':[str(binary.parent/'solver_frontier_tests.exe')],
              'python-checkers':[sys.executable,'-X','utf8','-m','unittest','test_milp_robustness','test_exact_binary_check',
                'test_result_parser','test_milp_diagnostics','test_lifted_cover_check','test_objective_lattice_check','test_milp_frontier_check','-v'],
              'marker-contract':[sys.executable,'-X','utf8',str(ROOT/'scripts/check_mps_marker_contract.py'),'--binary',str(binary),
                                 '--output',str(out/'marker-contract'),'--require-pass']}
    for name,command in commands.items():
        p=subprocess.run(command,text=True,capture_output=True,cwd=ROOT/'scripts' if name=='python-checkers' else ROOT)
        (out/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,(name,p.stdout,p.stderr)
        print(name,'PASS',flush=True)
    generated={}
    for profile,flags in EXTRA.items():
        test_milp.main(out/(profile+'-binary'),True,binary,flags);test_mixed_v2.main(out/(profile+'-mixed'),binary,flags)
        for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
            rows=json.loads((out/(profile+'-'+kind)/file).read_text());assert len(rows)==40 and all(r['passed'] for r in rows)
            generated[profile+'-'+kind]=len(rows)
    source=ROOT/'reports/milp-iteration-12/generated-lattice';specs=json.loads((source/'results.json').read_text());checks=[]
    assert len(specs)==100
    for spec in specs:
        key=f"generated{spec['case']:03d}";model=source/f"case{spec['case']:03d}.mps";assert sha(model)==spec['model_sha256']
        ours=timed([str(binary),str(model),'--milp','--json',*EXTRA['raw'],'--capture-frontier','--time-limit','5'],15,out/key)
        ref=reference(model,ours,5);save(out/(key+'.ours.json'),ours);save(out/(key+'.reference.json'),ref)
        category,errors,audits=verify(model,ours,ref,out,key,1e-6)
        assert not errors and category=='numerical_completion_checked' and abs(ours['objective']-spec['expected'])<=1e-7,(key,errors)
        assert not audits['frontier']['trace_truncated']
        checks.append({'key':key,'all_pass':True,'frontier_events':audits['frontier']['events_checked'],'model_sha256':sha(model)})
    save(out/'generated-frontier-checks.json',checks)
    # Short runs are INTEGRATION tests, not additional performance comparisons.
    integration=[]
    for name in ('gt2','p0201','misc03'):
        model=ROOT/'datasets/milp-robustness-wave1'/(name+'.mps');key='late-'+name
        ours=timed([str(binary),str(model),'--milp','--json',*FLAGS,*EXTRA['raw'],'--no-heuristics','--capture-frontier','--time-limit','2'],17,out/key)
        ref=reference(model,ours,5);save(out/(key+'.ours.json'),ours);save(out/(key+'.reference.json'),ref)
        category,errors,audits=verify(model,ours,ref,out,key,1e-6);assert not errors,(key,errors)
        assert ours['cut_restarts']==1 and audits['frontier']['resets_checked']==1 and not audits['frontier']['trace_truncated']
        integration.append({'key':key,'category':category,'all_pass':True,**audits['frontier']})
    # Root LP interruption followed by deferral. Independent optimum is -4.
    path=out/'deferred.mps';lines=['NAME DEFERRED','ROWS',' N OBJ']+[f' L R{i}' for i in range(7)]+['COLUMNS']
    for j in range(8):
        lines.append(f' X{j} OBJ -1')
        for i in range(7):
            if j in (i,i+1):lines.append(f' X{j} R{i} 1')
    lines+=['RHS']+[f' B R{i} 1.5' for i in range(7)]+['BOUNDS']+[f' BV B X{j}' for j in range(8)]+['ENDATA']
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    ours=timed([str(binary),str(path),'--milp','--json',*EXTRA['raw'],'--capture-frontier','--no-presolve','--no-heuristics','--no-cuts',
                '--lp-recovery','--iteration-limit','1','--time-limit','2'],17,out/'deferred')
    ref=reference(path,ours,5);save(out/'deferred.ours.json',ours);save(out/'deferred.reference.json',ref)
    category,errors,audits=verify(path,ours,ref,out,'deferred',1e-6)
    assert not errors and ours['deferred_nodes']>0 and ref['objective']==-4 and not audits['frontier']['trace_truncated']
    integration.append({'key':'deferred','category':category,'all_pass':True,**audits['frontier']})
    save(out/'integration.json',integration)
    summary={'all_pass':True,'commands':commands,'generated':generated,'reused_exhaustive_models':len(checks),
             'generated_frontier_events':sum(r['frontier_events'] for r in checks),'integration':integration,
             'binary_sha256':sha(binary),'runner_sha256':sha(Path(__file__)),'timing_note':'All checks occur after timed experiments.'}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
