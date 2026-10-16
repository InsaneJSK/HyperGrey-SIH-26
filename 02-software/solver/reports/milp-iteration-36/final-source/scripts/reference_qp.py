"""Reference only: independently parse original QPLIB, audit LP export, solve using OSQP."""
import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools/reference/qp"),str(ROOT/"tools/reference/python")]
import highspy
import numpy as np
import scipy.sparse as sparse
import osqp
from qplib_reference_reader import read as read_original
from qp_certificate import check as check_certificate

def main(model,candidate,limit):
    h=highspy.Highs();h.setOptionValue("output_flag",False)
    if h.readModel(str(model))==highspy.HighsStatus.kError:raise RuntimeError("Cannot parse official LP export")
    h.ensureColwise(); lp=h.getLp(); hs=h.getModel().hessian_; matrix=lp.a_matrix_;n=lp.num_col_
    if hs.format_!=highspy.HessianFormat.kTriangular:raise RuntimeError("Unexpected Hessian storage")
    lower=sparse.csc_matrix((hs.value_,hs.index_,hs.start_),shape=(n,n))
    exported_hessian=lower+lower.T-sparse.diags(lower.diagonal())
    original=read_original(model.with_suffix('.qplib'),np,sparse)
    full=original['hessian'];a=original['matrix'];n=len(original['cost'])
    if n!=lp.num_col_ or a.shape[0]!=lp.num_row_:raise RuntimeError('Original/export dimensions differ')
    if not all(name.startswith('x') and name[1:].isdigit() for name in lp.col_names_):raise RuntimeError('Unsupported export names')
    permutation=sorted(range(n),key=lambda j:int(lp.col_names_[j][1:]))
    discrepancy=exported_hessian[permutation,:][:,permutation]-full
    export_difference=float(max(abs(discrepancy.data),default=0))
    constrained=sparse.vstack([a,sparse.eye(n)],format='csc')
    lows=np.concatenate([original['row_lower'],original['lower']]);ups=np.concatenate([original['row_upper'],original['upper']])
    sign=original['sign'];cost=original['cost'];offset=original['offset']
    start=time.perf_counter();reference=osqp.OSQP()
    reference.setup(P=sparse.triu(sign*full,format='csc'),q=sign*cost,A=constrained,l=lows,u=ups,
                    eps_abs=1e-8,eps_rel=1e-8,max_iter=200000,time_limit=limit,verbose=False,polishing=False)
    result=reference.solve();elapsed=time.perf_counter()-start
    output={"solver":"OSQP","version":osqp.__version__,"parser":"independent Python QPLIB reader",
            "export_audit_parser":"HiGHS "+h.version(),"export_hessian_max_difference":export_difference,
            "export_hessian_changed_entries":discrepancy.nnz,
            "status":"Optimal" if result.info.status=='solved' else result.info.status,
            "objective":sign*result.info.obj_val+offset if math.isfinite(result.info.obj_val) else None,
            "total_seconds":elapsed,"solve_seconds":result.info.solve_time,"iterations":result.info.iter,
            "primal_residual":result.info.prim_res,"dual_residual":result.info.dual_res}
    x=np.asarray(candidate.get('primal',[]),dtype=float)
    if len(x)==n and np.all(np.isfinite(x)):
        activity=constrained@x;magnitude=abs(constrained)@abs(x)
        violation=0.0;scaled=0.0
        for values,bounds in [(lows-activity,lows),(activity-ups,ups)]:
            mask=np.isfinite(bounds)
            if np.any(mask):
                violation=max(violation,float(np.max(values[mask])))
                scaled=max(scaled,float(np.max(values[mask]/(1+abs(bounds[mask])+magnitude[mask]))))
        output.update(candidate_max_violation=violation,candidate_scaled_violation=scaled,
                      candidate_recomputed_objective=float(.5*x@(full@x)+cost@x+offset),
                      candidate_mapping="Original QPLIB variable indices; supplied start ignored")
        if a.shape[0]==0:
            gradient=sign*(full@x+cost)
            residual=np.max(abs(x-np.clip(x-gradient,original['lower'],original['upper']))/(1+abs(x)))
            output['candidate_independent_stationarity']=float(residual)
    output['candidate_certificate']=check_certificate(model.with_suffix('.qplib'),candidate)
    print(json.dumps(output,allow_nan=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--limit',type=float,default=15);args=p.parse_args()
    main(args.reference,json.loads(args.candidate.read_text()),args.limit)
