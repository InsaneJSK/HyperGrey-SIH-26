"""Focused, equal-budget MILP experiments; references never enter our solver."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import psutil
from benchmark_lp import ROOT,run


def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main(args):
    if args.limit<=0 or args.nodes<=0 or args.reference_limit<0:raise ValueError('Invalid limits')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    build=(ROOT/args.build).resolve();binary=build/('solver_cli.exe' if os.name=='nt' else 'solver_cli')
    experiment=getattr(args,'experiment','branching')
    variants={'fractionality':['--branching','fractionality'],'reliability':['--branching','reliability']}
    generated_variants=dict(variants)
    if experiment=='recovery':
        control=['--branching','fractionality','--capture-lp-failure']
        variants={'control':control,'recovery_neighborhood':control+['--lp-recovery','--improve-incumbent']}
        generated_variants={**variants,'recovery_only':control+['--lp-recovery']}
    if experiment=='repair':
        baseline=['--branching','fractionality','--lp-recovery','--improve-incumbent','--capture-lp-failure','--capture-rejected-candidates']
        variants={'baseline':baseline,'candidate_repair':baseline+['--repair-candidates']}
        generated_variants={**variants,'legacy_control':['--branching','fractionality']}
    if experiment=='neighborhood':
        common=['--branching','fractionality','--lp-recovery','--improve-incumbent','--repair-candidates',
                '--capture-lp-failure','--capture-rejected-candidates','--capture-neighborhood']
        variants={'guided':common+['--neighborhood','guided'],'diversified':common+['--neighborhood','diversified']}
        generated_variants={**variants,'legacy_control':['--branching','fractionality']}
    if experiment=='pacing':
        common=['--branching','fractionality','--lp-recovery','--improve-incumbent','--repair-candidates',
                '--capture-lp-failure','--capture-rejected-candidates','--capture-neighborhood','--neighborhood','guided']
        variants={'guided':common,'paced':common+['--pace-neighborhood']}
        generated_variants={**variants,'legacy_control':['--branching','fractionality']}
    if experiment=='reserved':
        common=['--branching','fractionality','--lp-recovery','--improve-incumbent','--repair-candidates',
                '--capture-lp-failure','--capture-rejected-candidates','--capture-neighborhood']
        variants={'guided':common+['--neighborhood','guided'],'reserved':common+['--neighborhood','reserved']}
        generated_variants={**variants,'legacy_control':['--branching','fractionality']}
    if experiment=='binary_meet':
        common=['--branching','fractionality','--lp-recovery','--improve-incumbent','--repair-candidates',
                '--capture-lp-failure','--capture-rejected-candidates','--capture-neighborhood','--neighborhood','guided']
        variants={'guided':common,'binary_meet':common+['--binary-meet']}
        generated_variants={**variants,'legacy_control':['--branching','fractionality']}
    selected_strategies=getattr(args,'strategies',None)
    if selected_strategies:
        if not set(selected_strategies)<=set(variants):raise ValueError('Unknown strategy for selected experiment')
        variants={name:flags for name,flags in variants.items() if name in selected_strategies}
    metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'profile':'milp_focus',
              'platform':platform.platform(),'python':sys.version,'physical_cores':psutil.cpu_count(logical=False),
              'logical_cores':psutil.cpu_count(),'ram_bytes':psutil.virtual_memory().total,
              'binary_sha256':sha(binary),'cmake_sha256':sha(ROOT/'CMakeLists.txt'),
              'cmake_cache_sha256':sha(build/'CMakeCache.txt'),'time_limit_seconds':args.limit,'node_limit':args.nodes,
              'reference_limit_seconds':args.reference_limit,'experiment':experiment,'strategies':list(variants),
              'strategy_flags':variants,'generated_strategy_flags':generated_variants,
              'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for folder in ('src','include','tests','scripts','docs') for p in sorted((ROOT/folder).rglob('*')) if p.suffix in ('.cpp','.hpp','.cu','.py','.md','.ps1')},
              'protocol':'One sequential run per strategy/model, alternating order by model; equal time/node/gap limits. References after all timed runs. CPU only.'}
    save(output/'metadata.json',metadata)
    shutil.copy2(build/'CMakeCache.txt',output/'CMakeCache.txt')
    checked=subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure'],capture_output=True,text=True)
    (output/'ctest.log').write_text(checked.stdout+checked.stderr)
    if checked.returncode:raise RuntimeError('C++ regression failure')
    import test_milp,test_mixed_v2
    groups={}
    for strategy,flags in generated_variants.items():
        test_milp.main(output/(strategy+'-binary'),True,binary,flags)
        test_mixed_v2.main(output/(strategy+'-mixed'),binary,flags)
        for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
            entries=json.loads((output/(strategy+'-'+kind)/file).read_text())
            groups['generated_'+strategy+'_'+kind]={'passed':sum(bool(r['passed']) for r in entries),'total':len(entries)}
    generated_ok=all(g['passed']==g['total'] for g in groups.values())
    save(output/'summary.json',{'groups':groups,'all_generated_passed':generated_ok,'hard_runs_completed':False,'gpu_verified':False})
    if not generated_ok:raise RuntimeError('Generated MILP checks failed; hard runs were not started')
    records=[];models={}
    specs=json.loads((ROOT/'datasets/miplib2017/manifest.json').read_text())['instances']
    selected=getattr(args,'models',None)
    if selected:specs=[spec for spec in specs if spec['name'] in selected]
    for index,spec in enumerate(specs):
        name=spec['name'];model=ROOT/'datasets/miplib2017'/(name+'.mps');models[name]=model
        assert sha(model)==spec.get('mps_sha256',spec.get('model_sha256')), 'Dataset changed: '+name
        for strategy in (metadata['strategies'] if index%2==0 else metadata['strategies'][::-1]):
            command=[str(binary),str(model),'--milp','--json',*variants[strategy],'--time-limit',str(args.limit),'--node-limit',str(args.nodes),'--gap','1e-6']
            ours=run(command,args.limit+20);key=name+'.'+strategy;save(output/(key+'.ours.json'),ours)
            record={k:ours.get(k) for k in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds','first_incumbent_seconds','strong_branch_probes','strong_branch_seconds','pseudocost_updates','lp_recovery_attempts','lp_recovery_successes','lp_recovery_seconds','deferred_nodes','unresolved_nodes','neighborhood_calls','neighborhood_nodes','neighborhood_improvements','neighborhood_seconds','rejected_integer_candidates','candidate_repair_attempts','candidate_repair_successes','repair_branch_nodes','candidate_repair_seconds')}
            record.update(name=name,strategy=strategy,key=key,model_sha256=sha(model),command=command)
            records.append(record);save(output/'results.json',records)
            print(name,strategy,record['status'],'objective',record['objective'],'gap',record['gap'],flush=True)
    references={};unsafe=[]
    for record in records:
        name,key=record['name'],record['key'];candidate=output/(key+'.ours.json')
        ref=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(models[name]),'--candidate',str(candidate),'--limit',str(0 if name in references else args.reference_limit)],args.reference_limit+20)
        save(output/(key+'.reference.json'),ref);references.setdefault(name,ref)
        ours=json.loads(candidate.read_text());obj=record['objective'];value=ref.get('candidate_recomputed_objective')
        valid=bool(obj is not None and value is not None and math.isfinite(obj) and abs(obj-value)<=1e-7*(1+abs(obj))
                   and ref.get('candidate_max_violation',math.inf)<=1e-7 and ref.get('candidate_integer_violation',math.inf)<=1e-7)
        record.update(candidate_verified=valid,independent_max_violation=ref.get('candidate_max_violation'),
                      independent_integer_violation=ref.get('candidate_integer_violation'),
                      reference_status=references[name].get('status'),reference_objective=references[name].get('objective'))
        expected=record['reference_objective']
        record['completed_verified']=bool(valid and record['status'] in ('optimal','gap_limit') and record['reference_status']=='Optimal'
                                          and expected is not None and abs(obj-expected)<=1e-6*(1+abs(expected)))
        if ((ours.get('primal') or obj is not None) and not valid) or record['status'] in ('error','process_error','external_timeout','numerical_error'):
            unsafe.append(key)
        if record['status'] in ('optimal','gap_limit') and not valid:unsafe.append(key)
        if record['status']=='infeasible' and expected is not None:unsafe.append(key)
        if record['status'] in ('optimal','gap_limit') and record['reference_status']=='Optimal' and not record['completed_verified']:unsafe.append(key)
        bound=record['best_bound']
        if bound is not None and ((obj is not None and bound>obj+1e-6*(1+abs(obj))) or
                                  (record['reference_status']=='Optimal' and expected is not None and bound>expected+1e-6*(1+abs(expected)))):unsafe.append(key)
    save(output/'results.json',records)
    summary={'profile':'milp_focus','experiment':experiment,'groups':groups,'all_generated_passed':generated_ok,'hard_runs_completed':True,
             'hard_run_count':len(records),'verified_candidates':sum(r['candidate_verified'] for r in records),
             'completed_reference_comparisons':sum(r['completed_verified'] for r in records),'unsafe_or_error_runs':sorted(set(unsafe)),
             'gpu_verified':False,'gpu_note':'MILP implementation is CPU-only; GPU acceleration is neither requested nor claimed.',
             'interpretation':'Experimental options are not promoted based on one timing pass. Limits and unresolved relaxations remain incomplete results, not infeasibility or optimality.'}
    save(output/'summary.json',summary)
    lines=['# Focused hard-MILP comparison','',metadata['protocol'],'',
           '| Model | Strategy | Status | Objective | Gap | Verified candidate |','| --- | --- | --- | ---: | ---: | --- |']
    lines += [f"| {r['name']} | {r['strategy']} | {r['status']} | {r['objective']} | {r['gap']} | {r['candidate_verified']} |" for r in records]
    lines += ['','Generated correctness: '+str(generated_ok)+'.','',summary['interpretation'],
              '','Inspect results.json, raw candidate/reference files, and incumbent_trace before choosing a default.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)
    return 1 if unsafe else 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--build',default='build-milp-focus')
    p.add_argument('--limit',type=float,default=180);p.add_argument('--nodes',type=int,default=250000);p.add_argument('--reference-limit',type=float,default=30)
    p.add_argument('--experiment',choices=['branching','recovery','repair','neighborhood','pacing','reserved','binary_meet'],default='branching')
    p.add_argument('--strategies',nargs='+',help='Optional single-strategy screen; omitted for a fresh paired comparison')
    p.add_argument('--models',nargs='+',choices=['blend2','binkar10_1','markshare_4_0'],help='Optional focused local subset; full comparisons default to all three')
    raise SystemExit(main(p.parse_args()))
