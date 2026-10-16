"""Failure-preserving fixed-node / equal-time frontier comparisons; CPU only."""
import argparse
from collections import Counter,defaultdict
import datetime
import hashlib
import json
from pathlib import Path
import platform
import sys
from benchmark_lp import ROOT
from milp_robustness import FLAGS,timed,classify
from validate_binary_proof import sha,save
from check_objective_lattice import check as lattice_check
from check_milp_frontier import check as frontier_check
from check_lifted_covers import check as cut_check
from exact_binary_check import check as exact_check,parse_mps

EXTRA={'control':[],'lattice':['--objective-lattice'],'raw':['--objective-lattice','--raw-lp-priority']}
HELPERS=['milp_robustness.py','benchmark_lp.py','validate_binary_proof.py','check_objective_lattice.py',
         'check_milp_frontier.py','check_lifted_covers.py','exact_binary_check.py']


def semantic(ours):
    fields=['status','objective','best_bound','gap','nodes','lp_iterations','primal','root_bound_before_cuts','root_bound_after_cuts','frontier']
    return hashlib.sha256(json.dumps({k:ours.get(k) for k in fields},sort_keys=True,allow_nan=False).encode()).hexdigest()


def verify(model,ours,ref,output,key,gap):
    errors=[];exact=False;checks={}
    if isinstance(ours.get('columns'),int):
        for kind,fn in [('lattice',lambda:lattice_check(model,ours)),('frontier',lambda:frontier_check(ours,ref.get('maximize',False))),('cuts',lambda:cut_check(model,ours))]:
            try:
                checks[kind]=fn();save(output/(key+f'.{kind}-check.json'),checks[kind])
            except Exception as e:errors.append(kind+'_check: '+repr(e))
        if ours.get('binary_proof',{}).get('verified'):
            try:
                checks['exact']=exact_check(parse_mps(model.read_text()),ours);save(output/(key+'.exact-check.json'),checks['exact'])
                exact=checks['exact']['all_checks_pass']
            except Exception as e:errors.append('exact_check: '+repr(e))
    category,validation=classify(ours,ref,gap,exact);errors+=validation
    return ('validation_failure' if errors else category),errors,checks


def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve();manifest_path=args.manifest.resolve()
    specs=json.loads(manifest_path.read_text())['instances']
    if args.models:
        assert set(args.models)<={s['name'] for s in specs};specs=[s for s in specs if s['name'] in args.models]
    limit=args.limit if args.limit is not None else (120 if args.node_screen else 30)
    nodes=args.nodes if args.nodes is not None else (2048 if args.node_screen else 250000)
    gap=0. if args.node_screen else 1e-6
    common=['--no-heuristics','--no-cuts','--capture-frontier'] if args.node_screen else FLAGS
    profiles={name:common+EXTRA[name] for name in args.profiles}
    files=[p for d in ('src','include') for p in (ROOT/d).glob('*') if p.is_file()]+[ROOT/'CMakeLists.txt',manifest_path,Path(__file__)]+[ROOT/'scripts'/n for n in HELPERS]
    meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary':str(binary),'binary_sha256':sha(binary),
          'file_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files},'manifest':str(manifest_path),
          'profiles':profiles,'models':[s['name'] for s in specs],'repeats':args.repeats,'limit':limit,'node_limit':nodes,
          'reference_limit':args.reference_limit,'gap':gap,'node_screen':args.node_screen,'platform':platform.platform(),
          'protocol':'Rotated profile order. Sequential own runs first, then independent references and checks. All outcomes retained; no external incumbents.'}
    save(out/'metadata.json',meta);records=[]
    for index,spec in enumerate(specs):
        if spec['status']!='ready':
            records.append({**spec,'category':'download_failed'});save(out/'results.json',records);continue
        model=ROOT/spec['model'];assert sha(model)==spec['model_sha256']
        for repeat in range(args.repeats):
            names=list(profiles);shift=(index+repeat)%len(names);order=names[shift:]+names[:shift]
            for profile in order:
                key=f"{spec['name']}.{profile}.{repeat}"
                command=[str(binary),str(model),'--milp','--json',*profiles[profile],'--time-limit',str(limit),
                         '--node-limit',str(nodes),'--gap',str(gap)]
                ours=timed(command,limit+15,out/key);save(out/(key+'.ours.json'),ours)
                r={**spec,'key':key,'profile':profile,'repeat':repeat,'command':command,'ours_sha256':sha(out/(key+'.ours.json')),
                   'semantic_sha256':semantic(ours),**{f:ours.get(f) for f in ('status','objective','best_bound','gap','nodes','total_seconds')}}
                records.append(r);save(out/'results.json',records)
                print(key,{f:r[f] for f in ('status','objective','best_bound','gap','nodes','total_seconds')},flush=True)
    for r in records:
        if 'key' not in r:continue
        key=r['key'];model=ROOT/r['model'];ours=json.loads((out/(key+'.ours.json')).read_text())
        command=[sys.executable,str(ROOT/'scripts/milp_robustness.py'),'--reference',str(model),'--candidate',str(out/(key+'.ours.json')),
                 '--reference-limit',str(args.reference_limit)]
        ref=timed(command,args.reference_limit+20,out/(key+'.reference'));save(out/(key+'.reference.json'),ref)
        category,errors,checks=verify(model,ours,ref,out,key,gap)
        r.update(category=category,validation_errors=errors,reference_status=ref['status'],reference_objective=ref.get('objective'),
                 candidate_violation=ref.get('candidate_max_violation'),reference_sha256=sha(out/(key+'.reference.json')))
        save(out/'results.json',records);print(key,category,errors,flush=True)
    assert sha(binary)==meta['binary_sha256']
    for name,digest in meta['file_sha256'].items():assert sha(ROOT/name)==digest,name
    repeated=defaultdict(list)
    for r in records:
        if 'key' in r:repeated[(r['name'],r['profile'])].append(r)
    deterministic=[]
    if args.node_screen:
        for (name,profile),rows in repeated.items():
            deterministic.append({'model':name,'profile':profile,'runs':len(rows),'same_semantics':len({r['semantic_sha256'] for r in rows})==1,
                                  'node_or_completion_terminated':all(r['status'] in ('node_limit','optimal','gap_limit','infeasible') for r in rows)})
    summary={'runs':sum('key' in r for r in records),'models':len(specs),'repeats':args.repeats,
             'categories':{p:dict(Counter(r['category'] for r in records if r.get('profile')==p)) for p in profiles},
             'download_failures':sum(r['category']=='download_failed' for r in records),
             'validation_failures':sum(r['category']=='validation_failure' for r in records),'deterministic_checks':deterministic,
             'limitation':'Bookkeeping replay does not certify underlying LP bounds or all branching domains. Numerical completion is not general exact proof.'}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--manifest',type=Path,default=ROOT/'datasets/milp-robustness-wave1/manifest.json');p.add_argument('--models',nargs='+')
    p.add_argument('--profiles',nargs='+',choices=list(EXTRA),default=['lattice','raw']);p.add_argument('--repeats',type=int,default=1)
    p.add_argument('--limit',type=float);p.add_argument('--nodes',type=int);p.add_argument('--reference-limit',type=float,default=5)
    p.add_argument('--node-screen',action='store_true');main(p.parse_args())
