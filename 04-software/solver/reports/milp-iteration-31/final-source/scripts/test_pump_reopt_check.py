import copy
import unittest
from check_pump_reopt import check,COUNTS,TIMES

def fixture():
    return {'pump_projections':2,'lp_iterations':5,'feasibility':{'enabled':False},
            'pump_reopt':{'enabled':True,**dict.fromkeys(COUNTS,0),**dict.fromkeys(TIMES,0),'calls':2,'compatible':1,'primal':1,'verified':1,'factorizations':2,'replay':None}}

class Checks(unittest.TestCase):
    def test_valid(self):self.assertTrue(check(fixture())['all_pass'])
    def test_invalid(self):
        for key,value in [('calls',5),('compatible',0),('verified',2),('dual',1),('factorizations',0),('phase_one_iterations',6),('pricing_seconds',float('nan')),('primal',True)]:
            with self.subTest(key=key):
                r=fixture();r['pump_reopt'][key]=value
                with self.assertRaises(AssertionError):check(r)
    def test_disabled(self):
        r=fixture();r['pump_reopt']['enabled']=False
        with self.assertRaises(AssertionError):check(r)
        for k in COUNTS+TIMES:r['pump_reopt'][k]=0
        self.assertTrue(check(r)['all_pass'])
    def test_replay(self):
        r=fixture();r['feasibility']['enabled']=True
        r['pump_reopt']['replay']={'captured':True,'cost':[1],'lower':[0],'upper':[1],'rows':[],'row_lower':[],'row_upper':[],
            'basis_mapping':[[[0,1]]],'basis_rows':[[[0,1]]],'basis_equality':[0],'input_basis_columns':[1],'basis_structural_columns':1,'basis_reduced_upper_bounds':False}
        self.assertTrue(check(r)['replay_captured'])
        for field,value in [('basis_rows',[]),('input_basis_columns',[20]),('basis_reduced_upper_bounds',True),('basis_mapping',[[[0,float('nan')]]])]:
            q=copy.deepcopy(r);q['pump_reopt']['replay'][field]=value
            with self.assertRaises(AssertionError):check(q)

if __name__=='__main__':unittest.main()
