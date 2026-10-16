"""Sparse accuracy correctness gate, not performance measurements."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from milp_robustness import timed,reference,FLAGS
from validate_milp_frontier import verify,semantic
from check_milp_work import check as work_check
from check_cut_policy import check as policy_check
from check_refinement_work import check as refinement_check
from check_heuristic_repair import check as heuristic_check
from check_pump_guidance import check as pump_guidance_check
from check_pump_distance import check as pump_distance_check
from check_pump_reopt import check as pump_reopt_check
from check_distance_reopt import check as distance_reopt_check
from check_distance_stage import check as distance_stage_check
from check_private_certificate import check as private_certificate_check
import test_milp
import test_mixed_v2

def main(a):
    assert __debug__
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=a.binary.resolve();digest=sha(binary)
    def command(key,cmd,cwd=ROOT):
        p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
        (out/(key+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
        assert p.returncode==0,(key,p.stdout,p.stderr)
        print(key,'PASS',flush=True);return p.stdout
    command('ctest',['ctest','--test-dir',str(binary.parent),'--output-on-failure'])
    points=command('retained-cpp',[str(binary.parent/'solver_sparse_accuracy_tests.exe'),str(ROOT/'tests/sparse_accuracy_fixture.mps'),str(ROOT/'tests/sparse_accuracy_basis.txt')])
    fixture_refs=[]
    for line in points.splitlines():
        if not line.startswith('POINT '):continue
        point=json.loads(line[6:]);ref=reference(ROOT/'tests/sparse_accuracy_fixture.mps',point,5)
        save(out/(point['label']+'.point.json'),point);save(out/(point['label']+'.reference.json'),ref)
        assert ref['candidate_checked'] and ref['candidate_max_violation']<=1e-7
        assert ref['status']=='Optimal' and abs(point['objective']-ref['objective'])<1e-7
        fixture_refs.append(point['label'])
    assert fixture_refs==['cold','warm']
    if a.selective:
        points=command('selective-cpp',[str(binary.parent/'solver_sparse_accuracy_tests.exe'),str(ROOT/'tests/sparse_accuracy_fixture.mps'),str(ROOT/'tests/sparse_accuracy_basis.txt'),'--checks'])
        for line in points.splitlines():
            if not line.startswith('POINT '):continue
            point=json.loads(line[6:]);ref=reference(ROOT/'tests/sparse_accuracy_fixture.mps',point,5);label='selective-'+point['label']
            save(out/(label+'.point.json'),point);save(out/(label+'.reference.json'),ref)
            assert ref['candidate_checked'] and ref['candidate_max_violation']<=1e-7
            assert ref['status']=='Optimal' and abs(point['objective']-ref['objective'])<1e-7
            fixture_refs.append(label)
    command('python',[sys.executable,'-X','utf8','-m','unittest','test_milp_robustness','test_exact_binary_check','test_result_parser',
        'test_milp_diagnostics','test_lifted_cover_check','test_objective_lattice_check','test_milp_frontier_check','test_milp_work_check','test_cut_policy_check','test_refinement_work_check','test_feasibility_trace_check','test_pump_guidance_check','test_pump_distance_check','test_pump_reopt_check','test_distance_reopt_check','test_distance_stage_check','-v'],ROOT/'scripts')
    command('marker-contract',[sys.executable,'-X','utf8',str(ROOT/'scripts/check_mps_marker_contract.py'),
        '--binary',str(binary),'--output',str(out/'marker-contract'),'--require-pass'])
    old=ROOT/'reports/milp-iteration-16/final_solver_cli.exe'
    assert sha(old)=='9fcd999d6226c9464513c22554680e78e90e586a521f6a1d0001a34283841502'
    specs=json.loads((ROOT/'datasets/milp-robustness-wave1/manifest.json').read_text())['instances'];parity=[]
    for name in ('gt2','lseu','mod008','misc03'):
        model=ROOT/next(s['model'] for s in specs if s['name']==name);signatures=[]
        for label,b in [('frozen16',old),('off',binary)]:
            key=name+'.'+label
            r=timed([str(b),str(model),'--milp','--json','--no-cuts','--no-heuristics','--node-limit','512','--time-limit','120',
                '--gap','0','--objective-lattice','--raw-lp-priority','--capture-work','--capture-frontier'],150,out/key)
            save(out/(key+'.json'),r);signatures.append(semantic(r));work_check(r)
        assert signatures[0]==signatures[1],(name,'Disabled arithmetic changed')
        parity.append(name);print(name,'disabled parity PASS',flush=True)
    generated={};reused=[]
    if not a.quick:
        mode=['--refine-basis']+(['--refine-at-checks'] if a.selective else [])
        if a.heuristic_repair:mode+=['--repair-candidates','--repair-heuristic-candidates']
        if a.pump_guidance:mode+=['--pump-guided-diving']
        if a.pump_distance:mode+=['--pump-distance-diving']
        if a.pump_reopt:mode+=['--pump-primal-reopt']
        if a.distance_reopt:mode+=['--pump-distance-reopt']
        if a.distance_stage:mode+=['--pump-distance-stage']
        if a.private_ranking:mode+=['--pump-distance-stable-ranking']
        if a.distance_reserve:mode+=['--pump-distance-alternate-reserve']
        if a.private_certificate:mode+=['--private-dual-certificate']
        if getattr(a,'stable_ratio',False):mode+=['--stable-primal-ratio']
        profiles=[('baseline',[]),('refined',mode),
            ('refined_compact',[*mode,'--compact-equalities']),
            ('refined_guard',[*mode,'--adaptive-cut-rounds','--cut-after-incumbent'])]
        if getattr(a,'stable_ratio',False):profiles.append(('stable_only',['--stable-primal-ratio']))
        for profile,extra in profiles:
            flags=[*FLAGS,'--objective-lattice','--raw-lp-priority','--capture-work','--capture-refinement','--capture-frontier','--capture-cut-rounds','--restart-nodes','2',*extra]
            test_milp.main(out/(profile+'-binary'),True,binary,flags)
            test_mixed_v2.main(out/(profile+'-mixed'),binary,flags)
            for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
                rows=json.loads((out/(profile+'-'+kind)/file).read_text())
                assert len(rows)==40 and all(r['passed'] for r in rows),(profile,kind)
                generated[profile+'-'+kind]=len(rows)
            for p in list((out/(profile+'-binary')).glob('*.result.json'))+list((out/(profile+'-mixed')).glob('case*.json')):
                r=json.loads(p.read_text());work_check(r);policy_check(r)
                refinement_check(r)
                heuristic_check(r)
                assert r['basis_refinement_enabled']==('--refine-basis' in flags)
                assert r['stable_primal_ratio_enabled']==('--stable-primal-ratio' in flags)
                assert r['pump_guidance']['enabled']==('--pump-guided-diving' in flags)
                model=p.with_name(p.name.replace('.result.json','.mps')) if p.name.endswith('.result.json') else p.with_suffix('.mps')
                pump_guidance_check(model,r)
                pump_distance_check(model,r)
                pump_reopt_check(r)
                distance_reopt_check(r)
                distance_stage_check(r)
                private_certificate_check(r)
        source=ROOT/'reports/milp-iteration-12/generated-lattice'
        for s in json.loads((source/'results.json').read_text()):
            key=f"generated{s['case']:03d}";model=source/f"case{s['case']:03d}.mps";assert sha(model)==s['model_sha256']
            r=timed([str(binary),str(model),'--milp','--json','--time-limit','5','--objective-lattice','--raw-lp-priority',
                *mode,'--capture-work','--capture-refinement','--capture-frontier'],20,out/key)
            ref=reference(model,r,5);save(out/(key+'.ours.json'),r);save(out/(key+'.reference.json'),ref)
            category,errors,checks=verify(model,r,ref,out,key,1e-6);work_check(r);policy_check(r)
            refinement_check(r)
            heuristic_check(r)
            pump_guidance_check(model,r)
            pump_distance_check(model,r)
            pump_reopt_check(r)
            distance_reopt_check(r)
            distance_stage_check(r)
            private_certificate_check(r)
            assert not errors and category=='numerical_completion_checked' and abs(r['objective']-s['expected'])<=1e-7,(key,errors)
            reused.append({'key':key,'all_pass':True,'model_sha256':sha(model)})
        save(out/'reused-checks.json',reused)
    assert sha(binary)==digest
    bad=timed([str(binary),str(ROOT/'tests/sparse_accuracy_fixture.mps'),'--json','--refine-at-checks'],10,out/'invalid-cli')
    assert bad['exit_code']==2 and 'requires refine-basis' in bad.get('stderr','')
    save(out/'SUMMARY.json',{'all_pass':True,'quick':a.quick,'selective':a.selective,'heuristic_repair':a.heuristic_repair,'pump_guidance':a.pump_guidance,'pump_distance':a.pump_distance,'pump_reopt':a.pump_reopt,'distance_reopt':a.distance_reopt,'distance_stage':a.distance_stage,'private_ranking':a.private_ranking,'distance_reserve':a.distance_reserve,'private_certificate':a.private_certificate,'stable_ratio':getattr(a,'stable_ratio',False),'binary_sha256':digest,'runner_sha256':sha(Path(__file__)),
        'fixture_independent_checks':fixture_refs,'disabled_parity':parity,'generated':generated,'reused_models':len(reused)})
    print('Sparse accuracy gate complete',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--quick',action='store_true');p.add_argument('--selective',action='store_true');p.add_argument('--heuristic-repair',action='store_true');p.add_argument('--pump-guidance',action='store_true');p.add_argument('--pump-distance',action='store_true');p.add_argument('--pump-reopt',action='store_true');p.add_argument('--distance-reopt',action='store_true');p.add_argument('--distance-stage',action='store_true');p.add_argument('--private-ranking',action='store_true');p.add_argument('--distance-reserve',action='store_true');p.add_argument('--private-certificate',action='store_true');p.add_argument('--stable-ratio',action='store_true');main(p.parse_args())
