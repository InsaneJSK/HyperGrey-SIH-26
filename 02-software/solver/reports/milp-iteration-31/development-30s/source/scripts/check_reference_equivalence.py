"""Check reference vector-validation fields against frozen14; not solver timing."""
import importlib.util
import json
from pathlib import Path
from time import perf_counter
from benchmark_lp import ROOT
import milp_robustness as current
from validate_binary_proof import sha,save

def main():
    if not __debug__:raise RuntimeError('Assertions required')
    out=ROOT/'reports/milp-iteration-15/reference-equivalence';out.mkdir(parents=True,exist_ok=False)
    old_path=ROOT/'reports/milp-iteration-14/final-source/scripts/milp_robustness.py'
    spec=importlib.util.spec_from_file_location('frozen14_reference',old_path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    keys=['rows','columns','maximize','integers','candidate_checked','candidate_max_violation','candidate_integer_violation','candidate_objective','candidate_error']
    results=[]
    rows=json.loads((ROOT/'reports/milp-iteration-14/wave-30s/results.json').read_text())
    for r in rows:
        if r['profile']!='baseline':continue
        model=ROOT/r['model'];assert sha(model)==r['model_sha256']
        p=ROOT/'reports/milp-iteration-14/wave-30s'/(r['key']+'.ours.json');assert sha(p)==r['ours_sha256']
        point=json.loads(p.read_text());synthetic=not bool(point.get('primal'))
        if synthetic:point['primal']=[0.]*point['columns']
        start=perf_counter();a=old.reference(model,point,0);old_seconds=perf_counter()-start
        start=perf_counter();b=current.reference(model,point,0);new_seconds=perf_counter()-start
        assert {k:a.get(k) for k in keys}=={k:b.get(k) for k in keys},r['name']
        results.append({'model':r['name'],'model_sha256':sha(model),'all_pass':True,'synthetic_zero_vector':synthetic,
                        'old_check_seconds':old_seconds,'new_check_seconds':new_seconds,'fields':{k:b.get(k) for k in keys}})
        save(out/'results.json',results);print(r['name'],'validation fields identical',flush=True)
    save(out/'SUMMARY.json',{'all_pass':True,'models':len(results),'old_helper_sha256':sha(old_path),
         'new_helper_sha256':sha(Path(current.__file__)),'results_sha256':sha(out/'results.json'),
         'scope':'Same validation outputs, same accumulation order, cached binding arrays. Zero solve limit; NOT optimizer trajectory or solver-speed equivalence.'})

if __name__=='__main__':main()
