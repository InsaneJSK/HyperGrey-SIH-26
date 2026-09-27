import copy
import unittest
from check_distance_stage import check,COUNTS,TIMES,FIELDS

def fixture():
    return {'lp_iterations':10,'pump_distance':{'dives':1},'distance_reopt':{'enabled':True,'compatible':1,'verified':1},'feasibility':{'enabled':False},
        'distance_stage':{'enabled':True,**dict.fromkeys(FIELDS,1),
            'reopt':{**dict.fromkeys(COUNTS+TIMES,0),'calls':1,'compatible':1,'primal':1,'verified':1,'factorizations':1},
            'samples':[{'node':0,'iterations':2,'eligible':True,'attempted':True,'verified':True,'accepted':True,'available_seconds':2.,'seconds':.01,'status':'optimal'}],
            'replay':None,'child_replay':None}}

class Checks(unittest.TestCase):
    def test_valid(self):self.assertTrue(check(fixture())['all_pass'])
    def test_invalid(self):
        for k,v in [('eligible',0),('verified',2),('attempts',0),('child_offers',3),('child_verified',2),('considered',True)]:
            with self.subTest(k=k):
                r=fixture();r['distance_stage'][k]=v
                with self.assertRaises(AssertionError):check(r)
    def test_bad_reopt(self):
        for k,v in [('calls',3),('dual',1),('factorizations',0),('pricing_seconds',float('nan'))]:
            r=fixture();r['distance_stage']['reopt'][k]=v
            with self.assertRaises(AssertionError):check(r)
    def test_samples(self):
        for k,v in [('eligible',False),('available_seconds',2.1),('seconds',float('nan')),('status','infeasible'),('iterations',True)]:
            r=fixture();r['distance_stage']['samples'][0][k]=v
            with self.assertRaises(AssertionError):check(r)
    def test_disabled(self):
        r=fixture();s=r['distance_stage'];s['enabled']=False
        with self.assertRaises(AssertionError):check(r)
        for k in FIELDS:s[k]=0
        for k in COUNTS+TIMES:s['reopt'][k]=0
        s['samples']=[];self.assertTrue(check(r)['all_pass'])
    def test_capture(self):
        r=fixture();r['feasibility']['enabled']=True
        f={'captured':True,'cost':[1],'lower':[0],'upper':[1],'rows':[],'row_lower':[],'row_upper':[],
            'basis_mapping':[[[0,1]]],'basis_rows':[[[0,1]]],'basis_equality':[0],'input_basis_columns':[1],
            'basis_structural_columns':1,'basis_reduced_upper_bounds':False}
        r['distance_stage']['replay']=f;r['distance_stage']['child_replay']=copy.deepcopy(f)
        self.assertTrue(check(r)['child_replay_captured'])
        r['distance_stage']['child_replay']['input_basis_columns']=[99]
        with self.assertRaises(AssertionError):check(r)

if __name__=='__main__':unittest.main()
