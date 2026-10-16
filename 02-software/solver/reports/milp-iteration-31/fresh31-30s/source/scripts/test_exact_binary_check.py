import copy
import unittest
from exact_binary_check import parse_mps,reduce_model,check,range_join,number

TEXT='''NAME CHECK
ROWS
 N OBJ
 G R
COLUMNS
 X OBJ 1 R 1
 Y OBJ 2 R 1
RHS
 B R 1
BOUNDS
 BV B X
 BV B Y
ENDATA
'''

class ExactCheckerTests(unittest.TestCase):
    def marker_text(self):
        return TEXT.replace('COLUMNS\n',"COLUMNS\n M0 'MARKER' 'INTORG'\n").replace('RHS\n'," M1 'MARKER' 'INTEND'\nRHS\n").replace('BOUNDS\n BV B X\n BV B Y\n','')
    def test_marker_default_literal_proof(self):
        p=parse_mps(self.marker_text())
        self.assertEqual(p['upper'],[1,1])
        self.assertTrue(check(p,self.ours)['all_checks_pass'])
    def test_marker_bound_is_column_local(self):
        p=parse_mps(self.marker_text().replace('ENDATA','BOUNDS\n UP B Y 4\nENDATA'))
        self.assertEqual(p['upper'],[1,4])
    def test_marker_explicit_lower_keeps_unbounded_upper(self):
        p=parse_mps(self.marker_text().replace('ENDATA','BOUNDS\n LO B X 0\nENDATA'))
        self.assertEqual(p['upper'],[None,1])
    def setUp(self):
        self.p=parse_mps(TEXT)
        self.ours={'binary_proof_enabled':True,'binary_proof_attempts':1,'nodes':1,'lp_iterations':0,
                   'status':'optimal','objective':1,'best_bound':1,'gap':0,'primal':[1,0],
                   'binary_proof':{'version':1,'arithmetic':'checked_int64','eligible':True,'verified':True,'completed':True,
                                   'feasible':True,'status':'optimal','binary_indices':[0,1],'left_states':2,'right_states':2,
                                   'query_nodes':3,'work':10,'work_limit':100,'primal':[1,0],'objective_minimization':1}}
    def test_valid_range_proof(self):self.assertTrue(check(self.p,self.ours)['all_checks_pass'])
    def test_literal_not_rounded(self):
        for token in ('1.000000000000000000000000001','.5','1e-3'):
            with self.assertRaises(ValueError):number(token)
        self.assertEqual(number('100D-2'),1)
    def test_false_infeasibility(self):
        self.ours.update(status='infeasible',objective=None,primal=[])
        self.ours['binary_proof'].update(feasible=False,status='infeasible',primal=[])
        with self.assertRaises(AssertionError):check(self.p,self.ours)
    def test_invalid_or_fractional_witness(self):
        for x in ([0,0],[.999999999,0],[True,0],[1,1]):
            self.ours['primal']=x;self.ours['binary_proof']['primal']=x
            with self.assertRaises(AssertionError):check(self.p,self.ours)
    def test_partial_or_tampered_proof(self):
        for key,value in [('completed',False),('verified',False),('left_states',1),('right_states',1),('objective_minimization',2),('work_limit',1),('binary_indices',[1,0])]:
            saved=copy.deepcopy(self.ours);self.ours['binary_proof'][key]=value
            with self.assertRaises(AssertionError):check(self.p,self.ours)
            self.ours=saved
    def test_false_optimum_rejected(self):
        self.ours.update(objective=2,best_bound=2,primal=[0,1]);self.ours['binary_proof'].update(primal=[0,1],objective_minimization=2)
        with self.assertRaises(AssertionError):check(self.p,self.ours)
    def test_exact_infeasibility(self):
        p=parse_mps(TEXT.replace('B R 1','B R 3'));self.ours.update(status='infeasible',objective=None,primal=[])
        self.ours['binary_proof'].update(status='infeasible',feasible=False,primal=[])
        self.assertTrue(check(p,self.ours)['all_checks_pass'])
    def test_maximum(self):
        p=parse_mps(TEXT.replace('NAME CHECK','NAME CHECK\nOBJSENSE\n MAX').replace(' G R',' L R'))
        self.ours.update(objective=2,best_bound=2,primal=[0,1]);self.ours['binary_proof'].update(objective_minimization=-2,primal=[0,1])
        self.assertTrue(check(p,self.ours)['all_checks_pass'])
    def test_hash_join_contradiction(self):
        text=TEXT.replace(' G R',' E R').replace(' X OBJ 1',' S OBJ 1').replace(' Y OBJ 2',' Y OBJ 0').replace(' BV B X',' UP B S 10')
        p=parse_mps(text);self.ours['binary_proof'].update(binary_indices=[1],left_states=1,right_states=2)
        with self.assertRaises(AssertionError):check(p,self.ours)

if __name__=='__main__':unittest.main()
