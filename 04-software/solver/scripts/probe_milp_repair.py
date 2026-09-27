"""Capture a bounded MILP run or independently diagnose its exact-integer fixing LPs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from benchmark_lp import ROOT,run
from inspect_lp_failure import export_model


def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main(args):
    args.output.mkdir(parents=True,exist_ok=False)
    if args.result is None:
        model=ROOT/'datasets/miplib2017/blend2.mps'
        command=[str(args.binary.resolve()),str(model),'--milp','--json','--lp-recovery','--improve-incumbent',
                 '--capture-rejected-candidates','--capture-lp-failure','--node-limit','6000','--time-limit',str(args.limit)]
        save(args.output/'metadata.json',{'command':command,'binary_sha256':sha(args.binary),'model_sha256':sha(model),
             'core_sha256':{p.relative_to(ROOT).as_posix():sha(p) for folder in ('src','include') for p in (ROOT/folder).glob('*') if p.is_file()}})
        result=run(command,args.limit+20);save(args.output/'result.json',result)
        print(json.dumps({k:result.get(k) for k in ('status','objective','nodes','rejected_integer_candidates','total_seconds')},indent=2))
        return
    result=json.loads(args.result.read_text(encoding='utf-8'));summary=[]
    for i,sample in enumerate(result.get('rejected_candidates',[])):
        if not sample['fixing']['captured']:continue
        folder=args.output/str(i);folder.mkdir();model=folder/'fixed.mps';offset=export_model(sample['fixing'],model)
        entry={'index':i,'node':sample['fixing']['node'],'initial_repair_status':sample['fixing']['status'],
               'rounded_violation':sample['rounded_violation'],'offset_omitted':offset,'runs':{}}
        for label,method,flags in [('sparse','sparse',[]),('dense','dense',[]),('unscaled','sparse',['--no-scaling'])]:
            command=[str(args.binary.resolve()),str(model.resolve()),'--json','--lp-method',method,'--tolerance','1e-11','--time-limit','5',*flags]
            ours=run(command,15);candidate=folder/(label+'.json');save(candidate,ours)
            reference=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(model.resolve()),'--candidate',str(candidate.resolve()),'--limit','5'],20)
            save(folder/(label+'.reference.json'),reference)
            entry['runs'][label]={'status':ours.get('status'),'objective':ours.get('objective'),'iterations':ours.get('iterations'),
                                'reference_status':reference.get('status'),'reference_objective':reference.get('objective'),
                                'absolute_violation':reference.get('candidate_max_violation')}
        summary.append(entry);print(json.dumps(entry,indent=2),flush=True)
    save(args.output/'SUMMARY.json',summary)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--result',type=Path);p.add_argument('--limit',type=float,default=75)
    main(p.parse_args())
