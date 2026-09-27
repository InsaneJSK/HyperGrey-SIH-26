"""Same binary, same model, same flags, three times. Any difference here means
the comparison methodology -- not the merge -- produced the earlier drift."""
import json, subprocess
from pathlib import Path
ROOT = Path('D:/sih-2026/SIH-backup-solver/SIH-backup-solver')
FROZEN = ROOT/'reports/milp-iteration-36/final_solver_cli.exe'
PROFILE = json.loads((ROOT/'reports/milp-iteration-37/CANDIDATE_PROFILE.json').read_text())['recommended_flags']
def find(n):
    for f in sorted((ROOT/'datasets').iterdir()):
        if f.is_dir() and (f/(n+'.mps')).exists(): return f/(n+'.mps')
for extra,label in ((( ),'recommended profile'),(('--no-heuristics',),'profile + --no-heuristics')):
    print(f'--- {label} ---')
    for name in ('gen-ip002','mas74','misc03'):
        m=find(name); seen=[]
        for _ in range(3):
            d=subprocess.run([str(FROZEN),str(m),'--json','--milp','--time-limit','900',
                              '--node-limit','2000','--gap','0',*PROFILE,*extra],
                             capture_output=True,text=True,timeout=1200)
            r=json.loads(d.stdout)
            seen.append((r['objective'],r['lp_iterations'],r['bound_tightenings']))
        same = len(set(seen))==1
        print(f'  {name:<12}{"DETERMINISTIC" if same else "VARIES BETWEEN RUNS"}')
        if not same:
            for s in seen: print(f'      obj={s[0]!r:>22} lp_iters={s[1]} tightenings={s[2]}')
