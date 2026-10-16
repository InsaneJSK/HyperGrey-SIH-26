import copy
import unittest
from check_feasibility_trace import verify
from check_heuristic_repair import check

class FeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.data={'integer':[True,False],'rows':[{0:1,1:1}],'lower':[0],'upper':[2]}
        e={'kind':'pump_target','status':'new','node':1,'call':1,'step':0,'mode':0,'variable':0,'iterations':0,
           'fractional':1,'alternate':False,'accepted':False,'distance':.25,'violation':0.,'point':[.25,.5],'target':[0.,0.]}
        self.r={'feasibility':{'enabled':True,'events':1,'calls':1,'stored_values':4,'samples':[e]}}
    def reject(self):
        with self.assertRaises(AssertionError):verify(self.data,self.r)
    def test_valid(self):self.assertTrue(verify(self.data,self.r)['all_pass'])
    def test_distance(self):self.r['feasibility']['samples'][0]['distance']=.1;self.reject()
    def test_fraction_count(self):self.r['feasibility']['samples'][0]['fractional']=0;self.reject()
    def test_repetition(self):self.r['feasibility']['samples'][0]['status']='repeat';self.reject()
    def test_storage(self):self.r['feasibility']['stored_values']=3;self.reject()
    def test_disabled(self):self.r['feasibility']['enabled']=False;self.reject()
    def test_nonfinite(self):self.r['feasibility']['samples'][0]['point'][0]=float('nan');self.reject()
    def test_false_accept(self):self.r['feasibility']['samples'][0]['accepted']=True;self.reject()

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.r={'candidate_repair_seconds':.3,'work':{'enabled':True,'phases':[{'name':'repair','lp_calls':2}]},
            'heuristic_repair':{'enabled':True,'attempts':1,'successes':1,'duplicate_skips':0,'sparse_calls':1,'dense_calls':1,'seconds':.3,'shared_seconds':.3,'allowance':3.}}
    def reject(self):
        with self.assertRaises(AssertionError):check(self.r)
    def test_valid(self):self.assertTrue(check(self.r)['all_pass'])
    def test_false_success(self):self.r['heuristic_repair']['successes']=2;self.reject()
    def test_budget_accounting(self):self.r['heuristic_repair']['shared_seconds']=.2;self.reject()
    def test_missing_lp(self):self.r['work']['phases'][0]['lp_calls']=1;self.reject()
    def test_disabled(self):self.r['heuristic_repair']['enabled']=False;self.reject()
    def test_attempt_cap(self):self.r['heuristic_repair']['attempts']=17;self.reject()

if __name__=='__main__':unittest.main()
