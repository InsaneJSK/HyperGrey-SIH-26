"""Reference-only original-QPLIB KKT checks and diagonal Lagrangian bounds.

No optimizer, C++ residual, claimed status, or supplied QPLIB start is trusted.
These floating-point checks are numerical certificates, not exact proofs.
"""
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(model, candidate, tolerance=1e-7):
    sys.path[:0] = [str(ROOT/'tools/reference/qp'), str(ROOT/'tools/reference/python')]
    import numpy as np
    import scipy.sparse as sparse
    from qplib_reference_reader import read
    q = read(model, np, sparse)
    x = np.asarray(candidate.get('primal', []), dtype=float)
    y = np.asarray(candidate.get('row_dual', []), dtype=float)
    a, h, c = q['matrix'], q['hessian'], q['cost']
    failed = {'candidate_valid_shape_and_finite': False, 'independent_kkt_passed': False,
              'diagonal_certificate_passed': False}
    if x.shape!=c.shape or y.shape!=(a.shape[0],) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        return failed
    activity=a@x; magnitude=abs(a)@abs(x); maximum=scaled=0.0
    if not np.all(np.isfinite(activity)) or not np.all(np.isfinite(magnitude)):
        return failed
    for values, sizes, lo, up in [(x,abs(x),q['lower'],q['upper']), (activity,magnitude,q['row_lower'],q['row_upper'])]:
        for delta, bound in [(lo-values,lo),(values-up,up)]:
            mask=np.isfinite(bound)
            if np.any(mask):
                maximum=max(maximum,float(np.max(delta[mask])))
                scaled=max(scaled,float(np.max(delta[mask]/(1+abs(bound[mask])+sizes[mask]))))
    value=float(.5*x@(h@x)+c@x+q['offset'])
    gradient=q['sign']*(h@x+c)+a.T@y
    stationarity=float(np.max(abs(x-np.clip(x-gradient,q['lower'],q['upper']))/(1+abs(x)), initial=0))
    complementarity=0.0
    for i in range(len(y)):
        if y[i]!=0:
            target=q['row_upper'][i] if y[i]>0 else q['row_lower'][i]
            residual=abs(float(y[i]*(activity[i]-target)))/(1+abs(value))
            complementarity=max(complementarity,residual) if math.isfinite(residual) else math.inf
    if not math.isfinite(value) or not np.all(np.isfinite(gradient)) or not math.isfinite(stationarity):
        return failed
    output={'candidate_valid_shape_and_finite':True,'recomputed_objective':value,
            'max_violation':maximum,'scaled_violation':scaled,'stationarity':stationarity,
            'complementarity':complementarity if math.isfinite(complementarity) else None,
            'independent_kkt_passed':max(scaled,stationarity,complementarity)<=tolerance,
            'diagonal_certificate_passed':False}
    diagonal=q['sign']*h.diagonal()
    if (h-sparse.diags(h.diagonal())).nnz==0 and np.all(diagonal>0):
        linear=q['sign']*c+a.T@y
        minimizer=np.clip(-linear/diagonal,q['lower'],q['upper'])
        # Exact formula for the separable Lagrangian minimum at any row dual.
        lower_bound=np.longdouble(q['sign']*q['offset'])
        lower_bound+=np.sum(.5*diagonal.astype(np.longdouble)*minimizer.astype(np.longdouble)**2
                            +linear.astype(np.longdouble)*minimizer, dtype=np.longdouble)
        for i in range(len(y)):
            if y[i]!=0:
                lower_bound-=np.longdouble(y[i])*(q['row_upper'][i] if y[i]>0 else q['row_lower'][i])
        gap=float(abs(q['sign']*value-lower_bound)/(1+abs(value))) if np.isfinite(lower_bound) else None
        output['dual_bound_minimization_sense']=float(lower_bound) if np.isfinite(lower_bound) else None
        output['relative_dual_gap']=gap
        output['diagonal_certificate_passed']=output['independent_kkt_passed'] and gap is not None and gap<=tolerance
    return output
