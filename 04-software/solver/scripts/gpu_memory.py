"""Optional NVML sampling with explicit missing-data and device-wide semantics."""


def connect_nvml():
    try:
        import pynvml
        pynvml.nvmlInit()
        return pynvml, pynvml.nvmlDeviceGetHandleByIndex(0), None
    except Exception as error:
        return None, None, type(error).__name__+': '+str(error)[:240]


class GpuMemorySampler:
    def __init__(self, api, handle, unavailable_reason=None):
        self.api, self.handle = api, handle
        self.unavailable_reason = unavailable_reason
        self.process_peak = None
        self.device_baseline = None
        self.device_peak = None
        self.pid_seen = False
        self.max_processes = 0
        self.errors = set()
        self.samples = 0
        if api is not None:
            self.device_baseline = self.device_used()
            self.device_peak = self.device_baseline

    @staticmethod
    def valid_bytes(value):
        # Reject unavailable sentinels and None, never turn missing data into zero.
        return isinstance(value, int) and 0 <= value < 2**63

    def device_used(self):
        try:
            value = self.api.nvmlDeviceGetMemoryInfo(self.handle).used
            if self.valid_bytes(value):
                return value
            self.errors.add('device_memory_value_unavailable')
        except Exception as error:
            self.errors.add('device_query: '+type(error).__name__+': '+str(error)[:240])
        return None

    def sample(self, pid):
        if self.api is None:
            return
        self.samples += 1
        used = self.device_used()
        if used is not None:
            self.device_peak = max(self.device_peak or 0, used)
        try:
            entries = self.api.nvmlDeviceGetComputeRunningProcesses(self.handle)
            self.max_processes = max(self.max_processes, len(entries))
            for entry in entries:
                if entry.pid == pid:
                    self.pid_seen = True
                    if self.valid_bytes(entry.usedGpuMemory):
                        self.process_peak = max(self.process_peak or 0, entry.usedGpuMemory)
                    else:
                        self.errors.add('process_memory_value_unavailable')
        except Exception as error:
            self.errors.add('process_query: '+type(error).__name__+': '+str(error)[:240])

    def report(self):
        if self.api is None:
            status = 'nvml_unavailable'
        elif self.process_peak is not None:
            status = 'sampled_for_matching_pid'
        elif self.pid_seen:
            status = 'matching_pid_memory_unavailable'
        elif any(e.startswith('process_query:') for e in self.errors):
            status = 'process_query_failed'
        else:
            status = 'no_matching_pid_observed'
        delta = None
        if self.device_peak is not None and self.device_baseline is not None:
            delta = max(0, self.device_peak-self.device_baseline)
        return {'peak_gpu_memory_sampled_bytes': self.process_peak,
                'gpu_process_memory_status': status,
                'gpu_memory_unavailable_reason': self.unavailable_reason,
                'gpu_memory_query_errors': sorted(self.errors),
                'gpu_memory_samples': self.samples,
                'gpu_matching_pid_observed': self.pid_seen,
                'gpu_max_visible_compute_processes': self.max_processes,
                'gpu_device_baseline_used_bytes': self.device_baseline,
                'gpu_device_peak_used_bytes': self.device_peak,
                'gpu_device_peak_increase_bytes': delta,
                'gpu_device_memory_scope': 'whole device; may include other processes and driver allocations; not solver-only memory'}
