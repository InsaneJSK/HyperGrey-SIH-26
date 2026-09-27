"""Reproducible, sequential LP comparison. HiGHS is used only in a separate worker."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def parse_json_output(stdout):
    """Accept one JSON result amid native-library diagnostics; retain the noise."""
    try:
        result = json.loads(stdout)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    results, diagnostics = [], []
    for line in stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            diagnostics.append(line)
            continue
        if isinstance(item, dict) and 'status' in item:
            results.append(item)
        else:
            diagnostics.append(line)
    if len(results) != 1:
        raise ValueError('Expected exactly one JSON result')
    result = results[0]
    result['stdout_diagnostics'] = '\n'.join(diagnostics)
    return result

def reference_worker(model, candidate, limit, quadratic=False):
    sys.path.insert(0, str(ROOT / "tools/reference/python"))
    import highspy
    import numpy as np
    h = highspy.Highs()
    for key, value in {"output_flag": False, "threads": 1, "random_seed": 0,
                       "time_limit": limit, "primal_feasibility_tolerance": 1e-8,
                       "dual_feasibility_tolerance": 1e-8}.items():
        if h.setOptionValue(key, value) == highspy.HighsStatus.kError:
            raise RuntimeError(f"HiGHS rejected {key}")
    start = time.perf_counter()
    if h.readModel(str(model)) == highspy.HighsStatus.kError:
        raise RuntimeError("HiGHS could not read original MPS")
    h.run()
    total = time.perf_counter() - start
    lp, solution = h.getLp(), h.getSolution()
    result = {"version": h.version(), "status": h.modelStatusToString(h.getModelStatus()),
              "objective": h.getObjectiveValue() if solution.value_valid else None,
              "solve_seconds": h.getRunTime(), "total_seconds": total,
              "rows": lp.num_row_, "columns": lp.num_col_}
    # Check our ORIGINAL-variable solution against HiGHS' independent MPS reader.
    x = np.asarray(candidate.get("primal", []), dtype=float)
    if quadratic and len(x)==lp.num_col_:
        # The selected QPLIB LP exports use sequential x2..x(n+1) names.
        ordered=sorted(lp.col_names_,key=lambda name:int(name[1:]))
        if not all(name.startswith('x') and name[1:].isdigit() for name in ordered):
            raise RuntimeError("Unsupported reference variable names")
        ranks={name:i for i,name in enumerate(ordered)}
        x=np.asarray([x[ranks[name]] for name in lp.col_names_])
        result["candidate_mapping"]="QPLIB index mapped to ascending numeric x names in official LP export"
    names = candidate.get("variable_names")
    if names and len(names) == len(x):
        by_name = dict(zip(names, x))
        x = np.asarray([by_name[name] for name in lp.col_names_])
    if len(x) == lp.num_col_ and np.all(np.isfinite(x)):
        h.ensureColwise()
        lp = h.getLp()
        matrix = lp.a_matrix_
        activity, magnitude = np.zeros(lp.num_row_), np.zeros(lp.num_row_)
        for j in range(lp.num_col_):
            for k in range(matrix.start_[j], matrix.start_[j+1]):
                i, value = matrix.index_[k], matrix.value_[k] * x[j]
                activity[i] += value; magnitude[i] += abs(value)
        maximum, normalized = 0.0, 0.0
        for values, scales, lows, ups in [(x, np.abs(x), lp.col_lower_, lp.col_upper_),
                                          (activity, magnitude, lp.row_lower_, lp.row_upper_)]:
            for value, scale, lo, up in zip(values, scales, lows, ups):
                for bound, v in [(lo, lo-value), (up, value-up)]:
                    if math.isfinite(bound):
                        maximum = max(maximum, v)
                        normalized = max(normalized, v/(1+abs(bound)+scale))
        result.update(candidate_max_violation=maximum, candidate_scaled_violation=normalized,
                      candidate_recomputed_objective=float(np.dot(lp.col_cost_, x)+lp.offset_))
        if quadratic:
            hessian=h.getModel().hessian_
            qvalue=0.0
            for j in range(hessian.dim_):
                for k in range(hessian.start_[j],hessian.start_[j+1]):
                    i,v=hessian.index_[k],hessian.value_[k]
                    qvalue+=(0.5 if i==j else 1.0)*v*x[i]*x[j]
            result["candidate_recomputed_objective"]+=qvalue
        integer_violation = 0.0
        if len(lp.integrality_) == lp.num_col_:
            for j, kind in enumerate(lp.integrality_):
                if kind != highspy.HighsVarType.kContinuous:
                    integer_violation = max(integer_violation, abs(float(x[j])-round(float(x[j]))))
        result["candidate_integer_violation"] = integer_violation
    print(json.dumps(result, allow_nan=False))

def run(command, timeout):
    start = time.perf_counter()
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        elapsed = time.perf_counter()-start
        try:
            data = parse_json_output(process.stdout)
        except ValueError:
            data = {"status": "process_error", "stdout": process.stdout, "stderr": process.stderr}
        data["process_seconds"] = elapsed
        data["exit_code"] = process.returncode
        return data
    except subprocess.TimeoutExpired:
        return {"status": "external_timeout", "process_seconds": time.perf_counter()-start}

def benchmark(output, limit):
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((ROOT / "datasets/netlib/manifest.json").read_text())
    source_files = sorted(p for folder in ["src", "include", "scripts", "tests"]
                          for p in (ROOT/folder).rglob("*") if p.suffix in {".cpp", ".hpp", ".py", ".ps1"})
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    metadata = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "platform": platform.platform(), "processor": platform.processor(),
                "logical_processors": os.cpu_count(), "python": sys.version,
                "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
                "compiler_flags": "-std=c++11 -O2 -Wall -Wextra -pedantic",
                "source_sha256": hashes,
                "executable_sha256": hashlib.sha256((ROOT/"build/solver_cli.exe").read_bytes()).hexdigest(),
                "time_limit_seconds": limit, "external_timeout_seconds": limit+15,
                "threads": 1, "reference_presolve": "default/on", "ours_presolve": "none",
                "ours_tolerance": 1e-9, "validation_tolerance": 1e-8,
                "peak_memory": "not measured", "gpu": "unused", "dataset_manifest": manifest}
    (output/"metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    records = []
    for spec in manifest["instances"]:
        name = spec["name"]
        model = ROOT/"datasets/netlib"/(name+".mps")
        if hashlib.sha256(model.read_bytes()).hexdigest() != spec["mps_sha256"]:
            raise RuntimeError(f"Dataset hash mismatch: {name}")
        ours = run([str(ROOT/"build/solver_cli.exe"), str(model), "--json", "--time-limit", str(limit)], limit+15)
        candidate = output/(name+".ours.json")
        candidate.write_text(json.dumps(ours, indent=2)+"\n")
        ref = run([sys.executable, str(Path(__file__).resolve()), "--reference", str(model),
                   "--candidate", str(candidate), "--limit", str(limit)], limit+15)
        (output/(name+".reference.json")).write_text(json.dumps(ref, indent=2)+"\n")
        obj, expected = ours.get("objective"), ref.get("objective")
        error = abs(obj-expected)/(1+abs(expected)) if obj is not None and expected is not None else None
        published_error = abs(expected-spec["objective"])/(1+abs(spec["objective"])) if expected is not None else None
        recomputed = ref.get("candidate_recomputed_objective")
        objective_consistent = (obj is not None and recomputed is not None and
                                abs(obj-recomputed)/(1+abs(obj)) <= 1e-8)
        passed = (ours.get("status") == "optimal" and ours.get("optimality_verified") is True
                  and ref.get("status") == "Optimal" and error is not None and error <= 1e-7
                  and published_error is not None and published_error <= 1e-7
                  and ref.get("candidate_scaled_violation", math.inf) <= 1e-8 and objective_consistent
                  and ours.get("rows") == ref.get("rows") and ours.get("columns") == ref.get("columns"))
        record = {"name": name, "passed": passed, "ours_status": ours.get("status"),
                  "reference_status": ref.get("status"), "objective": obj, "reference_objective": expected,
                  "relative_objective_error": error, "published_relative_error": published_error,
                  "rows": ours.get("rows"), "columns": ours.get("columns"), "nonzeros": ours.get("nonzeros"),
                  "ours_seconds": ours.get("solve_seconds"), "reference_seconds": ref.get("solve_seconds"),
                  "ours_process_seconds": ours.get("process_seconds"),
                  "independent_scaled_violation": ref.get("candidate_scaled_violation"),
                  "iterations": ours.get("iterations")}
        records.append(record)
        print(name, record["ours_status"], "PASS" if passed else "FAIL", flush=True)
        (output/"results.json").write_text(json.dumps(records, indent=2)+"\n")
    lines = ["# Netlib LP benchmark results", "", f"Passed: {sum(r['passed'] for r in records)}/{len(records)}.", "",
             "Predeclared smoke/stress subset; no industrial-scale or speedup claim. All failures retained.", "",
             "| Instance | Rows | Cols | Our status | Objective | HiGHS objective | Result |",
             "| --- | ---: | ---: | --- | ---: | ---: | --- |"]
    for r in records:
        lines.append(f"| {r['name']} | {r['rows']} | {r['columns']} | {r['ours_status']} | {r['objective']} | {r['reference_objective']} | {'PASS' if r['passed'] else 'FAIL'} |")
    lines += ["", "See metadata.json for source/input hashes and settings; per-instance JSON contains solutions, residuals, timing, and errors.",
              "Our MinGW internal timer may report zero for short runs. Process times include startup; reference process startup also includes Python imports. Do not use these to claim a solver speedup.",
              "Reference checks independently parse original MPS and recompute our solution feasibility and objective. Our dual check uses the transformed canonical model.",
              "Infeasible/unbounded statuses are not independently certified by our core yet. Peak memory is not measured."]
    (output/"REPORT.md").write_text("\n".join(lines)+"\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=float, default=30)
    parser.add_argument("--quadratic", action="store_true")
    args = parser.parse_args()
    if args.reference:
        reference_worker(args.reference, json.loads(args.candidate.read_text()), args.limit,args.quadratic)
    elif args.output:
        benchmark(args.output, args.limit)
    else:
        parser.error("--output is required")
