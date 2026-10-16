"""Execute the delivered notebook on real Linux, with reduced smoke-test limits."""
import ast
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

notebook_path = Path(sys.argv[1]).resolve()
notebook = json.loads(notebook_path.read_text(encoding='utf-8'))
run_directory = Path(tempfile.mkdtemp(prefix='sih26119-small-notebook-smoke-'))
dataset = run_directory/'input/datasets/test-user/attached-source/1'
dataset.mkdir(parents=True)
with zipfile.ZipFile(notebook_path.with_name('SIH26119_V2_source.zip')) as archive:
    archive.extractall(dataset)
os.chdir(run_directory)
namespace = {}
for index, cell in enumerate(c for c in notebook['cells'] if c['cell_type'] == 'code'):
    tree = ast.parse(''.join(cell['source']))
    if index == 1:
        # Only reduce time/scale settings, not setup, build, execution or export logic.
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name == 'PUBLIC_TIME_LIMIT':
                    node.value = ast.Constant(1)
                elif name == 'SIZES':
                    node.value = ast.List(elts=[ast.Constant(1000)], ctx=ast.Load())
    exec(compile(ast.fix_missing_locations(tree), 'delivered-notebook-cell-'+str(index), 'exec'), namespace)
assert namespace['status']['completed'], namespace['status']
assert not namespace['status']['gpu_enabled'], 'This smoke test expects CPU-only hardware'
assert namespace['summary']['all_generated_passed']
assert namespace['summary']['groups']['scale']['passed'] == 2
shutil.copy2(namespace['destination'], Path(__file__).with_name('SMALL_NOTEBOOK_SMOKE_RESULTS.zip'))
print('REAL LINUX NOTEBOOK SMOKE PASSED: all 230 generated checks, two scale checks, ZIP export')
