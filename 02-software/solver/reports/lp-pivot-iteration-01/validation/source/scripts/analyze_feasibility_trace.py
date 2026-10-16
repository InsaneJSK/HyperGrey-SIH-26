"""Audit and summarize a saved diagnostic batch without new solver runs."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from benchmark_lp import ROOT
from check_feasibility_trace import check
from validate_binary_proof import sha,save

def main(a):
    summaries=[]
    for row in json.loads((a.run/'results.json').read_text()):
        r=json.loads((a.run/(row['key']+'.ours.json')).read_text());c=check(ROOT/row['model'],r)
        save(a.run/(row['key']+'.feasibility-check.json'),c)
        calls=defaultdict(list)
        for e in r['feasibility']['samples']:calls[e['call']].append(e)
        pumps=[];dives=[]
        for call,es in calls.items():
            if es[0]['kind']=='pump_start':
                ps=[e for e in es if e['kind']=='pump_projection' and e['status']=='optimal' and e['distance'] is not None]
                pumps.append({'call':call,'root_distance':es[0]['distance'],'root_fractional':es[0]['fractional'],
                    'best_distance':min((e['distance'] for e in ps),default=None),
                    'best_fractional':min((e['fractional'] for e in ps),default=None),
                    'round_repeats':sum(e['kind']=='pump_round' and e['status']=='repeat' for e in es),
                    'target_repeats':sum(e['kind']=='pump_target' and e['status']=='repeat' for e in es),
                    'propagation_rejections':sum(e['kind']=='pump_propagation' and e['status']=='rejected' for e in es),
                    'projection_statuses':[e['status'] for e in es if e['kind']=='pump_projection']})
            else:
                dives.append({'call':call,'start_distance':es[0]['distance'],'start_fractional':es[0]['fractional'],
                    'last_kind':es[-1]['kind'],'last_status':es[-1]['status'],'last_step':es[-1]['step'],
                    'last_distance':es[-1]['distance']})
        summaries.append({'key':row['key'],'status':r['status'],'objective':r.get('objective'),'pumps':pumps,'dives':dives,
            'check':c,'model_sha256':sha(ROOT/row['model']),'result_sha256':sha(a.run/(row['key']+'.ours.json'))})
    save(a.run/'FEASIBILITY_DIAGNOSIS.json',{'all_pass':True,'runner_sha256':sha(Path(__file__)),
        'checker_sha256':sha(Path(__file__).with_name('check_feasibility_trace.py')),'runs':summaries})
    for s in summaries:print(json.dumps({k:v for k,v in s.items() if k not in ('check','model_sha256','result_sha256','dives')}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);main(p.parse_args())
