import copy
import unittest
from check_milp_frontier import check


def event(op,i,proof,rank,queued,deferred=0):
    return dict(op=op,id=i,proof=proof,rank=rank,queued=queued,deferred=deferred,depth=0)


class FrontierTests(unittest.TestCase):
    def setUp(self):
        trace=[event('push',1,10,0,1),event('push',2,1,.5,2),event('checkpoint',0,1,5,2),
               event('pop',1,10,0,1),event('defer',1,10,0,1,1),event('checkpoint',0,1,5,1,1),
               event('reset',0,1,5,1,1),event('push',3,1,'-inf',1),event('checkpoint',0,1,5,1)]
        self.result={'best_bound':1,'frontier':dict(raw_lp_priority=True,capture_enabled=True,event_count=len(trace),
                                                  trace_truncated=False,trace=trace,priority_minimum_mismatches=1)}
    def rejects(self):
        with self.assertRaises(AssertionError):check(self.result)
    def test_good(self):self.assertTrue(check(self.result)['all_pass'])
    def test_search_top_is_not_minimum(self):self.result['frontier']['trace'][2]['proof']=5;self.rejects()
    def test_wrong_pop(self):self.result['frontier']['trace'][3].update(id=2,proof=1,rank=.5);self.rejects()
    def test_missing_deferred(self):self.result['frontier']['trace'][4]['deferred']=0;self.rejects()
    def test_restart_overclaims(self):self.result['frontier']['trace'][6]['proof']=5;self.rejects()
    def test_restart_inheritance(self):self.result['frontier']['trace'][7]['proof']=5;self.rejects()
    def test_clear_changed_policy(self):self.result['frontier']['raw_lp_priority']=False;self.rejects()
    def test_bound_mismatch(self):self.result['best_bound']=5;self.rejects()
    def test_max_sign(self):self.result['best_bound']=-1;self.assertTrue(check(self.result,True)['all_pass'])
    def test_missing_events(self):self.result['frontier']['event_count']+=1;self.rejects()
    def test_honest_prefix(self):
        self.result['frontier'].update(trace=self.result['frontier']['trace'][:4],trace_truncated=True)
        self.assertTrue(check(self.result)['trace_truncated'])
    def test_nan_key(self):self.result['frontier']['trace'][0]['proof']=float('nan');self.rejects()
    def test_duplicate(self):self.result['frontier']['trace'][1]['id']=1;self.rejects()
    def test_incumbent_increases(self):self.result['frontier']['trace'][-1]['rank']=6;self.rejects()


if __name__=='__main__':unittest.main()
