import copy
import unittest
from check_distance_reopt import check,COUNTS,TIMES,SEED

def fixture():
    return {'lp_iterations':10,'pump_distance':{'enabled':True,'lp_calls':2,'dives':1},
            'pump_guidance':{'enabled':True,'improvements':1},'pump_reopt':{'enabled':True},'feasibility':{'enabled':False},
            'distance_reopt':{'enabled':True,**dict.fromkeys(COUNTS+TIMES+SEED,0),'calls':2,'compatible':2,'dual':2,'verified':2,'factorizations':2,
                'seed_updates':1,'seed_offers':1,'seed_compatible':1,'seed_verified':1,'replay':None}}

class Checks(unittest.TestCase):
    def test_valid(self):self.assertTrue(check(fixture())['all_pass'])
    def test_invalid_counts(self):
        for k,v in [('seed_updates',2),('seed_offers',3),('seed_compatible',2),('seed_verified',2),('calls',5),('verified',3),('compatible',0),('primal',True),('pricing_seconds',float('nan'))]:
            with self.subTest(k=k):
                r=fixture();r['distance_reopt'][k]=v
                with self.assertRaises(AssertionError):check(r)
    def test_disabled(self):
        r=fixture();r['distance_reopt']['enabled']=False
        with self.assertRaises(AssertionError):check(r)
        for k in COUNTS+TIMES+SEED:r['distance_reopt'][k]=0
        self.assertTrue(check(r)['all_pass'])
    def test_replay(self):
        r=fixture();r['feasibility']['enabled']=True
        f={'captured':True,'cost':[1],'lower':[0],'upper':[1],'rows':[],'row_lower':[],'row_upper':[],
           'basis_mapping':[[[0,1]],[[1,1]]],'basis_rows':[[[0,1]]],'basis_equality':[0],
           'input_basis_columns':[2],'basis_structural_columns':2,'basis_reduced_upper_bounds':False}
        r['distance_reopt']['replay']=f;self.assertTrue(check(r)['replay_captured'])
        for k,v in [('input_basis_columns',[99]),('basis_equality',[]),('basis_reduced_upper_bounds',True),('basis_rows',[[[2,1]]])]:
            bad=copy.deepcopy(r);bad['distance_reopt']['replay'][k]=v
            with self.assertRaises(AssertionError):check(bad)

if __name__=='__main__':unittest.main()
