"""Small original-model MPS domain tests against the independent HiGHS reader."""
import argparse
import json
from pathlib import Path
import sys
from benchmark_lp import ROOT, run
from validate_binary_proof import sha, save

BOUNDS = {'absent': '', 'unrelated': ' UP B Y 2\n', 'lower_zero': ' LO B X 0\n',
          'lower_two': ' LO B X 2\n', 'upper_four': ' UP B X 4\n', 'upper_zero': ' UP B X 0\n',
          'fixed_two': ' FX B X 2\n', 'free': ' FR B X\n', 'minus_infinity': ' MI B X\n',
          'plus_infinity': ' PL B X\n', 'binary': ' BV B X\n', 'integer_upper': ' UI B X 4\n',
          'integer_lower': ' LI B X 2\n', 'lower_and_upper': ' LO B X 2\n UP B X 4\n'}


def model(bounds, maximize):
    return ('NAME MARKER_CONTRACT\nOBJSENSE\n '+('MAX' if maximize else 'MIN')+
            '\nROWS\n N OBJ\n L CAP\n G FLOOR\nCOLUMNS\n M0 \'MARKER\' \'INTORG\'\n'+
            ' X OBJ '+('1' if maximize else '-1')+' CAP 1\n X FLOOR 1\n'+
            ' M1 \'MARKER\' \'INTEND\'\n Y OBJ 0\nRHS\n B CAP 7 FLOOR -4\n'+
            ('BOUNDS\n'+bounds if bounds else '')+'ENDATA\n')


def main(args):
    sys.path.insert(0, str(ROOT/'tools/reference/python')); import highspy
    output=args.output.resolve(); output.mkdir(parents=True,exist_ok=False); records=[]
    for name,bounds in BOUNDS.items():
        for maximize in (False,True):
            key=name+('.max' if maximize else '.min'); path=output/(key+'.mps')
            path.write_text(model(bounds,maximize),encoding='utf-8')
            ours=run([str(args.binary.resolve()),str(path),'--milp','--json','--time-limit','2','--binary-proof'],5)
            save(output/(key+'.ours.json'),ours)
            h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1)
            h.readModel(str(path));h.run();lp=h.getLp();expected=h.getObjectiveValue()
            point=ours.get('primal',[]); valid=len(point)==2
            if valid:
                valid=all(lo-1e-7<=x<=up+1e-7 for x,lo,up in zip(point,lp.col_lower_,lp.col_upper_)) and -4-1e-7<=point[0]<=7+1e-7 and abs(point[0]-round(point[0]))<=1e-7
            passed=valid and ours.get('status') in ('optimal','gap_limit') and h.getModelStatus()==highspy.HighsModelStatus.kOptimal and abs(ours['objective']-expected)<=1e-7
            norm=lambda x: x if abs(x)<float('inf') else ('-inf' if x<0 else '+inf')
            record={'key':key,'passed':bool(passed),'ours_status':ours['status'],'objective':ours.get('objective'),
                    'reference_objective':expected,'reference_lower':[norm(v) for v in lp.col_lower_],
                    'reference_upper':[norm(v) for v in lp.col_upper_],'model_sha256':sha(path)}
            records.append(record);save(output/'results.json',records)
    summary={'all_pass':all(r['passed'] for r in records),'passed':sum(r['passed'] for r in records),
             'cases':len(records),'binary_sha256':sha(args.binary),'script_sha256':sha(Path(__file__)),
             'reference_version':h.version()}
    save(output/'SUMMARY.json',summary);print(json.dumps({'summary':summary,'cases':records},indent=2),flush=True)
    if args.require_pass and not summary['all_pass']: raise AssertionError('MPS domain contract failure')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--require-pass',action='store_true');main(p.parse_args())
