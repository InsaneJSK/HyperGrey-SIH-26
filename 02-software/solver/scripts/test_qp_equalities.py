"""Deterministic planted-KKT diagonal equality QPs, including large scale changes."""
import argparse
import json
import math
from pathlib import Path
import random
from benchmark_lp import ROOT, run
from qp_certificate import check


def write_model(path, h, c, rows, b, lo, up, maximize=False, offset=0):
    n=len(c);m=len(rows);sign=-1 if maximize else 1
    lines=['PLANTED_DIAGONAL', 'DCL', 'maximize' if maximize else 'minimize', str(n), str(m), str(n)]
    lines += [f'{j+1} {j+1} {sign*v:.17g}' for j,v in enumerate(h)]
    def vector(values):
        return ['0',str(len(values))]+[f'{j+1} {v if math.isfinite(v) else math.copysign(1e100,v):.17g}' for j,v in enumerate(values)]
    lines += vector([sign*v for v in c])+[str(sign*offset),str(sum(len(row) for row in rows))]
    lines += [f'{i+1} {j+1} {v:.17g}' for i,row in enumerate(rows) for j,v in row]
    lines += ['1e100']+vector(b)+vector(b)+vector(lo)+vector(up)
    lines += ['0','0','0','0','0','0','0','0']
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main(output, binary=None):
    output.mkdir(parents=True,exist_ok=False)
    binary=binary or ROOT/'build/solver_cli.exe';rng=random.Random(900226119);records=[]
    # Full cross-product is fixed in advance, not selected from successful runs.
    specs=[(24,spread,scale,redundant) for spread in (0,6,12) for scale in (.01,1,1e4) for redundant in (False,True)]
    specs += [(600,12,1e4,True),(720,6,1,False)]
    for case,(n,spread,scale,redundant) in enumerate(specs):
        h=[10**(-spread*j/max(1,n-1)) for j in range(n)];units=[1/math.sqrt(v) for v in h]
        x=[rng.uniform(-.8,.8)*units[j]*scale for j in range(n)]
        lo=[-2*units[j]*scale for j in range(n)];up=[2*units[j]*scale for j in range(n)]
        bound_gradient=[0.0]*n
        for j in range(n):
            mode=j%6
            if mode==0:lo[j]=x[j];bound_gradient[j]=.3*scale/units[j]
            elif mode==1:up[j]=x[j];bound_gradient[j]=-.3*scale/units[j]
            elif mode==2:lo[j]=-math.inf
            elif mode==3:up[j]=math.inf
            elif mode==4:lo[j]=up[j]=x[j]
        # Sparse coupled blocks; column magnitudes reflect the curvature change.
        rows=[[(j,rng.uniform(.5,1.5)/units[j]) for j in range(k,min(k+6,n))] for k in range(0,n,6)]
        if redundant:rows += [[(j,2*v) for j,v in row] for row in rows[::2]]
        b=[math.fsum(v*x[j] for j,v in row) for row in rows]
        y=[rng.uniform(-1,1)*scale for _ in rows]
        c=[-h[j]*x[j]+bound_gradient[j] for j in range(n)]
        for row,dual in zip(rows,y):
            for j,v in row:c[j]-=v*dual
        offset=.125*scale*scale;maximize=case%2==1;sign=-1 if maximize else 1
        expected=sign*(math.fsum(.5*h[j]*x[j]*x[j]+c[j]*x[j] for j in range(n))+offset)
        model=output/f'case{case:02d}.qplib';write_model(model,h,c,rows,b,lo,up,maximize,offset)
        ours=run([str(binary),str(model),'--json','--time-limit','5'],15)
        certificate=check(model,ours);value=ours.get('objective');bound=ours.get('dual_bound_minimization_sense')
        error=abs(value-expected)/(1+abs(expected)) if value is not None else None
        passed=(ours.get('status')=='optimal' and certificate['diagonal_certificate_passed'] and error is not None and error<=1e-7
                and bound is not None and abs(bound-sign*expected)/(1+abs(expected))<=1e-7)
        record={'case':case,'columns':n,'curvature_orders':spread,'magnitude':scale,'redundant_rows':redundant,
                'maximize':maximize,'expected_objective':expected,'relative_objective_error':error,
                'passed':passed,'status':ours.get('status'),'algorithm':ours.get('algorithm'),'certificate':certificate}
        (output/f'case{case:02d}.result.json').write_text(json.dumps({'ours':ours,**record},indent=2)+'\n')
        records.append(record)
    # Known-infeasible equalities must not gain an optimality claim. No Farkas
    # certificate is required from this QP implementation, so non-optimal is OK.
    model=output/'infeasible.qplib';write_model(model,[1,1],[0,0],[[(0,1)],[(0,1)]],[0,1],[-2,-2],[2,2])
    ours=run([str(binary),str(model),'--json','--time-limit','.1'],10)
    certificate=check(model,ours)
    record={'case':'infeasible_equalities','passed':ours.get('status') not in ('optimal','process_error','error') and not ours.get('optimality_verified') and not certificate['independent_kkt_passed'],'status':ours.get('status')}
    (output/'infeasible.result.json').write_text(json.dumps({'ours':ours,'certificate':certificate,**record},indent=2)+'\n')
    records.append(record)
    (output/'summary.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Diagonal equality QP tests:',sum(r['passed'] for r in records),'/',len(records),flush=True)
    return all(r['passed'] for r in records)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--binary',type=Path)
    args=parser.parse_args();raise SystemExit(0 if main(args.output,args.binary) else 1)
