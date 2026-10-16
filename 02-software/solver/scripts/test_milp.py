"""MILP enumeration tests and historical MIPLIB smoke benchmarks."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys
from benchmark_lp import ROOT, run

def main(output, generated_only=False, binary=None, flags=None):
    output.mkdir(parents=True, exist_ok=False)
    rng = random.Random(26120)
    records = []
    for case in range(40):
        n = 7
        costs = [rng.randint(-8, 8) for _ in range(n)]
        rows = [[rng.randint(-3, 6) for _ in range(n)] for _ in range(3)]
        rhs = [rng.randint(-2, 12) for _ in rows]
        feasible = [(sum(c*x for c, x in zip(costs, point)), point) for point in itertools.product([0, 1], repeat=n)
                    if all(sum(a*x for a, x in zip(row, point)) <= b for row, b in zip(rows, rhs))]
        expected = min(feasible)[0] if feasible else None
        lines = ["NAME ENUM", "ROWS", " N OBJ"]+[f" L R{i}" for i in range(3)]+["COLUMNS"]
        for j in range(n):
            lines.append(f" X{j} OBJ {costs[j]}")
            lines.extend(f" X{j} R{i} {rows[i][j]}" for i in range(3))
        lines += ["RHS"]+[f" B R{i} {rhs[i]}" for i in range(3)]+["BOUNDS"]+[f" BV B X{j}" for j in range(n)]+["ENDATA"]
        model = output/f"enum{case:02d}.mps"; model.write_text('\n'.join(lines)+'\n')
        result = run([str(binary or ROOT/"build/solver_cli.exe"), str(model), "--milp", "--json", "--time-limit", "5", *(flags or [])], 10)
        value = result.get("objective")
        passed = result.get("status") == "infeasible" if expected is None else (
            result.get("status") in ["optimal", "gap_limit"] and value is not None and abs(value-expected) < 1e-7)
        if expected is not None:
            point = result.get("primal", [])
            passed = passed and len(point) == n and all(abs(x-round(x)) <= 1e-7 and 0 <= x <= 1 for x in point)
            passed = passed and all(sum(a*x for a, x in zip(row, point)) <= b+1e-7 for row, b in zip(rows, rhs))
        (output/f"enum{case:02d}.result.json").write_text(json.dumps({**result, "expected": expected, "passed": passed}, indent=2)+'\n')
        records.append({"case": case, "passed": passed, "status": result.get("status")})
    (output/"enumeration.json").write_text(json.dumps(records, indent=2)+'\n')
    print("Enumeration:", sum(r["passed"] for r in records), "/", len(records), flush=True)
    if generated_only:return
    manifest = json.loads((ROOT/"datasets/miplib/manifest.json").read_text())
    (output/"metadata.json").write_text(json.dumps({"manifest":manifest,"time_limit_seconds":15,
        "node_limit":10000,"relative_gap":1e-6,"threads":1,"source_sha256":{
            str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ["src","include","scripts"] for p in (ROOT/folder).glob('*') if p.is_file()}}, indent=2)+'\n')
    benchmarks=[]
    for spec in manifest["instances"]:
        name=spec["name"]; model=ROOT/"datasets/miplib"/(name+".mps")
        if hashlib.sha256(model.read_bytes()).hexdigest()!=spec["model_sha256"]: raise RuntimeError("Input hash changed")
        ours=run([str(ROOT/"build/solver_cli.exe"),str(model),"--milp","--json","--time-limit","15"],25)
        candidate=output/(name+".ours.json"); candidate.write_text(json.dumps(ours,indent=2)+'\n')
        ref=run([sys.executable,str(ROOT/"scripts/benchmark_lp.py"),"--reference",str(model),"--candidate",str(candidate),"--limit","15"],30)
        (output/(name+".reference.json")).write_text(json.dumps(ref,indent=2)+'\n')
        value,expected=ours.get("objective"),ref.get("objective")
        error=abs(value-expected)/(1+abs(expected)) if value is not None and expected is not None else None
        passed=(ours.get("status") in ["optimal","gap_limit"] and ref.get("status")=="Optimal"
                and error is not None and error<=1e-6 and ref.get("candidate_scaled_violation",math.inf)<=1e-8
                and ref.get("candidate_integer_violation",math.inf)<=1e-7)
        benchmarks.append({"name":name,"passed":passed,"ours":ours.get("status"),"reference":ref.get("status"),
                           "objective":value,"reference_objective":expected,"nodes":ours.get("nodes"),"gap":ours.get("gap")})
        print(name,ours.get("status"),"PASS" if passed else "FAIL",flush=True)
        (output/"results.json").write_text(json.dumps(benchmarks,indent=2)+'\n')

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True)
    main(parser.parse_args().output)
