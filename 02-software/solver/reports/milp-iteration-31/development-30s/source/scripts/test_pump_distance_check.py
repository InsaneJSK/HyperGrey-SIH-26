import unittest
from check_pump_distance import verify

class DistanceCheckTests(unittest.TestCase):
    def setUp(self):
        self.data={'integer':[True,False]}
        self.s={'node':0,'auxiliaries':1,'lp_calls':2,'verified_points':1,'warm_starts':1,
                'initial_distance':.1,'first_distance':.2,'last_distance':.2,'first_target_distance':.2,'last_target_distance':.2}
        self.r={'pump_distance':{'enabled':True,'dives':1,'lp_calls':2,'verified_points':1,'warm_starts':1,'samples':[self.s]},
                'pump_guidance':{'enabled':True,'dives':1,'samples':[]}}
    def reject(self):
        with self.assertRaises(AssertionError):verify(self.data,self.r)
    def test_valid(self):self.assertTrue(verify(self.data,self.r)['all_pass'])
    def test_disabled(self):self.r['pump_distance']['enabled']=False;self.reject()
    def test_prerequisite(self):self.r['pump_guidance']['enabled']=False;self.reject()
    def test_calls(self):self.r['pump_distance']['lp_calls']=129;self.reject()
    def test_totals(self):self.s['lp_calls']=1;self.reject()
    def test_nonfinite(self):self.s['initial_distance']=float('nan');self.reject()
    def test_missing_metric(self):self.s['first_distance']=None;self.reject()
    def test_auxiliary_cap(self):self.s['auxiliaries']=2;self.reject()
    def test_false_distance(self):self.s['first_distance']=.3;self.reject()
    def test_nearest_can_worsen(self):self.assertGreater(self.s['last_distance'],self.s['initial_distance']);self.test_valid()

if __name__=='__main__':unittest.main()
