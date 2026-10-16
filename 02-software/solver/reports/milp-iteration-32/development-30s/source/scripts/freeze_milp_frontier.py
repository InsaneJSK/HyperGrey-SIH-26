"""Freeze verified iteration13 artifacts; refuse to replace any archive."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save


def main():
    if not __debug__:raise RuntimeError('Assertions required')
    out=ROOT/'reports/milp-iteration-13';binary=ROOT/'build-milp-iter13/solver_cli.exe'
    snapshot=out/'final-source';archived=out/'final_solver_cli.exe'
    assert not snapshot.exists() and not archived.exists(),'Refuse to replace a frozen version'
    audit=json.loads((out/'final-audit/AUDIT.json').read_text());assert audit['all_pass']
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text());assert gate['all_pass']
    digest=sha(binary);assert digest==gate['binary_sha256']
    runs=['node-screen','wave1-paired-30s','target-repeats-30s','holdout-30s']
    assert {r['run'] for r in audit['runs']}==set(runs)
    for run in runs:
        metadata=json.loads((out/run/'metadata.json').read_text());assert metadata['binary_sha256']==digest
        for name,value in metadata['file_sha256'].items():assert sha(ROOT/name)==value,name
        entry=next(r for r in audit['runs'] if r['run']==run)
        assert entry['results_sha256']==sha(out/run/'results.json') and entry['metadata_sha256']==sha(out/run/'metadata.json')
    assert audit['audit_sha256']==sha(ROOT/'scripts/audit_milp_frontier.py')
    assert gate['runner_sha256']==sha(ROOT/'scripts/frontier_final_gate.py')
    prior={12:'3d29e6a0d5f0ed3bfb6c35e0a3ccee0bc158dda987b619242ed201aff3235a7d',
           11:'867191540898cb1ea7a4bb91a85949734d476b900ca94039025ae818f4ece0cf',
           10:'3cac5f39d5f2546006cb3bd5788ff0e44245ceaab282e86b8a4caf5062295eeb'}
    for version,value in prior.items():assert sha(ROOT/f'reports/milp-iteration-{version}/final_solver_cli.exe')==value
    old=ROOT/'reports/milp-iteration-12'
    for name,value in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/name)==value
    for name in ('REPORT.md','NEXT_STEP.md','TIMING_CONDITIONS.md','HOLDOUT_PLAN.md'):assert (out/name).is_file()
    assert 'Report assembly is in progress' not in (out/'REPORT.md').read_text(encoding='utf-8')
    sources=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        sources += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    snapshot.mkdir();manifest={}
    for path in sources:
        rel=path.relative_to(ROOT);target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target);manifest[rel.as_posix()]=sha(path);assert sha(target)==sha(path)
    shutil.copy2(binary,archived);assert sha(archived)==digest
    shutil.copy2(ROOT/'build-milp-iter13/CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    save(out/'SNAPSHOT_MANIFEST.json',manifest)
    summaries={r:json.loads((out/r/'SUMMARY.json').read_text()) for r in runs}
    assert all(s['validation_failures']==0 and s['download_failures']==0 for s in summaries.values())
    public_names={r['name'] for run in runs for r in json.loads((out/run/'results.json').read_text()) if 'key' in r}
    comparisons=json.loads((out/'final-audit/COMPARISON.json').read_text())
    evidence=[p for p in out.rglob('*') if p.is_file() and 'final-source' not in p.parts and
              (p.name in ('SUMMARY.json','AUDIT.json','COMPARISON.json','PLAN.md','REPORT.md','NEXT_STEP.md','TIMING_CONDITIONS.md','HOLDOUT_PLAN.md') or
               p.parent==out/'final-gate' and p.suffix=='.log')]
    state={'iteration':'milp-iteration-13','completed_local_date':str(datetime.date.today()),
           'status':'optional_separate_frontier_accounting_verified_breadth_incomplete','build':'build-milp-iter13',
           'binary_archive':archived.relative_to(ROOT).as_posix(),'source_archive':snapshot.relative_to(ROOT).as_posix(),
           'binary_sha256':digest,'binary_bytes':archived.stat().st_size,'snapshot_files_verified':len(manifest),
           'cmake_sha256':sha(ROOT/'CMakeLists.txt'),'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt'),
           'prior_iteration12_binary_and_source_preserved':True,'prior_iteration11_and10_binaries_preserved':True,
           'core_files_changed':['include/milp_frontier.hpp','include/milp.hpp','src/milp_v2.cpp','src/main.cpp'],
           'new_options':['--raw-lp-priority','--capture-frontier'],'default_enabled':False,'core_unchanged_after_timing':True,
           'summaries':summaries,'target_repeated_comparisons':[r for r in comparisons if r['run']=='target-repeats-30s'],
           'holdout_selection_manifest_sha256':sha(ROOT/'datasets/milp-frontier-holdout/manifest.json'),
           'public_distinct_models':len(public_names),'public_runs_audited':sum(r['records'] for r in audit['runs']),
           'observed_public_validation_failures':sum(s['validation_failures'] for s in summaries.values()),
           'saved_public_final_points_checked':sum(r['saved_final_points_checked'] for r in audit['runs']),
           'saved_public_lattice_events_rechecked':sum(r['lattice_events_rechecked'] for r in audit['runs']),
           'public_truncated_lattice_traces':sum(r['lattice_truncated_traces'] for r in audit['runs']),
           'saved_public_frontier_events_replayed':sum(r['frontier_events_replayed'] for r in audit['runs']),
           'public_truncated_frontier_traces':sum(r['frontier_truncated_traces'] for r in audit['runs']),
           'public_exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
           'public_cuts_rechecked':sum(r['cuts_rechecked'] for r in audit['runs']),
           'ctest_groups':11,'python_unit_tests':79,'cpp_randomized_queue_operations':100000,
           'cpp_new_exhaustive_models':240,'cpp_new_full_solves':720,'cpp_new_partial_and_zero_time_checks':1440,
           'reused_independent_exhaustive_mps_models':100,'posttiming_generated_milp_checks':sum(gate['generated'].values()),
           'independent_marker_domain_checks':28,'gpu_used':False,'user_upload_needed':False,'all_public_cases_proven':False,
           'evidence_sha256':{p.relative_to(out).as_posix():sha(p) for p in evidence},
           'limitations':['General LP/MILP bounds remain numerical, not exact rational certificates.',
                          'Separate frontier replay checks saved bookkeeping, not all LP bounds or branching domains.',
                          'Optional traces retain only prefixes: 4096 lattice improvements and 20000 frontier events.',
                          'Shared desktop timing was not controlled; two diagnostics overlapped the lseu/mod008 wave portion.',
                          'Four untouched MIPLIB2017 benchmark members are a small holdout, not full-library coverage.',
                          'No total RSS cap or memory instrumentation; only dense-fallback and external runtime guards.',
                          'No new full QP/GPU/industrial validation sweep or competition-rank evidence.'],
           'next_step':'reports/milp-iteration-13/NEXT_STEP.md'}
    save(out/'FINAL_STATE.json',state);print(json.dumps(state,indent=2),flush=True)


if __name__=='__main__':main()
