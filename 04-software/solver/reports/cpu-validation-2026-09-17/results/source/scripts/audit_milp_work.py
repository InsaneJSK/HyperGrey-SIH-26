"""Recheck saved outcomes and per-experiment source identities without new timings."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import statistics
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import verify
from check_milp_work import check

def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);summaries=[];comparisons=[]
    supplemental={};supp_meta=None;supp_used=[]
    if args.supplemental:
        supp_dir=args.supplemental.resolve();supp_meta=json.loads((supp_dir/'SUMMARY.json').read_text())
        assert supp_meta['all_pass'] and supp_meta['own_solver_reruns']==0 and supp_meta['reference_solve_limit_seconds']==5
        assert supp_meta['helper_sha256']==sha(ROOT/'scripts/milp_robustness.py')
        assert supp_meta['runner_sha256']==sha(ROOT/'scripts/resolve_work_references.py')
        assert supp_meta['results_sha256']==sha(supp_dir/'results.json')
        supp_rows=json.loads((supp_dir/'results.json').read_text());supplemental={r['key']:r for r in supp_rows}
        assert len(supplemental)==len(supp_rows)==supp_meta['records'] and all(r['all_pass'] for r in supp_rows)
    equivalent=json.loads((ROOT/'reports/milp-iteration-14/reader-equivalence/SUMMARY.json').read_text());assert equivalent['all_pass']
    assert equivalent['new_reader_sha256']==sha(ROOT/'scripts/check_objective_lattice.py')
    for folder in args.runs:
        folder=folder.resolve();dest=out/folder.name;dest.mkdir();meta=json.loads((folder/'metadata.json').read_text());plan=meta['plan']
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        for rel,digest in meta['source_sha256'].items():assert sha(folder/'source'/rel)==digest,rel
        original_reader=meta['source_sha256']['scripts/check_objective_lattice.py']
        assert original_reader in (equivalent['old_reader_sha256'],equivalent['new_reader_sha256'])
        rows=json.loads((folder/'results.json').read_text());expected=[]
        for index,name in enumerate(plan['models']):
            for repeat in range(plan.get('repeats',1)):
                order=list(plan['profiles']);shift=(index+repeat)%len(order)
                expected += [(name,p,repeat) for p in order[shift:]+order[:shift]]
        assert [(r['name'],r['profile'],r['repeat']) for r in rows]==expected
        groups=defaultdict(lambda:defaultdict(list));points=proofs=cuts=lattice=truncated=pending_points=rechecked_points=0
        for r in rows:
            key=r['key'];model=ROOT/r['model'];assert sha(model)==r['model_sha256']
            op=folder/(key+'.ours.json');rp=folder/(key+'.reference.json')
            assert sha(op)==r['ours_sha256'] and sha(rp)==r['reference_sha256']
            ours=json.loads(op.read_text());ref=json.loads(rp.read_text())
            assert r['command']==[meta['binary'],str(model),'--milp','--json',*plan.get('common',[]),*plan['profiles'][r['profile']],
                                  '--time-limit',str(plan['limit']),'--node-limit',str(plan.get('nodes',250000)),'--gap',str(plan.get('gap',1e-6))]
            for k in ('status','objective','best_bound','gap','nodes','lp_iterations','total_seconds'):assert r[k]==ours.get(k)
            category,errors,checks=verify(model,ours,ref,dest,key,plan.get('gap',1e-6));w=check(ours)
            assert not errors and category==r['category'] and not r['validation_errors']
            assert w==json.loads((folder/(key+'.work-check.json')).read_text());save(dest/(key+'.work-check.json'),w)
            for kind,value in checks.items():assert value==json.loads((folder/(key+f'.{kind}-check.json')).read_text())
            point_checked=bool(ours.get('primal')) and ref.get('candidate_checked') is True
            pending_points+=bool(ours.get('primal')) and not point_checked
            if supp_meta and sha(folder/'results.json')==supp_meta['original_results_sha256'] and key in supplemental:
                sr=supplemental[key]
                assert not point_checked and category=='incumbent_reference_pending'
                for field in ('model','model_sha256','ours_sha256'):assert sr[field]==r[field]
                assert sr['original_reference_sha256']==r['reference_sha256'] and sr['external_watchdog_seconds']==150
                assert sr['command'][1:]==['-X','utf8',str(ROOT/'scripts/milp_robustness.py'),'--reference',str(model),
                                           '--candidate',str(op),'--reference-limit','5']
                sp=supp_dir/(key+'.reference.json');assert sha(sp)==sr['reference_sha256'];fresh=json.loads(sp.read_text())
                sc,se,sa=verify(model,ours,fresh,dest,key+'.supplemental',plan.get('gap',1e-6))
                assert not se and not sr['validation_errors'] and sc==sr['category']=='feasible_limit' and fresh.get('candidate_checked') is True
                for kind,value in sa.items():assert value==json.loads((supp_dir/(key+f'.{kind}-check.json')).read_text())
                point_checked=True;rechecked_points+=1;supp_used.append(key)
            points+=point_checked;proofs+=bool(checks.get('exact',{}).get('all_checks_pass'))
            cuts+=checks.get('cuts',{}).get('cuts_checked',0);lattice+=checks.get('lattice',{}).get('events_checked',0)
            truncated+=checks.get('lattice',{}).get('trace_truncated',False)
            groups[r['name']][r['profile']].append((r,ours))
        categories={p:dict(Counter(r['category'] for r in rows if r['profile']==p)) for p in plan['profiles']}
        saved=json.loads((folder/'SUMMARY.json').read_text());assert saved['categories']==categories and not saved['validation_failures']
        assert saved['records']==len(rows) and saved['results_sha256']==sha(folder/'results.json')
        summaries.append({'run':folder.name,'all_pass':True,'records':len(rows),'categories':categories,'final_points_checked':points,
                          'initial_pending_points':pending_points,'supplemental_points_checked':rechecked_points,
                          'exact_proofs_recomputed':proofs,'cuts_rechecked':cuts,'lattice_events_rechecked':lattice,'lattice_truncated_traces':truncated,
                          'metadata_sha256':sha(folder/'metadata.json'),'results_sha256':sha(folder/'results.json')})
        for name,profiles in groups.items():
            c={'run':folder.name,'model':name}
            for profile,pairs in profiles.items():
                stats={'runs':len(pairs),'completed':sum(r['category'] in ('exact_proof_checked','numerical_completion_checked') for r,o in pairs)}
                for k in ('objective','best_bound','gap','total_seconds','nodes'):
                    values=[r[k] for r,o in pairs];stats['median_'+k]=statistics.median(values) if all(v is not None for v in values) else None
                stats['phase_median_seconds']={p['name']:statistics.median(next(q['seconds'] for q in o['work']['phases'] if q['name']==p['name']) for r,o in pairs) for p in pairs[0][1]['work']['phases']}
                c[profile]=stats
            comparisons.append(c)
        print(folder.name,'audit PASS',flush=True)
    assert len(supp_used)==len(supplemental) and set(supp_used)==set(supplemental)
    supplemental_evidence=None if not supp_meta else {'directory':str(supp_dir),'records':len(supp_used),
        'summary_sha256':sha(supp_dir/'SUMMARY.json'),'results_sha256':sha(supp_dir/'results.json')}
    save(out/'AUDIT.json',{'all_pass':True,'runs':summaries,'audit_sha256':sha(Path(__file__)),
          'supplemental_reference_checks':supplemental_evidence,
          'checker_sha256':{n:sha(ROOT/'scripts'/n) for n in ('validate_milp_frontier.py','check_milp_work.py','check_objective_lattice.py','check_lifted_covers.py','exact_binary_check.py','milp_robustness.py')},
          'scope':'Saved numerical/structural checks and exclusive phase accounting, not exact general LP/MILP proof. The optimized reader is checked equal to frozen13 on21 models.'})
    save(out/'COMPARISON.json',comparisons)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--supplemental',type=Path)
    p.add_argument('--output',type=Path,required=True);main(p.parse_args())
