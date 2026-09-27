"""Replay cut-allocation decisions; not a proof of LP or cut validity."""
import math

def decision(e):
    before,after,offset=e['before'],e['after'],e['offset']
    if not all(type(x) in (int,float) and math.isfinite(x) for x in (before,after,offset)):return 'invalid_metric'
    if e['round']<2:return 'minimum_rounds'
    if e['iterations']<256:return 'cheap_round'
    if e['root_iterations']==0:return 'missing_root_work'
    scale=max(1.,abs(before-offset),abs(after-offset));delta=after-before
    gain=max(0.,delta)/scale;effort=max(1.,e['iterations']/e['root_iterations']);threshold=.001*effort
    if not all(math.isfinite(x) for x in (scale,delta,gain,effort,threshold)):return 'invalid_metric'
    return 'diminishing_return' if gain<=threshold else 'productive_round'

def check(r):
    if not __debug__:raise RuntimeError('Assertions required')
    p=r['cut_policy'];trace=p['rounds'];cap=r['work']['root_cut_rounds']
    assert type(p['enabled']) is bool and type(p['capture_enabled']) is bool
    assert type(p['stops']) is int and p['stops']>=0
    version=p.get('version',1);assert type(version) is int and version in (1,2)
    guarded=p.get('require_incumbent',False)
    assert type(guarded) is bool and (not guarded or p['enabled'])
    if version==2:assert 'require_incumbent' in p
    else:assert not guarded
    assert not p['enabled'] or p['capture_enabled']
    if not p['capture_enabled']:assert not trace and p['stops']==0
    assert len(trace)<=cap*(1+r['cut_restarts'])
    previous={};roots={};closed=set();stops=rollbacks=infeasible=0;last_restart=-1
    for e in trace:
        for k in ('node','restart','round','root_iterations','iterations'):assert type(e[k]) is int and e[k]>=0
        assert last_restart<=e['restart']<=r['cut_restarts'];last_restart=e['restart']
        key=(e['restart'],e['node']);assert key not in closed
        assert e['round']==previous.get(key,{}).get('round',0)+1 and 1<=e['round']<=cap
        assert e['restart'] not in roots or roots[e['restart']]==key
        roots[e['restart']]=key
        if version==2:
            assert 'incumbent_objective' in e
            incumbent=e['incumbent_objective']
            assert incumbent is None or (type(incumbent) in (int,float) and math.isfinite(incumbent))
            if e['restart']>0:assert incumbent==r['cut_restart_objective']
        if key in previous:
            assert previous[key]['root_iterations']==e['root_iterations'] and previous[key]['after']==e['before']
            if version==2:assert previous[key]['incumbent_objective']==e['incumbent_objective']
        reason=e['decision']
        if reason in ('rollback','infeasible'):
            rollbacks+=reason=='rollback';infeasible+=reason=='infeasible';closed.add(key)
        else:
            expected='disabled' if not p['enabled'] else 'round_cap' if e['round']==cap else 'no_incumbent' if guarded and e['incumbent_objective'] is None else decision(e)
            assert reason==expected,(reason,expected,e)
            if reason in ('round_cap','diminishing_return'):closed.add(key)
            stops+=reason=='diminishing_return'
        previous[key]=e
    assert p['stops']==stops
    if p['capture_enabled']:
        assert rollbacks==r['cut_rollbacks']
        assert not infeasible or (r['status']=='infeasible' and not r.get('primal'))
        if r['work']['enabled']:
            cut=next(p for p in r['work']['phases'] if p['name']=='cut_lp')
            assert len(trace)==cut['lp_calls'] and sum(e['iterations'] for e in trace)>=cut['iterations']
        assert sum(e['iterations'] for e in trace)+sum(e['root_iterations'] for e in previous.values())<=r['lp_iterations']
    return {'all_pass':True,'rounds_checked':len(trace),'stops_checked':stops,'rollbacks_checked':rollbacks,
            'scope':__doc__}
