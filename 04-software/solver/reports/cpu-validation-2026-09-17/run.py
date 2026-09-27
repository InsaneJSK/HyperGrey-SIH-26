"""Current-binary retained LP/QP validation, with all own solves before references."""
import datetime
import hashlib
import importlib.util
import json
import math
import os
import platform
from pathlib import Path
import shutil
import sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from milp_robustness import timed
from qp_certificate import check as check_qp

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

def main():
    os.environ['PATH']=str(ROOT/'tools/local-toolchain/mingw64/bin')+os.pathsep+os.environ['PATH']
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    out=BASE/'results';out.mkdir(exist_ok=False)
    binary=ROOT/'build-milp-iter29/solver_cli.exe'
    gate=json.loads((ROOT/'reports/milp-iteration-29/gate-local-runtime/SUMMARY.json').read_text())
    screen=json.loads((ROOT/'reports/milp-iteration-29/screen-30s/SUMMARY.json').read_text())
    assert gate['all_pass'] and gate['binary_sha256']==sha(binary) and screen['validation_failures']==0
    wrapper=ROOT/'reports/milp-iteration-28/run_contained.py'
    spec=importlib.util.spec_from_file_location('continuous_monitor',wrapper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    identity={}
    for folder in ('src','include','scripts','tests'):
        for p in sorted((ROOT/folder).iterdir()):
            if p.is_file():
                target=out/'source'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
                identity[p.relative_to(ROOT).as_posix()]=sha(p)
    shutil.copy2(ROOT/'CMakeLists.txt',out/'source/CMakeLists.txt');identity['CMakeLists.txt']=sha(ROOT/'CMakeLists.txt')
    shutil.copy2(binary.parent/'CMakeCache.txt',out/'CMakeCache.txt')
    models=[]
    def snapshot(path,expected,relative=None):
        data=path.read_bytes();conversion=False
        if hashlib.sha256(data).hexdigest()!=expected:
            normalized=data.replace(b'\r\n',b'\n')
            assert hashlib.sha256(normalized).hexdigest()==expected,('Unexplained input change',path)
            data=normalized;conversion=True
        dst=out/'inputs'/(relative or path.relative_to(ROOT/'datasets'));dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
        models.append({'source':path.relative_to(ROOT).as_posix(),'working_copy_sha256':sha(path),'input_sha256':sha(dst),
                       'restored_manifest_lf_in_snapshot_only':conversion,'snapshot':dst.relative_to(out).as_posix()})
        return dst
    jobs=[]
    for s in json.loads((ROOT/'datasets/netlib/manifest.json').read_text())['instances']:
        model=snapshot(ROOT/'datasets/netlib'/(s['name']+'.mps'),s['mps_sha256'])
        for profile,extra in [('default',[]),('refined',['--refine-basis','--refine-at-checks'])]:
            jobs.append(dict(key=s['name']+'.'+profile,family='lp',name=s['name'],profile=profile,model=model,extra=extra))
    for s in json.loads((BASE/'additional-lp-verified/manifest.json').read_text())['instances']:
        model=snapshot(BASE/'additional-lp-verified'/(s['name']+'.mps'),s['mps_sha256'],Path('additional-lp')/(s['name']+'.mps'))
        for profile,extra in [('default',[]),('refined',['--refine-basis','--refine-at-checks'])]:
            jobs.append(dict(key=s['name']+'.'+profile,family='additional_lp',name=s['name'],profile=profile,model=model,extra=extra))
    qp_paths={}
    for s in json.loads((ROOT/'datasets/qplib/manifest.json').read_text())['instances']:
        model=snapshot(ROOT/'datasets/qplib'/(s['name']+'.qplib'),s['model_sha256'])
        snapshot(ROOT/'datasets/qplib'/(s['name']+'.lp'),s['reference_sha256'])
        qp_paths[s['name']]=model
        jobs.append(dict(key=s['name']+'.default',family='qp',name=s['name'],profile='default',model=model,extra=[]))
    for tolerance in ('1e-10','1e-12'):
        jobs.append(dict(key='9002.tol-'+tolerance,family='qp',name='9002',profile='tolerance_probe',model=qp_paths['9002'],extra=['--tolerance',tolerance]))
    save(out/'metadata.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':sha(binary),
        'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),'logical_cpus':os.cpu_count(),
        'cmake_cache_sha256':sha(out/'CMakeCache.txt'),
        'source_sha256':identity,'inputs':models,'runner_sha256':sha(Path(__file__)),'wrapper_sha256':sha(wrapper),
        'own_before_references':True,'limit_seconds':30,'watchdog_seconds':45,'memory_threshold_mib':1536})
    records=[]
    for job in jobs:
        key=job['key'];command=[str(binary),str(job['model']),'--json','--time-limit','30',*job['extra']]
        wrapped=mod.monitor(command,out/key,45,1536)
        native=dict(wrapped['native_result'] or {});native['status']=wrapped['status']
        save(out/(key+'.ours.json'),native)
        record={k:v for k,v in job.items() if k not in ('model','extra')}
        record.update(model=job['model'].relative_to(out).as_posix(),command=command,status=wrapped['status'],
                      objective=native.get('objective'),iterations=native.get('iterations'),process_seconds=wrapped['wall_seconds'],
                      peak_rss_mib=wrapped['peak_working_set_bytes']/1024**2,peak_commit_mib=wrapped['peak_commit_bytes']/1024**2)
        records.append(record);save(out/'ledger.json',records)
        print(key,wrapped['status'],native.get('objective'),flush=True)
    for r in records:
        key=r['key'];model=out/r['model'];candidate=out/(key+'.ours.json');own=json.loads(candidate.read_text())
        if r['family'] in ('lp','additional_lp'):
            # The native LP CLI exposes a vector in first-COLUMNS order.
            # Independently recover input names so the reference reader can
            # reorder its columns safely without assuming identical ordering.
            names=[];seen=set();section=None
            for line in model.read_text().splitlines():
                tokens=line.split()
                if not tokens or line.startswith('*'):continue
                if tokens[0] in ('ROWS','COLUMNS','RHS','BOUNDS','RANGES','ENDATA') and len(tokens)==1:
                    section=tokens[0];continue
                if section=='COLUMNS' and not any('MARKER' in t for t in tokens) and tokens[0] not in seen:
                    names.append(tokens[0]);seen.add(tokens[0])
            assert len(names)==own.get('columns',len(names))
            mapped=dict(own,variable_names=names)
            candidate=out/(key+'.reference-candidate.json');save(candidate,mapped)
            command=[sys.executable,'-B',str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(candidate),'--limit','30']
        else:
            command=[sys.executable,'-B',str(ROOT/'scripts/reference_qp.py'),'--reference',str(model.with_suffix('.lp')),'--candidate',str(candidate),'--limit','30']
        if r['family']=='qp' and r['profile']=='tolerance_probe':
            previous=out/'9002.default.reference.json'
            ref={k:v for k,v in json.loads(previous.read_text()).items() if not k.startswith('candidate_')}
            ref.update(reference_reused_from=previous.name,reference_reused_sha256=sha(previous),
                       reuse_scope='Same original 9002 model; each probe has its own fresh original-model KKT check.')
        else:
            ref=timed(command,45,out/(key+'.reference'))
        save(out/(key+'.reference.json'),ref)
        r['reference_status']=ref.get('status');r['reference_objective']=ref.get('objective')
        if r['family'] in ('lp','additional_lp'):
            objective=own.get('objective');expected=ref.get('objective');recomputed=ref.get('candidate_recomputed_objective')
            close=lambda a,b: a is not None and b is not None and math.isfinite(a) and math.isfinite(b) and abs(a-b)<=1e-6*(1+max(abs(a),abs(b)))
            r['absolute_violation']=ref.get('candidate_max_violation');r['scaled_violation']=ref.get('candidate_scaled_violation')
            r['checked_completion']=bool(own.get('status')=='optimal' and own.get('optimality_verified') and ref.get('status')=='Optimal'
                 and ref.get('candidate_scaled_violation',math.inf)<=1e-8 and close(objective,expected) and close(objective,recomputed))
            r['relative_objective_error']=abs(objective-expected)/(1+abs(expected)) if objective is not None and expected is not None else None
        else:
            independent=check_qp(model,own);save(out/(key+'.kkt.json'),independent)
            r['absolute_violation']=independent.get('max_violation');r['scaled_violation']=independent.get('scaled_violation')
            r['relative_dual_gap']=independent.get('relative_dual_gap')
            r['checked_completion']=bool(own.get('status')=='optimal' and independent.get('independent_kkt_passed') and
                 ('relative_dual_gap' not in independent or independent.get('diagonal_certificate_passed')))
            r['reference_comparison_completed']=bool(r['checked_completion'] and ref.get('status')=='Optimal' and
                own.get('objective') is not None and ref.get('objective') is not None and
                abs(own['objective']-ref['objective'])<=1e-6*(1+abs(ref['objective'])))
        # A reference mismatch does not erase a native or limited result.
        r['unvalidated_native_completion']=own.get('status')=='optimal' and not r['checked_completion']
        save(out/'ledger.json',records)
        print(key,'original check',r['checked_completion'],'reference',r['reference_status'],flush=True)
    assert sha(binary)==gate['binary_sha256']
    for rel,digest in identity.items():assert sha(ROOT/rel)==digest,rel
    sys.path[:0]=[str(ROOT/'tools/reference/qp'),str(ROOT/'tools/reference/python')]
    import numpy,scipy,highspy,osqp
    save(out/'DEPENDENCIES.json',{'numpy':numpy.__version__,'scipy':scipy.__version__,'highs':highspy.Highs().version(),
        'osqp':osqp.__version__,'compiler':'GCC14.2 x64 UCRT project-local toolchain; see iteration29 ENVIRONMENT.md',
        'reference_role':'Independent validation only; no reference points or bounds enter measured own solves.'})
    summary={'binary_sha256':sha(binary),'records':len(records),'unvalidated_native_completions':sum(r['unvalidated_native_completion'] for r in records),
        'groups':{family+'.'+profile:{'records':len(rows),'checked_completions':sum(r['checked_completion'] for r in rows)}
            for family,profile in sorted({(r['family'],r['profile']) for r in records})
            for rows in [[r for r in records if r['family']==family and r['profile']==profile]]},
        'ledger_sha256':sha(out/'ledger.json'),'scope':'Reused retained inputs; no GPU, fresh-holdout or fair-speed-ranking claim.'}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
