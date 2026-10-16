"""Audit, tabulate and freeze completed experiments without dropping failures."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_binary_proof import sha,save
from validate_milp_frontier import verify
from check_milp_work import check as work_check
from check_cut_policy import check as policy_check
from check_refinement_work import check as refinement_check
from check_feasibility_trace import check as trace_check
from check_heuristic_repair import check as heuristic_check
from check_pump_guidance import check as guidance_check
from check_pump_distance import check as distance_check
from check_pump_reopt import check as pump_check
from check_distance_reopt import check as reopt_check
from check_distance_stage import check as stage_check

def review(base,folders,binary):
    out=base/'audit';out.mkdir(exist_ok=False);facts={};ledgers=[]
    reader=ROOT/'scripts/check_objective_lattice.py'
    expected=json.loads((ROOT/'reports/milp-iteration-14/reader-equivalence/SUMMARY.json').read_text())['new_reader_sha256']
    assert hashlib.sha256(reader.read_bytes().replace(b'\r\n',b'\n')).hexdigest()==expected
    for name in folders:
        folder=base/name;dest=out/name;dest.mkdir()
        meta=json.loads((folder/'metadata.json').read_text());summary=json.loads((folder/'SUMMARY.json').read_text())
        assert not summary['validation_failures'] and summary['results_sha256']==sha(folder/'results.json')
        assert sha(binary)==meta['binary_sha256']
        for rel,h in meta['source_sha256'].items():assert sha(ROOT/rel)==sha(folder/'source'/rel)==h,rel
        plan=meta['plan'];order=[]
        for i,model in enumerate(plan['models']):
            for rep in range(plan.get('repeats',1)):
                profiles=list(plan['profiles']);shift=(i+rep)%len(profiles)
                order += [(model,p,rep) for p in profiles[shift:]+profiles[:shift]]
        rows=json.loads((folder/'results.json').read_text());assert [(r['name'],r['profile'],r['repeat']) for r in rows]==order
        compact=[]
        for row in rows:
            key=row['key'];model=ROOT/row['model'];assert sha(model)==row['model_sha256']
            op=folder/(key+'.ours.json');rp=folder/(key+'.reference.json')
            assert sha(op)==row['ours_sha256'] and sha(rp)==row['reference_sha256']
            ours=json.loads(op.read_text());ref=json.loads(rp.read_text())
            category,errors,_=verify(model,ours,ref,dest,key,plan['gap'])
            assert not errors and category==row['category'],(key,errors)
            assert not category.endswith('_pending'),(key,category)
            for fn in (work_check,policy_check,refinement_check,heuristic_check,pump_check,reopt_check,stage_check):fn(ours)
            for fn in (trace_check,guidance_check,distance_check):fn(model,ours)
            rank=ours['private_ranking'];assert rank['changes']<=rank['ties']<=rank['calls']
            assert rank['enabled']==('--pump-distance-stable-ranking' in row['command'])
            reserve=ours['private_alternate_reserve']
            # A primary rejected by propagation has no LP to cap, but its
            # alternate can still call the LP; these counts have no ordering law.
            assert all(isinstance(reserve[k],int) and reserve[k]>=0 for k in ('alternate_calls','primary_capped'))
            assert reserve['enabled']==('--pump-distance-alternate-reserve' in row['command'])
            if not reserve['enabled']:assert reserve['primary_capped']==reserve['alternate_calls']==0
            if ours['primal']:assert ref['candidate_checked'] and max(ref['candidate_max_violation'],ref['candidate_integer_violation'])<=1e-7
            item={k:row[k] for k in ('key','name','profile','repeat','status','objective','best_bound','gap','nodes','lp_iterations','total_seconds','category')}
            item.update(point=bool(ours['primal']),first_incumbent_seconds=ours['first_incumbent_seconds'],
                        private_ranking=rank,private_alternate_reserve=reserve,cut_restarts=ours.get('cut_restarts'),
                        work=ours['work']['phases'])
            item.update(process_seconds=ours.get('process_seconds'),resources=ours.get('resource_monitor'),
                        reference={k:ref.get(k) for k in ('status','objective','best_bound','gap','solve_seconds','candidate_max_violation','candidate_integer_violation')})
            item['peak_rss_mib']=ours.get('resource_monitor',{}).get('peak_working_set_bytes',0)/1048576 if 'resource_monitor' in ours else None
            item['peak_commit_mib']=ours.get('resource_monitor',{}).get('peak_commit_bytes',0)/1048576 if 'resource_monitor' in ours else None
            compact.append(item)
        profiles={p:{'categories':dict(Counter(r['category'] for r in compact if r['profile']==p)),
                     'points':sum(r['point'] for r in compact if r['profile']==p),
                     'completions':sum(r['category'] in ('numerical_completion_checked','exact_proof_checked') for r in compact if r['profile']==p),
                     'terminal_results':sum(r['category']=='terminal_status_crosschecked' for r in compact if r['profile']==p)} for p in plan['profiles']}
        facts[name]={'profiles':profiles,'records':compact,'results_sha256':sha(folder/'results.json')}
        f=lambda x:'—' if x is None else f'{x:.10g}' if isinstance(x,float) else str(x)
        ledgers += ['# '+name,'','| Run | Status/category | Objective | Bound | Gap | First point s | Total s | Nodes | LP iterations | Peak RSS MiB | Peak commit MiB |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in compact:ledgers.append('| '+r['key']+' | '+r['status']+' / '+r['category']+' | '+' | '.join(f(r[k]) for k in ('objective','best_bound','gap','first_incumbent_seconds','total_seconds','nodes','lp_iterations','peak_rss_mib','peak_commit_mib'))+' |')
        ledgers.append('')
    save(base/'FACTS.json',facts);(base/'MODEL_LEDGER.md').write_text('\n'.join(ledgers),encoding='utf-8')
    save(out/'AUDIT.json',{'all_pass':True,'binary_sha256':sha(binary),'folders':folders,
                         'records':sum(len(f['records']) for f in facts.values()),'points':sum(sum(r['point'] for r in f['records']) for f in facts.values()),
                         'source_verified':True,'reader_lf_equivalence':expected,'review_script_sha256':sha(Path(__file__))})
    print(json.dumps({name:f['profiles'] for name,f in facts.items()},indent=2))

def freeze(base,folders,binary,decision):
    assert decision and not (base/'FINAL_STATE.json').exists()
    audit=json.loads((base/'audit/AUDIT.json').read_text());assert audit['all_pass'] and audit['binary_sha256']==sha(binary)
    assert (base/'REPORT.md').is_file()
    meta=json.loads((base/folders[-1]/'metadata.json').read_text())
    for rel,h in meta['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    shutil.copytree(base/folders[-1]/'source',base/'final-source')
    dataset_snapshot=base/'DATASET_SNAPSHOT.json'
    if dataset_snapshot.exists():
        for rel,h in json.loads(dataset_snapshot.read_text(encoding='utf-8'))['files'].items():
            assert sha(ROOT/rel)==h,rel
            destination=base/'final-source'/rel;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/rel,destination);assert sha(destination)==h
    shutil.copy2(binary,base/'final_solver_cli.exe')
    shutil.copy2(binary.parent/'CMakeCache.txt',base/'FINAL_CMakeCache.txt')
    shutil.copy2(Path(__file__),base/'review-script.py')
    for name in ('libgcc_s_seh-1.dll','libstdc++-6.dll','libgomp-1.dll','libwinpthread-1.dll','libdl.dll'):
        shutil.copy2(ROOT/'tools/local-toolchain/mingw64/bin'/name,base/name)
    hashes={p.relative_to(base).as_posix():sha(p) for p in base.rglob('*') if p.is_file() and p.name not in ('FINAL_STATE.json','SNAPSHOT_MANIFEST.json')}
    save(base/'SNAPSHOT_MANIFEST.json',hashes)
    save(base/'FINAL_STATE.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':sha(binary),
        'decision':decision,'source_sha256':meta['source_sha256'],'audit':audit,'snapshot_manifest_sha256':sha(base/'SNAPSHOT_MANIFEST.json')})
    print('Frozen',base.name,sha(binary))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--folder',action='append',required=True)
    p.add_argument('--binary',type=Path,required=True);p.add_argument('--freeze',action='store_true');p.add_argument('--decision')
    a=p.parse_args();base=a.base.resolve();binary=a.binary.resolve()
    if a.freeze:freeze(base,a.folder,binary,a.decision)
    else:review(base,a.folder,binary)
