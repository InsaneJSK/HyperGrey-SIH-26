"""Retain exact development fixtures and predeclare iteration17 comparisons."""
import json
import shutil
from benchmark_lp import ROOT
from validate_binary_proof import sha,save

def main():
    out=ROOT/'reports/milp-iteration-17'
    fixture=ROOT/'reports/milp-iteration-16/mas74-diagnosis/captured-relaxation.mps'
    assert sha(fixture)=='3de0d967366662e95d8918c68b5cca7b077459d386c9cdb27525faa1a1e81339'
    target=ROOT/'tests/sparse_accuracy_fixture.mps';assert not target.exists();shutil.copy2(fixture,target)
    source=ROOT/'reports/milp-iteration-15/holdout-30s/mas74.baseline.0.ours.json'
    f=json.loads(source.read_text())['first_lp_failure'];assert f['captured']
    assert not f['basis_compact_equalities'] and not f['basis_reduced_upper_bounds']
    basis=ROOT/'tests/sparse_accuracy_basis.txt';assert not basis.exists()
    basis.write_text(str(f['basis_structural_columns'])+' '+str(len(f['input_basis_columns']))+'\n'+' '.join(map(str,f['input_basis_columns']))+'\n')
    save(out/'fixture-provenance.json',{'source':str(source),'source_sha256':sha(source),
        'model_sha256':sha(target),'basis_sha256':sha(basis),'source_node':f['node'],'source_depth':f['depth'],
        'source_iterations':f['iterations'],'ordinary_replay_iteration_limit':10000,
        'offset_omitted':f['offset'],'objective_normalized_to_minimization':True})
    plan=json.loads((ROOT/'reports/milp-iteration-16/WAVE.json').read_text())
    plan['profiles']={'baseline':[],'refined':['--refine-basis']}
    save(out/'WAVE.json',plan)
    plan['models']=['mas74'];plan['repeats']=2
    save(out/'SCREEN.json',plan)

if __name__=='__main__':main()
