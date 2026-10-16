"""Exercise actual notebook cells; external commands are mocked, not GPU-validated."""
import contextlib
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import nbformat

NOTEBOOK = Path(os.environ.get('SIH_KAGGLE_NOTEBOOK',
    str(Path(__file__).resolve().parents[2]/'kaggle_delivery/SIH26119_V2_Kaggle.ipynb'))).resolve()
SOURCE_ZIP = NOTEBOOK.with_name('SIH26119_V2_source.zip')
CELLS = [cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells if cell.cell_type == 'code']


class NotebookFlowTests(unittest.TestCase):
    def prepare_input(self, folder, unpacked=False):
        dataset = Path(folder)/'input/datasets/any-user/any-dataset-name/1'
        dataset.mkdir(parents=True)
        if unpacked:
            with zipfile.ZipFile(SOURCE_ZIP) as archive:
                archive.extractall(dataset)
        else:
            shutil.copy2(SOURCE_ZIP, dataset/SOURCE_ZIP.name)
        return dataset

    def exercise(self, failure=None, gpu=False, repeat=False, capability_ok=True, unpacked=False):
        original = Path.cwd()
        try:
            with tempfile.TemporaryDirectory(prefix='sih_notebook_test_') as folder:
                self.prepare_input(folder, unpacked)
                os.chdir(folder)
                namespace = {}
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(compile(CELLS[0], 'notebook-unpack', 'exec'), namespace)
                self.assertEqual(namespace['PYTHON'], sys.executable)
                self.assertTrue((namespace['WORK']/'scripts/test_result_parser.py').is_file())
                calls = []

                def fake_run(command, **kwargs):
                    command = list(map(str, command))
                    calls.append(command)
                    stage = namespace.get('stage')
                    if command[0] == 'nvidia-smi':
                        if len(command) > 1:
                            return subprocess.CompletedProcess(command, 0 if capability_ok else 1, '7.5\n' if capability_ok else '', '')
                        return subprocess.CompletedProcess(command, 0, 'MOCK GPU (control-flow test only)', '')
                    self.assertEqual(kwargs['cwd'], namespace['WORK'])
                    kwargs['stdout'].write('MOCK command output\n')
                    if stage == failure:
                        if failure == 'compiler':
                            raise FileNotFoundError('mock missing compiler')
                        return subprocess.CompletedProcess(command, 1)
                    if stage == 'validation':
                        results = Path(command[command.index('--output')+1])
                        results.mkdir(parents=True, exist_ok=False)
                        (results/'summary.json').write_text(json.dumps({'mock_test': True}))
                    return subprocess.CompletedProcess(command, 0)

                def fake_which(command):
                    if command in ('nvidia-smi', 'nvcc'):
                        return command if gpu else None
                    return command

                for _ in range(2 if repeat else 1):
                    with patch('subprocess.run', side_effect=fake_run), patch('shutil.which', side_effect=fake_which), contextlib.redirect_stdout(io.StringIO()):
                        exec(compile(CELLS[1], 'notebook-run', 'exec'), namespace)
                    with zipfile.ZipFile(namespace['destination']) as archive:
                        self.assertIsNone(archive.testzip())
                        status = json.loads(archive.read('run_logs/RUN_STATUS.json'))
                        self.assertIn('SNAPSHOT.json', archive.namelist())
                        self.assertIn('SOURCE_MANIFEST.json', archive.namelist())
                        if failure:
                            self.assertFalse(status['completed'])
                            self.assertEqual(status['failed_stage'], failure)
                            self.assertIn('run_logs/'+failure+'.log', archive.namelist())
                        else:
                            self.assertTrue(status['completed'])
                            self.assertEqual(status['gpu_enabled'], gpu)
                            self.assertIn('reports/kaggle_validation/summary.json', archive.namelist())
                configure = [c for c in calls if c[0] == 'cmake' and '-S' in c]
                if configure:
                    self.assertIn('-DSOVEREIGN_ENABLE_CUDA='+('ON' if gpu else 'OFF'), configure[0])
                    if gpu and capability_ok:
                        self.assertIn('-DCMAKE_CUDA_ARCHITECTURES=75', configure[0])
                    if gpu and not capability_ok:
                        self.assertFalse(any(c.startswith('-DCMAKE_CUDA_ARCHITECTURES=') for c in configure[0]))
                installs = [c for c in calls if 'pip' in c and 'install' in c]
                self.assertEqual(installs[0][0], sys.executable)
                os.chdir(original)
        finally:
            os.chdir(original)

    def test_cpu_only_and_second_cell_rerun(self):
        self.exercise(repeat=True)

    def test_gpu_commands(self):
        self.exercise(gpu=True)

    def test_optional_capability_query_failure(self):
        self.exercise(gpu=True, capability_ok=False)

    def test_install_failure_returns_zip(self):
        self.exercise(failure='install')

    def test_missing_compiler_returns_zip(self):
        self.exercise(failure='compiler')

    def test_build_failure_returns_zip(self):
        self.exercise(failure='build', gpu=True)

    def test_validation_failure_returns_zip(self):
        self.exercise(failure='validation', gpu=True)

    def test_unpacked_dataset(self):
        self.exercise(unpacked=True)

    def test_notebook_size_limit(self):
        self.assertLess(NOTEBOOK.stat().st_size, 1_000_000)
        self.assertEqual(len(CELLS), 2)

    def check_bad_input(self, kind, error_type):
        original = Path.cwd()
        try:
            with tempfile.TemporaryDirectory(prefix='sih_notebook_input_test_') as folder:
                if kind != 'missing':
                    dataset = self.prepare_input(folder, unpacked=(kind == 'changed'))
                    if kind == 'changed':
                        (dataset/'scripts/test_result_parser.py').write_text('modified fixture')
                    else:
                        (dataset/SOURCE_ZIP.name).write_bytes(b'wrong source zip fixture')
                os.chdir(folder)
                try:
                    with self.assertRaises(error_type):
                        exec(compile(CELLS[0], 'notebook-unpack', 'exec'), {})
                finally:
                    os.chdir(original)
        finally:
            os.chdir(original)

    def test_missing_dataset_gives_attach_instruction(self):
        self.check_bad_input('missing', FileNotFoundError)

    def test_wrong_zip_is_rejected(self):
        self.check_bad_input('wrong_zip', FileNotFoundError)

    def test_changed_unpacked_source_is_rejected(self):
        self.check_bad_input('changed', AssertionError)


if __name__ == '__main__':
    unittest.main()
