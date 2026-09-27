import copy
import unittest
from check_milp_work import check,NAMES

class WorkTests(unittest.TestCase):
    def setUp(self):
        self.r={'lp_iterations':3,'total_seconds':2,'work':{'enabled':True,'seconds':1,
            'phases':[dict(name=n,seconds=1 if i==0 else 0,lp_calls=1 if i==0 else 0,iterations=3 if i==0 else 0) for i,n in enumerate(NAMES)]}}
    def reject(self):
        with self.assertRaises(AssertionError):check(self.r)
    def test_good(self):self.assertTrue(check(self.r)['all_pass'])
    def test_double_count(self):self.r['work']['phases'][1]['seconds']=1;self.reject()
    def test_missing_phase(self):self.r['work']['phases'].pop();self.reject()
    def test_missing_iterations(self):self.r['lp_iterations']=4;self.reject()
    def test_negative(self):self.r['work']['phases'][1]['seconds']=-1;self.reject()
    def test_disabled_not_empty(self):self.r['work']['enabled']=False;self.reject()
    def test_outside_total(self):self.r['total_seconds']=.1;self.reject()
    def test_nonfinite(self):self.r['work']['seconds']=float('nan');self.reject()
    def test_bad_counter(self):self.r['work']['phases'][1]['lp_calls']=True;self.reject()

if __name__=='__main__':unittest.main()
