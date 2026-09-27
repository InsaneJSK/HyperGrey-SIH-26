"""Check private basis-handoff accounting and bounded replay shape, not proof."""
import math
from check_pump_reopt import COUNTS,TIMES
SEED=('seed_updates','seed_offers','seed_compatible','seed_verified')

def check(r):
    s=r['distance_reopt'];assert type(s['enabled']) is bool
    for k in COUNTS+SEED:assert type(s[k]) is int and s[k]>=0,k
    for k in TIMES:assert type(s[k]) in (int,float) and math.isfinite(s[k]) and s[k]>=0,k
    assert s['primal']+s['dual']+s['rejected']<=s['compatible']<=s['calls']
    assert s['verified']<=s['primal']+s['dual'] and s['compatible']<=s['factorizations']
    assert s['calls']<=2*r['pump_distance']['lp_calls']
    assert s['phase_one_iterations']<=r['lp_iterations']
    assert s['seed_updates']<=r['pump_guidance']['improvements']
    assert s['seed_verified']<=s['seed_compatible']<=s['seed_offers']<=2*r['pump_distance']['dives']
    assert s['seed_compatible']<=s['compatible'] and s['seed_verified']<=s['verified']
    if s['seed_offers']:assert s['seed_updates']>0
    if s['enabled']:
        assert r['pump_reopt']['enabled'] and r['pump_distance']['enabled'] and r['pump_guidance']['enabled']
        assert s['calls']>=r['pump_distance']['lp_calls']
    else:assert not any(s[k] for k in COUNTS+SEED+TIMES) and s['replay'] is None
    f=s['replay']
    if f is not None:
        assert s['seed_offers'] and r['feasibility']['enabled'] and type(f['captured']) is bool
        if f['captured']:
            n=len(f['cost']);m=len(f['rows']);cols=f['basis_structural_columns'];rows=len(f['basis_rows'])
            assert n<=10000 and m<=20000 and sum(map(len,f['rows']))<=200000
            assert len(f['lower'])==len(f['upper'])==n and len(f['row_lower'])==len(f['row_upper'])==m
            # Offered basis may have DIFFERENT dimensions: rejection is legitimate.
            assert len(f['input_basis_columns'])==len(f['basis_equality'])==rows
            assert len(set(f['input_basis_columns']))==rows and not f['basis_reduced_upper_bounds']
            assert all(type(j) is int and 0<=j<cols+rows for j in f['input_basis_columns'])
            for matrix,width in ((f['rows'],n),(f['basis_rows'],cols),(f['basis_mapping'],cols)):
                for row in matrix:
                    for j,v in row:assert type(j) is int and 0<=j<width and math.isfinite(v)
    return {'all_pass':True,**{k:s[k] for k in COUNTS+SEED},'replay_captured':bool(f and f['captured']),'scope':__doc__}
