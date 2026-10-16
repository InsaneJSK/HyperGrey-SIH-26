"""Post-timing regression gate for iteration12. All output paths must be fresh."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from benchmark_lp import ROOT
from validate_binary_proof import sha,save
import test_milp
import test_mixed_v2


def main(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);binary=args.binary.resolve()
    commands={
        'ctest':['ctest','--test-dir',str(binary.parent),'--output-on-failure'],
        'python-checkers':[sys.executable,'-X','utf8','-m','unittest','test_milp_robustness','test_exact_binary_check',
                           'test_result_parser','test_milp_diagnostics','test_lifted_cover_check','test_objective_lattice_check','-v'],
        'marker-contract':[sys.executable,'-X','utf8',str(ROOT/'scripts/check_mps_marker_contract.py'),
                           '--binary',str(binary),'--output',str(out/'marker-contract'),'--require-pass']}
    for name,command in commands.items():
        result=subprocess.run(command,cwd=ROOT/'scripts' if name=='python-checkers' else ROOT,text=True,capture_output=True)
        (out/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        assert result.returncode==0,(name,result.stdout,result.stderr)
        print(name,'PASS',flush=True)
    generated={}
    for profile,flags in [('control',[]),('lattice',['--objective-lattice'])]:
        test_milp.main(out/(profile+'-binary'),True,binary,flags)
        test_mixed_v2.main(out/(profile+'-mixed'),binary,flags)
        for kind,file in [('binary','enumeration.json'),('mixed','summary.json')]:
            records=json.loads((out/(profile+'-'+kind)/file).read_text());assert len(records)==40 and all(r['passed'] for r in records)
            generated[profile+'-'+kind]=len(records)
    summary={'all_pass':True,'commands':commands,'generated':generated,'binary_sha256':sha(binary),
             'runner_sha256':sha(Path(__file__)),'note':'Post-timing regression work; generated checks are not performance measurements.'}
    save(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
