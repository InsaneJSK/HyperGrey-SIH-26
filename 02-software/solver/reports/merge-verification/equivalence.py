"""Fixed-work equivalence, done the way iteration 33 did it.

The recommended profile is nondeterministic run to run: its heuristics take a
wall-clock slice, so the same binary returns different incumbents and LP counts
on repeated runs. Comparing two binaries under it measures that variance, not
the change. --no-heuristics removes the time dependence and makes the run
reproducible, which is the only condition under which "did the merge change
anything" is a question with an answer.

Control: iteration 36's frozen source, rebuilt here.
Merged:  the same source plus the weak-pivot safeguard, its flag off.
Both built with the same compiler and the same command on this machine.
"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path('D:/sih-2026/SIH-backup-solver/SIH-backup-solver')
CONTROL = Path('C:/Users/Admin/AppData/Local/Temp/it36build/solver_cli.exe')
MERGED  = ROOT/'build-merge-verify/solver_cli.exe'
PROFILE = json.loads((ROOT/'reports/milp-iteration-37/CANDIDATE_PROFILE.json').read_text())['recommended_flags']
FIELDS = ('status','objective','best_bound','gap','nodes','cuts','unresolved_nodes',
          'lp_iterations','warm_starts','bound_tightenings')
def find(n):
    for f in sorted((ROOT/'datasets').iterdir()):
        if f.is_dir() and (f/(n+'.mps')).exists(): return f/(n+'.mps')
def run(b,m,extra=()):
    d=subprocess.run([str(b),str(m),'--json','--milp','--time-limit','900','--node-limit','2000',
                      '--gap','0','--no-heuristics',*PROFILE,*extra],capture_output=True,text=True,timeout=1200)
    try: r=json.loads(d.stdout)
    except ValueError: return {'status':f'process_error(exit {d.returncode})'}
    return {k:r.get(k) for k in FIELDS}
rows=[];bad=0
for n in sys.argv[1].split(','):
    m=find(n)
    if not m: continue
    c,g=run(CONTROL,m),run(MERGED,m)
    d=[k for k in FIELDS if c.get(k)!=g.get(k)]
    bad+=bool(d); rows.append({'model':n,'differs':d,'control':c,'merged':g})
    print(f'{n:<14}{str(c.get("status")):<22}nodes={str(c.get("nodes")):>6}  {"MISMATCH "+",".join(d) if d else "identical"}',flush=True)
probe=find('p0033')
on=run(MERGED,probe,('--stable-primal-ratio',))
off=run(MERGED,probe)
print(f'\n--stable-primal-ratio on the merged build: accepted={not str(on.get("status","")).startswith("process_error")}, '
      f'status={on.get("status")}, objective matches flag-off run: {on.get("objective")==off.get("objective")}')
(ROOT/'reports/merge-verification/EQUIVALENCE.json').write_text(json.dumps(
    {'method':'fixed node limit, --no-heuristics (the profile is nondeterministic without it)',
     'node_limit':2000,'compared':len(rows),'mismatches':bad,'rows':rows},indent=1))
print(f'\n{len(rows)} models compared deterministically, {bad} mismatches')
