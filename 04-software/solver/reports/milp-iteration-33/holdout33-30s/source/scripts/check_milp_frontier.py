"""Independent event replay of queue selection and global bound bookkeeping.

This verifies saved operations, not the underlying LP bounds, valid branching
domains, incumbent feasibility, or the completeness of a MILP proof trace.
"""
import math


def number(value):
    if value in ('inf','-inf'):return float(value)
    assert isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
    return float(value)


def check(result,maximize=False):
    if not __debug__:raise RuntimeError('Frontier audit requires assertions')
    f=result['frontier'];trace=f['trace'];assert f['event_count']>=len(trace)
    assert f['trace_truncated']==(f['event_count']>len(trace))
    if not f['capture_enabled']:
        assert not trace and not f['event_count']
        return {'all_pass':True,'captured':False,'events_checked':0}
    queued={};deferred={};popped={};seen=set();pending=None;previous_inc=math.inf
    mismatches=0;resets=0;checkpoints=0
    minimum=lambda values:min((v[0] for v in values.values()),default=math.inf)
    for e in trace:
        op=e['op'];i=e['id'];depth=e['depth'];proof=number(e['proof']);rank=number(e['rank'])
        assert type(i) is int and i>=0 and type(depth) is int and depth>=0
        if pending is not None:assert op=='push' and proof==pending and rank==-math.inf
        if op=='push':
            assert i not in queued and i not in deferred
            if i in seen:
                assert i in popped and proof>=popped[i][0] and rank>=popped[i][1]
            queued[i]=(proof,rank,depth);seen.add(i);pending=None
        elif op=='pop':
            assert queued
            best=min(queued,key=lambda j:(queued[j][1] if f['raw_lp_priority'] else queued[j][0],-queued[j][2],j))
            assert i==best and queued[i]==(proof,rank,depth),'Wrong priority pop'
            mismatches+=proof!=minimum(queued)
            popped[i]=queued.pop(i)
        elif op=='defer':
            assert i in popped and i not in queued and i not in deferred
            assert proof>=popped[i][0] and rank>=popped[i][1]
            deferred[i]=(proof,rank,depth)
        elif op in ('checkpoint','reset'):
            assert rank<=previous_inc;previous_inc=rank
            assert proof==min(rank,minimum(queued),minimum(deferred)),'Wrong global proof minimum'
            checkpoints+=op=='checkpoint'
        else:raise AssertionError('Unknown frontier operation')
        assert e['queued']==len(queued) and e['deferred']==len(deferred),'Queue/deferred count mismatch'
        if op=='reset':queued.clear();deferred.clear();pending=proof;resets+=1
    if not f['trace_truncated']:
        assert pending is None and mismatches==f['priority_minimum_mismatches']
        if not result.get('binary_proof',{}).get('verified'):
            assert trace and trace[-1]['op']=='checkpoint'
            if result.get('best_bound') is not None:
                assert number(trace[-1]['proof'])==(-1 if maximize else 1)*result['best_bound'],'Final bound differs from frontier minimum'
    return {'all_pass':True,'captured':True,'events_checked':len(trace),'trace_truncated':f['trace_truncated'],
            'checkpoints_checked':checkpoints,'resets_checked':resets,'priority_minimum_mismatches_checked':mismatches,
            'scope':__doc__}
