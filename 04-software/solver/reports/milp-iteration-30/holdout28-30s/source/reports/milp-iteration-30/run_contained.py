"""Windows single-solver watchdog. Sampled memory threshold, not an allocation cap.

Native output is retained even on termination; forced stops never become solver
success. The core does not spawn child processes. This wrapper does not promise
containment of arbitrary process trees or real-time process creation/termination.
"""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

class MemoryCounters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
        (name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage',
        'QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]

def monitor(command,prefix,timeout,memory_mib=None,cancel_after=None):
    if os.name!='nt':raise RuntimeError('This resource monitor is validated for Windows only')
    for name,value in [('timeout',timeout),('memory_mib',memory_mib),('cancel_after',cancel_after)]:
        if value is not None and (not math.isfinite(value) or value<=0):raise ValueError('Invalid '+name)
    prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    memory=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
    memory.argtypes=[wintypes.HANDLE,ctypes.POINTER(MemoryCounters),wintypes.DWORD];memory.restype=wintypes.BOOL
    stdout=prefix.with_name(prefix.name+'.stdout.log');stderr=prefix.with_name(prefix.name+'.stderr.log')
    result={'command':list(command),'timeout_seconds':timeout,'memory_threshold_mib':memory_mib,
            'cancel_after_seconds':cancel_after,'sample_period_seconds':.02,'peak_working_set_bytes':0,
            'peak_commit_bytes':0,'status':'process_error','native_result':None,'independently_validated':False}
    started=time.monotonic();process=None;handle=None;forced=None
    try:
        with stdout.open('xb') as out,stderr.open('xb') as err:
            process=subprocess.Popen(command,stdout=out,stderr=err,shell=False)
            result['pid']=process.pid
            handle=kernel.OpenProcess(0x1000,False,process.pid)
            if not handle and process.poll() is None:raise ctypes.WinError(ctypes.get_last_error())
            while process.poll() is None:
                counters=MemoryCounters();counters.cb=ctypes.sizeof(counters)
                if memory(handle,ctypes.byref(counters),counters.cb):
                    result['peak_working_set_bytes']=max(result['peak_working_set_bytes'],counters.PeakWorkingSetSize)
                    result['peak_commit_bytes']=max(result['peak_commit_bytes'],counters.PeakPagefileUsage)
                elif process.poll() is None:raise ctypes.WinError(ctypes.get_last_error())
                elapsed=time.monotonic()-started
                if memory_mib is not None and counters.PagefileUsage>memory_mib*1024*1024:forced='memory_limit'
                elif cancel_after is not None and elapsed>=cancel_after:forced='cancelled'
                elif elapsed>=timeout:forced='external_timeout'
                if forced:
                    process.kill();break
                time.sleep(.02)
            process.wait(timeout=5)
        result['exit_code']=process.returncode
        try:
            native=json.loads(stdout.read_text(encoding='utf-8'))
            if isinstance(native,dict) and isinstance(native.get('status'),str):result['native_result']=native
        except (ValueError,UnicodeError):pass
        native_status=result['native_result']['status'] if result['native_result'] else None
        # solver_cli uses exit 1 for honest limits and non-optimal outcomes.
        # Never accept an optimal claim paired with an unsuccessful process exit.
        normal_nonoptimal={'infeasible','unbounded','time_limit','node_limit','iteration_limit',
                           'unresolved_relaxations','numerical_error','numerical_stall','resource_limit',
                           'unsupported','unsupported_nonconvex','unsupported_curvature','unsupported_structure'}
        valid_exit=(process.returncode==0 and native_status in {'optimal','gap_limit'}) or (process.returncode==1 and native_status in normal_nonoptimal)
        result['status']=forced or (native_status if valid_exit else 'process_error')
    except KeyboardInterrupt:
        result['status']='cancelled'
    except Exception as e:
        result['status']='monitor_error';result['error']=repr(e)
    finally:
        if process is not None:
            if process.poll() is None:process.kill()
            process.wait(timeout=5);result['exit_code']=process.returncode
            result['process_terminated']=process.poll() is not None
        if handle:kernel.CloseHandle(handle)
        result['wall_seconds']=time.monotonic()-started
        result['stdout_sha256']=hashlib.sha256(stdout.read_bytes()).hexdigest() if stdout.exists() else None
        result['stderr_sha256']=hashlib.sha256(stderr.read_bytes()).hexdigest() if stderr.exists() else None
        record=prefix.with_name(prefix.name+'.json')
        with record.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--timeout',type=float,required=True);p.add_argument('--memory-mib',type=float);p.add_argument('--cancel-after',type=float)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command:p.error('A solver command is required after --')
    r=monitor(command,a.output,a.timeout,a.memory_mib,a.cancel_after)
    print(json.dumps({k:v for k,v in r.items() if k!='native_result'},indent=2))
