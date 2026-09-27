"""A disposable HiGHS process; Linux address-space limits also cover model parsing."""
import json
import sys

from config import WORKER_MEMORY_MB


def main():
    if sys.platform == 'linux':
        import resource
        ceiling = WORKER_MEMORY_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    import solve

    if sys.argv[1:] == ['--check']:
        import highspy
        print(highspy.Highs().version())
        return
    try:
        result = solve._reference(sys.argv[1], sys.argv[2] == '1', float(sys.argv[3]))
    except MemoryError:
        result = solve._empty('reference', 'memory_limit', 'model exceeded the worker memory limit')
    except Exception:
        # Do not return local paths or user model contents in error messages.
        result = solve._empty('reference', 'engine_error', 'HiGHS could not process this model')
    print(json.dumps(solve.json_safe(result), allow_nan=False))


if __name__ == '__main__':
    main()
