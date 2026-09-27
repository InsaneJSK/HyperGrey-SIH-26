"""Materialize iteration16's fixed plans; never overwrite existing outputs."""
import json
from benchmark_lp import ROOT
from validate_binary_proof import save,sha

def main():
    out=ROOT/'reports/milp-iteration-16';old=ROOT/'reports/milp-iteration-15'
    assert sha(old/'final_solver_cli.exe')=='57ce59edcc13d7717e0a8fd3f964dd8960d79cb86f9acb0dde9ee7d78003d159'
    for rel,digest in json.loads((old/'SNAPSHOT_MANIFEST.json').read_text()).items():assert sha(old/'final-source'/rel)==digest
    common=json.loads((old/'SCREEN.json').read_text())['common']
    manifests=['datasets/milp-robustness-wave1/manifest.json','datasets/milp-frontier-holdout/manifest.json','datasets/milp-cut-policy-holdout/manifest.json']
    models=json.loads((old/'WAVE.json').read_text())['models']+json.loads((old/'HOLDOUT.json').read_text())['models']
    plans={
        'SCREEN.json':dict(models=['binkar10_1','p0282','mod008'],repeats=2),
        'WAVE.json':dict(models=models,repeats=1),
    }
    for name,spec in plans.items():
        path=out/name;assert not path.exists()
        save(path,{**spec,'limit':30,'reference_watchdog':150,'manifests':manifests,'common':common,
            'profiles':{'baseline':[],'guarded':['--adaptive-cut-rounds','--cut-after-incumbent']}})
    # Diagnostic ablations are run against frozen15, not the new candidate.
    path=out/'MAS74.json';assert not path.exists()
    without=[f for f in common if f not in ('--late-reduced-bound-lp','--late-compact-equalities')]
    # Keep transforms in common and remove them via explicit per-plan comparisons,
    # since CLI flags cannot undo an earlier enabling option.
    save(path,{'models':['mas74'],'repeats':1,'limit':30,'reference_watchdog':150,'manifests':manifests,
        'common':[f for f in without if f!='--capture-cut-rounds']+['--capture-frontier'],
        'profiles':{'late_transforms':['--late-compact-equalities','--late-reduced-bound-lp'],
                    'plain_restart':[],
                    'no_clock_restart':['--late-compact-equalities','--late-reduced-bound-lp','--restart-nodes','100000000']}})
    print('Plans created; frozen15 source and binary preserved')

if __name__=='__main__':main()
