"""Recheck breadth evidence identity/classification without rerunning timings."""
import argparse
import json
from pathlib import Path
from benchmark_lp import ROOT
from validate_binary_proof import sha, save
from milp_robustness import classify, FLAGS
from check_lifted_covers import check as check_cuts
from exact_binary_check import check as check_exact, parse_mps


def main(args):
    if not __debug__: raise RuntimeError('Audit requires assertions')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False);entries=[]
    for folder in args.runs:
        folder=folder.resolve();meta=json.loads((folder/'metadata.json').read_text())
        records=json.loads((folder/'results.json').read_text());source=Path(meta['source'])
        assert sha(Path(meta['binary']))==meta['binary_sha256']
        assert sha(source/'CMakeLists.txt')==meta['cmake_sha256']
        for name,digest in meta['source_sha256'].items():assert sha(source/name)==digest
        runner=folder.parent/('baseline-runner.py' if folder.name=='baseline-30s' else 'timed-runner.py')
        assert sha(runner)==meta['runner_sha256']
        for name,digest in meta.get('checker_sha256',{}).items():assert sha(ROOT/'scripts'/name)==digest
        manifest_path=ROOT/'datasets/milp-robustness-wave1/manifest.json'
        assert sha(manifest_path)==meta['manifest_sha256']
        manifest=json.loads(manifest_path.read_text())
        assert len(records)==len(manifest['instances'])==17
        assert [r['name'] for r in records]==[r['name'] for r in manifest['instances']]
        cuts=exact=points=0
        for r in records:
            name=r['name'];model=ROOT/r['model'];assert sha(model)==r['model_sha256']
            op=folder/(name+'.ours.json');rp=folder/(name+'.reference.json')
            assert sha(op)==r['ours_sha256'] and sha(rp)==r['reference_sha256']
            ours=json.loads(op.read_text());ref=json.loads(rp.read_text())
            expected=[meta['binary'],str(model),'--milp','--json',*FLAGS,'--time-limit',str(float(meta['limit'])),'--node-limit','250000','--gap','1e-6']
            assert r['command']==expected
            for raw,summary in [('status','ours_status'),('objective','objective'),('best_bound','best_bound'),('gap','gap'),('total_seconds','seconds'),('nodes','nodes')]:
                assert ours.get(raw)==r.get(summary)
            checked=check_cuts(model,ours);cuts+=checked['cuts_checked']
            proved=ours.get('binary_proof',{}).get('status') in ('optimal','infeasible')
            if proved:
                proof=check_exact(parse_mps(model.read_text()),ours);assert proof['all_checks_pass'];exact+=1
            category,errors=classify(ours,ref,meta['gap'],proved)
            assert not errors and category==r['category'],(name,category,errors)
            if ours.get('primal'):assert ref['candidate_checked'];points+=1
        entries.append({'run':folder.name,'all_pass':True,'records':len(records),'binary_sha256':meta['binary_sha256'],
                        'timing_source_files':len(meta['source_sha256']),'saved_reference_point_checks':points,
                        'exact_proofs_recomputed':exact,'retained_cuts_rechecked':cuts,
                        'results_sha256':sha(folder/'results.json'),'metadata_sha256':sha(folder/'metadata.json')})
    result={'all_pass':True,'runs':entries,'audit_sha256':sha(Path(__file__)),'final_classifier_sha256':sha(ROOT/'scripts/milp_robustness.py'),
            'limitation':'General internal LP bounds and unsaved intermediate points are not independently certified. Reference outputs are hash-checked saved post-timing checks. All 34 classifications are unchanged by the final gap-tolerance classifier correction.'}
    save(output/'AUDIT.json',result);print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
