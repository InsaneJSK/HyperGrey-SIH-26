"""Fresh min/max MPS cases checked by enumeration, HiGHS and rational algebra."""
import argparse
import itertools
import json
import math
from pathlib import Path
import random
from benchmark_lp import ROOT
from industrial_cases import MpsModel
from milp_robustness import timed,reference,classify
from check_objective_lattice import check
from validate_binary_proof import sha,save


def main(args):
    if not __debug__:raise RuntimeError('Assertions required')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve()
    rng=random.Random(26119120);records=[];events=0;derived=0
    for case in range(100):
        model=MpsModel('LATTICE_GENERATED');cost=[(1+case%5)*rng.randint(-7,7) for _ in range(4)]
        if not any(cost):cost[0]=5
        offset=(case%13-6)*.25;sign=-1 if case%2 else 1
        for j,c in enumerate(cost):model.var(f'x{j}',c,-2,2,True)
        definition=[rng.randint(-5,5) for _ in range(4)];unit=-1 if case%4<2 else 1;rhs=case%7-3
        recourse=case%3!=0
        if recourse:
            model.var('y',2 if case%4<2 else -3,None,None,False)
            model.row({**{f'x{j}':definition[j] for j in range(4)},'y':unit},'E',rhs)
        planted=[rng.randint(-2,2) for _ in range(4)]
        for i in range(3):
            a=[rng.randint(-4,4) for _ in range(4)];upper=sum(a[j]*planted[j] for j in range(4))+.5+rng.randint(0,2)
            model.row({f'x{j}':a[j] for j in range(4)},'L',upper)
        path=output/f'case{case:03d}.mps';model.write(path)
        source=path.read_text().replace('ROWS\n',f'OBJSENSE\n {"MAX" if sign==-1 else "MIN"}\nROWS\n',1)
        source=source.replace('RHS\n',f'RHS\n B OBJ {-offset:.17g}\n',1);path.write_text(source,encoding='utf-8')
        feasible=[]
        for point in itertools.product(range(-2,3),repeat=4):
            x={f'x{j}':point[j] for j in range(4)}
            if recourse:x['y']=(rhs-sum(definition[j]*point[j] for j in range(4)))/unit
            if all(abs(sum(a*x[n] for n,a in row.items())-b)<1e-9 if sense=='E' else sum(a*x[n] for n,a in row.items())<=b for row,sense,b in model.rows):
                feasible.append(sign*(offset+sum(v[0]*x[n] for n,v in model.vars.items())))
        assert feasible;expected=sign*min(feasible)
        command=[str(binary),str(path),'--milp','--json','--objective-lattice','--time-limit','5']
        if case%4==0:command+=['--no-presolve','--no-cuts','--no-heuristics']
        ours=timed(command,15,output/f'case{case:03d}');save(output/f'case{case:03d}.ours.json',ours)
        ref=reference(path,ours,5);save(output/f'case{case:03d}.reference.json',ref)
        audit=check(path,ours);save(output/f'case{case:03d}.lattice-check.json',audit)
        category,errors=classify(ours,ref,1e-6)
        assert not errors and category=='numerical_completion_checked',(case,category,errors)
        assert abs(ours['objective']-expected)<=1e-7 and abs(ref['objective']-expected)<=1e-7
        assert audit['eligible'],case
        events+=audit['events_checked'];derived+=bool(audit['substitutions_checked'])
        records.append({'case':case,'maximize':sign==-1,'derived':recourse,'expected':expected,'all_pass':True,
                        'events_checked':audit['events_checked'],'model_sha256':sha(path)})
    assert derived==66 and events>100
    save(output/'results.json',records)
    summary={'cases':len(records),'exhaustive_points_per_case':625,'independent_reference_completions':100,
             'derived_lattices':derived,'direct_lattices':100-derived,'rounding_events_checked':events,
             'all_pass':True,'binary_sha256':sha(binary),'runner_sha256':sha(Path(__file__))}
    save(output/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
