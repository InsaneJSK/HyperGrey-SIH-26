"""Seeded LPs with independently constructed primal/dual certificates."""
import argparse
import json
import math
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main(output):
    output.mkdir(parents=True, exist_ok=False)
    rng = random.Random(26119)
    results = []
    for case in range(120):
        n, m = rng.randint(2, 10), rng.randint(2, 12)
        x = [rng.randint(0, 5) for _ in range(n)]
        a = [[rng.randint(-5, 5) for _ in range(n)] for _ in range(m)]
        y = [-rng.randint(0, 4) for _ in range(m)]
        slack = [rng.randint(0, 5) if v == 0 else 0 for v in y]
        b = [sum(v*z for v, z in zip(row, x))+s for row, s in zip(a, slack)]
        reduced = [rng.randint(0, 4) if v == 0 else 0 for v in x]
        c = [sum(a[i][j]*y[i] for i in range(m))+reduced[j] for j in range(n)]
        expected = sum(ci*xi for ci, xi in zip(c, x))
        assert expected == sum(bi*yi for bi, yi in zip(b, y))
        # Row multipliers change conditioning without changing the feasible set.
        multipliers = [10.0**rng.randint(-10, 10) if case >= 60 else 1.0 for _ in range(m)]
        aa = [[v*factor for v in row] for row, factor in zip(a, multipliers)]
        bb = [v*factor for v, factor in zip(b, multipliers)]
        path = output/f"case{case:03d}.lpmini"
        path.write_text(f"{n} {m}\n"+' '.join(map(str, c))+"\n"+
                        '\n'.join(' '.join(format(v, '.17g') for v in row+[rhs]) for row, rhs in zip(aa, bb))+"\n")
        (output/f"case{case:03d}.certificate.json").write_text(json.dumps({
            "known_primal": x, "known_dual": [v/f for v, f in zip(y, multipliers)], "objective": expected}, indent=2)+"\n")
        proc = subprocess.run([str(ROOT/"build/solver_cli.exe"), str(path), "--json"], capture_output=True, text=True, timeout=35)
        try: result = json.loads(proc.stdout)
        except json.JSONDecodeError: result = {"status": "process_error", "stderr": proc.stderr}
        actual = result.get("objective")
        passed = (result.get("status") == "optimal" and result.get("optimality_verified") is True
                  and actual is not None and abs(actual-expected)/(1+abs(expected)) <= 1e-8)
        primal, dual = result.get("primal", []), result.get("canonical_dual", [])
        # Independently check raw returned vectors, not just the solver's boolean.
        if len(primal) == n and len(dual) == m and all(math.isfinite(v) for v in primal+dual):
            pv = max([0]+[-v/(1+abs(v)) for v in primal])
            dv = max([0]+[v/(1+abs(v)) for v in dual])
            for row, rhs in zip(aa, bb):
                terms = [v*z for v, z in zip(row, primal)]
                pv = max(pv, (math.fsum(terms)-rhs)/(1+abs(rhs)+sum(map(abs, terms))))
            for j in range(n):
                terms = [aa[i][j]*dual[i] for i in range(m)]
                dv = max(dv, (math.fsum(terms)-c[j])/(1+abs(c[j])+sum(map(abs, terms))))
            primal_obj = math.fsum(ci*xi for ci, xi in zip(c, primal))
            dual_obj = math.fsum(bi*yi for bi, yi in zip(bb, dual))
            gap = abs(primal_obj-dual_obj)/(1+max(abs(primal_obj), abs(dual_obj)))
            passed = passed and max(pv, dv, gap) <= 1e-8
        else: passed = False
        result.update(case=case, expected_objective=expected, passed=passed, row_scaled=case >= 60)
        (output/f"case{case:03d}.result.json").write_text(json.dumps(result, indent=2)+"\n")
        results.append({k:result[k] for k in ["case", "status", "expected_objective", "passed", "row_scaled"]})
    (output/"summary.json").write_text(json.dumps(results, indent=2)+"\n")
    count = sum(r["passed"] for r in results)
    print(f"Generated primal/dual certificate tests: {count}/{len(results)} passed")
    return 0 if count == len(results) else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    sys.exit(main(parser.parse_args().output))
