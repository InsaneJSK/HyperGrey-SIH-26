"""Validate refinement telemetry nested inside the existing exclusive work ledger."""
import math
from check_milp_work import check as work_check
COUNTS=('rhs_calls','primal_rhs','dual_rhs','scans','entries','attempts','accepted')

def stats(s):
    for k in COUNTS:assert type(s[k]) is int and s[k]>=0,k
    assert math.isfinite(s['seconds']) and s['seconds']>=0
    assert s['rhs_calls']==s['primal_rhs']+s['dual_rhs']
    assert s['accepted']<=s['attempts']<=2*s['rhs_calls']
    assert s['rhs_calls']<=s['scans']<=s['rhs_calls']+s['attempts']

def check(r):
    work_check(r);w=r['work'];enabled=w['refinement_enabled'];total=w['refinement'];stats(total)
    for p in w['phases']:
        s=p['refinement'];stats(s)
        assert s['seconds']<=p['seconds']+1e-7*(1+p['seconds'])
        if not enabled:assert all(s[k]==0 for k in (*COUNTS,'seconds'))
    for k in COUNTS:assert sum(p['refinement'][k] for p in w['phases'])==total[k],k
    assert abs(sum(p['refinement']['seconds'] for p in w['phases'])-total['seconds'])<=1e-8*(1+total['seconds'])
    assert total['seconds']<=w['seconds']+1e-7*(1+w['seconds'])
    assert not enabled or w['enabled']
    if not r['basis_refinement_enabled']:assert all(total[k]==0 for k in (*COUNTS,'seconds'))
    assert not r.get('basis_refinement_at_checks',False) or r['basis_refinement_enabled']
    return {'all_pass':True,'enabled':enabled,**total,'scope':__doc__}
