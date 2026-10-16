"""Keep exact-source, sequential QP experiments and independent original-model checks."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
from benchmark_lp import ROOT, run
from qp_certificate import check


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--variant',nargs=2,action='append',required=True)
    p.add_argument('--models',nargs='+',default=['9002']);p.add_argument('--limit',type=float,default=30)
    p.add_argument('--probe',action='store_true');p.add_argument('--repeats',type=int,default=1)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    files=[ROOT/'CMakeLists.txt',Path(__file__).resolve(),ROOT/'scripts/qp_certificate.py',ROOT/'scripts/qplib_reference_reader.py']
    probe=ROOT/'reports/qp-iteration-01/probe.cpp'
    if probe.is_file():files.append(probe)
    for directory in ('src','include','tests'):
        files += [f for f in (ROOT/directory).rglob('*') if f.is_file()]
    for f in files:
        dest=args.output/'source'/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    save(args.output/'metadata.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_sha256':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
        'binary_sha256':{label:hashlib.sha256(Path(binary).read_bytes()).hexdigest() for label,binary in args.variant},
        'limit':args.limit,'repeats':args.repeats,'probe':args.probe})
    records=[]
    for repeat in range(args.repeats):
        for model in args.models:
            path=ROOT/'datasets/qplib'/(model+'.qplib')
            for label,binary in (args.variant if repeat%2==0 else args.variant[::-1]):
                command=[str(Path(binary).resolve()),str(path)]
                command+= [str(args.limit)] if args.probe else ['--json','--time-limit',str(args.limit)]
                r=run(command,args.limit+15);key=f'{model}.{label}.{repeat+1}'
                save(args.output/(key+'.ours.json'),r)
                checked=check(path,r);save(args.output/(key+'.check.json'),checked)
                record={k:r.get(k) for k in ('status','objective','iterations','total_seconds','algorithm','primal_residual','stationarity_residual','optimality_verified')}
                record.update(model=model,variant=label,repeat=repeat+1,independent=checked)
                records.append(record);save(args.output/'results.json',records);print(json.dumps(record),flush=True)


if __name__=='__main__':main()
