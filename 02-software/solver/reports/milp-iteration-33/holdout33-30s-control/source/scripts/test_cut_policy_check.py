import copy
import math
import unittest
from unittest.mock import patch
from check_cut_policy import check,decision
from check_cut_incumbents import check as incumbent_check

def example():
    a=dict(node=0,restart=0,round=1,root_iterations=300,iterations=300,before=10.,after=10.,offset=0.,decision='minimum_rounds')
    b={**a,'round':2,'decision':'diminishing_return'}
    return {'cut_policy':{'enabled':True,'capture_enabled':True,'stops':1,'rounds':[a,b]},'cut_restarts':0,
            'cut_rollbacks':0,'status':'time_limit','primal':[1.],'lp_iterations':900,
            'work':{'root_cut_rounds':5,'enabled':True,'phases':[{'name':'cut_lp','lp_calls':2,'iterations':600}]}}

class CutPolicyTests(unittest.TestCase):
    def test_good(self):self.assertTrue(check(example())['all_pass'])
    def bad(self,fn):
        r=example();fn(r)
        with self.assertRaises(AssertionError):check(r)
    def test_wrong_reason(self):self.bad(lambda r:r['cut_policy']['rounds'][1].update(decision='productive_round'))
    def test_wrong_count(self):self.bad(lambda r:r['cut_policy'].update(stops=0))
    def test_after_stop(self):self.bad(lambda r:r['cut_policy']['rounds'].append({**r['cut_policy']['rounds'][-1],'round':3}))
    def test_gap_in_rounds(self):self.bad(lambda r:r['cut_policy']['rounds'][1].update(round=3))
    def test_wrong_work(self):self.bad(lambda r:r.update(lp_iterations=100))
    def test_wrong_lp_calls(self):self.bad(lambda r:r['work']['phases'][0].update(lp_calls=1))
    def test_disabled_capture(self):self.bad(lambda r:r['cut_policy'].update(capture_enabled=False))
    def test_changed_root(self):self.bad(lambda r:r['cut_policy']['rounds'][1].update(node=1))
    def test_wrong_continuity(self):self.bad(lambda r:r['cut_policy']['rounds'][1].update(before=11.))
    def test_boundaries(self):
        e={**example()['cut_policy']['rounds'][1],'root_iterations':256,'iterations':256,'before':0.,'after':.001}
        self.assertEqual(decision(e),'diminishing_return');e['after']=math.nextafter(.001,math.inf)
        self.assertEqual(decision(e),'productive_round')
    def test_missing_invalid_and_cheap(self):
        e=example()['cut_policy']['rounds'][1]
        self.assertEqual(decision({**e,'root_iterations':0}),'missing_root_work')
        self.assertEqual(decision({**e,'iterations':255}),'cheap_round')
        self.assertEqual(decision({**e,'before':None}),'invalid_metric')
        self.assertEqual(decision({**e,'before':1.79e308,'after':-1.79e308}),'invalid_metric')

class GuardedPolicyTests(unittest.TestCase):
    def guarded(self,known=False):
        r=example();r['cut_policy'].update(version=2,require_incumbent=True)
        for e in r['cut_policy']['rounds']:e.update(incumbent_objective=11. if known else None)
        if not known:
            r['cut_policy']['stops']=0
            for e in r['cut_policy']['rounds']:e['decision']='no_incumbent'
        return r
    def test_protect_unknown(self):self.assertTrue(check(self.guarded())['all_pass'])
    def test_allow_known(self):self.assertTrue(check(self.guarded(True))['all_pass'])
    def test_stop_without_point(self):
        r=self.guarded();r['cut_policy']['rounds'][-1]['decision']='diminishing_return';r['cut_policy']['stops']=1
        with self.assertRaises(AssertionError):check(r)
    def test_missing_field(self):
        r=self.guarded();del r['cut_policy']['rounds'][0]['incumbent_objective']
        with self.assertRaises(AssertionError):check(r)
    def test_nonfinite(self):
        r=self.guarded(True);r['cut_policy']['rounds'][0]['incumbent_objective']=math.inf
        with self.assertRaises(AssertionError):check(r)
    def test_root_context_changes(self):
        r=self.guarded(True);r['cut_policy']['rounds'][-1]['incumbent_objective']=12.
        with self.assertRaises(AssertionError):check(r)
    def test_restart_source(self):
        r=self.guarded(True);r.update(cut_restarts=1,cut_restart_objective=12.)
        for e in r['cut_policy']['rounds']:e['restart']=1
        with self.assertRaises(AssertionError):check(r)
    def test_requires_adaptive(self):
        r=self.guarded();r['cut_policy']['enabled']=False
        with self.assertRaises(AssertionError):check(r)
    def test_cap_precedes_protection(self):
        r=self.guarded();r['work']['root_cut_rounds']=2;r['cut_policy']['rounds'][-1]['decision']='round_cap'
        self.assertTrue(check(r)['all_pass'])

class CutIncumbentTests(unittest.TestCase):
    def sample(self):
        r=GuardedPolicyTests().guarded(True);r.update(cut_restarts=1,cut_restart_objective=11.,cut_restart_primal=[1.],columns=1)
        for e in r['cut_policy']['rounds']:e['restart']=1
        return r
    def ref(self):return dict(candidate_checked=True,columns=1,candidate_objective=11.,candidate_max_violation=0.,candidate_integer_violation=0.,version='test')
    def test_source_checked_once(self):
        with patch('check_cut_incumbents.reference',return_value=self.ref()) as ref:
            self.assertEqual(incumbent_check(None,self.sample())['points_checked'],1);self.assertEqual(ref.call_count,1)
    def test_missing_source_rejected(self):
        r=self.sample();r['cut_restart_primal']=[]
        with self.assertRaises(AssertionError):incumbent_check(None,r)
    def test_infeasible_source_rejected(self):
        with patch('check_cut_incumbents.reference',return_value={**self.ref(),'candidate_max_violation':.01}):
            with self.assertRaises(AssertionError):incumbent_check(None,self.sample())
    def test_false_objective_rejected(self):
        with patch('check_cut_incumbents.reference',return_value={**self.ref(),'candidate_objective':10.}):
            with self.assertRaises(AssertionError):incumbent_check(None,self.sample())
    def test_unchecked_source_rejected(self):
        with patch('check_cut_incumbents.reference',return_value={**self.ref(),'candidate_checked':False}):
            with self.assertRaises(AssertionError):incumbent_check(None,self.sample())
    def test_partial_binary_source(self):
        r=self.sample();r['cut_restarts']=0;r['binary_proof']={'feasible':True,'completed':False,'primal':[1.]}
        for e in r['cut_policy']['rounds']:e['restart']=0
        with patch('check_cut_incumbents.reference',return_value=self.ref()):
            self.assertEqual(incumbent_check(None,r)['checks'][0]['source'],'partial_binary_witness')

if __name__=='__main__':unittest.main()
