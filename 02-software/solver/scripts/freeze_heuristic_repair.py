"""Freeze iteration19 with prior controls, diagnostics and final paired evidence."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from check_feasibility_trace import check as trace_check

def read(p):return json.loads(p.read_text())

def main():
    out=ROOT/'reports/milp-iteration-19';binary=ROOT/'build-milp-iter19/solver_cli.exe'
    assert not (out/'final-source').exists() and not (out/'final_solver_cli.exe').exists()
    gate=read(out/'final-gate/SUMMARY.json');audit=read(out/'final-audit/AUDIT.json');policy=read(out/'final-audit/POLICY_AUDIT.json')
    accuracy=read(out/'final-audit/ACCURACY_AUDIT.json');selective=read(out/'final-audit/SELECTIVE_AUDIT.json');heuristic=read(out/'final-audit/HEURISTIC_AUDIT.json')
    assert gate['all_pass'] and gate['selective'] and gate['heuristic_repair'] and not gate['quick']
    assert gate['binary_sha256']==sha(binary) and gate['runner_sha256']==sha(ROOT/'scripts/sparse_accuracy_gate.py')
    for a in (audit,policy,accuracy,selective,heuristic):assert a['all_pass']
    for a,name in ((accuracy,'audit_sparse_accuracy.py'),(selective,'audit_selective_accuracy.py'),(heuristic,'audit_heuristic_repair.py')):assert a['runner_sha256']==sha(ROOT/'scripts'/name)
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    for a in (audit,policy,heuristic):
        for name,digest in a['checker_sha256'].items():assert sha(ROOT/'scripts'/name)==digest
    assert selective['checker_sha256']==sha(ROOT/'scripts/check_refinement_work.py')
    assert accuracy['work_audit_sha256']==policy['work_audit_sha256']==sha(out/'final-audit/AUDIT.json')
    assert accuracy['policy_audit_sha256']==sha(out/'final-audit/POLICY_AUDIT.json')
    assert selective['accuracy_audit_sha256']==sha(out/'final-audit/ACCURACY_AUDIT.json')
    assert heuristic['selective_audit_sha256']==sha(out/'final-audit/SELECTIVE_AUDIT.json')
    assert {r['run'] for r in audit['runs']}=={'screen-30s','wave-30s'}
    models=set();summaries={}
    for r in audit['runs']:
        folder=out/r['run'];meta=read(folder/'metadata.json')
        assert sha(folder/'results.json')==r['results_sha256'] and sha(folder/'metadata.json')==r['metadata_sha256']
        assert meta['binary_sha256']==sha(binary)
        for rel,digest in meta['source_sha256'].items():assert sha(ROOT/rel)==sha(folder/'source'/rel)==digest,rel
        models.update(row['name'] for row in read(folder/'results.json'));summaries[r['run']]=read(folder/'SUMMARY.json')
    old=ROOT/'reports/milp-iteration-18';state18=read(old/'FINAL_STATE.json')
    assert sha(old/'final_solver_cli.exe')==state18['binary_sha256']
    for rel,digest in read(old/'SNAPSHOT_MANIFEST.json').items():assert sha(old/'final-source'/rel)==digest
    for rel,digest in state18['evidence_sha256'].items():assert sha(old/rel)==digest
    diagnostic_runs=0
    for run,archive in (('diagnostic-30s','profile_solver_cli.exe'),('rejection-capture','capture_solver_cli.exe')):
        folder=out/run;meta=read(folder/'metadata.json');summary=read(folder/'SUMMARY.json')
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        if not (out/archive).exists():shutil.copy2(meta['binary'],out/archive)
        assert sha(out/archive)==meta['binary_sha256']
        assert summary['validation_failures']==0 and summary['results_sha256']==sha(folder/'results.json')
        for rel,digest in meta['source_sha256'].items():assert sha(folder/'source'/rel)==digest
        for row in read(folder/'results.json'):
            assert sha(ROOT/row['model'])==row['model_sha256']
            assert sha(folder/(row['key']+'.ours.json'))==row['ours_sha256']
            assert sha(folder/(row['key']+'.reference.json'))==row['reference_sha256']
            assert not row['validation_errors'];trace_check(ROOT/row['model'],read(folder/(row['key']+'.ours.json')))
        diagnostic_runs+=summary['records']
    replay=read(out/'rejection-replay/SUMMARY.json')
    assert replay['all_pass'] and replay['binary_sha256']==state18['binary_sha256']
    assert replay['runner_sha256']==sha(ROOT/'scripts/diagnose_heuristic_rejection.py')
    assert replay['fixing_sha256']==sha(out/'rejection-replay/integer-fixing.mps')
    assert replay['source_sha256']==sha(out/'rejection-capture/blend2.capture.0.ours.json')
    parity=read(out/'control-parity/SUMMARY.json')
    assert parity['all_pass'] and parity['binary_sha256']==sha(binary) and parity['frozen18_sha256']==state18['binary_sha256']
    assert parity['runner_sha256']==sha(ROOT/'scripts/heuristic_control_parity.py') and parity['results_sha256']==sha(out/'control-parity/results.json')
    for row in read(out/'control-parity/results.json'):assert row['result_sha256']==sha(out/'control-parity'/(row['key']+'.json'))
    for name in ('REPORT.md','NEXT_STEP.md'):assert 'ASSEMBLY_PENDING' not in (out/name).read_text(encoding='utf-8')
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    manifest={};snapshot=out/'final-source';snapshot.mkdir()
    for p in files:
        rel=p.relative_to(ROOT);dest=snapshot/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        manifest[rel.as_posix()]=sha(p);assert sha(dest)==sha(p)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe');shutil.copy2(binary.parent/'CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    state={'iteration':19,'date':str(datetime.date.today()),'status':'heuristic_repair_experiment_complete_breadth_incomplete',
        'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),'previous18_preserved':True,
        'source_and_checkers_unchanged_during_timings':True,'public_models':len(models),'fresh_public_models':0,
        'paired_public_runs':sum(r['records'] for r in audit['runs']),'diagnostic_public_runs':diagnostic_runs,
        'saved_final_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
        'pending_reference_points':sum(r['initial_pending_points'] for r in audit['runs']),
        'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
        'saved_lattice_events':sum(r['lattice_events_rechecked'] for r in audit['runs']),
        'truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
        'retained_cuts_checked':sum(r['cuts_rechecked'] for r in audit['runs']),
        'cut_rounds_checked':sum(r['rounds_checked'] for r in policy['runs']),
        'cut_source_incumbents_checked':sum(r['incumbents_checked'] for r in policy['runs']),
        'heuristic_repair_attempts':sum(r['attempts'] for r in heuristic['runs']),
        'heuristic_repair_successes':sum(r['successes'] for r in heuristic['runs']),
        'ctest_groups':19,'python_tests':140,'transformed_lp_checks':24,'fixture_independent_checks':len(gate['fixture_independent_checks']),
        'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_models':gate['reused_models'],
        'frozen18_parity_cases':parity['cases'],'heuristic_repair_default':False,'gpu_used':False,'user_upload_needed':False,
        'all_public_milps_proven':False,'observed_public_validation_failures':0,'summaries':summaries}
    state['evidence_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and
        'source' not in p.parts and 'final-source' not in p.parts and p.name!='FINAL_STATE.json'}
    save(out/'FINAL_STATE.json',state)
    for rel,digest in state['evidence_sha256'].items():assert sha(out/rel)==digest
    print(json.dumps({k:v for k,v in state.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)

if __name__=='__main__':main()
