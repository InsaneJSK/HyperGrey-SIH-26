"""Local exact-proof experiment: sequential timing, then independent checks."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from benchmark_lp import ROOT,run
from exact_binary_check import parse_mps,check

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main(args):
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    build=(ROOT/args.build).resolve();binary=build/('solver_cli.exe' if os.name=='nt' else 'solver_cli')
    common=['--branching','fractionality','--lp-recovery','--improve-incumbent','--repair-candidates','--neighborhood','guided','--capture-neighborhood']
    profiles={'guided':common,'binary_meet':common+['--binary-meet'],'binary_proof':common+['--binary-meet','--binary-proof']}
    metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'python':sys.version,
              'binary_sha256':sha(binary),'cmake_sha256':sha(ROOT/'CMakeLists.txt'),'cmake_cache_sha256':sha(build/'CMakeCache.txt'),
              'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for folder in ('src','include','tests','scripts') for p in (ROOT/folder).glob('*') if p.suffix in ('.cpp','.hpp','.cu','.py')},
              'profiles':profiles,'time_limit':30,'node_limit':250000,'repeats':3,
              'protocol':'Three sequential runs per profile/model, alternating order. Public models: markshare_4_0 and p0033. Reference and independent integer checks AFTER all timed runs. CPU only.'}
    save(output/'metadata.json',metadata);shutil.copy2(build/'CMakeCache.txt',output/'CMakeCache.txt')
    ctest=subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure'],text=True,capture_output=True)
    (output/'ctest.log').write_text(ctest.stdout+ctest.stderr);assert ctest.returncode==0
    import test_milp,test_mixed_v2
    generated={};generated_exact=[]
    for profile,flags in profiles.items():
        test_milp.main(output/(profile+'-binary'),True,binary,flags);test_mixed_v2.main(output/(profile+'-mixed'),binary,flags)
        for kind,name in [('binary','enumeration.json'),('mixed','summary.json')]:
            entries=json.loads((output/(profile+'-'+kind)/name).read_text());assert len(entries)==40 and all(r['passed'] for r in entries)
            generated[profile+'-'+kind]=len(entries)
    for path in sorted((output/'binary_proof-binary').glob('*.result.json')):
        model=path.with_name(path.name.replace('.result.json','.mps'));verified=check(parse_mps(model.read_text()),json.loads(path.read_text()))
        generated_exact.append({'model':model.name,**verified})
    save(output/'generated_exact_checks.json',generated_exact)
    save(output/'summary.json',{'generated':generated,'generated_exact_checks':len(generated_exact),'timed_runs_complete':False})
    models=[ROOT/'datasets/miplib2017/markshare_4_0.mps',ROOT/'datasets/miplib/p0033.mps'];records=[]
    for model_index,model in enumerate(models):
        for repeat in range(3):
            order=['binary_meet','binary_proof'] if (repeat+model_index)%2==0 else ['binary_proof','binary_meet']
            for profile in order:
                command=[str(binary),str(model),'--milp','--json',*profiles[profile],'--time-limit','30','--node-limit','250000','--gap','1e-6']
                ours=run(command,45);key=f'{model.stem}.{profile}.{repeat}';save(output/(key+'.ours.json'),ours)
                assert ours['status'] in ('optimal','gap_limit','time_limit','node_limit')
                records.append({'key':key,'model':str(model),'model_sha256':sha(model),'profile':profile,'repeat':repeat,'command':command,
                                **{field:ours.get(field) for field in ('status','objective','best_bound','gap','nodes','total_seconds')}})
                save(output/'results.json',records);print(key,ours['status'],ours['objective'],flush=True)
    # Recompute mathematical claims only after measurements finish.
    references={};exact_checks=[]
    for record in records:
        key=record['key'];model=Path(record['model']);path=output/(key+'.ours.json');ours=json.loads(path.read_text())
        reference=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(path),
                       '--limit',str(0 if model.stem in references else 30)],45)
        save(output/(key+'.reference.json'),reference);references.setdefault(model.stem,reference)
        assert reference['candidate_max_violation']<=1e-7 and reference['candidate_integer_violation']<=1e-7
        assert abs(reference['candidate_recomputed_objective']-ours['objective'])<=1e-7*(1+abs(ours['objective']))
        if ours['binary_proof']['verified']:
            verified=run([sys.executable,str(ROOT/'scripts/exact_binary_check.py'),str(model),str(path),'--output',str(output/(key+'.exact.json'))],180)
            assert verified.get('all_checks_pass'),verified
            exact_checks.append({'key':key,**verified})
        if references[model.stem]['status']=='Optimal':assert abs(ours['objective']-references[model.stem]['objective'])<=1e-7
    assert len(exact_checks)==6,'Not all requested exact runs completed and passed independent proof checks'
    save(output/'exact_checks.json',exact_checks)
    summary={'generated':generated,'generated_exact_checks':len(generated_exact),'timed_runs_complete':True,'timed_run_count':len(records),
             'independent_exact_public_checks':len(exact_checks),'independent_final_point_checks':len(records),'all_pass':True,
             'reference_status':{name:{'status':r['status'],'objective':r['objective']} for name,r in references.items()},
             'interpretation':'Two eligible public models plus generated tests; no general MILP speedup, arbitrary-input exact solver or GPU claim.'}
    save(output/'summary.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--build',default='build-milp-iter7');parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args())
