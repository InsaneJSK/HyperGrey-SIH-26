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
    out=BASE/'results';out.mkdir(exist_ok=False)
    binary=ROOT/'build-milp-iter29/solver_cli.exe'
    prior=ROOT/'reports/cpu-validation-2026-09-17/results'
    model=prior/'inputs/additional-lp/bandm.mps'
    names=json.loads((prior/'bandm.default.reference-candidate.json').read_text())['variable_names']
    wrapper=ROOT/'reports/milp-iteration-28/run_contained.py'
    spec=importlib.util.spec_from_file_location('bandm_monitor',wrapper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    profiles={'unscaled':['--no-scaling'],'compact':['--compact-equalities'],
              'compact_refined':['--compact-equalities','--refine-basis','--refine-at-checks'],
              'compact_unscaled':['--compact-equalities','--no-scaling'],
              'compact_unscaled_refined':['--compact-equalities','--no-scaling','--refine-basis','--refine-at-checks'],
              'dense':['--lp-method','dense']}
    save(out/'metadata.json',{'binary_sha256':sha(binary),'model_sha256':sha(model),'profiles':profiles,'runner_sha256':sha(Path(__file__))})
    records=[]
    for name,flags in profiles.items():
        cmd=[str(binary),str(model),'--json','--time-limit','30',*flags]
        wrapped=mod.monitor(cmd,out/name,45,1536)
        own=dict(wrapped['native_result'] or {},status=wrapped['status']);save(out/(name+'.ours.json'),own)
        record={'profile':name,'status':own['status'],'objective':own.get('objective'),'iterations':own.get('iterations'),
                'process_seconds':wrapped['wall_seconds'],'peak_rss_mib':wrapped['peak_working_set_bytes']/1024**2}
        records.append(record);save(out/'ledger.json',records);print(record,flush=True)
    for r in records:
        name=r['profile'];own=json.loads((out/(name+'.ours.json')).read_text())
        candidate=out/(name+'.candidate.json');save(candidate,dict(own,variable_names=names))
        ref=timed([sys.executable,'-B',str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model),'--candidate',str(candidate),'--limit','30'],45,out/(name+'.reference'))
        save(out/(name+'.reference.json'),ref)
        r['checked_completion']=bool(
             own['status']=='optimal' and own.get('optimality_verified') and ref.get('status')=='Optimal'
             and ref.get('candidate_scaled_violation',1)<=1e-8 and own.get('objective') is not None
             and abs(own['objective']-ref['objective'])<=1e-6*(1+abs(ref['objective']))
             and abs(own['objective']-ref['candidate_recomputed_objective'])<=1e-6*(1+abs(own['objective'])))
        r['absolute_violation']=ref.get('candidate_max_violation');r['scaled_violation']=ref.get('candidate_scaled_violation')
        save(out/'ledger.json',records)
    save(out/'SUMMARY.json',{'records':len(records),'checked_completions':sum(r['checked_completion'] for r in records),
                           'default_sparse_fixed':False,'binary_sha256':sha(binary),'ledger_sha256':sha(out/'ledger.json')})
    print('Bandm diagnostic complete',flush=True)

if __name__=='__main__':main()
