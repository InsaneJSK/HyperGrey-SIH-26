"""Freeze iteration18 and its separately retained Stage A without altering17."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    out=ROOT/'reports/milp-iteration-18';binary=ROOT/'build-milp-iter18/solver_cli.exe'
    assert not (out/'final-source').exists() and not (out/'final_solver_cli.exe').exists()
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text());audit=json.loads((out/'final-audit/AUDIT.json').read_text())
    policy=json.loads((out/'final-audit/POLICY_AUDIT.json').read_text());accuracy=json.loads((out/'final-audit/ACCURACY_AUDIT.json').read_text())
    selective=json.loads((out/'final-audit/SELECTIVE_AUDIT.json').read_text())
    assert gate['all_pass'] and gate['selective'] and not gate['quick'] and gate['binary_sha256']==sha(binary)
    assert gate['runner_sha256']==sha(ROOT/'scripts/sparse_accuracy_gate.py')
    assert all(a['all_pass'] for a in (audit,policy,accuracy,selective))
    assert selective['runner_sha256']==sha(ROOT/'scripts/freeze_selective_accuracy.py'.replace('freeze_','audit_'))
    assert selective['checker_sha256']==sha(ROOT/'scripts/check_refinement_work.py')
    assert selective['accuracy_audit_sha256']==sha(out/'final-audit/ACCURACY_AUDIT.json')
    assert accuracy['work_audit_sha256']==policy['work_audit_sha256']==sha(out/'final-audit/AUDIT.json')
    assert accuracy['policy_audit_sha256']==sha(out/'final-audit/POLICY_AUDIT.json')
    for name,digest in {**audit['checker_sha256'],**policy['checker_sha256']}.items():assert sha(ROOT/'scripts'/name)==digest
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    assert accuracy['runner_sha256']==sha(ROOT/'scripts/audit_sparse_accuracy.py')
    models=set();summaries={}
    assert {r['run'] for r in audit['runs']}=={'screen-30s','wave-30s','holdout-30s'}
    for run in audit['runs']:
        folder=out/run['run'];meta=json.loads((folder/'metadata.json').read_text())
        assert sha(folder/'results.json')==run['results_sha256'] and sha(folder/'metadata.json')==run['metadata_sha256']
        assert meta['binary_sha256']==sha(binary)
        for rel,digest in meta['source_sha256'].items():assert sha(ROOT/rel)==sha(folder/'source'/rel)==digest,rel
        models.update(r['name'] for r in json.loads((folder/'results.json').read_text()))
        summaries[run['run']]=json.loads((folder/'SUMMARY.json').read_text())
    profile=out/'profile';ps=json.loads((profile/'SUMMARY.json').read_text());pm=json.loads((profile/'metadata.json').read_text())
    assert ps['all_pass'] and ps['three_way_semantic_parity'] and ps['results_sha256']==sha(profile/'results.json')
    assert ps['binary_sha256']==pm['binary_sha256']==sha(profile/'solver_cli.exe')
    for rel,digest in pm['source_sha256'].items():assert sha(profile/'source'/rel)==digest
    for row in json.loads((profile/'results.json').read_text()):
        assert sha(profile/(row['key']+'.json'))==row['result_sha256'] and sha(ROOT/row['model'])==row['model_sha256']
    old=ROOT/'reports/milp-iteration-17';oldstate=json.loads((old/'FINAL_STATE.json').read_text())
    assert sha(old/'final_solver_cli.exe')==oldstate['binary_sha256']==pm['frozen17_sha256']
    for rel,digest in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/rel)==digest
    for rel,digest in oldstate['evidence_sha256'].items():assert sha(old/rel)==digest
    holdout=json.loads((ROOT/'datasets/milp-accuracy-holdout/manifest.json').read_text())
    assert holdout['plan_sha256']==sha(out/'HOLDOUT_PLAN.md') and not holdout['prior_results_matches']
    for s in holdout['instances']:assert s['status']=='ready' and sha(ROOT/s['model'])==s['model_sha256']
    for f in ('REPORT.md','NEXT_STEP.md'):assert 'ASSEMBLY_PENDING' not in (out/f).read_text(encoding='utf-8')
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    manifest={};snapshot=out/'final-source';snapshot.mkdir()
    for p in files:
        rel=p.relative_to(ROOT);dest=snapshot/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        manifest[rel.as_posix()]=sha(p);assert sha(dest)==sha(p)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe');shutil.copy2(binary.parent/'CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    state={'iteration':18,'date':str(datetime.date.today()),'status':'selective_accuracy_experiment_complete_breadth_incomplete',
        'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),'previous17_preserved':True,
        'source_and_checkers_unchanged_during_timings':True,'public_models':len(models),'fresh_public_models':len(holdout['instances']),
        'public_experiment_runs':sum(r['records'] for r in audit['runs']),'saved_final_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
        'pending_reference_points':sum(r['initial_pending_points'] for r in audit['runs']),
        'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
        'saved_lattice_events':sum(r['lattice_events_rechecked'] for r in audit['runs']),
        'truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
        'retained_cuts_checked':sum(r['cuts_rechecked'] for r in audit['runs']),
        'cut_rounds_checked':sum(r['rounds_checked'] for r in policy['runs']),
        'cut_source_incumbents_checked':sum(r['incumbents_checked'] for r in policy['runs']),
        'ctest_groups':17,'python_tests':126,'transformed_lp_checks':24,'fixture_independent_checks':len(gate['fixture_independent_checks']),
        'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_models':gate['reused_models'],
        'disabled_parity_cases':len(gate['disabled_parity']),'profile_three_way_parity_cases':ps['cases'],'profile_runs':ps['runs'],
        'refine_basis_default':False,'refine_at_checks_default':False,'gpu_used':False,'user_upload_needed':False,
        'all_public_milps_proven':False,'observed_public_validation_failures':0,'summaries':summaries,'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt')}
    state['evidence_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and
        'source' not in p.parts and 'final-source' not in p.parts and p.name!='FINAL_STATE.json'}
    save(out/'FINAL_STATE.json',state)
    for rel,digest in state['evidence_sha256'].items():assert sha(out/rel)==digest
    print(json.dumps({k:v for k,v in state.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)

if __name__=='__main__':main()
