"""Verify cached sparse-array extraction against the frozen iteration13 reader."""
import importlib.util
import json
from pathlib import Path
import time
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from check_objective_lattice import read

out=ROOT/'reports/milp-iteration-14/reader-equivalence';out.mkdir(parents=True,exist_ok=False)
path=ROOT/'reports/milp-iteration-13/final-source/scripts/check_objective_lattice.py'
manifest=json.loads((ROOT/'reports/milp-iteration-13/SNAPSHOT_MANIFEST.json').read_text())
assert sha(path)==manifest['scripts/check_objective_lattice.py']
spec=importlib.util.spec_from_file_location('frozen_lattice_reader',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
models=[]
for f in ('datasets/milp-robustness-wave1/manifest.json','datasets/milp-frontier-holdout/manifest.json'):
    models+=json.loads((ROOT/f).read_text())['instances']
rows=[]
for s in models:
    model=ROOT/s['model'];assert sha(model)==s['model_sha256']
    t=time.perf_counter();before=old.read(model);old_seconds=time.perf_counter()-t
    t=time.perf_counter();after=read(model);new_seconds=time.perf_counter()-t
    assert before==after,s['name']
    rows.append({'model':s['name'],'identical':True,'old_seconds':old_seconds,'new_seconds':new_seconds,'model_sha256':sha(model)})
    save(out/'results.json',rows);print(s['name'],'identical',flush=True)
save(out/'SUMMARY.json',{'all_pass':True,'models':len(rows),'old_reader_sha256':sha(path),
     'new_reader_sha256':sha(ROOT/'scripts/check_objective_lattice.py'),'note':'Reader timing is NOT optimization-solver timing.'})
