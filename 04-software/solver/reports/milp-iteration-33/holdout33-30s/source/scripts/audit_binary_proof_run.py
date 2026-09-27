"""Check saved run identities, budgets, exact-verifier links and aggregates."""
import argparse
import hashlib
import json
from pathlib import Path
from benchmark_lp import ROOT
from exact_binary_check import parse_mps,check

if not __debug__:raise RuntimeError('Audit requires assertions')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

def main(args):
    source=args.results.resolve();meta=read(source/'metadata.json');summary=read(source/'summary.json');records=read(source/'results.json')
    assert sha(args.binary)==meta['binary_sha256'] and sha(ROOT/'CMakeLists.txt')==meta['cmake_sha256']
    for name,digest in meta['source_sha256'].items():assert sha(ROOT/name)==digest,name
    assert sha(source/'CMakeCache.txt')==meta['cmake_cache_sha256']
    assert 'SOVEREIGN_ENABLE_CUDA:BOOL=OFF' in (source/'CMakeCache.txt').read_text()
    assert '100% tests passed' in (source/'ctest.log').read_text()
    assert summary['all_pass'] and summary['timed_runs_complete'] and len(records)==12
    assert len({r['key'] for r in records})==12
    for profile in meta['profiles']:
        for kind,name in [('binary','enumeration.json'),('mixed','summary.json')]:
            entries=read(source/(profile+'-'+kind)/name);assert len(entries)==40 and all(x['passed'] for x in entries)
            assert summary['generated'][profile+'-'+kind]==40
    generated=0
    for path in sorted((source/'binary_proof-binary').glob('*.result.json')):
        model=path.with_name(path.name.replace('.result.json','.mps'));assert check(parse_mps(model.read_text()),read(path))['all_checks_pass'];generated+=1
    assert generated==40
    manifests={}
    for folder in ('miplib','miplib2017'):
        for spec in read(ROOT/'datasets'/folder/'manifest.json')['instances']:manifests[spec['name']]=spec.get('mps_sha256',spec.get('model_sha256'))
    exact=0;hashes={}
    for record in records:
        model=Path(record['model']);key=record['key'];path=source/(key+'.ours.json');ours=read(path);hashes[path.name]=sha(path)
        assert sha(model)==record['model_sha256']==manifests[model.stem]
        assert sha(Path(record['command'][0]))==meta['binary_sha256']
        command=record['command'];assert command[1]==str(model)
        assert command[2:]==['--milp','--json',*meta['profiles'][record['profile']],'--time-limit','30','--node-limit','250000','--gap','1e-6']
        for field in ('status','objective','best_bound','gap','nodes','total_seconds'):assert record[field]==ours[field]
        reference=read(source/(key+'.reference.json'))
        assert reference['candidate_max_violation']<=1e-7 and reference['candidate_integer_violation']<=1e-7
        assert abs(reference['candidate_recomputed_objective']-ours['objective'])<=1e-7*(1+abs(ours['objective']))
        if record['profile']=='binary_proof':
            assert ours['binary_proof']['verified'] and ours['status']=='optimal' and ours['objective']==ours['best_bound'] and ours['gap']==0
            evidence=read(source/(key+'.exact.json'));assert evidence['all_checks_pass'] and evidence['literal_integer_model_verified']
            assert evidence['result_sha256']==sha(path) and evidence['model_sha256']==sha(model)
            assert evidence['checker_sha256']==sha(ROOT/'scripts/exact_binary_check.py');exact+=1
        else:assert not ours['binary_proof_enabled'] and not ours['binary_proof']['verified']
    for model in ('markshare_4_0','p0033'):
        for profile in ('binary_meet','binary_proof'):
            assert sorted(r['repeat'] for r in records if Path(r['model']).stem==model and r['profile']==profile)==[0,1,2]
    assert exact==summary['independent_exact_public_checks']==6
    result={'all_pass':True,'binary_sha256':meta['binary_sha256'],'identity_files_checked':len(meta['source_sha256']),
            'public_runs':12,'linked_independent_exact_checks':6,'replayed_generated_exact_checks':40,'raw_sha256':hashes,
            'audit_script_sha256':sha(Path(__file__)),'limitation':'Replays generated proofs and verifies provenance links for already completed public independent checks; no new timed comparison.'}
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('results',type=Path);parser.add_argument('--binary',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args())
