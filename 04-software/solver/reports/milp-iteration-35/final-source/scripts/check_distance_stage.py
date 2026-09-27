"""Check staged private-LP accounting and bounded snapshots, not global proof."""
import math
from check_pump_reopt import COUNTS,TIMES
FIELDS=('considered','eligible','attempts','verified','incumbents','child_offers','child_compatible','child_verified')

def check(r):
    s=r['distance_stage'];d=s['reopt'];assert type(s['enabled']) is bool
    for k in FIELDS:assert type(s[k]) is int and s[k]>=0,k
    for k in COUNTS:assert type(d[k]) is int and d[k]>=0,k
    for k in TIMES:assert type(d[k]) in (int,float) and math.isfinite(d[k]) and d[k]>=0,k
    assert s['incumbents']<=s['verified']<=s['attempts']<=s['eligible']<=s['considered']<=r['pump_distance']['dives']
    assert s['attempts']<=d['calls']<=2*s['attempts']
    assert d['primal']+d['dual']+d['rejected']<=d['compatible']<=d['calls']
    assert d['verified']<=d['primal']+d['dual'] and d['compatible']<=d['factorizations']
    assert d['phase_one_iterations']<=r['lp_iterations']
    assert s['child_verified']<=s['child_compatible']<=s['child_offers']<=2*s['verified']
    assert s['child_compatible']<=r['distance_reopt']['compatible'] and s['child_verified']<=r['distance_reopt']['verified']
    assert len(s['samples'])==min(8,s['considered'])
    if s['enabled']:assert r['distance_reopt']['enabled'] and s['considered']==r['pump_distance']['dives']
    else:assert not any(s[k] for k in FIELDS) and not any(d[k] for k in COUNTS+TIMES) and s['replay'] is s['child_replay'] is None
    totals=dict.fromkeys(('eligible','attempted','verified','accepted'),0)
    for sample in s['samples']:
        for k in ('node','iterations'):assert type(sample[k]) is int and sample[k]>=0
        for k in totals:assert type(sample[k]) is bool;totals[k]+=sample[k]
        assert sample['accepted']<=sample['verified']<=sample['attempted']<=sample['eligible']
        assert isinstance(sample['status'],str) and sample['status']
        for k in ('available_seconds','seconds'):assert type(sample[k]) in (int,float) and math.isfinite(sample[k]) and sample[k]>=0
        assert sample['available_seconds']<=2.000001
        if sample['verified']:assert sample['status']=='optimal'
        if not sample['eligible']:assert sample['status']=='ineligible'
    for k,target in [('eligible','eligible'),('attempted','attempts'),('verified','verified'),('accepted','incumbents')]:
        assert totals[k]<=s[target] and (s['considered']>8 or totals[k]==s[target])
    for name,count in [('replay',s['attempts']),('child_replay',s['child_offers'])]:
        f=s[name]
        if f is None:continue
        assert count>0 and r['feasibility']['enabled'] and type(f['captured']) is bool
        if not f['captured']:continue
        n=len(f['cost']);m=len(f['rows']);cols=f['basis_structural_columns'];rows=len(f['basis_rows'])
        assert n<=10000 and m<=20000 and sum(map(len,f['rows']))<=200000
        assert len(f['lower'])==len(f['upper'])==n and len(f['row_lower'])==len(f['row_upper'])==m
        assert len(f['input_basis_columns'])==len(f['basis_equality'])==rows
        assert len(set(f['input_basis_columns']))==rows and not f['basis_reduced_upper_bounds']
        assert all(type(j) is int and 0<=j<cols+rows for j in f['input_basis_columns'])
        for matrix,width in ((f['rows'],n),(f['basis_rows'],cols),(f['basis_mapping'],cols)):
            for row in matrix:
                for j,v in row:assert type(j) is int and 0<=j<width and math.isfinite(v)
    return {'all_pass':True,**{k:s[k] for k in FIELDS},'reopt':{k:d[k] for k in COUNTS},
            'replay_captured':bool(s['replay'] and s['replay']['captured']),
            'child_replay_captured':bool(s['child_replay'] and s['child_replay']['captured']),'scope':__doc__}
