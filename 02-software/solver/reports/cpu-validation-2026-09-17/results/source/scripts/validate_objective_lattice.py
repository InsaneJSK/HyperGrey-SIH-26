"""Predeclared matched local runs: control and opt-in objective lattice.

Own CPU timings are sequential; all reference optimization/checks follow them.
No external objective or point is passed to the solver. Failures are retained.
"""
import argparse
from collections import Counter
import datetime
import json
from pathlib import Path
import platform
import sys
from benchmark_lp import ROOT
from milp_robustness import FLAGS, timed, classify
from validate_binary_proof import sha, save
from check_objective_lattice import check as lattice_check
from check_lifted_covers import check as cut_check
from exact_binary_check import check as exact_check, parse_mps


def main(args):
    if not __debug__: raise RuntimeError('Validation requires assertions')
    output=args.output.resolve(); output.mkdir(parents=True,exist_ok=False)
    binary=args.binary.resolve(); manifest_path=ROOT/'datasets/milp-robustness-wave1/manifest.json'
    manifest=json.loads(manifest_path.read_text()); specs=manifest['instances']
    if args.models:
        assert set(args.models) <= {s['name'] for s in specs}
        specs=[s for s in specs if s['name'] in args.models]
    profiles={'control':FLAGS,'lattice':FLAGS+['--objective-lattice']}
    files=[p for folder in ('src','include') for p in (ROOT/folder).glob('*') if p.is_file()]
    files += [ROOT/'CMakeLists.txt',manifest_path,Path(__file__)]
    files += [ROOT/'scripts'/s for s in ('milp_robustness.py','benchmark_lp.py','validate_binary_proof.py',
                                      'check_objective_lattice.py','check_lifted_covers.py','exact_binary_check.py')]
    metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'binary':str(binary),
              'binary_sha256':sha(binary),'file_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files},
              'profiles':profiles, 'models':[s['name'] for s in specs], 'repeats':args.repeats,
              'limit':args.limit,'reference_limit':args.reference_limit,'node_limit':250000,'gap':1e-6,
              'platform':platform.platform(), 'protocol':__doc__}
    save(output/'metadata.json',metadata); records=[]
    for index,spec in enumerate(specs):
        assert spec['status']=='ready'; model=ROOT/spec['model']; assert sha(model)==spec['model_sha256']
        for repeat in range(args.repeats):
            order=['control','lattice'] if (index+repeat)%2==0 else ['lattice','control']
            for profile in order:
                key=f"{spec['name']}.{profile}.{repeat}"
                command=[str(binary),str(model),'--milp','--json',*profiles[profile],
                         '--time-limit',str(args.limit),'--node-limit','250000','--gap','1e-6']
                ours=timed(command,args.limit+15,output/key); save(output/(key+'.ours.json'),ours)
                record={**spec,'key':key,'profile':profile,'repeat':repeat,'command':command,
                        'ours_sha256':sha(output/(key+'.ours.json')),
                        **{f:ours.get(f) for f in ('status','objective','best_bound','gap','total_seconds','nodes')}}
                records.append(record);save(output/'results.json',records)
                print(key,{f:record[f] for f in ('status','objective','best_bound','gap','total_seconds')},flush=True)
    # Do not overlap independent solves or exact enumeration with own timings.
    for r in records:
        key=r['key'];model=ROOT/r['model']; ours=json.loads((output/(key+'.ours.json')).read_text())
        command=[sys.executable,str(ROOT/'scripts/milp_robustness.py'),'--reference',str(model),
                 '--candidate',str(output/(key+'.ours.json')),'--reference-limit',str(args.reference_limit)]
        ref=timed(command,args.reference_limit+20,output/(key+'.reference'));save(output/(key+'.reference.json'),ref)
        errors=[];exact=False
        for kind,checker in [('lattice',lambda:lattice_check(model,ours)),('cuts',lambda:cut_check(model,ours))]:
            try: save(output/(key+f'.{kind}-check.json'),checker())
            except Exception as e: errors.append(kind+'_check: '+repr(e))
        if ours.get('binary_proof',{}).get('verified'):
            try:
                proof=exact_check(parse_mps(model.read_text()),ours); save(output/(key+'.exact-check.json'),proof)
                exact=proof['all_checks_pass']
            except Exception as e: errors.append('exact_check: '+repr(e))
        category,validation=classify(ours,ref,1e-6,exact);errors+=validation
        if errors:category='validation_failure'
        r.update(category=category,validation_errors=errors,reference_status=ref['status'],
                 reference_objective=ref.get('objective'),candidate_violation=ref.get('candidate_max_violation'),
                 reference_sha256=sha(output/(key+'.reference.json')))
        save(output/'results.json',records);print(key,category,errors,flush=True)
    assert sha(binary)==metadata['binary_sha256']
    for name,digest in metadata['file_sha256'].items():assert sha(ROOT/name)==digest,name
    summary={'runs':len(records),'models':len(specs),'repeats':args.repeats,
             'categories':{p:dict(Counter(r['category'] for r in records if r['profile']==p)) for p in profiles},
             'validation_failures':sum(r['category']=='validation_failure' for r in records),
             'all_public_cases_proven':False,
             'limitation':'Numerical completions and checked rounding are not exact general MILP certificates. All limits retained.'}
    save(output/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--limit',type=float,default=30);p.add_argument('--reference-limit',type=float,default=5)
    p.add_argument('--models',nargs='+');p.add_argument('--repeats',type=int,default=1)
    main(p.parse_args())
