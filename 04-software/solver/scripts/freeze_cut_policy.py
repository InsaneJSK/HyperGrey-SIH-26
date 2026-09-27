"""Freeze iteration15 with unchanged run snapshots and preserved iteration14."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    if not __debug__:raise RuntimeError('Assertions required')
    out=ROOT/'reports/milp-iteration-15';binary=ROOT/'build-milp-iter15/solver_cli.exe';snapshot=out/'final-source'
    assert not snapshot.exists() and not (out/'final_solver_cli.exe').exists()
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text());audit=json.loads((out/'final-audit/AUDIT.json').read_text())
    policy=json.loads((out/'final-audit/POLICY_AUDIT.json').read_text())
    assert gate['all_pass'] and not gate['quick'] and audit['all_pass'] and policy['all_pass']
    assert gate['binary_sha256']==sha(binary) and gate['runner_sha256']==sha(ROOT/'scripts/cut_policy_gate.py')
    assert policy['checker_sha256']==sha(ROOT/'scripts/check_cut_policy.py') and policy['audit_sha256']==sha(ROOT/'scripts/audit_cut_policy.py')
    assert policy['work_audit_sha256']==sha(out/'final-audit/AUDIT.json')
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    for name,digest in audit['checker_sha256'].items():assert sha(ROOT/'scripts'/name)==digest
    expected={'screen-30s','repeats-30s','wave-30s','holdout-30s'}
    assert {r['run'] for r in audit['runs']}==expected and {r['run'] for r in policy['runs']}==expected
    names=set();summaries={}
    for run in audit['runs']:
        folder=out/run['run'];meta=json.loads((folder/'metadata.json').read_text());rows=json.loads((folder/'results.json').read_text())
        assert sha(folder/'metadata.json')==run['metadata_sha256'] and sha(folder/'results.json')==run['results_sha256']
        assert meta['binary_sha256']==sha(binary)
        for rel,digest in meta['source_sha256'].items():assert sha(folder/'source'/rel)==digest and sha(ROOT/rel)==digest,rel
        names.update(r['name'] for r in rows);summaries[run['run']]=json.loads((folder/'SUMMARY.json').read_text())
        assert not summaries[run['run']]['validation_failures']
    old=ROOT/'reports/milp-iteration-14';old_state=json.loads((old/'FINAL_STATE.json').read_text())
    assert sha(old/'final_solver_cli.exe')==old_state['binary_sha256']=='f31c1181bc6b775f197a47aee543c9f997955df4a9ff9cb7da61a9820a69df69'
    for rel,digest in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/rel)==digest
    for rel,digest in old_state['evidence_sha256'].items():assert sha(old/rel)==digest
    assert 'ASSEMBLY_PENDING' not in (out/'REPORT.md').read_text(encoding='utf-8') and (out/'NEXT_STEP.md').is_file()
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    snapshot.mkdir();manifest={}
    for p in files:
        rel=p.relative_to(ROOT);target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        manifest[rel.as_posix()]=sha(p);assert sha(p)==sha(target)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe')
    shutil.copy2(ROOT/'build-milp-iter15/CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    state={'iteration':'milp-iteration-15','local_date':str(datetime.date.today()),'status':'optional_selective_cut_policy_checked_breadth_incomplete',
           'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),'previous14_preserved':True,
           'candidate_and_checkers_unchanged_during_timings':True,'adaptive_policy_default':False,'root_cut_rounds_default':5,
           'public_models':len(names),'fresh_holdout_models':3,'public_experiment_runs':sum(r['records'] for r in audit['runs']),
           'saved_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
           'unresolved_reference_points':sum(r['initial_pending_points']-r['supplemental_points_checked'] for r in audit['runs']),
           'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
           'saved_lattice_events':sum(r['lattice_events_rechecked'] for r in audit['runs']),
           'truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
           'cuts_rechecked':sum(r['cuts_rechecked'] for r in audit['runs']),
           'policy_rounds_checked':sum(r['rounds_checked'] for r in policy['runs']),'policy_stops_checked':sum(r['stops_checked'] for r in policy['runs']),
           'ctest_groups':13,'python_tests':100,'new_exhaustive_cpp_models':120,'new_cpp_full_solves':720,'new_cpp_partial_checks':1440,
           'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_mps_models':gate['reused_models'],
           'default_parity_cases':len(gate['parity']),'reference_equivalence_models':21,'observed_validation_failures':0,
           'gpu_used':False,'user_upload_needed':False,'all_public_milps_proven':False,'summaries':summaries,
           'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt'),
           'evidence_sha256':{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and 'source' not in p.parts and 'final-source' not in p.parts and
               (p.name in ('SUMMARY.json','AUDIT.json','POLICY_AUDIT.json','COMPARISON.json','REPORT.md','NEXT_STEP.md','PLAN.md','SCREEN.json','WAVE.json','REPEATS.json','HOLDOUT.json') or p.parent==out/'final-gate' and p.suffix=='.log')},
           'limits':['General LP/MILP bounds remain numerical.','Allocation heuristics are not proof or hard resource limits.',
                     'Shared desktop and clock-driven search vary.','No universal, industrial or competition-percentile guarantee.']}
    save(out/'FINAL_STATE.json',state);print(json.dumps({k:v for k,v in state.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)

if __name__=='__main__':main()
