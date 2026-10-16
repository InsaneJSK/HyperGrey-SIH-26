import json
from pathlib import Path
import subprocess
import sys
from benchmark_lp import ROOT
from milp_robustness import timed
from validate_binary_proof import sha,save
from validate_milp_frontier import semantic
from check_milp_work import check

out=ROOT/'reports/milp-iteration-14/preflight';out.mkdir(parents=True,exist_ok=False)
old=ROOT/'reports/milp-iteration-13/final_solver_cli.exe';new=ROOT/'build-milp-iter14-diag/solver_cli.exe';rows=[]
assert sha(old)=='bdfdb8fc7a21d411d47557f093e728e018e86960c359f86573393711b5b4757e'
for name in ('gt2','lseu','mod008','misc03'):
    signatures=[]
    for mode,binary,flags in [('old',old,[]),('off',new,[]),('on',new,['--capture-work'])]:
        key=name+'.'+mode
        cmd=[str(binary),str(ROOT/'datasets/milp-robustness-wave1'/(name+'.mps')),'--milp','--json',
             '--objective-lattice','--raw-lp-priority','--capture-frontier','--no-heuristics','--no-cuts',
             '--node-limit','512','--time-limit','120','--gap','0',*flags]
        r=timed(cmd,135,out/key);save(out/(key+'.json'),r);assert r['status']=='node_limit'
        if mode!='old':check(r)
        signatures.append(semantic(r))
    assert len(set(signatures))==1,name
    rows.append({'model':name,'semantic_identical':True})
p=subprocess.run([sys.executable,'-X','utf8','-m','unittest','test_milp_work_check','-v'],cwd=ROOT/'scripts',capture_output=True,text=True)
(out/'units.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0
save(out/'SUMMARY.json',{'all_pass':True,'comparisons':rows,'old_sha256':sha(old),'diagnostic_sha256':sha(new)})
print('Four fixed-node comparisons (old / capture-off / capture-on) and nine mutation tests PASS',flush=True)
