"""Preserve and audit the focused Kaggle MILP return, including fresh MPS checks."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import shutil
import sys
import zipfile
from benchmark_lp import ROOT,run


def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def main(returned,source,output):
    returned=returned.resolve();source=source.resolve();output=output.resolve()
    if output.exists():raise FileExistsError('Use a new audit directory')
    prefix='reports/milp_focus/'
    with zipfile.ZipFile(returned) as z,zipfile.ZipFile(source) as s:
        assert z.testzip() is None and s.testzip() is None,'ZIP CRC failure'
        names=z.namelist();assert len(names)==len(set(names)),'Duplicate output paths'
        assert sum(e.file_size for e in z.infolist())<500_000_000,'Unexpected archive size'
        for e in z.infolist():
            p=PurePosixPath(e.filename)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in e.filename and ':' not in e.filename,'Unsafe ZIP path'
            assert not ((e.external_attr>>16)&0o170000)==0o120000,'ZIP symlink rejected'
        read=lambda name:json.loads(z.read(name))
        snapshot=read('SNAPSHOT.json')['snapshot_sha256']
        assert sha(source.read_bytes())==snapshot,'Wrong source ZIP'
        assert z.read('SOURCE_MANIFEST.json')==s.read('SOURCE_MANIFEST.json'),'Source manifest mismatch'
        manifest=read('SOURCE_MANIFEST.json')
        for name,digest in manifest.items():assert sha(s.read(name))==digest,'Corrupt source: '+name
        meta=read(prefix+'metadata.json');summary=read(prefix+'summary.json');records=read(prefix+'results.json')
        experiment=meta.get('experiment','branching')
        assert experiment in ('branching','recovery','repair'),'Unknown experiment'
        strategies=('control','recovery_neighborhood') if experiment=='recovery' else ('fractionality','reliability')
        generated_strategies=strategies+('recovery_only',) if experiment=='recovery' else strategies
        if experiment=='repair':strategies=('baseline','candidate_repair');generated_strategies=strategies+('legacy_control',)
        assert meta['profile']=='milp_focus' and meta['time_limit_seconds']==180 and meta['node_limit']==250000
        for name,digest in meta['source_sha256'].items():assert manifest[name]==digest,'Runtime source differs: '+name
        assert meta['cmake_sha256']==manifest['CMakeLists.txt']
        assert sha(z.read(prefix+'CMakeCache.txt'))==meta['cmake_cache_sha256']
        assert b'SOVEREIGN_ENABLE_CUDA:BOOL=OFF' in z.read(prefix+'CMakeCache.txt')
        assert read('run_logs/RUN_STATUS.json')['completed'] is True
        assert b'100% tests passed' in z.read(prefix+'ctest.log')
        groups={}
        for strategy in generated_strategies:
            for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
                entries=read(prefix+strategy+'-'+kind+'/'+file)
                groups['generated_'+strategy+'_'+kind]={'passed':sum(r['passed'] is True for r in entries),'total':len(entries)}
                assert len(entries)==40 and all(r['passed'] is True for r in entries)
        assert groups==summary['groups'] and summary['all_generated_passed'] is True
        expected={(m,b) for m in ('markshare_4_0','blend2','binkar10_1') for b in strategies}
        assert len(records)==6 and {(r['name'],r['strategy']) for r in records}==expected
        for r in records:
            model='datasets/miplib2017/'+r['name']+'.mps'
            assert r['model_sha256']==manifest[model]==sha((ROOT/model).read_bytes()),'Model identity mismatch'
            ours=read(prefix+r['key']+'.ours.json')
            for field in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds','strong_branch_probes','strong_branch_seconds','pseudocost_updates'):
                assert r[field]==ours[field],'Aggregate/raw mismatch: '+r['key']+'/'+field
            command=r['command']
            branching='fractionality' if experiment in ('recovery','repair') else r['strategy']
            for flag,value in [('--branching',branching),('--time-limit','180.0'),('--node-limit','250000'),('--gap','1e-6')]:
                assert command[command.index(flag)+1]==value,'Unequal comparison configuration'
            assert ours['branching']==branching
            if experiment in ('recovery','repair'):
                assert '--capture-lp-failure' in command
                for flag in ('--lp-recovery','--improve-incumbent'):
                    assert (flag in command)==(experiment=='repair' or r['strategy']=='recovery_neighborhood'),'Wrong experimental options'
                for field in ('lp_recovery_attempts','lp_recovery_successes','lp_recovery_seconds','deferred_nodes','unresolved_nodes','neighborhood_calls','neighborhood_nodes','neighborhood_improvements','neighborhood_seconds'):
                    assert r[field]==ours[field],'Recovery aggregate/raw mismatch'
            if experiment=='repair':
                assert '--capture-rejected-candidates' in command
                assert ('--repair-candidates' in command)==(r['strategy']=='candidate_repair')
                for field in ('rejected_integer_candidates','candidate_repair_attempts','candidate_repair_successes','repair_branch_nodes','candidate_repair_seconds'):
                    assert r[field]==ours[field],'Repair aggregate/raw mismatch'
        output.mkdir(parents=True)
        shutil.copy2(returned,output/'returned_results.zip');shutil.copy2(source,output/'submitted_source.zip')
        notebook=source.with_name('SIH26119_V2_Kaggle.ipynb')
        if notebook.is_file():shutil.copy2(notebook,output/'submitted_notebook.ipynb')
        z.extractall(output/'raw')
    independent=[]
    for r in records:
        ours_path=output/'raw'/prefix/(r['key']+'.ours.json');ours=json.loads(ours_path.read_text())
        model=ROOT/'datasets/miplib2017'/(r['name']+'.mps')
        # Zero solve time: read/recompute only; no new reference incumbent is fed back.
        checked=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(ours_path),'--limit','0'],20)
        save(output/(r['key']+'.independent.json'),checked)
        obj=ours.get('objective');value=checked.get('candidate_recomputed_objective')
        valid=bool(obj is not None and value is not None and math.isfinite(obj) and abs(obj-value)<=1e-7*(1+abs(obj))
                   and checked.get('candidate_max_violation',math.inf)<=1e-7 and checked.get('candidate_integer_violation',math.inf)<=1e-7)
        assert valid==r['candidate_verified'],'Fresh independent candidate check disagrees'
        if ours.get('primal') or obj is not None:assert valid,'Unverified returned incumbent'
        trace=ours.get('incumbent_trace',[])
        assert all(0<=t[0]<=ours['total_seconds'] for t in trace)
        assert all(trace[i][0]<=trace[i+1][0] and trace[i][1]>trace[i+1][1] for i in range(len(trace)-1))
        if valid:assert trace and trace[-1][1]==obj,'Trace/final incumbent mismatch'
        independent.append({**r,'fresh_candidate_verified':valid,'fresh_max_violation':checked.get('candidate_max_violation'),
                            'fresh_integer_violation':checked.get('candidate_integer_violation'),'incumbent_trace':trace})
    count=sum(r['fresh_candidate_verified'] for r in independent)
    assert count==summary['verified_candidates'] and summary['hard_run_count']==6
    audit={'profile':'milp_focus','experiment':experiment,'returned_zip_sha256':sha(returned.read_bytes()),'snapshot_sha256':snapshot,
           'source_files_verified':len(manifest),'runtime_source_files_verified':len(meta['source_sha256']),
           'reported_linux_binary_sha256':meta['binary_sha256'],'groups_recounted':groups,
           'fresh_verified_candidates':count,'completed_reference_comparisons':summary['completed_reference_comparisons'],
           'platform':meta['platform'],'python':meta['python'],'physical_cores':meta['physical_cores'],'logical_cores':meta['logical_cores'],
           'ram_bytes':meta['ram_bytes'],'gpu_used':False,'results':independent,
           'conclusion':'Keep experimental options opt-in pending paired result review and repeated evidence; incomplete runs remain incomplete.'}
    save(output/'AUDIT.json',audit)
    print(json.dumps({k:v for k,v in audit.items() if k!='results'},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('returned',type=Path);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();main(args.returned,args.source,args.output)
