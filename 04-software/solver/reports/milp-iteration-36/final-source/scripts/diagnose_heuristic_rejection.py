"""Retain an actual rejected dive point and cold-replay its integer fixing."""
import json
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from milp_robustness import timed,reference
from inspect_lp_failure import export_model
from check_feasibility_trace import check

def main():
    run=ROOT/'reports/milp-iteration-19/rejection-capture';out=ROOT/'reports/milp-iteration-19/rejection-replay'
    out.mkdir(parents=True,exist_ok=True);assert not any(out.iterdir()),'Refuse to overwrite replay evidence'
    source=run/'blend2.capture.0.ours.json';r=json.loads(source.read_text())
    model=ROOT/json.loads((run/'results.json').read_text())[0]['model']
    checked=check(model,r);save(out/'trace-check.json',checked)
    x=r['feasibility']['rejected_point'];assert len(x)==353
    sys.path.insert(0,str(ROOT/'tools/reference/python'));import highspy
    h=highspy.Highs();h.setOptionValue('output_flag',False);assert h.readModel(str(model))!=highspy.HighsStatus.kError
    h.ensureColwise();lp=h.getLp();integers=[t==highspy.HighsVarType.kInteger for t in lp.integrality_]
    rounded=[round(v) if b else v for v,b in zip(x,integers)]
    raw_ref=reference(model,{'primal':x},0);rounded_ref=reference(model,{'primal':rounded},0)
    assert raw_ref['candidate_max_violation']>1e-7 and rounded_ref['candidate_max_violation']>1e-7
    save(out/'raw-reference.json',raw_ref);save(out/'rounded-reference.json',rounded_ref)
    rows=[[] for _ in range(lp.num_row_)];a=lp.a_matrix_;starts,indices,values=a.start_,a.index_,a.value_
    for j in range(lp.num_col_):
        for k in range(starts[j],starts[j+1]):rows[indices[k]].append([j,float(values[k])])
    finite=lambda v:float(v) if math.isfinite(v) else None
    f={'cost':list(lp.col_cost_),'offset':lp.offset_,'maximize':lp.sense_==highspy.ObjSense.kMaximize,'rows':rows,
       'lower':[rounded[j] if integers[j] else finite(v) for j,v in enumerate(lp.col_lower_)],
       'upper':[rounded[j] if integers[j] else finite(v) for j,v in enumerate(lp.col_upper_)],
       'row_lower':[finite(v) for v in lp.row_lower_],'row_upper':[finite(v) for v in lp.row_upper_]}
    fixing=out/'integer-fixing.mps';offset=export_model(f,fixing);assert offset==0
    save(out/'rejected-point.json',{'primal':x,'rounded':rounded,'source_sha256':sha(source),'model_sha256':sha(model),
        'node':r['feasibility']['rejected_node'],'call':r['feasibility']['rejected_call'],'step':r['feasibility']['rejected_step']})
    binary=ROOT/'reports/milp-iteration-18/final_solver_cli.exe';replays=[]
    for method in ('sparse','dense'):
        cmd=[str(binary),str(fixing),'--json','--lp-method',method,'--refine-basis','--refine-at-checks','--tolerance','1e-11','--time-limit','1','--iteration-limit','10000']
        p=timed(cmd,15,out/method);save(out/(method+'.json'),p)
        original_check=reference(model,p,0);fixing_check=reference(fixing,p,5)
        save(out/(method+'.original-reference.json'),original_check);save(out/(method+'.fixing-reference.json'),fixing_check)
        replays.append({'method':method,'status':p['status'],'objective':p.get('objective'),
            'seconds':p.get('total_seconds'),'original_violation':original_check.get('candidate_max_violation'),
            'integer_violation':original_check.get('candidate_integer_violation'),'fixing_reference_status':fixing_check['status'],
            'valid':original_check.get('candidate_checked',False) and original_check.get('candidate_max_violation',math.inf)<=1e-7 and original_check.get('candidate_integer_violation',math.inf)<=1e-7})
    assert any(p['valid'] for p in replays)
    save(out/'SUMMARY.json',{'all_pass':True,'raw_violation':raw_ref['candidate_max_violation'],
        'rounded_violation':rounded_ref['candidate_max_violation'],'replays':replays,'binary_sha256':sha(binary),
        'runner_sha256':sha(Path(__file__)),'fixing_sha256':sha(fixing),'source_sha256':sha(source),
        'scope':'Cold fixing replay, not original warm LP pivot replay. Reference points are never fed to the core.'})
    print(json.dumps(replays,indent=2),flush=True)

if __name__=='__main__':main()
