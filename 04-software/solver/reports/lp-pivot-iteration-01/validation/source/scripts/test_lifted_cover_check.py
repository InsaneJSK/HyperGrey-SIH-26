import copy
import unittest
from check_lifted_covers import verify_rows

class CoverCheckerTest(unittest.TestCase):
    def setUp(self):
        self.rows=[[(0,2.),(1,2.),(2,3.)]]
        self.cut={'source_row':0,'side':0,'rhs':1,'assignments':5,'row':[[0,1],[2,1]]}
    def verify(self,cut,**kwargs):
        return verify_rows(kwargs.get('rows',self.rows),kwargs.get('lows',[-float('inf')]),kwargs.get('ups',[4.]),
                           [True]*3,[0.]*3,[1.]*3,[cut])
    def test_valid(self):self.assertTrue(self.verify(self.cut)['all_pass'])
    def test_invalid(self):
        cut=copy.deepcopy(self.cut);cut['rhs']=0
        with self.assertRaises(AssertionError):self.verify(cut)
    def test_counts(self):
        cut=copy.deepcopy(self.cut);cut['assignments']=4
        with self.assertRaises(AssertionError):self.verify(cut)
    def test_extra_column(self):
        cut=copy.deepcopy(self.cut);cut['row'].append([10,1])
        with self.assertRaises(AssertionError):self.verify(cut)
    def test_fractional_coefficient(self):
        cut=copy.deepcopy(self.cut);cut['row'][0][1]=1.00000001
        with self.assertRaises(AssertionError):self.verify(cut)
    def test_complement_and_lower_side(self):
        cut={'source_row':0,'side':1,'rhs':0,'assignments':5,'row':[[0,-1],[2,1]]}
        self.assertTrue(self.verify(cut,rows=[[(0,2.),(1,-2.),(2,-3.)]],lows=[-2.],ups=[float('inf')])['all_pass'])

if __name__=='__main__':unittest.main()
