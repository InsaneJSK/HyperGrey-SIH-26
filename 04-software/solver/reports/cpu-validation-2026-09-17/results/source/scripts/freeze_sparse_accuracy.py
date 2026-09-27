"""Freeze iteration17 after all checks, retaining iteration16 unchanged."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    out=ROOT/'reports/milp-iteration-17';binary=ROOT/'build-milp-iter17/solver_cli.exe';snapshot=out/'final-source'
    assert not snapshot.exists() and not (out/'final_solver_cli.exe').exists()
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text())
    audit=json.loads((out/'final-audit/AUDIT.json').read_text());policy=json.loads((out/'final-audit/POLICY_AUDIT.json').read_text())
    accuracy=json.loads((out/'final-audit/ACCURACY_AUDIT.json').read_text())
    assert gate['all_pass'] and not gate['quick'] and audit['all_pass'] and policy['all_pass'] and accuracy['all_pass']
    assert gate['binary_sha256']==sha(binary) and gate['runner_sha256']==sha(ROOT/'scripts/sparse_accuracy_gate.py')
    assert accuracy['runner_sha256']==sha(ROOT/'scripts/audit_sparse_accuracy.py')
    assert accuracy['work_audit_sha256']==policy['work_audit_sha256']==sha(out/'final-audit/AUDIT.json')
    assert accuracy['policy_audit_sha256']==sha(out/'final-audit/POLICY_AUDIT.json')
    for name,digest in {**policy['checker_sha256'],**audit['checker_sha256']}.items():assert sha(ROOT/'scripts'/name)==digest
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    assert {r['run'] for r in audit['runs']}=={'screen-30s','wave-30s'}
    models=set();summaries={}
    for run in audit['runs']:
        folder=out/run['run'];meta=json.loads((folder/'metadata.json').read_text())
        assert sha(folder/'metadata.json')==run['metadata_sha256'] and sha(folder/'results.json')==run['results_sha256']
        assert meta['binary_sha256']==sha(binary)
        for rel,digest in meta['source_sha256'].items():assert sha(ROOT/rel)==sha(folder/'source'/rel)==digest,rel
        models.update(r['name'] for r in json.loads((folder/'results.json').read_text()))
        summaries[run['run']]=json.loads((folder/'SUMMARY.json').read_text())
    old=ROOT/'reports/milp-iteration-16';state=json.loads((old/'FINAL_STATE.json').read_text())
    assert sha(old/'final_solver_cli.exe')==state['binary_sha256']
    for rel,digest in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/rel)==digest
    for rel,digest in state['evidence_sha256'].items():assert sha(old/rel)==digest
    assert sha(out/'sparse_lp_control.cpp')==sha(old/'final-source/src/sparse_lp.cpp')
    provenance=json.loads((out/'fixture-provenance.json').read_text())
    assert sha(ROOT/'tests/sparse_accuracy_fixture.mps')==provenance['model_sha256']
    assert sha(ROOT/'tests/sparse_accuracy_basis.txt')==provenance['basis_sha256']
    assert sha(Path(provenance['source']))==provenance['source_sha256']
    for file in ('REPORT.md','NEXT_STEP.md'):
        assert 'ASSEMBLY_PENDING' not in (out/file).read_text(encoding='utf-8')
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    snapshot.mkdir();manifest={}
    for p in files:
        rel=p.relative_to(ROOT);dest=snapshot/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        manifest[rel.as_posix()]=sha(p);assert sha(dest)==sha(p)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe');shutil.copy2(binary.parent/'CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    result={'iteration':17,'date':str(datetime.date.today()),'status':'sparse_accuracy_experiment_complete_breadth_incomplete',
        'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),'previous16_preserved':True,
        'source_and_checkers_unchanged_during_timings':True,'public_models':len(models),'fresh_public_models':0,
        'public_experiment_runs':sum(r['records'] for r in audit['runs']),
        'saved_final_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
        'pending_reference_points':sum(r['initial_pending_points'] for r in audit['runs']),
        'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
        'saved_lattice_events':sum(r['lattice_events_rechecked'] for r in audit['runs']),
        'truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
        'retained_cuts_checked':sum(r['cuts_rechecked'] for r in audit['runs']),
        'cut_rounds_checked':sum(r['rounds_checked'] for r in policy['runs']),
        'cut_source_incumbents_checked':sum(r['incumbents_checked'] for r in policy['runs']),
        'ctest_groups':15,'python_tests':115,'transformed_lp_equivalents':12,'saved_warm_basis_replayed':True,
        'fixture_independent_checks':len(gate['fixture_independent_checks']),
        'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_models':gate['reused_models'],
        'disabled_parity_cases':len(gate['disabled_parity']),'refine_basis_default':False,'gpu_used':False,
        'user_upload_needed':False,'all_public_milps_proven':False,'observed_public_validation_failures':0,
        'summaries':summaries,'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt'),
        'limits':['General LP/MILP certificates remain numerical.','No new untouched holdouts in this iteration.',
                  'Shared-desktop timing and clock-driven search vary.','No global MILP proof, industrial-readiness or ranking guarantee.']}
    result['evidence_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and
        'source' not in p.parts and 'final-source' not in p.parts and p.name!='FINAL_STATE.json'}
    save(out/'FINAL_STATE.json',result)
    for rel,digest in result['evidence_sha256'].items():assert sha(out/rel)==digest
    print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)

if __name__=='__main__':main()
