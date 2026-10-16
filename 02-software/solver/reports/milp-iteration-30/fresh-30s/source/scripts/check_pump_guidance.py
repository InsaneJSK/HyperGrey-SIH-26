"""Check bounded pump-seed telemetry; fractional points are NOT MILP solutions."""
import math
from check_objective_lattice import read
from milp_robustness import reference


def verify(data, r):
    g=r['pump_guidance'];n=len(data['integer'])
    assert type(g['enabled']) is bool
    fields=('calls','candidates','rejected','improvements','dives','steps','stored_values')
    for k in fields:assert type(g[k]) is int and g[k]>=0
    assert g['improvements']+g['rejected']<=g['candidates']
    assert g['dives']<=min(g['calls'],g['improvements']) and g['steps']<=64*g['dives']
    assert len(g['samples'])==min(8,g['calls']) and g['stored_values']<=20000
    if not g['enabled']:assert not any(g[k] for k in fields)
    totals={k:0 for k in ('candidates','rejected','improvements','steps')};used=0;values=0;points=0
    for s in g['samples']:
        for k in ('node','candidates','rejected','improvements','steps'):assert type(s[k]) is int and s[k]>=0
        for k in ('selected','used'):assert type(s[k]) is bool
        assert s['improvements']+s['rejected']<=s['candidates']
        assert s['selected']==(s['improvements']>0) and (not s['used'] or s['selected'])
        assert s['steps']<=64*int(s['used']);used+=s['used']
        for k in totals:totals[k]+=s[k]
        for k in ('initial_distance','best_distance'):
            assert s[k] is None or type(s[k]) in (float,int) and math.isfinite(s[k]) and s[k]>=0
        if s['selected']:assert s['best_distance']<s['initial_distance']
        else:assert s['initial_distance']==s['best_distance'] and not s['point'] and not s['initial']
        assert bool(s['point'])==bool(s['initial'])
        for label,metric in (('initial','initial_distance'),('point','best_distance')):
            x=s[label];values+=len(x)
            if not x:continue
            assert len(x)==n<=10000 and all(type(v) in (int,float) and math.isfinite(v) for v in x)
            d=math.fsum(abs(v-round(v)) for v,b in zip(x,data['integer']) if b)
            assert abs(d-s[metric])<=1e-10*(1+d)
            if label=='point':
                for row,lo,up in zip(data['rows'],data['lower'],data['upper']):
                    activity=math.fsum(float(a)*x[j] for j,a in row.items())
                    assert lo-activity<=1e-7 and activity-up<=1e-7
                points+=1
    assert values==g['stored_values']
    for k,v in totals.items():assert v<=g[k] and (g['calls']>8 or v==g[k])
    assert used<=g['dives'] and (g['calls']>8 or used==g['dives'])
    return {'all_pass':True,'calls':g['calls'],'guided_dives':g['dives'],'guided_steps':g['steps'],
            'seed_points_checked':points,'stored_values':values,'samples_truncated':g['calls']>8,
            'scope':__doc__}


def check(model,r):
    c=verify(read(model),r);refs=[]
    for s in r['pump_guidance']['samples']:
        if not s['point']:continue
        ref=reference(model,{'primal':s['point']},0)
        assert ref.get('candidate_checked') is True and ref['candidate_max_violation']<=1e-7
        refs.append({'node':s['node'],'row_bound_violation':ref['candidate_max_violation'],
                     'integer_violation':ref['candidate_integer_violation'],'version':ref['version']})
    c['independent_original_model_checks']=refs
    return c
