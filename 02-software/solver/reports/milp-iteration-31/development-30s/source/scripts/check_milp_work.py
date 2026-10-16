"""Check exclusive phase bookkeeping, not the correctness of LP bounds."""
import math
NAMES=['other','root_lp','cut_lp','tree_lp','pump','pump_fix','pump_projection','dive',
       'neighborhood','repair','branch_probe','lp_recovery','presolve','cut_separation','validation','restart','binary']

def check(result):
    if not __debug__:raise RuntimeError('Assertions required')
    w=result['work'];rows=w['phases'];assert [r['name'] for r in rows]==NAMES
    for r in rows:
        assert isinstance(r['seconds'],(int,float)) and math.isfinite(r['seconds']) and r['seconds']>=0
        for k in ('lp_calls','iterations'):assert type(r[k]) is int and r[k]>=0
    assert math.isfinite(w['seconds']) and w['seconds']>=0
    assert abs(sum(r['seconds'] for r in rows)-w['seconds'])<=1e-8*(1+w['seconds'])
    assert w['seconds']<=result['total_seconds']+1e-6
    if w['enabled']:assert sum(r['iterations'] for r in rows)==result['lp_iterations']
    else:assert w['seconds']==0 and all(r['seconds']==r['lp_calls']==r['iterations']==0 for r in rows)
    if 'root_cut_rounds' in w:
        assert type(w['root_cut_rounds']) is int and 0<=w['root_cut_rounds']<=5
        assert rows[NAMES.index('cut_lp')]['lp_calls']<=w['root_cut_rounds']*(1+result['cut_restarts'])
        if w['restart_by_nodes'] and result['cut_restarts']:assert result['cut_restart_nodes']==w['restart_nodes']
    return {'all_pass':True,'enabled':w['enabled'],'iterations':sum(r['iterations'] for r in rows),
            'scope':__doc__}
