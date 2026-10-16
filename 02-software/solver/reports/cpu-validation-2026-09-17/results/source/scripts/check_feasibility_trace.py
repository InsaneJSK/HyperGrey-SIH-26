"""Independent saved trace metrics/repetition checks, not general LP certificates."""
import math
from collections import Counter
from check_objective_lattice import read

KINDS={'pump_start','pump_round','pump_target','pump_propagation','pump_fix','pump_projection',
       'dive_start','dive_trial','dive_point','distance_stage','heuristic_repair'}

def verify(data,r):
    t=r['feasibility'];samples=t['samples'];n=len(data['integer']);vectors=len(t.get('rejected_point',[]));checked=0
    if vectors:
        assert vectors==n<=2048 and all(math.isfinite(v) for v in t['rejected_point'])
        assert all(abs(v-round(v))<=1e-7 for v,b in zip(t['rejected_point'],data['integer']) if b)
        assert t['rejected_rounded_violation']>1e-7
    assert type(t['enabled']) is bool
    for key in ('events','calls','stored_values'):
        assert type(t[key]) is int and t[key]>=0
    assert len(samples)==min(512,t['events']) and t['stored_values']<=100000
    if not t['enabled']:assert not samples and t['events']==t['calls']==t['stored_values']==0
    visited={};complete={};counts=Counter()
    for e in samples:
        assert e['kind'] in KINDS;counts[e['kind']+':'+e['status']]+=1
        for key in ('node','call','step','mode','variable','iterations','fractional'):
            assert type(e[key]) is int and e[key]>=0
        assert 0<e['call']<=t['calls'] and e['fractional']<=sum(data['integer'])
        for key in ('alternate','accepted'):assert type(e[key]) is bool
        for key in ('distance','violation'):
            assert e[key] is None or isinstance(e[key],(int,float)) and not isinstance(e[key],bool) and math.isfinite(e[key]) and e[key]>=0
        x=e['point'];target=e['target'];vectors+=len(x)+len(target)
        for v in (x,target):assert not v or len(v)==n<=2048 and all(math.isfinite(a) for a in v)
        if x:
            distances=[abs(a-round(a)) for a,integer in zip(x,data['integer']) if integer]
            assert abs(sum(distances)-e['distance'])<=1e-10*(1+sum(distances))
            assert sum(d>1e-7 for d in distances)==e['fractional']
            violation=0.
            for row,lo,up in zip(data['rows'],data['lower'],data['upper']):
                activity=math.fsum(float(a)*x[j] for j,a in row.items());violation=max(violation,lo-activity,activity-up)
            assert violation<=e['violation']+1e-7*(1+violation)
            if e['accepted']:assert not e['fractional'] and violation<=1e-7 and e['violation']<=1e-7
            checked+=1
        call=e['call'];visited.setdefault(call,set());complete.setdefault(call,True)
        if e['kind'] in ('pump_round','pump_target'):
            if not target:complete[call]=False
            else:
                key=tuple(v for v,b in zip(target,data['integer']) if b)
                assert all(a==round(a) for a in key)
                # Fixed variables are part of the tuple in both records; adding
                # the same fixed coordinates preserves equality of pump keys.
                if complete[call]:assert e['status']==('repeat' if key in visited[call] else 'new')
                if e['kind']=='pump_target':visited[call].add(key)
    assert vectors==t['stored_values']
    return {'all_pass':True,'events_checked':len(samples),'events_truncated':t['events']>len(samples),
            'point_metrics_checked':checked,'stored_values':vectors,'counts':dict(counts),
            'scope':'Independent integer distances, saved target repetition, original row residual floor and bounded trace; not full LP or unrecorded-history proof.'}

def check(model,r):return verify(read(model),r)
