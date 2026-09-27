"""Freeze tested iteration21 experiment without modifying any older archive."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save


def read(path):return json.loads(path.read_text())


def main():
    out=ROOT/'reports/milp-iteration-21';binary=ROOT/'build-milp-iter21/solver_cli.exe'
    assert not (out/'final-source').exists() and not (out/'final_solver_cli.exe').exists()
    gate=read(out/'final-gate/SUMMARY.json')
    assert gate['all_pass'] and gate['selective'] and gate['heuristic_repair'] and gate['pump_guidance'] and gate['pump_distance'] and not gate['quick']
    assert gate['binary_sha256']==sha(binary) and gate['runner_sha256']==sha(ROOT/'scripts/sparse_accuracy_gate.py')
    names=('AUDIT','POLICY_AUDIT','ACCURACY_AUDIT','SELECTIVE_AUDIT','HEURISTIC_AUDIT','PUMP_GUIDANCE_AUDIT','PUMP_DISTANCE_AUDIT')
    audits={n:read(out/'final-audit'/(n+'.json')) for n in names}
    assert all(a['all_pass'] for a in audits.values())
    audit=audits['AUDIT'];policy=audits['POLICY_AUDIT'];guidance=audits['PUMP_GUIDANCE_AUDIT']
    for n,script in (('ACCURACY_AUDIT','audit_sparse_accuracy.py'),('SELECTIVE_AUDIT','audit_selective_accuracy.py'),
                     ('HEURISTIC_AUDIT','audit_heuristic_repair.py'),('PUMP_GUIDANCE_AUDIT','audit_pump_guidance.py'),('PUMP_DISTANCE_AUDIT','audit_pump_distance.py')):
        assert audits[n]['runner_sha256']==sha(ROOT/'scripts'/script)
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    for n in ('AUDIT','POLICY_AUDIT','HEURISTIC_AUDIT'):
        for script,digest in audits[n]['checker_sha256'].items():assert sha(ROOT/'scripts'/script)==digest
    assert audits['SELECTIVE_AUDIT']['checker_sha256']==sha(ROOT/'scripts/check_refinement_work.py')
    assert guidance['checker_sha256']==sha(ROOT/'scripts/check_pump_guidance.py')
    assert audits['PUMP_DISTANCE_AUDIT']['checker_sha256']==sha(ROOT/'scripts/check_pump_distance.py')
    for outer,field,inner in (('POLICY_AUDIT','work_audit_sha256','AUDIT'),('ACCURACY_AUDIT','work_audit_sha256','AUDIT'),
        ('ACCURACY_AUDIT','policy_audit_sha256','POLICY_AUDIT'),('SELECTIVE_AUDIT','accuracy_audit_sha256','ACCURACY_AUDIT'),
        ('HEURISTIC_AUDIT','selective_audit_sha256','SELECTIVE_AUDIT'),('PUMP_GUIDANCE_AUDIT','heuristic_audit_sha256','HEURISTIC_AUDIT'),('PUMP_DISTANCE_AUDIT','guidance_audit_sha256','PUMP_GUIDANCE_AUDIT')):
        assert audits[outer][field]==sha(out/'final-audit'/(inner+'.json'))
    assert {r['run'] for r in audit['runs']}=={'screen-30s','wave-30s'}
    models=set();summaries={}
    for r in audit['runs']:
        folder=out/r['run'];meta=read(folder/'metadata.json')
        assert sha(folder/'results.json')==r['results_sha256'] and sha(folder/'metadata.json')==r['metadata_sha256']
        assert meta['binary_sha256']==sha(binary)
        for rel,digest in meta['source_sha256'].items():assert sha(ROOT/rel)==sha(folder/'source'/rel)==digest,rel
        models.update(row['name'] for row in read(folder/'results.json'));summaries[r['run']]=read(folder/'SUMMARY.json')
    old=ROOT/'reports/milp-iteration-20';state20=read(old/'FINAL_STATE.json')
    assert sha(old/'final_solver_cli.exe')==state20['binary_sha256']=='0da07acbe45aaf097162c93eb8c33ef41321d692337e31dfbb5bab3612ef53d4'
    for rel,digest in read(old/'SNAPSHOT_MANIFEST.json').items():assert sha(old/'final-source'/rel)==digest
    for rel,digest in state20['evidence_sha256'].items():assert sha(old/rel)==digest
    parity=read(out/'control-parity/SUMMARY.json')
    assert parity['all_pass'] and parity['binary_sha256']==sha(binary) and parity['frozen20_sha256']==state20['binary_sha256']
    assert parity['runner_sha256']==sha(ROOT/'scripts/pump_distance_parity.py') and parity['results_sha256']==sha(out/'control-parity/results.json')
    for row in read(out/'control-parity/results.json'):assert row['result_sha256']==sha(out/'control-parity'/(row['key']+'.json'))
    mechanism=out/'mechanism-root';mechanism_meta=read(mechanism/'metadata.json');mechanism_summary=read(mechanism/'SUMMARY.json')
    assert mechanism_meta['binary_sha256']==sha(binary) and mechanism_meta['plan']['nodes']==1
    assert mechanism_summary['validation_failures']==0 and mechanism_summary['results_sha256']==sha(mechanism/'results.json')
    for rel,digest in mechanism_meta['source_sha256'].items():assert sha(ROOT/rel)==sha(mechanism/'source'/rel)==digest,rel
    mechanism_dives=0
    for row in read(mechanism/'results.json'):
        key=row['key'];assert sha(ROOT/row['model'])==row['model_sha256'] and not row['validation_errors']
        assert sha(mechanism/(key+'.ours.json'))==row['ours_sha256'] and sha(mechanism/(key+'.reference.json'))==row['reference_sha256']
        from check_pump_distance import check
        c=check(ROOT/row['model'],read(mechanism/(key+'.ours.json')))
        assert c==read(mechanism/(key+'.pump-distance-check.json'));mechanism_dives+=c['dives']
    assert mechanism_dives>0,'Public guided-dive path was not exercised'
    for name in ('REPORT.md','NEXT_STEP.md','MODEL_LEDGER.md'):assert 'ASSEMBLY_PENDING' not in (out/name).read_text(encoding='utf-8')
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    manifest={};snapshot=out/'final-source';snapshot.mkdir()
    for p in files:
        rel=p.relative_to(ROOT);dest=snapshot/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        manifest[rel.as_posix()]=sha(p);assert sha(dest)==sha(p)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe');shutil.copy2(binary.parent/'CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    state={'iteration':21,'date':str(datetime.date.today()),'status':'distance_dive_experiment_complete_breadth_incomplete',
        'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),'previous20_preserved':True,
        'source_and_checkers_unchanged_during_timings':True,'public_models':len(models),'fresh_public_models':0,
        'paired_public_runs':sum(r['records'] for r in audit['runs']),
        'mechanism_root_runs':mechanism_summary['records'],'mechanism_guided_dives':mechanism_dives,
        'saved_final_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
        'pending_reference_points':sum(r['initial_pending_points'] for r in audit['runs']),
        'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
        'guided_dives':sum(r['guided_dives'] for r in guidance['runs']),
        'seed_points_checked':sum(r['seed_points_checked'] for r in guidance['runs']),
        'ctest_groups':21,'python_tests':162,'transformed_lp_checks':24,
        'fixture_independent_checks':len(gate['fixture_independent_checks']),
        'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_models':gate['reused_models'],
        'frozen20_parity_cases':parity['cases'],'pump_guided_diving_default':False,'pump_distance_diving_default':False,'gpu_used':False,'user_upload_needed':False,
        'all_public_milps_proven':False,'observed_public_validation_failures':0,'summaries':summaries}
    state['evidence_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and
        'source' not in p.parts and 'final-source' not in p.parts and p.name!='FINAL_STATE.json'}
    save(out/'FINAL_STATE.json',state)
    for rel,digest in state['evidence_sha256'].items():assert sha(out/rel)==digest
    print(json.dumps({k:v for k,v in state.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)


if __name__=='__main__':main()
