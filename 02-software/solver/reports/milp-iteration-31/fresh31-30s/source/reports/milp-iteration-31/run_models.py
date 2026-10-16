"""Sequential, failure-preserving CPU comparisons with per-run source snapshots."""
import argparse
from collections import Counter
import datetime
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from benchmark_lp import ROOT
import importlib.util
_path=Path(__file__).resolve().parent/'run_contained.py'
_spec=importlib.util.spec_from_file_location('contained',_path)
_module=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_module)
def own_timed(command,timeout,prefix,memory):
    record=_module.monitor(command,prefix,timeout,memory)
    result=dict(record['native_result'] or {'status':record['status']})
    if record['status'] in ('external_timeout','memory_limit','cancelled','process_error','monitor_error'):
        result['status']=record['status']
    result.update(process_seconds=record['wall_seconds'],exit_code=record['exit_code'],
                  resource_monitor={k:v for k,v in record.items() if k!='native_result'})
    stderr=prefix.with_name(prefix.name+'.stderr.log').read_text(encoding='utf-8',errors='replace')
    if stderr:result['stderr']=stderr
    return result
from milp_robustness import timed
from validate_binary_proof import sha,save
from validate_milp_frontier import verify
from check_milp_work import check as work_check
from check_cut_policy import check as policy_check
from check_cut_incumbents import check as cut_incumbent_check
from check_refinement_work import check as refinement_check
from check_feasibility_trace import check as feasibility_check
from check_heuristic_repair import check as heuristic_check
from check_pump_guidance import check as pump_guidance_check
from check_pump_distance import check as pump_distance_check
from check_pump_reopt import check as pump_reopt_check
from check_distance_reopt import check as distance_reopt_check
from check_distance_stage import check as distance_stage_check
from check_private_certificate import check as private_certificate_check
from check_bounded_lp import check as bounded_lp_check
from check_search_heuristics import check as search_heuristics_check

def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve()
    plan=json.loads(args.plan.read_text());models={}
    for f in plan.get('manifests',['datasets/milp-robustness-wave1/manifest.json','datasets/milp-frontier-holdout/manifest.json']):
        models.update({s['name']:s for s in json.loads((ROOT/f).read_text())['instances']})
    files=[ROOT/'CMakeLists.txt',Path(__file__),args.plan.resolve(),_path,Path(__file__).resolve().parent/'CANDIDATE_PROFILE.json']
    files += [p for folder in ('src','include','scripts','tests') for p in (ROOT/folder).iterdir() if p.is_file()]
    identities={}
    for p in set(files):
        rel=p.relative_to(ROOT);dest=out/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        identities[rel.as_posix()]=sha(p);assert sha(dest)==sha(p)
    meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary':str(binary),'binary_sha256':sha(binary),
          'source_sha256':identities,'plan':plan,'plan_path':str(args.plan.resolve()),'own_before_references':True}
    save(out/'metadata.json',meta);records=[]
    for index,name in enumerate(plan['models']):
        s=models[name];assert s['status']=='ready';model=ROOT/s['model'];assert sha(model)==s['model_sha256']
        for repeat in range(plan.get('repeats',1)):
            order=list(plan['profiles']);shift=(index+repeat)%len(order);order=order[shift:]+order[:shift]
            for profile in order:
                key=f'{name}.{profile}.{repeat}'
                command=[str(binary),str(model),'--milp','--json',*plan.get('common',[]),*plan['profiles'][profile],
                         '--time-limit',str(plan['limit']),'--node-limit',str(plan.get('nodes',250000)),'--gap',str(plan.get('gap',1e-6))]
                ours=own_timed(command,plan['limit']+15,out/key,plan['memory_threshold_mib']);save(out/(key+'.ours.json'),ours)
                r={'name':name,'profile':profile,'repeat':repeat,'key':key,'model':s['model'],'model_sha256':sha(model),
                   'command':command,'ours_sha256':sha(out/(key+'.ours.json')),
                   **{k:ours.get(k) for k in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds')}}
                records.append(r);save(out/'results.json',records);print(key,{k:r[k] for k in ('status','objective','gap','nodes')},flush=True)
    for r in records:
        key=r['key'];model=ROOT/r['model'];ours=json.loads((out/(key+'.ours.json')).read_text())
        command=[sys.executable,'-X','utf8',str(ROOT/'scripts/milp_robustness.py'),'--reference',str(model),
                 '--candidate',str(out/(key+'.ours.json')),'--reference-limit',str(plan['reference_limit'])]
        ref=timed(command,plan.get('reference_watchdog',25),out/(key+'.reference'));save(out/(key+'.reference.json'),ref)
        category,errors,checks=verify(model,ours,ref,out,key,plan.get('gap',1e-6))
        try:save(out/(key+'.work-check.json'),work_check(ours))
        except Exception as e:errors.append('work_check: '+repr(e))
        if 'refinement_enabled' in ours.get('work',{}):
            try:save(out/(key+'.refinement-check.json'),refinement_check(ours))
            except Exception as e:errors.append('refinement_check: '+repr(e))
        if 'feasibility' in ours:
            try:save(out/(key+'.feasibility-check.json'),feasibility_check(model,ours))
            except Exception as e:errors.append('feasibility_check: '+repr(e))
        if 'heuristic_repair' in ours:
            try:save(out/(key+'.heuristic-check.json'),heuristic_check(ours))
            except Exception as e:errors.append('heuristic_check: '+repr(e))
        if 'pump_guidance' in ours:
            try:save(out/(key+'.pump-guidance-check.json'),pump_guidance_check(model,ours))
            except Exception as e:errors.append('pump_guidance_check: '+repr(e))
        if 'pump_distance' in ours:
            try:save(out/(key+'.pump-distance-check.json'),pump_distance_check(model,ours))
            except Exception as e:errors.append('pump_distance_check: '+repr(e))
        if 'pump_reopt' in ours:
            try:save(out/(key+'.pump-reopt-check.json'),pump_reopt_check(ours))
            except Exception as e:errors.append('pump_reopt_check: '+repr(e))
        if 'distance_reopt' in ours:
            try:save(out/(key+'.distance-reopt-check.json'),distance_reopt_check(ours))
            except Exception as e:errors.append('distance_reopt_check: '+repr(e))
        if 'distance_stage' in ours:
            try:save(out/(key+'.distance-stage-check.json'),distance_stage_check(ours))
            except Exception as e:errors.append('distance_stage_check: '+repr(e))
        if 'private_dual_certificate' in ours:
            try:save(out/(key+'.private-certificate-check.json'),private_certificate_check(ours))
            except Exception as e:errors.append('private_certificate_check: '+repr(e))
        try:
            heuristics=search_heuristics_check(ours);save(out/(key+'.search-heuristics-check.json'),heuristics)
            for flag,section in (('--tree-dives','tree_dives'),('--fix-propagate','fix_propagate')):
                if ours[section]['enabled']!=(flag in r['command']):errors.append('search_heuristics_check: '+section+' flag mismatch')
        except Exception as e:errors.append('search_heuristics_check: '+repr(e))
        try:
            bounded=bounded_lp_check(ours);save(out/(key+'.bounded-lp-check.json'),bounded)
            if bounded['enabled']!=('--bounded-lp' in r['command']):errors.append('bounded_lp_check: engine flag mismatch')
        except Exception as e:errors.append('bounded_lp_check: '+repr(e))
        if 'cut_policy' in ours:
            try:save(out/(key+'.policy-check.json'),policy_check(ours))
            except Exception as e:errors.append('policy_check: '+repr(e))
            if ours['cut_policy'].get('version',1)>=2:
                try:save(out/(key+'.cut-incumbent-check.json'),cut_incumbent_check(model,ours))
                except Exception as e:errors.append('cut_incumbent_check: '+repr(e))
        r.update(category='validation_failure' if errors else category,validation_errors=errors,reference_sha256=sha(out/(key+'.reference.json')))
        save(out/'results.json',records);print(key,r['category'],errors,flush=True)
    assert sha(binary)==meta['binary_sha256']
    for rel,digest in identities.items():assert sha(ROOT/rel)==digest,rel
    summary={'records':len(records),'models':len(plan['models']),
             'categories':{p:dict(Counter(r['category'] for r in records if r['profile']==p)) for p in plan['profiles']},
             'validation_failures':sum(bool(r['validation_errors']) for r in records),'results_sha256':sha(out/'results.json')}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);main(p.parse_args())
