"""Repeated CPU/GPU box-QP validation for the SIH26119 solver (Kaggle GPU session).

Builds the current source with CUDA enabled, then measures the same planted
convex box-QP family on one CPU thread, on multiple CPU threads and on the GPU,
with repeats, at the same accuracy contract. Every run checks its own answer
against the planted optimum, and CPU and GPU objectives are compared.

Scope: box-constrained convex QP only. This is not a GPU MILP or general
constrained-QP claim.
"""
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

WORK = Path('/kaggle/working')
INPUT = Path('/kaggle/input')
BUILD = WORK / 'build'
SIZES = [10000, 50000, 200000, 500000, 1000000]
BACKENDS = [('cpu', 1), ('cpu', 4), ('cuda', 1)]
REPEATS = 3
LIMIT = 120


def run(command, **kwargs):
    return subprocess.run(command, capture_output=True, text=True, **kwargs)


def device_report():
    info = {}
    smi = run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version,compute_cap',
               '--format=csv,noheader'])
    info['nvidia_smi'] = smi.stdout.strip()
    info['nvcc'] = run(['nvcc', '--version']).stdout.strip().splitlines()[-1:]
    info['cpu'] = next((line.split(':', 1)[1].strip() for line in open('/proc/cpuinfo')
                        if line.startswith('model name')), 'unknown')
    info['cpu_count'] = os.cpu_count()
    print(json.dumps(info, indent=1), flush=True)
    return info


def find_source():
    for marker in sorted(INPUT.rglob('src/cuda_box.cu')):
        return marker.parent.parent
    raise SystemExit('source with CUDA kernel not found under /kaggle/input')


def build(src):
    BUILD.mkdir(parents=True, exist_ok=True)
    stage = WORK / 'source'
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(src, stage)
    configure = run(['cmake', '-S', str(stage), '-B', str(BUILD), '-DCMAKE_BUILD_TYPE=Release',
                     '-DSOVEREIGN_ENABLE_CUDA=ON'])
    print('cmake exit', configure.returncode)
    if configure.returncode:
        print(configure.stdout[-3000:], configure.stderr[-3000:])
        raise SystemExit('configure failed')
    made = run(['cmake', '--build', str(BUILD), '--target', 'solver_scale', '-j', '4'])
    print('build exit', made.returncode)
    if made.returncode:
        print(made.stdout[-4000:], made.stderr[-4000:])
        raise SystemExit('build failed')
    return BUILD / 'solver_scale'


def measure(binary, n, backend, threads):
    started = time.time()
    done = run([str(binary), str(n), backend, str(threads), str(LIMIT)], timeout=LIMIT + 120)
    record = {'columns': n, 'backend': backend, 'threads': threads, 'exit_code': done.returncode,
              'wall_seconds': time.time() - started}
    try:
        record.update(json.loads(done.stdout))
    except ValueError:
        record['status'] = 'process_error'
        record['stderr'] = done.stderr.strip()[-400:]
    return record


def main():
    info = device_report()
    binary = build(find_source())
    rows = []
    for n in SIZES:
        for backend, threads in BACKENDS:
            for repeat in range(REPEATS):
                row = measure(binary, n, backend, threads)
                row['repeat'] = repeat
                rows.append(row)
                (WORK / 'results.json').write_text(json.dumps(rows), encoding='utf-8')
                print(f"n={n:>8} {backend}:{threads} repeat {repeat} -> {row.get('status')}"
                      f" passed={row.get('passed')} solve={row.get('solve_seconds')}"
                      f" obj_err={row.get('relative_objective_error')}", flush=True)
    summary = {'device': info, 'sizes': SIZES, 'backends': BACKENDS, 'repeats': REPEATS,
               'limit_seconds': LIMIT, 'records': len(rows),
               'passed': sum(bool(r.get('passed')) for r in rows),
               'failed': [f"{r['columns']}:{r['backend']}:{r['threads']}:{r['repeat']}" for r in rows
                          if not r.get('passed')]}
    # Same-accuracy comparison: median solve seconds per size and backend, plus
    # the CPU/GPU objective agreement that makes the comparison meaningful.
    table = {}
    for n in SIZES:
        entry = {}
        for backend, threads in BACKENDS:
            times = [r['solve_seconds'] for r in rows
                     if r['columns'] == n and r['backend'] == backend and r['threads'] == threads
                     and r.get('solve_seconds') is not None and r.get('passed')]
            entry[f'{backend}:{threads}'] = {'median_solve_seconds': statistics.median(times) if times else None,
                                             'runs': len(times)}
        objectives = [r['objective'] for r in rows if r['columns'] == n and r.get('objective') is not None]
        entry['objective_spread'] = (max(objectives) - min(objectives)) if objectives else None
        table[str(n)] = entry
    summary['per_size'] = table
    summary['caveat'] = ('Box-constrained convex QP only, one planted family, one session. '
                         'Timings are end-to-end process measurements including transfers and setup.')
    (WORK / 'SUMMARY.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    print(json.dumps(summary, indent=1))
    shutil.rmtree(WORK / 'source', ignore_errors=True)
    shutil.rmtree(BUILD, ignore_errors=True)


if __name__ == '__main__':
    main()
