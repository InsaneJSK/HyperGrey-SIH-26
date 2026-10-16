"""Audit a local hard-MILP run and every captured accepted repair, without solving MILPs.

The core never receives these reference candidates. Run after timed measurements
finish; output must be a new directory so previous evidence cannot be overwritten.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT,run


def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def neighborhood_samples(ours,command,integers,lower,upper,sign):
    """Check diagnostic accounting; returned vectors still need original-MPS checks."""
    captured=ours.get('neighborhood_trace',[]);samples=[]
    reserved=ours.get('neighborhood')=='reserved'
    def material(before,after):return before is None or sign*(before-after)>1e-6*(1+abs(before))
    strong_calls=guided_calls=stalls=0;spent=guided_spent=0.;previous=None;strong_center=None;strong_start=0.
    paced='--pace-neighborhood' in command
    assert ours.get('neighborhood_paced',False)==paced
    if paced:
        spacing=min(5.,.02*float(command[command.index('--time-limit')+1]))
        assert ours['neighborhood_min_spacing_seconds']==spacing
        assert all(captured[i+1]['start_seconds']-captured[i]['start_seconds']>=spacing-1e-8 for i in range(len(captured)-1))
    if '--capture-neighborhood' in command:
        assert len(captured)==ours['neighborhood_calls']<=16
        assert sum(s['nodes'] for s in captured)==ours['neighborhood_nodes']
        assert sum(s['improved'] for s in captured)==ours['neighborhood_improvements']
        assert math.isclose(sum(s['seconds'] for s in captured),ours['neighborhood_seconds'],rel_tol=1e-10,abs_tol=1e-12)
        assert ours['neighborhood']==command[command.index('--neighborhood')+1]
    for i,sample in enumerate(captured):
        free=sample['free_variables']
        assert len(free)==len(set(free)) and all(type(j) is int and j in integers and lower[j]<upper[j] for j in free)
        adaptive=ours['neighborhood']=='diversified' and sample['stalls_before']>=4
        strong=reserved and sample['strong']
        ball=sample['selection']=='local_branching'
        assert (ball or len(free)<=96) and 0<=sample['nodes']<=(512 if strong else (128 if adaptive else 64)) and 0<=sample['lp_failures']<=sample['nodes']
        assert 0<sample['budget']<=(4 if adaptive or strong else 2) and 0<=sample['start_seconds']<=ours['total_seconds']
        assert math.isfinite(sample['seconds']) and 0<=sample['seconds']<=ours['total_seconds']
        assert sample['selection'] in ('guided','diverse','expanded_diverse','local_branching')
        if ours['neighborhood']=='guided':assert sample['selection']=='guided'
        if sample['selection']!='guided':assert strong or sample['stalls_before']>=4
        before,after=sample['objective_before'],sample['objective_after']
        assert math.isfinite(before) and math.isfinite(after)
        assert sample['improved']==(sign*after<sign*before)
        if reserved:
            assert sample['material_improved']==material(before,after)
            limit=float(command[command.index('--time-limit')+1]);total=min(30.,.15*limit)
            elapsed=sample['start_seconds'];remaining=max(0.,limit-elapsed)
            if material(previous,before):stalls=0
            assert sample['stalls_before']==stalls
            expected_strong=strong_calls>0 or stalls>=4 or guided_calls>=12 or guided_spent>=.8*total-.001
            assert strong==expected_strong
            if strong:
                released=1 if elapsed<.4*limit else (3 if elapsed<.65*limit else 4)
                assert strong_calls<released
                if strong_calls and not material(strong_center,before):assert elapsed>=strong_start+.1*limit-1e-8
                budget_cap=min(4.,max(0.,total-spent)/(4-strong_calls))
                strong_calls+=1;strong_center=before;strong_start=elapsed
            else:
                assert guided_calls<12
                budget_cap=min(2.,max(0.,.8*total-guided_spent));guided_calls+=1;guided_spent+=sample['seconds']
            assert sample['budget']<=min(budget_cap,.2*remaining,total-spent)+1e-4
            spent+=sample['seconds'];stalls=0 if sample['material_improved'] else stalls+1;previous=after
        else:assert not sample.get('strong',False)
        if ball:
            assert strong and sample['radius']==(4 if strong_calls%2 else 8)
            binaries=[j for j in integers if math.isfinite(lower[j]) and math.isfinite(upper[j]) and math.ceil(lower[j])==0 and math.floor(upper[j])==1]
            assert set(free)==set(binaries)
            center=sample['center_primal']
            if len(lower)<=10000:
                assert len(center)==len(lower) and all(math.isfinite(x) for x in center)
                assert all(center[j] in (0,1) for j in binaries)
                samples.append((f'center_{i}',center,False,before))
                if sample['improved']:
                    point=sample['improved_primal']
                    assert len(point)==len(center)
                    assert sum(point[j]!=center[j] for j in binaries)<=sample['radius']
                    assert all(point[j]==center[j] for j in integers if j not in binaries)
        else:assert not sample.get('center_primal',[]) and sample.get('radius',0)==0
        if sample['improved'] and len(lower)<=10000:
            assert sample['improved_primal'] and any(v==after for _,v in ours['incumbent_trace'])
            samples.append((f'neighborhood_{i}',sample['improved_primal'],False,after))
        else:assert not sample['improved_primal']
    return samples


def main(args):
    source=args.results.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    metadata=json.loads((source/'metadata.json').read_text());summary=json.loads((source/'summary.json').read_text())
    records=json.loads((source/'results.json').read_text())
    assert summary['all_generated_passed'] and summary['hard_runs_completed']
    assert not summary['unsafe_or_error_runs'],'Run has unsafe/error statuses'
    assert len(records)==summary['hard_run_count'] and records,'Missing hard runs'
    assert len({r['key'] for r in records})==len(records),'Duplicate hard run'
    assert sha(args.binary)==metadata['binary_sha256'],'Wrong numerical binary'
    for name,digest in metadata['source_sha256'].items():
        if name.split('/')[0] in ('src','include','tests'):assert sha(ROOT/name)==digest,'Core/test source changed: '+name
    assert sha(ROOT/'CMakeLists.txt')==metadata['cmake_sha256']
    for name in ('scripts/benchmark_lp.py','scripts/validate_milp_focus.py','scripts/test_milp.py','scripts/test_mixed_v2.py'):
        assert sha(ROOT/name)==metadata['source_sha256'][name],'Validation source changed: '+name
    assert sha(source/'CMakeCache.txt')==metadata['cmake_cache_sha256']
    assert 'SOVEREIGN_ENABLE_CUDA:BOOL=OFF' in (source/'CMakeCache.txt').read_text(),'Expected CPU-only build'
    assert '100% tests passed' in (source/'ctest.log').read_text()
    groups={}
    for strategy in metadata['generated_strategy_flags']:
        for kind,name in (('binary','enumeration.json'),('mixed','summary.json')):
            entries=json.loads((source/(strategy+'-'+kind)/name).read_text())
            assert len(entries)==40 and all(r['passed'] is True for r in entries)
            groups['generated_'+strategy+'_'+kind]={'passed':len(entries),'total':len(entries)}
    assert groups==summary['groups'],'Generated aggregates differ from raw checks'
    sys.path.insert(0,str(ROOT/'tools/reference/python'))
    import highspy
    checks=[];raw_hashes={}
    for record in records:
        key=record['key'];path=source/(key+'.ours.json');raw_hashes[path.name]=sha(path)
        ours=json.loads(path.read_text());model=ROOT/'datasets/miplib2017'/(record['name']+'.mps')
        for field in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds'):
            assert record[field]==ours[field],'Aggregate/raw mismatch: '+key+'/'+field
        command=record['command']
        for flag,value in (('--time-limit',metadata['time_limit_seconds']),('--node-limit',metadata['node_limit'])):
            assert float(command[command.index(flag)+1])==value,'Unequal comparison budget'
        assert command[command.index('--gap')+1]=='1e-6'
        for flag in metadata['strategy_flags'][record['strategy']]:assert flag in command
        assert sha(model)==record['model_sha256']
        reader=highspy.Highs();reader.setOptionValue('output_flag',False)
        assert reader.readModel(str(model))!=highspy.HighsStatus.kError
        lp=reader.getLp();maximize=lp.sense_==highspy.ObjSense.kMaximize;sign=-1 if maximize else 1
        integers=[i for i,kind in enumerate(lp.integrality_) if kind!=highspy.HighsVarType.kContinuous]
        trace=ours.get('incumbent_trace',[]);objective=ours.get('objective');bound=ours.get('best_bound')
        assert all(0<=t<=ours['total_seconds'] and math.isfinite(v) for t,v in trace)
        assert all(trace[i][0]<=trace[i+1][0] and sign*trace[i][1]>sign*trace[i+1][1] for i in range(len(trace)-1))
        if objective is not None:assert trace and trace[-1][1]==objective
        else:assert not trace and not ours.get('primal')
        if bound is not None and objective is not None:
            expected=max(0,sign*(objective-bound))/(1+abs(objective))
            assert math.isclose(ours['gap'],expected,rel_tol=1e-10,abs_tol=1e-12),'Gap arithmetic mismatch'
        samples=[('final',ours.get('primal',[]),False,objective)] if ours.get('primal') else []
        samples+=neighborhood_samples(ours,command,integers,lp.col_lower_,lp.col_upper_,sign)
        enabled='--binary-meet' in command
        assert ours.get('binary_meet_enabled',False)==enabled
        if enabled:
            assert ours['binary_meet_attempts'] in (0,1)
            assert 0<=ours['binary_meet_seconds']<=ours['total_seconds']
            assert 0<=ours['binary_meet_budget']<=min(5.,.05*metadata['time_limit_seconds'])
            assert 0<=ours['binary_meet_left_states']<=2**18 and 0<=ours['binary_meet_right_states']<=2**18
            assert not ours['binary_meet_completed'] or ours['binary_meet_eligible']
            point=ours['binary_meet_primal']
            assert bool(point)==ours['binary_meet_improved']
            if point:
                assert ours['binary_meet_eligible'] and ours['binary_meet_attempts']==1
                samples.append(('binary_meet',point,False,None))
        for i,sample in enumerate(ours.get('rejected_candidates',[])):
            if not sample['fixing']['captured']:continue
            x=sample['relaxation'];rounded=list(x)
            for j in integers:rounded[j]=math.floor(x[j]+.5) if x[j]>=0 else math.ceil(x[j]-.5)
            assert rounded==sample['rounded'],'Captured rounding differs from core rule'
            if sample.get('repair_accepted'):samples.append((f'repair_{i}',sample['repair_primal'],True,None))
            if sample.get('fallback_accepted'):samples.append((f'fallback_{i}',sample['fallback_primal'],True,None))
        assert ours.get('candidate_repair_successes',0)<=ours.get('candidate_repair_attempts',0)
        for label,point,round_first,claimed in samples:
            assert len(point)==lp.num_col_ and all(math.isfinite(x) for x in point)
            point=list(point)
            if round_first:
                for j in integers:
                    nearest=math.floor(point[j]+.5) if point[j]>=0 else math.ceil(point[j]-.5)
                    assert abs(point[j]-nearest)<=1e-7
                    point[j]=nearest
            candidate=output/(key+'.'+label+'.candidate.json');save(candidate,{'primal':point})
            checked=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),
                         '--candidate',str(candidate),'--limit','0'],20)
            save(output/(key+'.'+label+'.reference.json'),checked)
            value=checked.get('candidate_recomputed_objective')
            valid=(value is not None and math.isfinite(value) and checked.get('candidate_max_violation',math.inf)<=1e-7
                   and checked.get('candidate_integer_violation',math.inf)<=1e-7)
            if claimed is not None:valid=valid and abs(value-claimed)<=1e-7*(1+abs(claimed))
            checks.append({'key':key,'sample':label,'valid':valid,'objective':value,
                           'max_violation':checked.get('candidate_max_violation'),'integer_violation':checked.get('candidate_integer_violation')})
            assert valid,'Accepted point failed independent original-MPS audit: '+key+'.'+label
    result={'results_directory':str(source),'binary_sha256':metadata['binary_sha256'],
            'audit_script_sha256':sha(Path(__file__)),'reference_version':highspy.Highs().version(),
            'generated_raw_checks':groups,'comparison_budget_and_aggregate_checks':'passed',
            'raw_sha256':raw_hashes,'core_and_model_identity_verified':True,'trace_and_gap_checks':'passed',
            'checks':checks,'all_accepted_points_checked_pass':True,
            'limitation':'Checks final incumbents, captured accepted repairs (first four rejection snapshots per run), and last improved vectors per captured neighborhood call when the model has at most 10000 variables. Uncaptured intermediate incumbents have objective-only traces and cannot be independently recomputed.'}
    save(output/'AUDIT.json',result)
    print(json.dumps({'run_count':len(records),'accepted_points_checked':len(checks),'all_pass':True},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('results',type=Path);p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);main(p.parse_args())
