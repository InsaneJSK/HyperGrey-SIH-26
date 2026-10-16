"""Audit reduced-bound timings, retained cuts and saved original-model points."""
import argparse
import json
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT,run
from validate_binary_proof import sha,save
from check_lifted_covers import check as check_cuts
from audit_local_milp import neighborhood_samples

if not __debug__:raise RuntimeError('Audit requires assertions')

def main(args):
    source=args.results.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    read=lambda name:json.loads((source/name).read_text())
    meta=read('metadata.json');summary=read('summary.json');records=read('results.json')
    assert summary['all_pass'] and len(records)==summary['timed_runs']
    assert sha(args.binary)==meta['binary_sha256'] and sha(ROOT/'CMakeLists.txt')==meta['cmake_sha256']
    for name,digest in meta['source_sha256'].items():assert sha(ROOT/name)==digest,name
    assert sha(source/'CMakeCache.txt')==meta['cmake_cache_sha256'] and '100% tests passed' in (source/'ctest.log').read_text()
    assert 'SOVEREIGN_ENABLE_CUDA:BOOL=OFF' in (source/'CMakeCache.txt').read_text()
    assert len({r['key'] for r in records})==len(records)
    for label,count in summary['generated'].items():
        name='enumeration.json' if label.endswith('-binary') else 'summary.json'
        entries=json.loads((source/label/name).read_text())
        assert len(entries)==count and all(e['passed'] for e in entries)
    sys.path.insert(0,str(ROOT/'tools/reference/python'));import highspy
    total_cuts=0;vector_checks=[];hashes={}
    for r in records:
        key=r['key'];model=Path(r['model']);ours=read(key+'.ours.json');command=r['command'];hashes[key]=sha(source/(key+'.ours.json'))
        assert sha(model)==r['model_sha256'] and sha(Path(command[0]))==meta['binary_sha256']
        expected=[str(args.binary.resolve()),str(model),'--milp','--json',*meta['profiles'][r['profile']],*(['--no-heuristics'] if meta['root_only'] else []),
                  '--time-limit',str(float(meta['limit'])),'--node-limit',str(meta['nodes']),'--gap','1e-6']
        assert command==expected
        for field in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds','root_bound_before_cuts','root_bound_after_cuts','lifted_cover_seconds'):
            assert ours.get(field)==r[field],field
        assert ours['lifted_covers_enabled']==any(f in command for f in ('--lifted-covers','--late-lifted-covers'))
        compact=any(f in command for f in ('--compact-equalities','--late-compact-equalities'))
        delayed='--late-compact-equalities' in command
        assert ours.get('late_compact_equalities_enabled',False)==delayed
        assert ours['compact_equalities_enabled']==compact
        assert 0<=ours['compact_lp_fallbacks']<=ours['compact_lp_calls']
        if not compact:assert ours['compact_lp_calls']==ours['compact_lp_fallbacks']==ours['root_compact_equalities']==0
        if delayed and not ours['cut_restarts']:assert ours['compact_lp_calls']==ours['root_compact_equalities']==0
        for field in ('compact_lp_calls','compact_lp_fallbacks','root_lp_rows','root_compact_equalities'):
            assert ours[field]==r[field],field
        reduction=any(f in command for f in ('--reduced-bound-lp','--late-reduced-bound-lp'))
        late_reduction='--late-reduced-bound-lp' in command
        assert ours['reduced_bound_lp_enabled']==reduction and ours['late_reduced_bound_lp_enabled']==late_reduction
        assert 0<=ours['reduced_bound_lp_fallbacks']<=ours['reduced_bound_lp_calls']
        assert 0<=ours['reduced_bound_lp_accepted']<=ours['reduced_bound_lp_calls']
        if not reduction or (late_reduction and not ours['cut_restarts']):
            assert ours['reduced_bound_lp_calls']==ours['root_reduced_upper_bounds']==0
        for field in ('reduced_bound_lp_calls','reduced_bound_lp_fallbacks','reduced_bound_lp_accepted','reduced_upper_candidates','root_reduced_upper_bounds'):
            assert ours[field]==r[field],field
        verified=check_cuts(model,ours);total_cuts+=verified['cuts_checked']
        assert ours['lifted_cover_checked']>=len(ours['lifted_cover_trace']) and ours['cuts']>=len(ours['lifted_cover_trace'])
        reader=highspy.Highs();reader.setOptionValue('output_flag',False);reader.readModel(str(model));lp=reader.getLp()
        integers=[j for j,t in enumerate(lp.integrality_) if t!=highspy.HighsVarType.kContinuous];sign=-1 if lp.sense_==highspy.ObjSense.kMaximize else 1
        trace=ours['incumbent_trace'];obj=ours['objective'];bound=ours['best_bound']
        assert all(0<=t<=ours['total_seconds'] and math.isfinite(v) for t,v in trace)
        assert all(trace[i][0]<=trace[i+1][0] and sign*(trace[i][1]-trace[i+1][1])>0 for i in range(len(trace)-1))
        if obj is not None:
            assert trace[-1][1]==obj
            if bound is not None:assert math.isclose(ours['gap'],max(0,sign*(obj-bound))/(1+abs(obj)),rel_tol=1e-10,abs_tol=1e-12)
        else:assert not trace and not ours['primal']
        # The CLI default is guided when the optional selector is absent.
        diagnostic_command=command if '--neighborhood' in command else command+['--neighborhood','guided']
        samples=neighborhood_samples(ours,diagnostic_command,integers,lp.col_lower_,lp.col_upper_,sign)
        late='--late-lifted-covers' in command
        assert ours.get('late_lifted_covers_enabled',False)==late
        assert ours.get('cut_restarts',0) in (0,1)
        if ours.get('cut_restarts',0):
            assert late and .5*meta['limit']<=ours['cut_restart_seconds']<=ours['total_seconds']
            assert ours['cut_restart_nodes']<ours['nodes']
            carried=ours['cut_restart_bound'];carried_obj=ours['cut_restart_objective']
            if carried is not None and ours['root_bound_after_cuts'] is not None:
                assert sign*(ours['root_bound_after_cuts']-carried)>=-1e-7
            if carried_obj is not None:
                assert any(t<=ours['cut_restart_seconds'] and v==carried_obj for t,v in trace)
                assert sign*(obj-carried_obj)<=1e-7
                assert len(ours['cut_restart_primal'])==lp.num_col_
                samples.append(('restart',ours['cut_restart_primal'],False,carried_obj))
        elif not late:assert not ours.get('cut_restart_primal',[])
        if ours['primal']:samples.append(('final',ours['primal'],False,obj))
        for i,sample in enumerate(ours.get('rejected_candidates',[])):
            if sample.get('repair_accepted'):samples.append((f'repair_{i}',sample['repair_primal'],True,None))
            if sample.get('fallback_accepted'):samples.append((f'fallback_{i}',sample['fallback_primal'],True,None))
        for label,point,round_first,objective in samples:
            assert len(point)==lp.num_col_ and all(math.isfinite(v) for v in point)
            point=list(point)
            if round_first:
                for j in integers:
                    nearest=math.floor(point[j]+.5) if point[j]>=0 else math.ceil(point[j]-.5)
                    assert abs(point[j]-nearest)<=1e-7
                    point[j]=nearest
            path=output/(key+'.'+label+'.json');save(path,{'primal':point})
            ref=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(path),'--limit','0'],20)
            save(output/(key+'.'+label+'.check.json'),ref)
            assert ref['candidate_max_violation']<=1e-7 and ref['candidate_integer_violation']<=1e-7
            if objective is not None:assert abs(ref['candidate_recomputed_objective']-objective)<=1e-7*(1+abs(objective))
            vector_checks.append({'key':key,'sample':label,'objective':objective,'violation':ref['candidate_max_violation']})
    result={'all_pass':True,'source_identity_files':len(meta['source_sha256']),'binary_sha256':meta['binary_sha256'],
            'public_runs':len(records),'independent_cuts_rechecked':total_cuts,'original_model_vectors_checked':len(vector_checks),
            'vectors':vector_checks,'raw_sha256':hashes,'audit_script_sha256':sha(Path(__file__)),
            'limitation':'Only saved final/restart/neighborhood/repair vectors are rechecked. Objective-only intermediate incumbents and all internal LP dual bounds are not independently certified by this audit.'}
    save(output/'AUDIT.json',result);print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args())
