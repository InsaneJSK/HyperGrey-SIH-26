"""Build a notebook below 1 MB with a separate Kaggle input source ZIP."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def main(output, evidence=None, profile='full'):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = [ROOT/'CMakeLists.txt', ROOT/'README.md', ROOT/'Problem Statement.txt']
    files += [ROOT/'reports'/name for name in ('V2_REPORT.md', 'V1_REPORT.md')]
    files += [p for p in (ROOT/'reports/KAGGLE_GPU_REPORT.md', ROOT/'reports/kaggle-gpu-01/AUDIT.json') if p.is_file()]
    evidence = (evidence or ROOT/'reports/v2-final-cpu').resolve()
    evidence_name = evidence.relative_to(ROOT).as_posix()
    metadata = json.loads((evidence/'metadata.json').read_text(encoding='utf-8'))
    for name, digest in metadata['source_sha256'].items():
        if name.split('/')[0] in ('src', 'include', 'tests'):
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'Stale CPU evidence: '+name
    assert hashlib.sha256((ROOT/'CMakeLists.txt').read_bytes()).hexdigest() == metadata['cmake_sha256']
    assert json.loads((evidence/'summary.json').read_text())['all_generated_passed'], 'Generated regression gate failed'
    files += [p for p in evidence.iterdir() if p.is_file() and p.suffix in ('.json', '.md', '.log', '.txt')]
    files += [p for p in (evidence.parent/'REPORT.md',) if p.is_file()]
    if profile=='milp_recovery':
        # Keep the initial failed experiment and longer final-source check
        # distinct from the selected final correctness gate.
        for name in ('local-60s','final-blend-90s','lp-diagnostic-checked'):
            files += [p for p in (evidence.parent/name).glob('*') if p.is_file() and p.suffix in ('.json','.md','.log','.txt','.mps')]
        files += [p for p in (evidence.parent/'initial_milp_v2.cpp',) if p.is_file()]
    if profile=='milp_repair':
        for name in ('blend-90s','capture','diagnosis'):
            files += [p for p in (evidence.parent/name).rglob('*') if p.is_file() and p.suffix in ('.json','.md','.log','.txt','.mps')]
        files += [p for p in (evidence.parent/'PROOF_REGRESSION.json',evidence.parent/'proof-counterexample.mps') if p.is_file()]
    files += [p for p in (evidence/'miplib2017').glob('*.json')]
    files += [p for p in (evidence/'qplib').glob('*.json')]
    files += [p for p in (ROOT/'reports/v2-reference-audit').iterdir() if p.is_file()]
    for folder in ('src', 'include', 'tests', 'scripts', 'docs', 'examples', 'datasets'):
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file()
                  and p.suffix in ('.cpp', '.hpp', '.cu', '.py', '.ps1', '.md', '.mps', '.qplib', '.lp', '.lpmini', '.json')
                  and '__pycache__' not in p.parts]
    contents = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in sorted(set(files))}
    contents['SNAPSHOT_INFO.json'] = (json.dumps({'cpu_evidence': evidence_name,
        'cuda_execution': 'This new snapshot requires its own Kaggle return; earlier GPU evidence is historical.'}, indent=2)+'\n').encode('utf-8')
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in manifest:
            info = zipfile.ZipInfo(name, (2026, 9, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, contents[name])
        manifest_bytes = (json.dumps(manifest, indent=2)+'\n').encode('utf-8')
        archive.writestr('SOURCE_MANIFEST.json', manifest_bytes)
    payload = buffer.getvalue()
    digest = hashlib.sha256(payload).hexdigest()
    (output/'SIH26119_V2_source.zip').write_bytes(payload)

    intro = '''# SIH26119 — simple Kaggle run

1. Import this small notebook (under 1 MB).
2. Upload **SIH26119_V2_source.zip** as a **private Kaggle dataset** and attach it
   to this notebook using **Add Input**. Any dataset name is fine.
3. Select **GPU** in Settings → Accelerator and enable **Internet**.
4. **Run All** (or Save Version → Save & Run All).
5. Download **sih26119_kaggle_results.zip** from the output and send it back.

The companion ZIP is required: it keeps the source and datasets out of the
notebook's size limit. Both zipped and unpacked input layouts are detected
automatically. No path edits or second virtual environment. The notebook uses
Kaggle's Python and builds a separate copy without changing the Windows project.

This is a quick iteration run: one timing repetition per configuration, not a
final speedup study. Without a usable GPU/compiler it runs CPU-only and labels
that clearly. If a build/test fails, send the diagnostic ZIP it produces.
CUDA covers convex box QPs only; LP/MILP/constrained QP run on CPU.

[Kaggle notebook settings help](https://www.kaggle.com/docs/notebooks)
'''
    if profile in ('milp','milp_recovery','milp_repair'):
        intro='''# SIH26119 — focused hard-MILP experiment

1. Import this small notebook (under 1 MB).
2. Upload the matching **SIH26119_V2_source.zip** as a **private Kaggle dataset**
   and attach it using **Add Input**. Any dataset name works; zipped/unpacked
   layouts are detected automatically.
3. Enable **Internet**. **GPU is not needed**: this MILP implementation runs on CPU.
4. **Run All**, or **Save Version → Save & Run All**. Allow about **20-25 minutes**.
5. Download **sih26119_milp_results.zip** from Output and send it back.

Compares current fractionality branching and experimental reliability branching
on blend2, binkar10_1, and markshare_4_0. Each gets the SAME 180-second and
250,000-node limits. All failures remain visible, and candidates are independently
checked. A shorter local smoke run passed the generated correctness gate; hard
case performance at these longer limits is not yet established.

There are only two code cells. No manual path edits or second environment.
This is separate from the previous QP/MILP notebooks and does not run the GPU
scale sweep. The companion ZIP is input data, outside the notebook size limit.
'''
        if profile=='milp_recovery':
            intro=intro.replace('focused hard-MILP experiment','MILP iteration 03: recovery + incumbent improvement')
            intro=intro.replace('Compares current fractionality branching and experimental reliability branching',
                                'Compares the current control against opt-in LP recovery + neighbourhood search\n(both retain fractionality branching)')
            intro += '''
240 generated correctness checks cover control, recovery-only, and the combined
mode. The six hard runs compare control against the combined mode. Failed tree
LP snapshots, recovery counts, checked incumbent history and unresolved-node
bounds are included in the result ZIP. Incomplete results remain incomplete;
this experiment does not promise a hard-case optimum or an overall speedup.
'''
        if profile=='milp_repair':
            intro=intro.replace('focused hard-MILP experiment','MILP iteration 04: checked candidate repair')
            intro=intro.replace('Compares current fractionality branching and experimental reliability branching',
                                'Compares the recovery + neighbourhood baseline against the same solver\nwith an opt-in dense candidate-repair fallback')
            intro += '''
240 generated checks cover the baseline, repair mode and legacy control.
Both hard-run modes include the shared proof-safety fix: repairing a nearly
integer point does not prove that the entire node is solved. Rejected points,
fixed-integer LP results, fallback counts and checked incumbent traces are
saved in the output ZIP. Feasibility/integrality tolerances are unchanged.
'''
    unpack = (ROOT/'scripts/kaggle_unpack_cell.py').read_text(encoding='utf-8')
    unpack = unpack.replace('__SNAPSHOT_SHA256__', digest)
    unpack = unpack.replace('__MANIFEST_SHA256__', hashlib.sha256(manifest_bytes).hexdigest())
    run_cell=(ROOT/'scripts'/('kaggle_milp_run_cell.py' if profile in ('milp','milp_recovery','milp_repair') else 'kaggle_run_cell.py')).read_text(encoding='utf-8')
    if profile=='milp_recovery':run_cell=run_cell.replace('EXPERIMENT = "branching"','EXPERIMENT = "recovery"')
    if profile=='milp_repair':run_cell=run_cell.replace('EXPERIMENT = "branching"','EXPERIMENT = "repair"')
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell(intro),
        nbformat.v4.new_code_cell(unpack),
        nbformat.v4.new_markdown_cell('''## Run and get the ZIP

The following cell installs comparison packages in the current Python, builds
the solver, and runs the checks. Leave it running until it prints the ZIP path.
Known hard benchmark timeouts remain in the results; they are not hidden.
'''),
        nbformat.v4.new_code_cell(run_cell),
    ])
    notebook.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                         'language_info': {'name': 'python', 'version': '3'}}
    nbformat.validate(notebook)
    nbformat.write(notebook, output/'SIH26119_V2_Kaggle.ipynb')
    notebook_bytes = (output/'SIH26119_V2_Kaggle.ipynb').stat().st_size
    assert notebook_bytes < 1_000_000, 'Notebook must stay below the user\'s 1 MB limit'
    (output/'README.md').write_text('''# Simple Kaggle delivery

Import **SIH26119_V2_Kaggle.ipynb** (under 1 MB).
Upload the NEW **SIH26119_V2_source.zip** as a **private Kaggle dataset**, then
attach that dataset to the notebook using **Add Input**. Any dataset name works.
Select GPU + Internet, and Run All.
You can also use Save Version → Save & Run All.
Download **sih26119_kaggle_results.zip** from Output and send it back.

There are only two code cells: unpack, then run. No second virtual environment
or manual path changes. Uses the current Python and standard pip/subprocess.
The companion source ZIP is REQUIRED. It is input data, not notebook/kernel
code, so its approximately 2.2 MB size is kept outside the notebook size limit.
The notebook detects either the ZIP or its extracted files automatically.

This quick run uses one timing repetition per size/configuration. It keeps all
public results and tests sizes 1,000, 100,000 and 1,000,000. It does not establish
repeatable GPU speedups. Missing GPU/compiler is clearly labeled CPU-only.
Installation/build/check errors are captured in a diagnostic ZIP. Send that ZIP
too; don't spend time repairing the notebook yourself.

This source snapshot is separate from the local Windows project. It passed
the generated CPU regression gate linked in SNAPSHOT_INFO.json. Public hard
cases can remain incomplete; see the included evidence, not just the exit code.
Actual Kaggle/CUDA execution of this NEW snapshot remains unverified until your run.

Source SHA-256: '''+digest+'\n', encoding='utf-8')
    if profile in ('milp','milp_recovery','milp_repair'):
        (output/'README.md').write_text(intro+'\nSource SHA-256: '+digest+'\n',encoding='utf-8')
    print(json.dumps({'notebook': str(output/'SIH26119_V2_Kaggle.ipynb'),
                      'snapshot_sha256': digest, 'files': len(manifest),
                      'code_cells': 2, 'snapshot_bytes': len(payload),
                      'notebook_bytes': notebook_bytes}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT.parent/'kaggle_delivery')
    parser.add_argument('--evidence', type=Path, default=ROOT/'reports/v2-final-cpu')
    parser.add_argument('--profile',choices=['full','milp','milp_recovery','milp_repair'],default='full')
    args = parser.parse_args()
    main(args.output, args.evidence,args.profile)
