"""Freeze iteration14 without overwriting previous evidence."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    if not __debug__:raise RuntimeError('Assertions required')
    out=ROOT/'reports/milp-iteration-14';binary=ROOT/'build-milp-iter14/solver_cli.exe';snapshot=out/'final-source'
    assert not snapshot.exists() and not (out/'final_solver_cli.exe').exists()
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text());audit=json.loads((out/'final-audit/AUDIT.json').read_text())
    assert gate['all_pass'] and audit['all_pass'] and gate['binary_sha256']==sha(binary)
    assert gate['runner_sha256']==sha(ROOT/'scripts/work_final_gate.py') and audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_work.py')
    for name,digest in audit['checker_sha256'].items():assert sha(ROOT/'scripts'/name)==digest
    supplemental=audit['supplemental_reference_checks'];assert supplemental and supplemental['records']==2
    supplemental_path=Path(supplemental['directory'])
    assert sha(supplemental_path/'SUMMARY.json')==supplemental['summary_sha256']
    assert sha(supplemental_path/'results.json')==supplemental['results_sha256']
    supplemental_summary=json.loads((supplemental_path/'SUMMARY.json').read_text())
    assert supplemental_summary['runner_sha256']==sha(ROOT/'scripts/resolve_work_references.py')
    expected={'diagnostic-30s','screen-30s','wave-30s','repeats-30s'};assert {r['run'] for r in audit['runs']}==expected
    summaries={};names=set()
    for r in audit['runs']:
        folder=out/r['run'];meta=json.loads((folder/'metadata.json').read_text())
        assert sha(folder/'metadata.json')==r['metadata_sha256'] and sha(folder/'results.json')==r['results_sha256']
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        for name,digest in meta['source_sha256'].items():
            assert sha(folder/'source'/name)==digest
            if r['run']!='diagnostic-30s' and (name.startswith(('src/','include/')) or name=='CMakeLists.txt'):assert sha(ROOT/name)==digest
        summaries[r['run']]=json.loads((folder/'SUMMARY.json').read_text());assert not summaries[r['run']]['validation_failures']
        names.update(row['name'] for row in json.loads((folder/'results.json').read_text()))
    old=ROOT/'reports/milp-iteration-13';old_state=json.loads((old/'FINAL_STATE.json').read_text())
    assert sha(old/'final_solver_cli.exe')==old_state['binary_sha256']=='bdfdb8fc7a21d411d47557f093e728e018e86960c359f86573393711b5b4757e'
    for name,digest in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/name)==digest
    for name,digest in old_state['evidence_sha256'].items():assert sha(old/name)==digest
    for version,digest in [(12,'3d29e6a0d5f0ed3bfb6c35e0a3ccee0bc158dda987b619242ed201aff3235a7d'),
                           (11,'867191540898cb1ea7a4bb91a85949734d476b900ca94039025ae818f4ece0cf'),
                           (10,'3cac5f39d5f2546006cb3bd5788ff0e44245ceaab282e86b8a4caf5062295eeb')]:
        assert sha(ROOT/f'reports/milp-iteration-{version}/final_solver_cli.exe')==digest
    report=(out/'REPORT.md').read_text(encoding='utf-8');assert 'ASSEMBLY_PENDING' not in report and (out/'NEXT_STEP.md').is_file()
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    snapshot.mkdir();manifest={}
    for path in files:
        rel=path.relative_to(ROOT);target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
        manifest[rel.as_posix()]=sha(path);assert sha(path)==sha(target)
    save(out/'SNAPSHOT_MANIFEST.json',manifest);shutil.copy2(binary,out/'final_solver_cli.exe')
    shutil.copy2(ROOT/'build-milp-iter14/CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    identity={'iteration':'milp-iteration-14','local_date':str(datetime.date.today()),'status':'optional_root_cut_budget_checked_breadth_incomplete',
        'binary_sha256':sha(binary),'binary_bytes':binary.stat().st_size,'snapshot_files':len(manifest),
        'source_archive':'reports/milp-iteration-14/final-source','binary_archive':'reports/milp-iteration-14/final_solver_cli.exe',
        'new_options':['--capture-work','--root-cut-rounds','--restart-nodes'],'root_cut_rounds_default':5,'tested_candidate_rounds':1,
        'candidate_core_unchanged_since_screen':True,'prior13_binary_source_evidence_preserved':True,'prior12_11_10_binaries_preserved':True,
        'public_models':len(names),'public_experiment_runs':sum(r['records'] for r in audit['runs']),
        'observed_validation_failures':sum(s['validation_failures'] for s in summaries.values()),'summaries':summaries,
        'saved_points_checked':sum(r['final_points_checked'] for r in audit['runs']),
        'initial_reference_pending_points':sum(r['initial_pending_points'] for r in audit['runs']),
        'supplemental_reference_points_checked':sum(r['supplemental_points_checked'] for r in audit['runs']),
        'exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
        'saved_lattice_events':sum(r['lattice_events_rechecked'] for r in audit['runs']),
        'truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
        'cuts_rechecked':sum(r['cuts_rechecked'] for r in audit['runs']),
        'ctest_groups':12,'python_tests':88,'new_exhaustive_cpp_models':120,'new_cpp_full_solves':360,'new_cpp_partial_checks':720,
        'generated_regression_runs':sum(gate['generated'].values()),'reused_exhaustive_mps_models':gate['reused_exhaustive_models'],
        'reader_equivalence_models':21,'gpu_used':False,'user_upload_needed':False,'all_public_milps_proven':False,
        'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt'),
        'evidence_sha256':{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and 'source' not in p.parts and 'final-source' not in p.parts and
                          (p.name in ('SUMMARY.json','AUDIT.json','COMPARISON.json','REPORT.md','NEXT_STEP.md','PLAN.md','CANDIDATE.md','DIAGNOSTIC.json','SCREEN.json','WAVE.json','REPEATS.json') or p.parent==out/'final-gate' and p.suffix=='.log')},
        'limits':['Numerical general LP/MILP certificates; exact binary scope unchanged.','Round caps do not impose hard pivot/FLOP/memory limits.',
                  'Shared desktop; instrumented timing and clock-triggered search remain variable.','All21 public cases are development cases, not new holdouts.',
                  'No new full QP/GPU/industrial validation or universal/competition-rank claim.']}
    save(out/'FINAL_STATE.json',identity);print(json.dumps({k:v for k,v in identity.items() if k not in ('evidence_sha256','summaries')},indent=2),flush=True)

if __name__=='__main__':main()
