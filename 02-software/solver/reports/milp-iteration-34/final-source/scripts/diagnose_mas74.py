"""Frozen15 mas74 ablations and cold replay, separate from candidate timings."""
import json
from pathlib import Path
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
from milp_robustness import timed
from validate_milp_frontier import verify
from check_milp_work import check as work_check
from inspect_lp_failure import export_model

def main():
    out=ROOT/'reports/milp-iteration-16/mas74-diagnosis';out.mkdir(parents=True,exist_ok=False)
    old=ROOT/'reports/milp-iteration-15';binary=old/'final_solver_cli.exe';digest=sha(binary)
    assert digest=='57ce59edcc13d7717e0a8fd3f964dd8960d79cb86f9acb0dde9ee7d78003d159'
    plan_path=out.parent/'MAS74.json';plan=json.loads(plan_path.read_text());model=ROOT/'datasets/milp-cut-policy-holdout/mas74.mps'
    original=old/'holdout-30s/mas74.baseline.0.ours.json';source=json.loads(original.read_text())
    save(out/'metadata.json',{'binary':str(binary),'binary_sha256':digest,'binary_source_manifest':str(old/'SNAPSHOT_MANIFEST.json'),
        'binary_source_manifest_sha256':sha(old/'SNAPSHOT_MANIFEST.json'),'plan':plan,'plan_sha256':sha(plan_path),
        'model_sha256':sha(model),'saved_original_sha256':sha(original),'runner_sha256':sha(Path(__file__)),
        'scope':'Frozen15 diagnostic ablations. Cold replay does not reproduce the saved warm pivot sequence. No engine fix in this experiment.'})
    records=[]
    for label,extra in plan['profiles'].items():
        cmd=[str(binary),str(model),'--milp','--json',*plan['common'],*extra,'--time-limit','30','--node-limit','250000','--gap','1e-6']
        r=timed(cmd,45,out/label);save(out/(label+'.ours.json'),r)
        entry={'profile':label,'command':cmd,'ours_sha256':sha(out/(label+'.ours.json')),
            **{k:r.get(k) for k in ('status','objective','gap','nodes','total_seconds','lp_recovery_attempts','lp_recovery_successes',
                'lp_recovery_seconds','cut_restarts','cut_restart_seconds','cut_restart_nodes','deferred_nodes','unresolved_nodes')}}
        records.append(entry);save(out/'results.json',records);print(label,entry,flush=True)
    for row in records:
        label=row['profile'];r=json.loads((out/(label+'.ours.json')).read_text())
        ref=timed([sys.executable,'-X','utf8',str(ROOT/'scripts/milp_robustness.py'),'--reference',str(model),
            '--candidate',str(out/(label+'.ours.json')),'--reference-limit','5'],150,out/(label+'.reference'))
        save(out/(label+'.reference.json'),ref);category,errors,checks=verify(model,r,ref,out,label,1e-6);work_check(r)
        row.update(category=category,errors=errors,reference_sha256=sha(out/(label+'.reference.json')),
                   frontier_truncated=r['frontier']['event_count']>len(r['frontier']['trace']))
        save(out/'results.json',records);assert not errors,(label,errors)
    # Reuse the original captured node, including its unchanged domain. Exporter
    # normalizes objective sense/offset; it does NOT recreate a warm-start basis.
    capture=source['first_lp_failure'];assert capture['captured'];relaxation=out/'captured-relaxation.mps';offset=export_model(capture,relaxation)
    cold=[]
    for method in ('sparse','dense'):
        cmd=[str(binary),str(relaxation),'--json','--lp-method',method,'--time-limit','5','--iteration-limit','10000']
        r=timed(cmd,20,out/('cold-'+method));save(out/('cold-'+method+'.json'),r)
        ref=timed([sys.executable,'-X','utf8',str(ROOT/'scripts/milp_robustness.py'),'--reference',str(relaxation),
            '--candidate',str(out/('cold-'+method+'.json')),'--reference-limit','5'],150,out/('cold-'+method+'.reference'))
        save(out/('cold-'+method+'.reference.json'),ref)
        cold.append({'method':method,'command':cmd,'status':r['status'],'message':r.get('message'),'iterations':r.get('iterations'),
            'objective':r.get('objective'),'reference_status':ref['status'],'reference_objective':ref.get('objective'),
            'candidate_checked':ref.get('candidate_checked'),'candidate_violation':ref.get('candidate_max_violation'),
            'ours_sha256':sha(out/('cold-'+method+'.json')),'reference_sha256':sha(out/('cold-'+method+'.reference.json'))})
    save(out/'cold-replay.json',{'captured_node':capture['node'],'captured_depth':capture['depth'],'captured_status':capture['status'],
        'captured_iterations':capture['iterations'],'minimization_offset_omitted':offset,'model_sha256':sha(relaxation),'runs':cold})
    assert sha(binary)==digest
    save(out/'SUMMARY.json',{'all_public_output_checks_pass':True,'diagnostic_runs':len(records),'cold_replays':len(cold),
        'binary_sha256':digest,'runner_sha256':sha(Path(__file__)),'results_sha256':sha(out/'results.json'),
        'cold_replay_sha256':sha(out/'cold-replay.json'),'no_core_recovery_change':True})
    print('mas74 diagnosis complete',flush=True)

if __name__=='__main__':main()
