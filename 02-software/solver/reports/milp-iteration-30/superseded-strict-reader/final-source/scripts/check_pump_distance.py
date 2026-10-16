"""Check bounded private-distance telemetry, not an optimality certificate."""
import math
from check_objective_lattice import read


def verify(data,r):
    g=r['pump_distance'];guidance=r['pump_guidance'];fields=('dives','lp_calls','verified_points','warm_starts')
    assert type(g['enabled']) is bool
    for k in fields:assert type(g[k]) is int and g[k]>=0
    assert g['dives']<=guidance['dives'] and g['lp_calls']<=128*g['dives']
    assert g['verified_points']<=min(g['lp_calls'],64*g['dives']) and g['warm_starts']<=g['lp_calls']
    if g['enabled']:assert guidance['enabled'] and g['dives']==guidance['dives']
    else:assert not any(g[k] for k in fields)
    assert len(g['samples'])==min(8,g['dives'])
    totals={k:0 for k in fields if k!='dives'};checked=0
    events=r.get('feasibility',{}).get('samples',[])
    for s in g['samples']:
        for k in ('node','auxiliaries',*totals):assert type(s[k]) is int and s[k]>=0
        assert s['auxiliaries']<=sum(data['integer']) and s['lp_calls']<=128
        assert s['verified_points']<=min(64,s['lp_calls']) and s['warm_starts']<=s['lp_calls']
        for k in totals:totals[k]+=s[k]
        assert type(s['initial_distance']) in (float,int) and math.isfinite(s['initial_distance']) and s['initial_distance']>=0
        for k in ('first_distance','last_distance','first_target_distance','last_target_distance'):
            assert (s[k] is not None)==(s['verified_points']>0)
            if s[k] is not None:assert type(s[k]) in (float,int) and math.isfinite(s[k]) and s[k]>=0
        if s['verified_points']:
            assert s['first_distance']<=s['first_target_distance']+1e-8
            assert s['last_distance']<=s['last_target_distance']+1e-8
        seeds=[v for v in guidance['samples'] if v['node']==s['node'] and v['used']]
        if seeds:
            seed=seeds[0];assert abs(seed['best_distance']-s['initial_distance'])<=1e-10*(1+s['initial_distance'])
            starts=[e for e in events if e['node']==s['node'] and e['kind']=='dive_start' and e['status']=='pump_distance']
            if starts:
                start=starts[0];points=[e for e in events if e['call']==start['call'] and e['mode']==0 and e['kind']=='dive_point']
                assert len(points)<=s['verified_points']
                for e in points:
                    if not e['point'] or not seed['point']:continue
                    target=[math.copysign(math.floor(abs(v)+.5),v) for v in seed['point']]
                    distance=math.fsum(abs(x-t) for x,t,b in zip(e['point'],target,data['integer']) if b)
                    if e is points[0]:assert abs(distance-s['first_target_distance'])<=1e-8*(1+distance)
                    if len(points)==s['verified_points'] and e is points[-1]:assert abs(distance-s['last_target_distance'])<=1e-8*(1+distance)
                    checked+=1
                if points:assert abs(points[0]['distance']-s['first_distance'])<=1e-10*(1+s['first_distance'])
                if points and len(points)==s['verified_points']:assert abs(points[-1]['distance']-s['last_distance'])<=1e-10*(1+s['last_distance'])
    for k,v in totals.items():assert v<=g[k] and (g['dives']>8 or v==g[k])
    return {'all_pass':True,**{k:g[k] for k in fields},'distance_metrics_checked':checked,
            'samples_truncated':g['dives']>8,'scope':__doc__}


def check(model,r):return verify(read(model),r)
