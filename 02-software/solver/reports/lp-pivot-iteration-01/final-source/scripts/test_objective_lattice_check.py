"""Mutation tests for the independent checker; no solver code imported."""
import copy
from fractions import Fraction as F
import unittest
from check_objective_lattice import verify


class LatticeChecks(unittest.TestCase):
    def setUp(self):
        self.data={'cost':[F(0),F(0),F(1)],'offset':F(1,4),'sign':1,'integer':[True,True,False],
                   'rows':[{0:F(-5),1:F(10),2:F(1)}],'lower':[2.],'upper':[2.]}
        self.result={'objective_lattice':{'enabled':True,'eligible':True,'reason':'checked_parsed_model_lattice',
                      'offset_minimization':2.25,'step':5,'coefficients_minimization':[5,-10,0],
                      'substitutions':[{'column':2,'row':0}],'bound_calls':1,'bound_improvements':1,
                      'trace_truncated':False,'trace':[{'node':0,'before_minimization':3.,'after_minimization':7.249999999999999}]}}
    def rejects(self):
        with self.assertRaises(AssertionError):verify(self.data,self.result)
    def test_valid(self):self.assertTrue(verify(self.data,self.result)['all_checks_pass'])
    def test_wrong_step(self):self.result['objective_lattice']['step']=10;self.rejects()
    def test_wrong_offset(self):self.result['objective_lattice']['offset_minimization']=2.5;self.rejects()
    def test_wrong_coefficients(self):self.result['objective_lattice']['coefficients_minimization'][0]=-5;self.rejects()
    def test_wrong_sense(self):self.data['sign']=-1;self.rejects()
    def test_inequality(self):self.data['upper'][0]=2.000000001;self.rejects()
    def test_continuous_remainder(self):self.data['integer'][0]=False;self.rejects()
    def test_skipped_grid(self):self.result['objective_lattice']['trace'][0]['after_minimization']=7.250000000000001;self.rejects()
    def test_repeated_definition(self):self.result['objective_lattice']['substitutions']*=2;self.rejects()
    def test_missing_definition(self):self.result['objective_lattice']['substitutions']=[];self.rejects()
    def test_missing_events(self):self.result['objective_lattice']['bound_improvements']=2;self.result['objective_lattice']['bound_calls']=2;self.rejects()
    def test_honest_truncation(self):
        self.result['objective_lattice'].update(bound_calls=2,bound_improvements=2,trace_truncated=True)
        self.assertTrue(verify(self.data,self.result)['trace_truncated'])
    def test_disabled(self):
        self.result['objective_lattice'].update(enabled=False,eligible=False,substitutions=[],trace=[],bound_calls=0,bound_improvements=0)
        self.assertFalse(verify(self.data,self.result)['eligible'])


if __name__=='__main__':unittest.main()
