"""Sampler regression tests with explicit mocked NVML data, not GPU evidence."""
from types import SimpleNamespace
import unittest
from gpu_memory import GpuMemorySampler


class FakeNvml:
    used = 100
    entries = []
    fail = False

    def nvmlDeviceGetMemoryInfo(self, handle):
        return SimpleNamespace(used=self.used)

    def nvmlDeviceGetComputeRunningProcesses(self, handle):
        if self.fail:
            raise RuntimeError('not supported')
        return self.entries


class GpuMemoryTests(unittest.TestCase):
    def test_matching_pid_and_peak(self):
        api = FakeNvml()
        sampler = GpuMemorySampler(api, 0)
        api.used = 160
        api.entries = [SimpleNamespace(pid=42, usedGpuMemory=50)]
        sampler.sample(42)
        api.used = 140
        sampler.sample(42)
        result = sampler.report()
        self.assertEqual(result['peak_gpu_memory_sampled_bytes'], 50)
        self.assertEqual(result['gpu_device_peak_increase_bytes'], 60)
        self.assertEqual(result['gpu_process_memory_status'], 'sampled_for_matching_pid')

    def test_other_pid_is_not_misattributed(self):
        api = FakeNvml()
        sampler = GpuMemorySampler(api, 0)
        api.used = 200
        api.entries = [SimpleNamespace(pid=99, usedGpuMemory=100)]
        sampler.sample(42)
        result = sampler.report()
        self.assertIsNone(result['peak_gpu_memory_sampled_bytes'])
        self.assertEqual(result['gpu_device_peak_increase_bytes'], 100)
        self.assertEqual(result['gpu_process_memory_status'], 'no_matching_pid_observed')
        self.assertIn('not solver-only', result['gpu_device_memory_scope'])

    def test_unavailable_sentinels_remain_null(self):
        for value in (None, 2**64-1):
            api = FakeNvml()
            sampler = GpuMemorySampler(api, 0)
            api.entries = [SimpleNamespace(pid=42, usedGpuMemory=value)]
            sampler.sample(42)
            result = sampler.report()
            self.assertIsNone(result['peak_gpu_memory_sampled_bytes'])
            self.assertEqual(result['gpu_process_memory_status'], 'matching_pid_memory_unavailable')

    def test_query_failure_is_preserved(self):
        api = FakeNvml()
        api.fail = True
        sampler = GpuMemorySampler(api, 0)
        sampler.sample(42)
        result = sampler.report()
        self.assertEqual(result['gpu_process_memory_status'], 'process_query_failed')
        self.assertIn('not supported', result['gpu_memory_query_errors'][0])
        self.assertEqual(result['gpu_device_peak_used_bytes'], 100)

    def test_no_nvml(self):
        sampler = GpuMemorySampler(None, None, 'driver not available')
        sampler.sample(42)
        result = sampler.report()
        self.assertEqual(result['gpu_process_memory_status'], 'nvml_unavailable')
        self.assertEqual(result['gpu_memory_unavailable_reason'], 'driver not available')
        self.assertIsNone(result['gpu_device_peak_used_bytes'])

    def test_measured_zero_is_not_missing(self):
        api = FakeNvml()
        api.entries = [SimpleNamespace(pid=42, usedGpuMemory=0)]
        sampler = GpuMemorySampler(api, 0)
        sampler.sample(42)
        self.assertEqual(sampler.report()['peak_gpu_memory_sampled_bytes'], 0)
        self.assertEqual(sampler.report()['gpu_process_memory_status'], 'sampled_for_matching_pid')


if __name__ == '__main__':
    unittest.main()
