"""Post-benchmark checks on the four preserved application models.

LP models deliberately use the MILP facade, with no integer declarations, to
exercise the main-tree reduction helper. This is not production validation.
"""
import argparse
import json
from pathlib import Path
import sys
from benchmark_lp import ROOT, run
from validate_binary_proof import sha, save

if not __debug__:
    raise RuntimeError('Checks require assertions')


def main(args):
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    binary=args.binary.resolve();records=[]
    manifest=ROOT/'examples/industrial/manifest.json'
    for spec in json.loads(manifest.read_text()):
        path=manifest.parent/(spec['name']+'.mps');assert sha(path)==spec['sha256']
        for mode in ('control','reduced'):
            command=[str(binary),str(path),'--milp','--json','--compact-equalities',
                     '--lp-recovery','--repair-candidates','--no-heuristics',
                     *(['--reduced-bound-lp'] if mode=='reduced' else []),
                     '--time-limit','30','--node-limit','250000','--gap','1e-6']
            result=run(command,45);key=spec['name']+'.'+mode
            candidate=output/(key+'.ours.json');save(candidate,result)
            records.append({'key':key,'name':spec['name'],'mode':mode,'model':str(path),
                            'model_sha256':sha(path),'command':command,'input_is_milp':spec['milp'],
                            'synthetic_data':spec['synthetic_data'],'status':result['status'],
                            'objective':result.get('objective'),'root_reduced_upper_bounds':result['root_reduced_upper_bounds']})
            save(output/'results.json',records)
    for record in records:
        candidate=output/(record['key']+'.ours.json');ours=json.loads(candidate.read_text())
        checked=run([sys.executable,str(ROOT/'scripts/benchmark_lp.py'),'--reference',record['model'],
                     '--candidate',str(candidate),'--limit','10'],25)
        save(output/(record['key']+'.reference.json'),checked)
        assert ours['status'] in ('optimal','gap_limit') and checked['status']=='Optimal',record
        assert checked['candidate_max_violation']<=1e-7 and checked['candidate_integer_violation']<=1e-7
        assert abs(ours['objective']-checked['objective'])<=1e-6*(1+abs(checked['objective']))
        assert abs(ours['objective']-checked['candidate_recomputed_objective'])<=1e-7*(1+abs(ours['objective']))
        record['passed']=True;record['reference_objective']=checked['objective'];record['violation']=checked['candidate_max_violation']
        record['result_sha256']=sha(candidate)
    for name in {r['name'] for r in records}:
        values=[r['objective'] for r in records if r['name']==name]
        assert abs(values[0]-values[1])<=1e-6*(1+abs(values[0]))
    # Tighter sulfur cannot improve the cost-minus-revenue objective.
    for mode in ('control','reduced'):
        objectives={r['name']:r['objective'] for r in records if r['mode']==mode}
        assert objectives['marco_low_sulfur']>=objectives['marco_refinery']-1e-7
    save(output/'results.json',records)
    summary={'all_pass':True,'models':4,'profile_checks':len(records),'binary_sha256':sha(binary),
             'manifest_sha256':sha(manifest),'script_sha256':sha(Path(__file__)),
             'root_removed_bound_rows':{r['key']:r['root_reduced_upper_bounds'] for r in records},
             'limitation':'Literature teaching and synthetic application models, not MRPL production data or domain-expert validation. LPs routed through MILP facade to exercise reduction; not a timing comparison.'}
    save(output/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args())
