"""Stage A: arithmetic-preserving instrumentation and fixed-node diagnostics."""
import json
import shutil
import subprocess
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import semantic
from milp_robustness import timed
from check_refinement_work import check

def main():
    out=ROOT/'reports/milp-iteration-18/profile';out.mkdir(parents=True,exist_ok=False)
    build=ROOT/'build-milp-iter18-profile';binary=out/'solver_cli.exe';shutil.copy2(build/'solver_cli.exe',binary)
    old=ROOT/'reports/milp-iteration-17/final_solver_cli.exe';assert sha(old)=='a4b9f9350638f97a5230923554c5788af3c4c95bb552282686aeb408524f88c4'
    sources={}
    for p in [ROOT/'CMakeLists.txt']+[p for d in ('src','include','scripts','tests') for p in (ROOT/d).iterdir() if p.is_file()]:
        rel=p.relative_to(ROOT);dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);sources[rel.as_posix()]=sha(p)
    specs={}
    for manifest in ('milp-robustness-wave1','milp-frontier-holdout','milp-cut-policy-holdout'):
        specs.update({s['name']:s for s in json.loads((ROOT/'datasets'/manifest/'manifest.json').read_text())['instances']})
    cases=[(n,64,False) for n in ('p0201','lseu','enigma','mas74')]+[('eil33-2',4,False),('p0201',64,True)]
    save(out/'metadata.json',{'binary_sha256':sha(binary),'frozen17_sha256':sha(old),'source_sha256':sources,
        'cases':cases,'scope':'Fixed-node diagnostics; not final first-feasible or equal-wall-budget performance evidence.'})
    for name,cmd,cwd in [('ctest',['ctest','--test-dir',str(build),'--output-on-failure'],ROOT),
        ('checker-units',[sys.executable,'-m','unittest','test_refinement_work_check','-v'],ROOT/'scripts')]:
        p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0,(name,p.stdout,p.stderr);print(name,'PASS',flush=True)
    rows=[]
    for name,nodes,restart in cases:
        spec=specs[name];model=ROOT/spec['model'];assert sha(model)==spec['model_sha256'];signatures=[]
        flags=['--late-reduced-bound-lp','--root-cut-rounds','1','--restart-nodes','2'] if restart else ['--no-cuts']
        for label,b,extra in [('frozen17',old,['--refine-basis']),('plain',binary,['--refine-basis']),
            ('traced',binary,['--refine-basis','--capture-refinement']),('unrefined',binary,['--capture-refinement'])]:
            key=f'{name}.{int(restart)}.{label}'
            cmd=[str(b),str(model),'--milp','--json','--no-heuristics','--node-limit',str(nodes),'--time-limit','120',
                '--gap','0','--objective-lattice','--raw-lp-priority','--capture-work','--capture-frontier',*flags,*extra]
            r=timed(cmd,140,out/key);save(out/(key+'.json'),r)
            assert r['status'] not in ('time_limit','timeout','process_error'),(key,r['status'])
            if label!='unrefined':signatures.append(semantic(r))
            checked=check(r) if label!='frozen17' else None
            row={'key':key,'name':name,'restart':restart,'profile':label,'model':spec['model'],'model_sha256':sha(model),'command':cmd,
                'result_sha256':sha(out/(key+'.json')),'semantic':semantic(r),'seconds':r['total_seconds'],'iterations':r['lp_iterations'],
                'nodes':r['nodes'],'status':r['status'],'refinement':checked}
            rows.append(row);save(out/'results.json',rows);print(key,r['status'],r['total_seconds'],checked,flush=True)
        assert len(set(signatures))==1,(name,restart,'Instrumentation changed fixed-node result')
    for rel,digest in sources.items():assert sha(ROOT/rel)==digest
    save(out/'SUMMARY.json',{'all_pass':True,'binary_sha256':sha(binary),'cases':len(cases),'runs':len(rows),
        'three_way_semantic_parity':True,'results_sha256':sha(out/'results.json'),'runner_sha256':sha(ROOT/'scripts/profile_refinement.py')})

if __name__=='__main__':main()
