"""Evaluate one unchanged-source compact LP profile on all sixteen inputs."""
import importlib.util
import json
import os
from pathlib import Path
import sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from milp_robustness import timed
from validate_binary_proof import sha,save

def main():
    os.environ['PATH']=str(ROOT/'tools/local-toolchain/mingw64/bin')+os.pathsep+os.environ['PATH']
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    prior=ROOT/'reports/cpu-validation-2026-09-17/results'
    jobs=[r for r in json.loads((prior/'ledger.json').read_text()) if r['family'] in ('lp','additional_lp') and r['profile']=='default']
    assert len(jobs)==16
    out=BASE/'lp-profile';out.mkdir(exist_ok=False)
    binary=ROOT/'build-milp-iter29/solver_cli.exe';flags=['--compact-equalities','--refine-basis','--refine-at-checks']
    assert sha(binary)==json.loads((prior/'metadata.json').read_text())['binary_sha256']
    wrapper=ROOT/'reports/milp-iteration-28/run_contained.py'
    spec=importlib.util.spec_from_file_location('lp_profile_monitor',wrapper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    save(out/'metadata.json',{'binary_sha256':sha(binary),'flags':flags,'source_metadata_sha256':sha(prior/'metadata.json'),
         'runner_sha256':sha(Path(__file__)),'own_before_references':True,'purpose':'One explicit LP profile, not default promotion or a speed ranking.'})
    records=[]
    for job in jobs:
        name=job['name'];model=prior/job['model'];command=[str(binary),str(model),'--json','--time-limit','30',*flags]
        wrapped=mod.monitor(command,out/name,45,1536);own=dict(wrapped['native_result'] or {},status=wrapped['status'])
        save(out/(name+'.ours.json'),own)
        record={'name':name,'family':job['family'],'model':str(model),'model_sha256':sha(model),'status':own['status'],
             'objective':own.get('objective'),'iterations':own.get('iterations'),'compact_fallback':own.get('compact_fallback'),
             'process_seconds':wrapped['wall_seconds'],'peak_rss_mib':wrapped['peak_working_set_bytes']/1024**2}
        records.append(record);save(out/'ledger.json',records);print(name,own['status'],own.get('objective'),flush=True)
    for r in records:
        name=r['name'];own=json.loads((out/(name+'.ours.json')).read_text())
        names=json.loads((prior/(name+'.default.reference-candidate.json')).read_text())['variable_names']
        candidate=out/(name+'.candidate.json');save(candidate,dict(own,variable_names=names))
        ref=timed([sys.executable,'-B',str(ROOT/'scripts/benchmark_lp.py'),'--reference',r['model'],'--candidate',str(candidate),'--limit','30'],45,out/(name+'.reference'))
        save(out/(name+'.reference.json'),ref)
        r['checked_completion']=bool(own['status']=='optimal' and own.get('optimality_verified') and ref.get('status')=='Optimal'
             and ref.get('candidate_scaled_violation',1)<=1e-8 and own.get('objective') is not None
             and abs(own['objective']-ref['objective'])<=1e-6*(1+abs(ref['objective']))
             and abs(own['objective']-ref['candidate_recomputed_objective'])<=1e-6*(1+abs(own['objective'])))
        r['absolute_violation']=ref.get('candidate_max_violation');r['scaled_violation']=ref.get('candidate_scaled_violation')
        save(out/'ledger.json',records)
    summary={'all_pass':all(r['checked_completion'] for r in records),'records':16,'checked_completions':sum(r['checked_completion'] for r in records),
             'compact_fallbacks':sum(bool(r['compact_fallback']) for r in records),'binary_sha256':sha(binary),'ledger_sha256':sha(out/'ledger.json')}
    save(out/'SUMMARY.json',summary)
    save(BASE/'LP_PROFILE.json',{'name':'Compact equality LP evaluation profile','flags':flags,'default_changed':False,
         'binary_sha256':sha(binary),'models':16,'checked_completions':summary['checked_completions'],
         'limitations':'Small public LP set, including reused cases. No timing/industrial/general-MILP claim.'})
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
