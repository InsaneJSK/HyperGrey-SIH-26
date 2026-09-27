"""Sequential local cut experiment; independent references/checks after timings."""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from benchmark_lp import ROOT,run
from validate_binary_proof import sha,save
from check_lifted_covers import check as check_cuts
from exact_binary_check import check as check_exact,parse_mps

if not __debug__:raise RuntimeError('Validation requires assertions')

def main(args):
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    build=(ROOT/args.build).resolve();binary=build/('solver_cli.exe' if os.name=='nt' else 'solver_cli')
    common=['--lp-recovery','--improve-incumbent','--repair-candidates','--capture-neighborhood','--capture-lp-failure','--capture-rejected-candidates']
    profiles={'guided':common,'lifted':common+(['--late-lifted-covers'] if args.late else ['--lifted-covers'])}
    metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':sha(binary),'cmake_sha256':sha(ROOT/'CMakeLists.txt'),
              'cmake_cache_sha256':sha(build/'CMakeCache.txt'),'profiles':profiles,'limit':args.limit,'nodes':args.nodes,'root_only':args.root_only,'repeats':args.repeats,
              'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for folder in ('src','include','tests','scripts') for p in (ROOT/folder).glob('*') if p.suffix in ('.cpp','.hpp','.cu','.py')},
              'protocol':'Sequential equal-budget runs, alternating order by model and repeat; independent references/cut checks AFTER all timed runs. CPU only.'}
    save(output/'metadata.json',metadata);shutil.copy2(build/'CMakeCache.txt',output/'CMakeCache.txt')
    test=subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure'],capture_output=True,text=True)
    (output/'ctest.log').write_text(test.stdout+test.stderr);assert test.returncode==0
    generated={};generated_cuts=0
    if not args.root_only:
        import test_milp,test_mixed_v2
        for profile,flags in {**profiles,'proof':common+['--lifted-covers','--binary-proof']}.items():
            test_milp.main(output/(profile+'-binary'),True,binary,flags);test_mixed_v2.main(output/(profile+'-mixed'),binary,flags)
            for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
                data=json.loads((output/(profile+'-'+kind)/file).read_text());assert len(data)==40 and all(x['passed'] for x in data);generated[profile+'-'+kind]=40
            for path in (output/(profile+'-binary')).glob('*.result.json'):
                model=path.with_name(path.name.replace('.result.json','.mps'));result=json.loads(path.read_text())
                generated_cuts+=check_cuts(model,result)['cuts_checked']
                if result['binary_proof']['verified']:assert check_exact(parse_mps(model.read_text()),result)['all_checks_pass']
    records=[];models=[]
    for name in args.models:
        folder='miplib' if name=='p0033' else 'miplib2017';model=ROOT/'datasets'/folder/(name+'.mps')
        specs=json.loads((model.parent/'manifest.json').read_text())['instances'];spec=next(s for s in specs if s['name']==name)
        assert sha(model)==spec.get('mps_sha256',spec.get('model_sha256'));models.append(model)
    for i,model in enumerate(models):
        for repeat in range(args.repeats):
            order=list(profiles) if (i+repeat)%2==0 else list(profiles)[::-1]
            for profile in order:
                flags=profiles[profile]+(['--no-heuristics'] if args.root_only else [])
                command=[str(binary),str(model),'--milp','--json',*flags,'--time-limit',str(args.limit),'--node-limit',str(args.nodes),'--gap','1e-6']
                ours=run(command,args.limit+20);key=f'{model.stem}.{profile}.{repeat}';save(output/(key+'.ours.json'),ours)
                records.append({'key':key,'model':str(model),'model_sha256':sha(model),'profile':profile,'repeat':repeat,'command':command,
                                **{field:ours.get(field) for field in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds','root_bound_before_cuts','root_bound_after_cuts','lifted_cover_seconds')}})
                save(output/'results.json',records);print(key,ours['status'],'objective',ours['objective'],'bound',ours['best_bound'],'root',ours['root_bound_after_cuts'],flush=True)
    checks=[];references={};points=0
    for r in records:
        path=output/(r['key']+'.ours.json');ours=json.loads(path.read_text());model=Path(r['model'])
        assert ours['status'] in ('optimal','gap_limit','time_limit','node_limit','unresolved_relaxations'),ours['status']
        checked=check_cuts(model,ours);checks.append({'key':r['key'],'result_sha256':sha(path),'model_sha256':sha(model),**checked})
        ref=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(path),'--limit',str(0 if args.root_only or model.stem in references else 30)],50)
        save(output/(r['key']+'.reference.json'),ref);references.setdefault(model.stem,ref)
        if ours.get('primal'):
            assert ref['candidate_max_violation']<=1e-7 and ref['candidate_integer_violation']<=1e-7
            assert abs(ref['candidate_recomputed_objective']-ours['objective'])<=1e-7*(1+abs(ours['objective']));points+=1
        reference=references[model.stem]
        if reference.get('objective') is not None:
            assert ours['best_bound'] is None or ours['best_bound']<=reference['objective']+1e-6*(1+abs(reference['objective']))
            if reference['status']=='Optimal' and ours['status'] in ('optimal','gap_limit'):
                assert abs(ours['objective']-reference['objective'])<=1e-6*(1+abs(reference['objective']))
    save(output/'cut_checks.json',checks)
    # Preserve markshare's independent exact proof as a post-timing sentinel.
    model=ROOT/'datasets/miplib2017/markshare_4_0.mps'
    sentinel=run([str(binary),str(model),'--milp','--json','--lifted-covers','--binary-proof','--time-limit','30'],45)
    save(output/'markshare-proof-sentinel.json',sentinel);assert check_exact(parse_mps(model.read_text()),sentinel)['all_checks_pass']
    summary={'all_pass':True,'generated':generated,'generated_cuts_checked':generated_cuts,'timed_runs':len(records),
             'public_cuts_checked':sum(x['cuts_checked'] for x in checks),'final_points_checked':points,'markshare_exact_sentinel_pass':True,
             'reference_status':{k:{'status':v['status'],'objective':v.get('objective')} for k,v in references.items()},
             'interpretation':'Root-only screens are not full solves; neutral/regressive profiles remain experimental. No general speedup or exact global MILP claim.'}
    save(output/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',default='build-milp-iter8');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--limit',type=float,default=180);p.add_argument('--nodes',type=int,default=250000);p.add_argument('--repeats',type=int,default=1)
    p.add_argument('--models',nargs='+',default=['binkar10_1'],choices=['binkar10_1','blend2','p0033']);p.add_argument('--root-only',action='store_true')
    p.add_argument('--late',action='store_true',help='Delay checked cuts until a single full-domain half-time restart')
    main(p.parse_args())
