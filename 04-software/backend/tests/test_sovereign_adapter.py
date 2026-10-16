"""Keep the opt-in C++ adapter aligned with the current CLI contract."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import solve


def test_milp_command_uses_current_recommended_profile(monkeypatch, tmp_path):
    profile = Path(__file__).resolve().parents[2] / 'solver' / 'reports' / 'milp-iteration-37' / 'CANDIDATE_PROFILE.json'
    recommended = json.loads(profile.read_text(encoding='utf-8'))['recommended_flags']
    algorithm_flags = [flag for flag in recommended if not flag.startswith('--capture-')]
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout='{"status":"optimal"}', stderr='')

    monkeypatch.setattr(solve.subprocess, 'run', run)
    model = tmp_path / 'model.mps'
    solve._sovereign(model, True, 3.0)
    assert calls[0][0] == [solve.BINARY, str(model), '--json', '--time-limit', '3.0',
                           '--milp', '--node-limit', '100000000', '--gap', '1e-6',
                           *algorithm_flags]
    assert calls[0][1]['timeout'] == 3.0 + solve.SOLVE_TIMEOUT_GRACE


def test_continuous_command_keeps_explicit_bounded_relaxation(monkeypatch, tmp_path):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout='{"status":"optimal"}', stderr='')

    monkeypatch.setattr(solve.subprocess, 'run', run)
    model = tmp_path / 'model.mps'
    solve._sovereign(model, False, 3.0)
    assert calls == [[solve.BINARY, str(model), '--json', '--time-limit', '3.0',
                      '--lp-method', 'bounded']]


@pytest.mark.parametrize('returncode,status', [(2, 'input_rejected'), (1, 'engine_error'), (-9, 'engine_error')])
def test_cli_failure_without_json_preserves_rejected_input(monkeypatch, tmp_path, returncode, status):
    monkeypatch.setattr(solve.subprocess, 'run', lambda *args, **kwargs:
                        SimpleNamespace(returncode=returncode, stdout='', stderr='error: invalid model'))
    result = solve._sovereign(tmp_path / 'model.mps', True, 3.0)
    assert result['status'] == status
    assert result['message'] == 'error: invalid model'
    assert result['objective'] is None
    assert result['primal'] == []


def test_nonoptimal_json_retains_incumbent(monkeypatch, tmp_path):
    record = {'status': 'time_limit', 'objective': 12.0, 'primal': [1.0, 2.0],
              'best_bound': 10.0, 'gap': 1.0 / 6.0}
    monkeypatch.setattr(solve.subprocess, 'run', lambda *args, **kwargs:
                        SimpleNamespace(returncode=1, stdout=json.dumps(record), stderr=''))
    result = solve._sovereign(tmp_path / 'model.mps', True, 3.0)
    for key, value in record.items():
        assert result[key] == value
