"""Check candidate-only repair accounting; no fixing-LP bound is a MILP proof."""
import math

def check(r):
    h=r['heuristic_repair'];assert type(h['enabled']) is bool
    for k in ('attempts','successes','duplicate_skips','sparse_calls','dense_calls'):
        assert type(h[k]) is int and h[k]>=0
    assert h['successes']<=h['attempts']<=16
    assert h['dense_calls']<=h['sparse_calls']<=h['attempts']
    for k in ('seconds','shared_seconds','allowance'):
        assert type(h[k]) in (int,float) and math.isfinite(h[k]) and h[k]>=0
    assert h['seconds']<=h['shared_seconds']+1e-10
    assert h['shared_seconds']==r['candidate_repair_seconds']
    if not h['enabled']:assert all(h[k]==0 for k in ('attempts','successes','duplicate_skips','sparse_calls','dense_calls','seconds'))
    if r['work']['enabled']:
        phase=next(p for p in r['work']['phases'] if p['name']=='repair')
        assert h['sparse_calls']+h['dense_calls']<=phase['lp_calls']
    return {'all_pass':True,'attempts':h['attempts'],'successes':h['successes'],
            'scope':'Counters and shared spent allowance; not hard OS wall-time containment or exact general proof.'}
