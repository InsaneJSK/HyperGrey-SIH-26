"""Why do 17 MIPLIB instances never leave the root LP?

Diagnostic, not evidence: no comparison, no promotion. Each instance is solved to
the root only (node limit 1) with the bounded engine's debug output on, so the
log shows whether the root relaxation runs out of time, fails its own
verification, or is rejected somewhere else. Four instances run at a time; each
is single-threaded, and absolute timings here are indicative only.
"""
import concurrent.futures as futures
import sys
import gzip
import io
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
DATA = BASE / 'instances'
BINARY = ROOT / 'reports/milp-iteration-33/final_solver_cli.exe'
MODELS = ['dano3_3', 'dano3_5', 'neos-662469', 'neos-827175', 'neos-933966', 'neos-957323',
          'neos-1354092', 'mzzv11', 'mzzv42z', 'CMS750_4', 'ns1208400', 'neos-3656078-kumeu']
LIMIT = 300
# Optional: extra solver flags and a run label, e.g. --iteration-limit 100000000 uncapped
EXTRA = sys.argv[1].split() if len(sys.argv) > 1 else []
LABEL = sys.argv[2] if len(sys.argv) > 2 else 'runs'


def fetch(name):
    target = DATA / (name + '.mps')
    if not target.exists():
        with urllib.request.urlopen(f'https://miplib.zib.de/WebData/instances/{name}.mps.gz', timeout=600) as r:
            raw = r.read()
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            target.write_bytes(stream.read())
    return target


def run(name):
    model = fetch(name)
    command = [str(BINARY), str(model), '--milp', '--json', '--bounded-lp', '--lp-recovery',
               '--capture-lp-failure', '--capture-work', '--node-limit', '1', '--time-limit', str(LIMIT), *EXTRA]
    env = dict(os.environ, SOVEREIGN_BOUNDED_DEBUG='1')
    started = time.time()
    done = subprocess.run(command, capture_output=True, text=True, timeout=LIMIT + 300, env=env)
    wall = time.time() - started
    try:
        result = json.loads(done.stdout)
    except ValueError:
        result = {'status': 'process_error'}
    failure = result.get('first_lp_failure') or {}
    bounded = result.get('bounded_lp') or {}
    record = {'name': name, 'status': result.get('status'), 'message': result.get('message'),
              'wall_seconds': round(wall, 1), 'rows': result.get('rows'), 'columns': result.get('columns'),
              'root_lp_failure_status': failure.get('status'), 'root_lp_iterations': failure.get('iterations'),
              'bounded': {k: bounded.get(k) for k in ('calls', 'optimal', 'failures', 'fallbacks', 'iterations',
                                                      'verification_rejected', 'farkas_rejected', 'refactors',
                                                      'singular_repairs', 'seconds')},
              'lp_recovery': {'attempts': result.get('lp_recovery_attempts'),
                              'successes': result.get('lp_recovery_successes'),
                              'seconds': result.get('lp_recovery_seconds')},
              'debug': [line for line in done.stderr.splitlines() if line.startswith(('bounded', '  '))][:12]}
    (BASE / LABEL / (name + '.json')).write_text(json.dumps(record, indent=1), encoding='utf-8')
    return record


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    (BASE / LABEL).mkdir(exist_ok=True)
    with futures.ThreadPoolExecutor(4) as pool:
        for r in pool.map(run, MODELS):
            b = r['bounded']
            print(f"{r['name']:22s} {str(r['rows']):>6s}x{str(r['columns']):<6s} {str(r['status']):22s} "
                  f"{r['wall_seconds']:>6.1f}s root_lp={r['root_lp_failure_status']} "
                  f"bounded: calls={b['calls']} ok={b['optimal']} fail={b['failures']} "
                  f"verif_rej={b['verification_rejected']} it={b['iterations']} "
                  f"recovery={r['lp_recovery']['attempts']}/{r['lp_recovery']['successes']}", flush=True)
            for line in r['debug'][:3]:
                print('     ', line[:150], flush=True)


if __name__ == '__main__':
    main()
