import copy
import unittest
from check_refinement_work import check,COUNTS
from check_milp_work import NAMES

class RefinementWorkTests(unittest.TestCase):
    def setUp(self):
        zero={**dict.fromkeys(COUNTS,0),'seconds':0.}
        self.r={'basis_refinement_enabled':True,'lp_iterations':3,'total_seconds':2,
            'work':{'enabled':True,'seconds':1.,'refinement_enabled':True,'refinement':copy.deepcopy(zero),
                'phases':[dict(name=n,seconds=1. if i==0 else 0.,lp_calls=1 if i==0 else 0,iterations=3 if i==0 else 0,refinement=copy.deepcopy(zero)) for i,n in enumerate(NAMES)]}}
        s={'rhs_calls':2,'primal_rhs':1,'dual_rhs':1,'scans':3,'entries':15,'attempts':1,'accepted':1,'seconds':.1}
        self.r['work']['refinement']=copy.deepcopy(s);self.r['work']['phases'][0]['refinement']=copy.deepcopy(s)
    def reject(self):
        with self.assertRaises(AssertionError):check(self.r)
    def test_valid(self):self.assertTrue(check(self.r)['all_pass'])
    def test_missing_total(self):self.r['work']['refinement']['entries']+=1;self.reject()
    def test_wrong_direction(self):self.r['work']['refinement']['dual_rhs']=0;self.reject()
    def test_accept_without_attempt(self):self.r['work']['refinement']['accepted']=2;self.reject()
    def test_bad_scan_count(self):self.r['work']['refinement']['scans']=9;self.reject()
    def test_outside_phase(self):self.r['work']['phases'][0]['refinement']['seconds']=2;self.reject()
    def test_disabled_nonzero(self):self.r['work']['refinement_enabled']=False;self.reject()
    def test_algorithm_off_nonzero(self):self.r['basis_refinement_enabled']=False;self.reject()
    def test_nonfinite(self):self.r['work']['refinement']['seconds']=float('nan');self.reject()
    def test_boolean_count(self):self.r['work']['refinement']['primal_rhs']=True;self.reject()
    def test_too_many_corrections(self):self.r['work']['refinement']['attempts']=5;self.reject()

if __name__=='__main__':unittest.main()
