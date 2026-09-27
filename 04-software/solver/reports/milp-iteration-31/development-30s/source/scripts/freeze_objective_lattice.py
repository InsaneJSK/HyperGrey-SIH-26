"""Freeze verified iteration12 artifacts without replacing any prior archive."""
import datetime
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save


def main():
    out=ROOT/'reports/milp-iteration-12';binary=ROOT/'build-milp-iter12/solver_cli.exe'
    snapshot=out/'final-source';archived=out/'final_solver_cli.exe'
    assert not snapshot.exists() and not archived.exists(), 'Refuse to replace a frozen version'
    audit=json.loads((out/'final-audit/AUDIT.json').read_text());assert audit['all_pass']
    gate=json.loads((out/'final-gate/SUMMARY.json').read_text());assert gate['all_pass']
    generated=json.loads((out/'generated-lattice/SUMMARY.json').read_text());assert generated['all_pass']
    digest=sha(binary);assert digest==gate['binary_sha256']==generated['binary_sha256']
    for run in ('target-screen-30s','wave1-paired-30s','target-repeats-30s'):
        metadata=json.loads((out/run/'metadata.json').read_text());assert metadata['binary_sha256']==digest
        for name,value in metadata['file_sha256'].items():assert sha(ROOT/name)==value,name
    old=ROOT/'reports/milp-iteration-11/final_solver_cli.exe'
    assert sha(old)=='867191540898cb1ea7a4bb91a85949734d476b900ca94039025ae818f4ece0cf'
    old_manifest=json.loads((ROOT/'reports/milp-iteration-11/SNAPSHOT_MANIFEST.json').read_text())
    for name,value in old_manifest.items():assert sha(ROOT/'reports/milp-iteration-11/final-source'/name)==value
    assert sha(ROOT/'reports/milp-iteration-10/final_solver_cli.exe')=='3cac5f39d5f2546006cb3bd5788ff0e44245ceaab282e86b8a4caf5062295eeb'
    sources=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'Problem Statement.txt']
    for folder in ('src','include','tests','scripts','docs','examples'):
        sources += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.hpp','.cu','.md','.txt','.mps','.lpmini','.qplib')]
    snapshot.mkdir();manifest={}
    for path in sources:
        rel=path.relative_to(ROOT);target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target);manifest[rel.as_posix()]=sha(path);assert sha(target)==sha(path)
    shutil.copy2(binary,archived);assert sha(archived)==digest
    shutil.copy2(ROOT/'build-milp-iter12/CMakeCache.txt',out/'FINAL_CMakeCache.txt')
    save(out/'SNAPSHOT_MANIFEST.json',manifest)
    wave=json.loads((out/'wave1-paired-30s/SUMMARY.json').read_text())
    comparisons=json.loads((out/'final-audit/COMPARISON.json').read_text())
    repeated=[r for r in comparisons if r['run']=='target-repeats-30s']
    evidence=[p for p in out.rglob('*') if p.is_file() and 'final-source' not in p.parts and
              (p.name in ('SUMMARY.json','AUDIT.json','COMPARISON.json','PLAN.md','REPORT.md','NEXT_STEP.md') or
               p.parent==out/'final-gate' and p.suffix=='.log')]
    state={'iteration':'milp-iteration-12','completed_local_date':str(datetime.date.today()),
           'status':'optional_lattice_bounds_verified_breadth_incomplete','build':'build-milp-iter12',
           'binary_archive':archived.relative_to(ROOT).as_posix(),'source_archive':snapshot.relative_to(ROOT).as_posix(),
           'binary_sha256':digest,'binary_bytes':archived.stat().st_size,'snapshot_files_verified':len(manifest),
           'cmake_sha256':sha(ROOT/'CMakeLists.txt'),'cmake_cache_sha256':sha(out/'FINAL_CMakeCache.txt'),
           'prior_iteration11_binary_and_source_preserved':True,'prior_iteration10_binary_preserved':True,
           'core_files_changed':['include/objective_lattice.hpp','include/milp.hpp','src/milp_v2.cpp','src/main.cpp'],
           'new_option':'--objective-lattice','default_enabled':False,'core_unchanged_after_timing':True,
           'wave1_models':17,'wave1_categories':wave['categories'],'target_repeated_comparisons':repeated,
           'observed_public_validation_failures':sum(json.loads((out/r['run']/'SUMMARY.json').read_text())['validation_failures'] for r in audit['runs']),
           'public_runs_audited':sum(r['records'] for r in audit['runs']),
           'saved_public_final_points_checked':sum(r['saved_final_point_checks'] for r in audit['runs']),
           'saved_public_lattice_events_rechecked':sum(r['rounding_events_rechecked'] for r in audit['runs']),
           'public_truncated_lattice_traces':sum(r['truncated_traces'] for r in audit['runs']),
           'public_exact_proofs_recomputed':sum(r['exact_proofs_recomputed'] for r in audit['runs']),
           'public_cuts_rechecked':sum(r['retained_cuts_rechecked'] for r in audit['runs']),
           'ctest_groups':10,'python_unit_tests':65,'cpp_exhaustive_models':300,'cpp_partial_and_zero_time_checks':600,
           'cpp_near_grid_checks':10005,'independent_generated_lattice_models':100,'posttiming_generated_milp_checks':160,
           'independent_marker_domain_checks':28,'gpu_used':False,'user_upload_needed':False,'all_public_cases_proven':False,
           'evidence_sha256':{p.relative_to(out).as_posix():sha(p) for p in evidence},
           'limitations':['General LP/MILP bounds remain numerical, not exact rational proofs.',
                          'First-wave selection is small and mostly historical, not full MIPLIB2017.',
                          'Only the two target models have three new matched repetitions.',
                          'Lattice telemetry retains only the first 4096 improvements; truncated events are not independently rechecked.',
                          'Unsupported objective structures keep the original solver; detection does not guarantee a runtime improvement.',
                          'No new full QP/GPU/industrial validation sweep.'],
           'next_step':'reports/milp-iteration-12/NEXT_STEP.md'}
    save(out/'FINAL_STATE.json',state);print(json.dumps(state,indent=2),flush=True)


if __name__=='__main__':main()
