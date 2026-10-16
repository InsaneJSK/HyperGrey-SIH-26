"""Small adversarial tests for the call-level MILP evidence checker."""
import copy
import unittest
from audit_local_milp import neighborhood_samples


class NeighborhoodDiagnostics(unittest.TestCase):
    def setUp(self):
        self.command=['--capture-neighborhood','--neighborhood','guided']
        self.sample={'nodes':3,'lp_failures':0,'stalls_before':0,'start_seconds':.1,
                     'seconds':1.,'budget':2.,'selection':'guided','free_variables':[0,2],
                     'objective_before':10.,'objective_after':9.,'improved':True,'improved_primal':[1.,2.,3.]}
        self.ours={'neighborhood':'guided','neighborhood_trace':[self.sample],
                   'neighborhood_calls':1,'neighborhood_nodes':3,'neighborhood_improvements':1,
                   'neighborhood_seconds':1.,'total_seconds':5.,'incumbent_trace':[[.2,9.]]}

    def check(self,sign=1):
        return neighborhood_samples(self.ours,self.command,[0,2],[-5.,0.,0.],[5.,5.,5.],sign)

    def test_valid_minimum(self):
        self.assertEqual(self.check(),[('neighborhood_0',[1.,2.,3.],False,9.)])

    def test_valid_maximum(self):
        self.sample['objective_before']=-10.;self.sample['objective_after']=-9.
        self.ours['incumbent_trace']=[[.2,-9.]]
        self.assertEqual(self.check(-1)[0][-1],-9.)

    def test_invalid_released_indices(self):
        for indices in ([0,0],[1],[True],[3],[-1]):
            with self.subTest(indices=indices):
                self.sample['free_variables']=indices
                with self.assertRaises(AssertionError):self.check()

    def test_tampered_aggregates(self):
        for field in ('neighborhood_calls','neighborhood_nodes','neighborhood_improvements','neighborhood_seconds'):
            with self.subTest(field=field):
                saved=self.ours[field];self.ours[field]+=1
                with self.assertRaises(AssertionError):self.check()
                self.ours[field]=saved

    def test_guided_cannot_claim_diversification(self):
        self.sample['selection']='diverse';self.sample['stalls_before']=4
        with self.assertRaises(AssertionError):self.check()

    def test_late_budget_only(self):
        self.command[-1]='diversified';self.ours['neighborhood']='diversified'
        self.sample.update(selection='expanded_diverse',stalls_before=4,budget=4.,nodes=128)
        self.ours['neighborhood_nodes']=128
        self.assertEqual(len(self.check()),1)
        self.sample['stalls_before']=3
        with self.assertRaises(AssertionError):self.check()

    def test_false_improvement(self):
        self.sample['objective_after']=11.;self.ours['incumbent_trace']=[[.2,11.]]
        with self.assertRaises(AssertionError):self.check()

    def test_missing_or_untraced_vector(self):
        self.sample['improved_primal']=[]
        with self.assertRaises(AssertionError):self.check()
        self.sample['improved_primal']=[1.,2.,3.];self.ours['incumbent_trace']=[]
        with self.assertRaises(AssertionError):self.check()

    def test_nonfinite_objective(self):
        self.sample['objective_after']=float('nan')
        with self.assertRaises(AssertionError):self.check()

    def test_invalid_budget_and_elapsed(self):
        for field,value in (('budget',0),('budget',2.1),('seconds',float('nan')),('start_seconds',-1)):
            with self.subTest(field=field,value=value):
                saved=self.sample[field];self.sample[field]=value
                with self.assertRaises(AssertionError):self.check()
                self.sample[field]=saved

    def test_pacing_and_early_call_rejected(self):
        self.command+=['--pace-neighborhood','--time-limit','180']
        second=copy.deepcopy(self.sample);second.update(start_seconds=3.7,objective_before=9.,objective_after=9.,improved=False,improved_primal=[])
        self.ours.update(neighborhood_paced=True,neighborhood_min_spacing_seconds=3.6,
                         neighborhood_trace=[self.sample,second],neighborhood_calls=2,neighborhood_nodes=6,neighborhood_seconds=2.)
        self.assertEqual(len(self.check()),1)
        second['start_seconds']=3.69
        with self.assertRaises(AssertionError):self.check()

    def reserved_example(self):
        self.command=['--capture-neighborhood','--neighborhood','reserved','--time-limit','180']
        calls=[]
        for i in range(4):
            s=copy.deepcopy(self.sample)
            s.update(start_seconds=.1*(i+1),seconds=.01,stalls_before=i,objective_after=10.,improved=False,
                     material_improved=False,strong=False,improved_primal=[],radius=0,center_primal=[])
            calls.append(s)
        strong=copy.deepcopy(self.sample)
        strong.update(start_seconds=1.,seconds=.5,stalls_before=4,budget=4.,selection='local_branching',
                      radius=4,strong=True,material_improved=True,center_primal=[1.,2.,0.],improved_primal=[0.,2.,0.])
        calls.append(strong)
        self.ours.update(neighborhood='reserved',neighborhood_trace=calls,neighborhood_calls=5,
                         neighborhood_nodes=15,neighborhood_seconds=.54,incumbent_trace=[[1.4,9.]])
        return strong

    def check_reserved(self):
        return neighborhood_samples(self.ours,self.command,[0,2],[0.,0.,0.],[1.,5.,1.],1)

    def test_reserved_center_and_gain(self):
        strong=self.reserved_example()
        self.assertEqual(len(self.check_reserved()),2)
        strong['material_improved']=False
        with self.assertRaises(AssertionError):self.check_reserved()

    def test_reserved_false_domain(self):
        strong=self.reserved_example();strong['free_variables']=[0]
        with self.assertRaises(AssertionError):self.check_reserved()

    def test_reserved_false_radius(self):
        strong=self.reserved_example();strong['radius']=8
        with self.assertRaises(AssertionError):self.check_reserved()

    def test_reserved_tiny_gain_not_progress(self):
        self.reserved_example();first=self.ours['neighborhood_trace'][0]
        first.update(objective_before=10.+1e-8,improved=True,improved_primal=[1.,2.,0.])
        self.ours['neighborhood_improvements']=2;self.ours['incumbent_trace'].insert(0,[.105,10.])
        self.assertEqual(len(self.check_reserved()),3)
        self.ours['neighborhood_trace'][1]['stalls_before']=0
        with self.assertRaises(AssertionError):self.check_reserved()


if __name__=='__main__':unittest.main()
