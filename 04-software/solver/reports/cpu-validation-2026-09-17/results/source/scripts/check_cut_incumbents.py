"""Check saved source incumbents behind cut decisions against original MPS."""
import math
from milp_robustness import reference
from check_cut_policy import check as policy_check

def check(model,r):
    if not __debug__:raise RuntimeError('Assertions required')
    policy_check(r);p=r['cut_policy'];seen=set();checks=[]
    if p.get('version',1)<2:return {'all_pass':True,'points_checked':0,'checks':[],'scope':__doc__}
    for e in p['rounds']:
        if e['incumbent_objective'] is None:continue
        key=(e['restart'],e['node'])
        if key in seen:continue
        seen.add(key)
        if e['restart']:
            x=r['cut_restart_primal'];source='restart'
            assert e['incumbent_objective']==r['cut_restart_objective']
        else:
            proof=r['binary_proof'];assert proof['feasible'] and not proof['completed']
            x=proof['primal'];source='partial_binary_witness'
        # Existing restart capture is capped at 10000 columns. An absent source
        # is explicitly unverified, never silently accepted by this audit.
        assert len(x)==r['columns'] and len(x)>0,'Cut-incumbent vector unavailable for independent check'
        ref=reference(model,{'primal':x},0)
        assert ref.get('candidate_checked') is True and ref['columns']==r['columns']
        assert ref['candidate_max_violation']<=1e-7 and ref['candidate_integer_violation']<=1e-7
        value=ref['candidate_objective'];assert math.isfinite(value)
        assert abs(value-e['incumbent_objective'])<=1e-7*(1+abs(value))
        checks.append({'restart':e['restart'],'node':e['node'],'source':source,'objective':e['incumbent_objective'],
            'reference_objective':value,'row_bound_violation':ref['candidate_max_violation'],
            'integer_violation':ref['candidate_integer_violation'],'reference_version':ref['version']})
    return {'all_pass':True,'points_checked':len(checks),'checks':checks,'scope':__doc__}
