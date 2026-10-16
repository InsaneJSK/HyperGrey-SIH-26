"""Independently check mixed models that actually exercise bound-row reduction."""
import argparse
import math
from pathlib import Path
import random
import sys
from benchmark_lp import ROOT, run
from industrial_cases import MpsModel
from validate_binary_proof import save, sha

if not __debug__:
    raise RuntimeError('Checks require assertions')


def main(args):
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(ROOT/'tools/reference/python'))
    import highspy
    rng=random.Random(26119101);records=[];accepted=0
    for case in range(80):
        model=MpsModel('REDUCED_BOUND_REFERENCE');point={}
        for j in range(7):
            name=f'x{j}';cap=rng.randint(3,8)
            model.var(name,rng.randint(-9,9)/4,0,1 if j<3 else None,j<3)
            point[name]=rng.randint(0,1) if j<3 else rng.randint(0,4*cap)/4
            if j>=3:model.row({name:1},'L',cap)
        for i in range(4):
            row={name:rng.randint(-4,4)/2 for name in model.vars}
            rhs=sum(row[n]*x for n,x in point.items())
            model.row(row,'E' if i==0 else ('L' if i%2 else 'G'),rhs+(0 if i==0 else (2 if i%2 else -2)))
        path=output/f'case{case:02d}.mps';model.write(path)
        if case%2:path.write_text(path.read_text().replace('ROWS\n','OBJSENSE\n MAX\nROWS\n',1))
        command=[str(args.binary.resolve()),str(path),'--milp','--json','--compact-equalities','--reduced-bound-lp','--time-limit','10','--node-limit','10000']
        ours=run(command,15);save(output/f'case{case:02d}.ours.json',ours)
        h=highspy.Highs()
        for key,value in {'output_flag':False,'threads':1,'random_seed':0,'time_limit':10.,'mip_rel_gap':1e-9}.items():
            assert h.setOptionValue(key,value)!=highspy.HighsStatus.kError
        assert h.readModel(str(path))!=highspy.HighsStatus.kError
        h.run();expected=h.getObjectiveValue();x=ours.get('primal',[])
        valid=len(x)==7 and all(math.isfinite(v) for v in x)
        violation=error=None
        if valid:
            by_name=dict(zip(model.vars,x))
            violation=max([0.]+[-v for v in x]+[x[j]-1 for j in range(3)]+[abs(x[j]-round(x[j])) for j in range(3)])
            for row,sense,rhs in model.rows:
                delta=sum(v*by_name[n] for n,v in row.items())-rhs
                violation=max(violation,abs(delta) if sense=='E' else (delta if sense=='L' else -delta))
            objective=sum(c*by_name[n] for n,(c,_,_,_) in model.vars.items())
            error=abs(objective-expected)
            valid=violation<=1e-7 and error<=1e-6*(1+abs(expected)) and abs(objective-ours['objective'])<=1e-7
        valid=valid and ours['status'] in ('optimal','gap_limit') and h.getModelStatus()==highspy.HighsModelStatus.kOptimal
        accepted+=ours.get('reduced_bound_lp_accepted',0)
        record={'case':case,'passed':bool(valid),'status':ours['status'],'reference_status':h.modelStatusToString(h.getModelStatus()),
                'reference_objective':expected,'violation':violation,'objective_error':error,
                'reduced_lp_accepted':ours.get('reduced_bound_lp_accepted',0),'fallbacks':ours.get('reduced_bound_lp_fallbacks',0),
                'command':command,'model_sha256':sha(path),'result_sha256':sha(output/f'case{case:02d}.ours.json')}
        records.append(record);save(output/'results.json',records)
        assert valid,record
    assert accepted>=80,'Insufficient reduction coverage'
    summary={'all_pass':True,'cases':80,'accepted_reduced_lps':accepted,'reference_version':h.version(),
             'fallbacks':sum(r['fallbacks'] for r in records),'binary_sha256':sha(args.binary),'script_sha256':sha(Path(__file__)),
             'limitation':'Small generated mixed models, not industrial/public timing evidence or exact MILP proofs.'}
    save(output/'SUMMARY.json',summary);print(summary,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args())
