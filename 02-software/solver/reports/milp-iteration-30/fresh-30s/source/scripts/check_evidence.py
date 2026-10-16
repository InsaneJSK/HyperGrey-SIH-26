"""Check final core/source correspondence and report counts without rerunning solvers."""
import hashlib
import importlib.metadata
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'reports/v1-2026-09-14'
metadata=json.loads((folder/'netlib/metadata.json').read_text())
checked=0
for name,expected in metadata['source_sha256'].items():
    path=ROOT/name
    if path.suffix in {'.cpp','.hpp'}:
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,f'Core changed since final validation: {name}'
        checked+=1
assert hashlib.sha256((ROOT/'build/solver_cli.exe').read_bytes()).hexdigest()==metadata['executable_sha256']
counts={}
for label,file in [('generated_lp','generated-lp/summary.json'),('netlib','netlib/results.json'),
                   ('generated_milp','milp/enumeration.json'),('miplib','milp/results.json'),
                   ('generated_qp','qp-corrected-reference/generated.json'),('qplib','qp-corrected-reference/results.json')]:
    records=json.loads((folder/file).read_text());counts[label]={'passed':sum(bool(x['passed']) for x in records),'total':len(records)}
assert counts=={'generated_lp':{'passed':120,'total':120},'netlib':{'passed':12,'total':12},
                'generated_milp':{'passed':40,'total':40},'miplib':{'passed':1,'total':4},
                'generated_qp':{'passed':30,'total':30},'qplib':{'passed':2,'total':3}}
packages={}
for target in ['tools/reference/python','tools/reference/qp']:
    packages[target]={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(ROOT/target)])}
result={'core_files_verified':checked,'executable_sha256':metadata['executable_sha256'],
        'counts':counts,'reference_packages':packages}
(folder/'evidence-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
