"""Validate private reoptimization accounting; not a mathematical LP certificate."""
import math

COUNTS=('calls','compatible','primal','dual','rejected','verified','phase_one_iterations','factorizations')
TIMES=('canonical_seconds','factor_seconds','pricing_seconds')

def check(r):
    s=r['pump_reopt'];assert type(s['enabled']) is bool
    for k in COUNTS:assert type(s[k]) is int and s[k]>=0,k
    for k in TIMES:assert type(s[k]) in (int,float) and math.isfinite(s[k]) and s[k]>=0,k
    assert s['primal']+s['dual']+s['rejected']<=s['compatible']<=s['calls']
    assert s['verified']<=s['primal']+s['dual'] and s['compatible']<=s['factorizations']
    assert s['calls']<=2*r['pump_projections'] # Compact fallback may add a second cold call.
    assert s['phase_one_iterations']<=r['lp_iterations']
    if s['enabled']:assert s['calls']>=r['pump_projections']
    else:assert not any(s[k] for k in COUNTS+TIMES) and s['replay'] is None
    replay=s['replay']
    if replay is not None:
        assert s['primal']>0 and r['feasibility']['enabled'] and type(replay['captured']) is bool
        if replay['captured']:
            n=len(replay['cost']);m=len(replay['rows']);assert n<=10000 and m<=20000
            assert sum(map(len,replay['rows']))<=200000
            assert len(replay['lower'])==len(replay['upper'])==n
            assert len(replay['row_lower'])==len(replay['row_upper'])==m
            assert len(replay['basis_mapping'])==n and len(replay['basis_rows'])==len(replay['basis_equality'])==len(replay['input_basis_columns'])
            assert len(set(replay['input_basis_columns']))==len(replay['input_basis_columns'])
            assert not replay['basis_reduced_upper_bounds']
            cols=replay['basis_structural_columns']
            assert all(type(j) is int and 0<=j<cols+len(replay['basis_rows']) for j in replay['input_basis_columns'])
            for rows,width in ((replay['rows'],n),(replay['basis_rows'],cols),(replay['basis_mapping'],cols)):
                for row in rows:
                    for j,v in row:assert type(j) is int and 0<=j<width and math.isfinite(v)
    return {'all_pass':True,**{k:s[k] for k in COUNTS},'replay_captured':bool(replay and replay['captured']),'scope':__doc__}
