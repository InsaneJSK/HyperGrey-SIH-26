"""Re-audit frozen matched-run identity, classifications, cuts and lattice data."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import statistics
from benchmark_lp import ROOT
from milp_robustness import FLAGS,classify
from validate_binary_proof import sha,save
from check_objective_lattice import check as lattice_check
from check_lifted_covers import check as cut_check
from exact_binary_check import check as exact_check,parse_mps


def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False);summaries=[];comparisons=[]
    for folder in args.runs:
        folder=folder.resolve();meta=json.loads((folder/'metadata.json').read_text());records=json.loads((folder/'results.json').read_text())
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        for name,digest in meta['file_sha256'].items():assert sha(ROOT/name)==digest,name
        assert meta['profiles']=={'control':FLAGS,'lattice':FLAGS+['--objective-lattice']}
        expected=[]
        for index,name in enumerate(meta['models']):
            for repeat in range(meta['repeats']):
                for profile in (['control','lattice'] if (index+repeat)%2==0 else ['lattice','control']):expected.append((name,profile,repeat))
        assert [(r['name'],r['profile'],r['repeat']) for r in records]==expected
        events=cuts=exact=points=eligible=truncated=0;by_model=defaultdict(lambda:defaultdict(list))
        for r in records:
            key=r['key'];model=ROOT/r['model'];assert sha(model)==r['model_sha256']
            op=folder/(key+'.ours.json');rp=folder/(key+'.reference.json')
            assert sha(op)==r['ours_sha256'] and sha(rp)==r['reference_sha256']
            ours=json.loads(op.read_text());ref=json.loads(rp.read_text())
            command=[meta['binary'],str(model),'--milp','--json',*meta['profiles'][r['profile']],
                     '--time-limit',str(meta['limit']),'--node-limit','250000','--gap','1e-6']
            assert command==r['command']
            for field in ('status','objective','best_bound','gap','total_seconds','nodes'):assert r[field]==ours.get(field)
            lattice=lattice_check(model,ours);assert lattice==json.loads((folder/(key+'.lattice-check.json')).read_text())
            events+=lattice['events_checked'];eligible+=lattice['eligible'];truncated+=lattice.get('trace_truncated',False)
            cut=cut_check(model,ours);assert cut==json.loads((folder/(key+'.cuts-check.json')).read_text());cuts+=cut['cuts_checked']
            proved=ours.get('binary_proof',{}).get('verified',False)
            if proved:
                proof=exact_check(parse_mps(model.read_text()),ours);assert proof['all_checks_pass'];exact+=1
            category,errors=classify(ours,ref,meta['gap'],proved)
            assert not errors and not r['validation_errors'] and category==r['category'],(key,errors)
            if ours.get('primal'):assert ref['candidate_checked'];points+=1
            by_model[r['name']][r['profile']].append(r)
        categories={p:dict(Counter(r['category'] for r in records if r['profile']==p)) for p in meta['profiles']}
        saved=json.loads((folder/'SUMMARY.json').read_text());assert saved['categories']==categories and saved['validation_failures']==0
        summaries.append({'run':folder.name,'records':len(records),'all_pass':True,'categories':categories,
                          'eligible_records':eligible,'rounding_events_rechecked':events,'truncated_traces':truncated,
                          'retained_cuts_rechecked':cuts,'exact_proofs_recomputed':exact,'saved_final_point_checks':points,
                          'results_sha256':sha(folder/'results.json'),'metadata_sha256':sha(folder/'metadata.json')})
        for name,profiles in by_model.items():
            item={'run':folder.name,'model':name}
            for profile,rows in profiles.items():
                item[profile]={'runs':len(rows),'completed':sum(r['category'] in ('exact_proof_checked','numerical_completion_checked') for r in rows),
                               'median_seconds':statistics.median(r['total_seconds'] for r in rows),
                               'median_objective':statistics.median(r['objective'] for r in rows) if all(r['objective'] is not None for r in rows) else None,
                               'median_bound':statistics.median(r['best_bound'] for r in rows) if all(r['best_bound'] is not None for r in rows) else None,
                               'median_gap':statistics.median(r['gap'] for r in rows) if all(r['gap'] is not None for r in rows) else None}
            comparisons.append(item)
    audit={'all_pass':True,'runs':summaries,'audit_sha256':sha(Path(__file__)),
           'scope':'File/command identity, saved final-point reference checks, exact subset recomputation, cuts and all saved lattice events. General input LP bounds remain numerical.'}
    save(output/'AUDIT.json',audit);save(output/'COMPARISON.json',comparisons);print(json.dumps(audit,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',type=Path,nargs='+');p.add_argument('--output',type=Path,required=True);main(p.parse_args())
