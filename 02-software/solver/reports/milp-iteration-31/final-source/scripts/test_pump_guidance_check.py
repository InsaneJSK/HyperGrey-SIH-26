import unittest
from check_pump_guidance import verify


class PumpGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.data={'integer':[True,False],'rows':[{0:1,1:1}],'lower':[0.],'upper':[2.]}
        s={'node':1,'candidates':2,'rejected':0,'improvements':1,'steps':3,'selected':True,'used':True,
           'initial_distance':.4,'best_distance':.1,'initial':[.4,.5],'point':[.1,.5]}
        self.r={'pump_guidance':{'enabled':True,'calls':1,'candidates':2,'rejected':0,'improvements':1,
                                'dives':1,'steps':3,'stored_values':4,'samples':[s]}}
    def reject(self):
        with self.assertRaises(AssertionError):verify(self.data,self.r)
    def test_valid(self):self.assertTrue(verify(self.data,self.r)['all_pass'])
    def test_disabled(self):self.r['pump_guidance']['enabled']=False;self.reject()
    def test_metric(self):self.r['pump_guidance']['samples'][0]['best_distance']=.2;self.reject()
    def test_false_progress(self):self.r['pump_guidance']['samples'][0]['best_distance']=.5;self.reject()
    def test_row(self):self.r['pump_guidance']['samples'][0]['point'][1]=3.;self.reject()
    def test_nonfinite(self):self.r['pump_guidance']['samples'][0]['point'][1]=float('nan');self.reject()
    def test_storage(self):self.r['pump_guidance']['stored_values']=3;self.reject()
    def test_missing_source(self):self.r['pump_guidance']['samples'][0]['initial']=[];self.reject()
    def test_counter(self):self.r['pump_guidance']['steps']=2;self.reject()
    def test_step_cap(self):self.r['pump_guidance']['steps']=65;self.r['pump_guidance']['samples'][0]['steps']=65;self.reject()
    def test_unselected_use(self):self.r['pump_guidance']['samples'][0]['selected']=False;self.reject()
    def test_vectorless(self):
        s=self.r['pump_guidance']['samples'][0];s['point']=s['initial']=[];self.r['pump_guidance']['stored_values']=0
        self.assertEqual(verify(self.data,self.r)['seed_points_checked'],0)


if __name__=='__main__':unittest.main()
