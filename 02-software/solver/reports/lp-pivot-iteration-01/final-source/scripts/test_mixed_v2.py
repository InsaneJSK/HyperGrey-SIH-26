"""Bound/row-sense regression on mixed continuous/general-integer models."""
import json,random,sys,math
from pathlib import Path
from industrial_cases import MpsModel
from benchmark_lp import ROOT,run

def main(output,binary=None,flags=None):
    sys.path.insert(0,str(ROOT/'tools/reference/python'))
    import highspy
    output.mkdir(parents=True,exist_ok=False);rng=random.Random(26219);results=[]
    for case in range(40):
        model=MpsModel('MIXED_REGRESSION');planted=[rng.randint(-2,3),rng.randint(-1,3),rng.randint(0,4),rng.uniform(-3,2),rng.uniform(0,4)]
        bounds=[(-2,3),(-1,3),(0,4),(-3,2),(0,4)]
        for j,(lo,up) in enumerate(bounds):model.var(f'x{j}',rng.randint(-7,7),lo,up,j<3)
        for i in range(5):
            row={f'x{j}':rng.randint(-3,4) for j in range(5)};activity=sum(row[f'x{j}']*planted[j] for j in range(5))
            sense='E' if i==0 and case%3==0 else ('L' if i%2==0 else 'G')
            rhs=activity+(rng.uniform(0,4)*(1 if sense=='L' else -1) if sense!='E' else 0);model.row(row,sense,rhs)
        path=output/f'case{case:02d}.mps';model.write(path)
        ours=run([str(binary or ROOT/'build/solver_cli.exe'),str(path),'--milp','--json','--time-limit','5',*(flags or [])],10)
        h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1);h.setOptionValue('mip_rel_gap',1e-9);h.readModel(str(path));h.run()
        expected=h.getObjectiveValue();x=ours.get('primal',[]);violation=math.inf
        if len(x)==5:
            violation=max([0]+[max(lo-x[j],x[j]-up) for j,(lo,up) in enumerate(bounds)]+[abs(x[j]-round(x[j])) for j in range(3)])
            for row,sense,rhs in model.rows:
                delta=sum(v*x[int(name[1:])] for name,v in row.items())-rhs
                violation=max(violation,abs(delta) if sense=='E' else (delta if sense=='L' else -delta))
        passed=ours.get('status') in ('optimal','gap_limit') and h.getModelStatus()==highspy.HighsModelStatus.kOptimal and ours.get('objective') is not None and abs(ours['objective']-expected)/(1+abs(expected))<=1e-6 and violation<=1e-7
        record={**ours,'case':case,'passed':passed,'reference_objective':expected,'independent_violation':violation}
        (output/f'case{case:02d}.json').write_text(json.dumps(record,indent=2)+'\n');results.append({'case':case,'passed':passed,'status':ours.get('status')})
    (output/'summary.json').write_text(json.dumps(results,indent=2)+'\n');print('Mixed-integer/continuous regressions:',sum(r['passed'] for r in results),'/',len(results),flush=True)
    return results

if __name__=='__main__':main(Path(sys.argv[1]))
