"""Run the actual small-notebook cells with external build/solver calls mocked."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import nbformat

NOTEBOOK=Path(os.environ['SIH_KAGGLE_NOTEBOOK']).resolve()
CELLS=[cell.source for cell in nbformat.read(NOTEBOOK,as_version=4).cells if cell.cell_type=='code']


class MilpNotebookTests(unittest.TestCase):
    def exercise(self,unpacked=False,failure=None,repeat=False):
        cwd=Path.cwd()
        try:
            with tempfile.TemporaryDirectory(prefix='milp_notebook_test_') as folder, contextlib.ExitStack() as cleanup:
                cleanup.callback(os.chdir,cwd)
                base=Path(folder);dataset=base/'input/any-name';dataset.mkdir(parents=True)
                source=NOTEBOOK.with_name('SIH26119_V2_source.zip')
                if unpacked:
                    with zipfile.ZipFile(source) as z:z.extractall(dataset)
                else:shutil.copy2(source,dataset/source.name)
                os.chdir(base);namespace={};calls=[]
                with contextlib.redirect_stdout(io.StringIO()):exec(compile(CELLS[0],'unpack','exec'),namespace)
                def fake_run(command,**kwargs):
                    command=list(map(str,command));calls.append(command);self.assertEqual(kwargs['cwd'],namespace['WORK'])
                    kwargs['stdout'].write('MOCK external command\n')
                    if namespace['stage']==failure:return subprocess.CompletedProcess(command,1)
                    if namespace['stage']=='validation':
                        target=Path(command[command.index('--output')+1]);target.mkdir(parents=True)
                        (target/'summary.json').write_text(json.dumps({'mock':True}))
                    return subprocess.CompletedProcess(command,0)
                for _ in range(2 if repeat else 1):
                    with patch('subprocess.run',side_effect=fake_run),contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(CELLS[1],'milp-run','exec'),namespace)
                    with zipfile.ZipFile(namespace['destination']) as z:
                        self.assertIsNone(z.testzip());status=json.loads(z.read('run_logs/RUN_STATUS.json'))
                        self.assertEqual(status['completed'],failure is None);self.assertFalse(status['gpu_enabled'])
                        self.assertEqual(namespace['destination'].name,'sih26119_milp_results.zip')
                        self.assertIn('SOURCE_MANIFEST.json',z.namelist());self.assertIn('SNAPSHOT.json',z.namelist())
                        if failure:self.assertEqual(status['failed_stage'],failure)
                config=next(c for c in calls if c[0]=='cmake' and '-S' in c)
                self.assertIn('-DSOVEREIGN_ENABLE_CUDA=OFF',config)
                if not failure:
                    validation=next(c for c in calls if any('validate_milp_focus.py' in token for token in c))
                    self.assertEqual(validation[validation.index('--limit')+1],'180')
                    self.assertEqual(validation[validation.index('--nodes')+1],'250000')
                    if 'EXPERIMENT' in namespace:
                        self.assertEqual(validation[validation.index('--experiment')+1],namespace['EXPERIMENT'])
                        self.assertEqual(status['experiment'],namespace['EXPERIMENT'])
        finally:os.chdir(cwd)

    def test_zipped(self):self.exercise()
    def test_unpacked(self):self.exercise(unpacked=True)
    def test_rerun(self):self.exercise(repeat=True)
    def test_build_failure_zip(self):self.exercise(failure='build')
    def test_validation_failure_zip(self):self.exercise(failure='validation')


if __name__=='__main__':unittest.main()
