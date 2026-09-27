"""Re-audit retained frontier experiments without rerunning performance tests."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import statistics
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from validate_milp_frontier import verify,semantic


def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);entries=[];comparisons=[]
    for folder in args.runs:
        folder=folder.resolve();sub=out/folder.name;sub.mkdir();meta=json.loads((folder/'metadata.json').read_text());records=json.loads((folder/'results.json').read_text())
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        for name,digest in meta['file_sha256'].items():assert sha(ROOT/name)==digest,name
        manifest=json.loads(Path(meta['manifest']).read_text());by_name={s['name']:s for s in manifest['instances']}
        expected=[]
        for index,name in enumerate(meta['models']):
            if by_name[name]['status']!='ready':continue
            for repeat in range(meta['repeats']):
                names=list(meta['profiles']);shift=(index+repeat)%len(names)
                expected += [(name,p,repeat) for p in names[shift:]+names[:shift]]
        assert [(r['name'],r['profile'],r['repeat']) for r in records if 'key' in r]==expected
        points=exact=cuts=events=lattice_truncated=frontier_events=frontier_truncated=resets=0;groups=defaultdict(lambda:defaultdict(list))
        for r in records:
            if 'key' not in r:assert r['category']=='download_failed';continue
            key=r['key'];model=ROOT/r['model'];assert sha(model)==r['model_sha256']==by_name[r['name']]['model_sha256']
            op=folder/(key+'.ours.json');rp=folder/(key+'.reference.json');assert sha(op)==r['ours_sha256'] and sha(rp)==r['reference_sha256']
            ours=json.loads(op.read_text());ref=json.loads(rp.read_text());assert semantic(ours)==r['semantic_sha256']
            expected_command=[meta['binary'],str(model),'--milp','--json',*meta['profiles'][r['profile']],
                              '--time-limit',str(meta['limit']),'--node-limit',str(meta['node_limit']),'--gap',str(meta['gap'])]
            assert r['command']==expected_command
            for f in ('status','objective','best_bound','gap','nodes','total_seconds'):assert r[f]==ours.get(f)
            category,errors,checks=verify(model,ours,ref,sub,key,meta['gap'])
            assert not errors and category==r['category'] and not r['validation_errors'],(key,category,errors)
            for kind,data in checks.items():assert data==json.loads((folder/(key+f'.{kind}-check.json')).read_text())
            points+=bool(ours.get('primal'));exact+=bool(checks.get('exact',{}).get('all_checks_pass'))
            cuts+=checks.get('cuts',{}).get('cuts_checked',0);events+=checks.get('lattice',{}).get('events_checked',0)
            lattice_truncated+=checks.get('lattice',{}).get('trace_truncated',False)
            frontier=checks.get('frontier',{});frontier_events+=frontier.get('events_checked',0)
            frontier_truncated+=frontier.get('trace_truncated',False);resets+=frontier.get('resets_checked',0)
            groups[r['name']][r['profile']].append(r)
        categories={p:dict(Counter(r['category'] for r in records if r.get('profile')==p)) for p in meta['profiles']}
        summary=json.loads((folder/'SUMMARY.json').read_text());assert categories==summary['categories'] and not summary['validation_failures']
        entries.append({'run':folder.name,'all_pass':True,'records':len(expected),'categories':categories,'saved_final_points_checked':points,
                        'exact_proofs_recomputed':exact,'cuts_rechecked':cuts,'lattice_events_rechecked':events,
                        'lattice_truncated_traces':lattice_truncated,
                        'frontier_events_replayed':frontier_events,'frontier_truncated_traces':frontier_truncated,'frontier_resets_replayed':resets,
                        'results_sha256':sha(folder/'results.json'),'metadata_sha256':sha(folder/'metadata.json')})
        for name,profiles in groups.items():
            c={'run':folder.name,'model':name}
            for profile,rows in profiles.items():
                c[profile]={'runs':len(rows),'completed':sum(r['category'] in ('exact_proof_checked','numerical_completion_checked') for r in rows),
                            'median_seconds':statistics.median(r['total_seconds'] for r in rows) if all(r['total_seconds'] is not None for r in rows) else None,
                            'median_objective':statistics.median(r['objective'] for r in rows) if all(r['objective'] is not None for r in rows) else None,
                            'median_bound':statistics.median(r['best_bound'] for r in rows) if all(r['best_bound'] is not None for r in rows) else None,
                            'median_gap':statistics.median(r['gap'] for r in rows) if all(r['gap'] is not None for r in rows) else None,
                            'node_repeat_identical':len({r['semantic_sha256'] for r in rows})==1 if meta['node_screen'] else None}
            comparisons.append(c)
    audit={'all_pass':True,'runs':entries,'audit_sha256':sha(Path(__file__)),
           'limitation':'Replays saved frontier accounting and rechecks recorded outcomes. Does not certify every raw LP bound or all branching domains.'}
    save(out/'AUDIT.json',audit);save(out/'COMPARISON.json',comparisons);print(json.dumps(audit,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
