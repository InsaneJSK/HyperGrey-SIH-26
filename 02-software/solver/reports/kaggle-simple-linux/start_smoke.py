"""Prepare an isolated local Linux test runtime; not part of the Kaggle notebook."""
from pathlib import Path
import subprocess
import sys
import tempfile

run_directory = Path(tempfile.mkdtemp(prefix='sih26119-notebook-test-'))
print('Linux smoke directory:', run_directory, flush=True)
subprocess.check_call([sys.executable, '-m', 'venv', str(run_directory/'env')])
python = run_directory/'env/bin/python'
subprocess.check_call([str(python), '-m', 'pip', 'install', '--quiet', 'ipython'])
subprocess.check_call([str(python), str(Path(__file__).with_name('run_smoke.py')), sys.argv[1]], cwd=run_directory)
# run_smoke.py preserves its own SMALL_NOTEBOOK_SMOKE_RESULTS.zip beside this script.
