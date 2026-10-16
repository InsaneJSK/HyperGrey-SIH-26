"""Planted KKT tests and original QPLIB/official LP-export comparison."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from benchmark_lp import ROOT, run

def write_qplib(path,h,c,a,b,lower,upper):
    n=len(c);m=len(a)
    entries=[(i,j,h[i][j]*(1 if i==j else 2)) for i in range(n) for j in range(i+1) if h[i][j]!=0]
    lines=["GENERATED","CCL" if m else "CCB","minimize",str(n)]
    if m: lines.append(str(m))
    lines += [str(len(entries))]+[f"{i+1} {j+1} {v:.17g}" for i,j,v in entries]
    def vector(values):
        return ["0",str(len(values))]+[f"{i+1} {v:.17g}" for i,v in enumerate(values)]
    lines += vector(c)+["0"]
    if m:
        entries=[(i,j,a[i][j]) for i in range(m) for j in range(n) if a[i][j]!=0]
        lines += [str(len(entries))]+[f"{i+1} {j+1} {v:.17g}" for i,j,v in entries]
    lines += ["1e20"]
    if m: lines += ["-1e20","0"]+vector(b)
    lines += vector(lower)+vector(upper)+["0","0"]
    if m: lines += ["0","0"]
    lines += ["0","0","0","0"]
    path.write_text('\n'.join(lines)+'\n')

def main(output, generated_only=False):
    output.mkdir(parents=True,exist_ok=False)
    rng=random.Random(26121); records=[]
    for case in range(30):
        n=5;m=3 if case>=15 else 0
        r=[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)]
        h=[[sum(r[k][i]*r[k][j] for k in range(n))+(1 if i==j else 0) for j in range(n)] for i in range(n)]
        optimum=[rng.uniform(-1,1) for _ in range(n)]
        a=[[rng.uniform(-1,1) for _ in range(n)] for _ in range(m)]
        y=[rng.uniform(.2,2) for _ in range(m)]
        b=[sum(v*x for v,x in zip(row,optimum)) for row in a]
        c=[-sum(h[i][j]*optimum[j] for j in range(n))-sum(a[k][i]*y[k] for k in range(m)) for i in range(n)]
        expected=sum(c[i]*optimum[i]+.5*sum(h[i][j]*optimum[i]*optimum[j] for j in range(n)) for i in range(n))
        model=output/f"case{case:02d}.qplib";write_qplib(model,h,c,a,b,[-3]*n,[3]*n)
        ours=run([str(ROOT/"build/solver_cli.exe"),str(model),"--json","--time-limit","5"],10)
        value=ours.get("objective");x=ours.get("primal",[]);dual=ours.get("row_dual",[])
        passed=ours.get("status")=="optimal" and value is not None and abs(value-expected)/(1+abs(expected))<=1e-6
        if len(x)==n and len(dual)==m:
            gradient=[sum(h[i][j]*x[j] for j in range(n))+c[i]+sum(a[k][i]*dual[k] for k in range(m)) for i in range(n)]
            residual=max(abs(xi-max(-3,min(3,xi-gi)))/(1+abs(xi)) for xi,gi in zip(x,gradient))
            passed=passed and residual<=2e-7 and all(-3<=xi<=3 for xi in x)
            passed=passed and all(sum(v*xi for v,xi in zip(row,x))<=bi+1e-6 for row,bi in zip(a,b))
        else:passed=False
        (output/f"case{case:02d}.result.json").write_text(json.dumps({**ours,"expected_objective":expected,"passed":passed},indent=2)+'\n')
        records.append({"case":case,"passed":passed,"status":ours.get("status")})
    (output/"generated.json").write_text(json.dumps(records,indent=2)+'\n')
    print("Planted QP KKT tests:",sum(r["passed"] for r in records),"/",len(records),flush=True)
    if generated_only:return
    manifest=json.loads((ROOT/"datasets/qplib/manifest.json").read_text());benchmarks=[]
    (output/"metadata.json").write_text(json.dumps({"manifest":manifest,"time_limit_seconds":15,
        "iteration_limit":200000,"kkt_tolerance":1e-7,"threads":1,"starting_point":"zero projected to variable bounds; supplied solution/start ignored",
        "source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for folder in ["src","include","scripts"] for p in (ROOT/folder).glob('*') if p.is_file()}},indent=2)+'\n')
    for spec in manifest["instances"]:
        name=spec["name"];model=ROOT/"datasets/qplib"/(name+".qplib")
        reference_model=ROOT/"datasets/qplib"/(name+".lp")
        if hashlib.sha256(model.read_bytes()).hexdigest()!=spec["model_sha256"]:raise RuntimeError("Input hash mismatch")
        if hashlib.sha256(reference_model.read_bytes()).hexdigest()!=spec["reference_sha256"]:raise RuntimeError("Reference input hash mismatch")
        ours=run([str(ROOT/"build/solver_cli.exe"),str(model),"--json","--time-limit","15"],25)
        candidate=output/(name+".ours.json");candidate.write_text(json.dumps(ours,indent=2)+'\n')
        ref=run([sys.executable,str(ROOT/"scripts/reference_qp.py"),"--reference",str(reference_model),"--candidate",str(candidate),"--limit","15"],30)
        (output/(name+".reference.json")).write_text(json.dumps(ref,indent=2)+'\n')
        value,expected,recomputed=ours.get("objective"),ref.get("objective"),ref.get("candidate_recomputed_objective")
        error=abs(value-expected)/(1+abs(expected)) if value is not None and expected is not None else None
        passed=(ours.get("status")=="optimal" and ref.get("status")=="Optimal" and error is not None and error<=1e-6
                and ref.get("candidate_scaled_violation",math.inf)<=1e-7 and recomputed is not None
                and abs(value-recomputed)/(1+abs(value))<=1e-7)
        benchmarks.append({"name":name,"passed":passed,"ours":ours.get("status"),"reference":ref.get("status"),
                           "objective":value,"reference_objective":expected,"relative_error":error,
                           "rows":ours.get("rows"),"columns":ours.get("columns"),"iterations":ours.get("iterations")})
        print(name,ours.get("status"),"PASS" if passed else "FAIL",flush=True)
        (output/"results.json").write_text(json.dumps(benchmarks,indent=2)+'\n')

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True)
    main(parser.parse_args().output)
