"""Cold-replay a captured tree LP, after timed experiments have finished.

The input basis is retained in the original JSON. These runs deliberately use
fresh bases: they diagnose whether the same relaxation is difficult cold; they
do not replay the warm pivot sequence or certify why that sequence stalled.
"""
import argparse
import json
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT,run
from industrial_cases import MpsModel


def export_model(failure,path):
    model=MpsModel('CAPTURED_CONTINUOUS_NODE')
    n=len(failure['cost']);sign=-1 if failure['maximize'] else 1
    if len(failure['lower'])!=n or len(failure['upper'])!=n:raise ValueError('Invalid bounds')
    for j,cost in enumerate(failure['cost']):
        if not math.isfinite(cost):raise ValueError('Nonfinite objective')
        model.var('x'+str(j),sign*cost,failure['lower'][j],failure['upper'][j])
    rows=failure['rows']
    if len(failure['row_lower'])!=len(rows) or len(failure['row_upper'])!=len(rows):raise ValueError('Invalid rows')
    for entries,lo,up in zip(rows,failure['row_lower'],failure['row_upper']):
        coefficients={}
        for j,value in entries:
            if not isinstance(j,int) or not 0<=j<n or not math.isfinite(value):raise ValueError('Invalid coefficient')
            key='x'+str(j);coefficients[key]=coefficients.get(key,0)+value
        if lo is not None and lo==up:model.row(coefficients,'E',lo)
        else:
            if up is not None:model.row(coefficients,'L',up)
            if lo is not None:model.row(coefficients,'G',lo)
    model.write(path)
    return sign*failure['offset']


def main(args):
    source=json.loads(args.result.read_text(encoding='utf-8'))
    failure=source.get('first_lp_failure')
    if not failure or not failure.get('captured'):
        raise ValueError('No captured LP in this result')
    if args.limit<=0:raise ValueError('Diagnostic limit must be positive')
    args.output.mkdir(parents=True,exist_ok=False)
    path=args.output/'relaxation.mps';offset=export_model(failure,path)
    iterations=int(failure['iterations'])
    results={}
    for method in ('sparse','dense'):
        results[method]=run([str(args.binary.resolve()),str(path.resolve()),'--json','--lp-method',method,
                             '--iteration-limit',str(iterations),'--time-limit',str(args.limit)],args.limit+10)
        (args.output/(method+'.json')).write_text(json.dumps(results[method],indent=2,allow_nan=False)+'\n',encoding='utf-8')
    results['reference']=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',str(path.resolve()),
                              '--candidate',str((args.output/'sparse.json').resolve()),'--limit',str(args.limit)],args.limit+15)
    report={'source_result':str(args.result.resolve()),'failure_status':failure['status'],
            'node':failure['node'],'depth':failure['depth'],'iteration_limit':iterations,
            'time_limit_seconds':args.limit,'minimization_offset_omitted':offset,
            'interpretation':'Fresh-basis solves of the same constraints/objective, normalized to minimization without the constant. Starting warm basis is in the source JSON, not replayed here.',
            'results':results}
    (args.output/'REPORT.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({name:{k:value.get(k) for k in ('status','objective','iterations','total_seconds')} for name,value in results.items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--binary',type=Path,required=True);p.add_argument('--limit',type=float,default=5)
    main(p.parse_args())
