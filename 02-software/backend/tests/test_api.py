import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app
import limits
import solve


INFEASIBLE_MIP = """NAME TEST
ROWS
 N OBJ
 G LOWER
 L UPPER
COLUMNS
 MARK0000 'MARKER' 'INTORG'
 X OBJ 1 LOWER 1
 X UPPER 1
 MARK0001 'MARKER' 'INTEND'
RHS
 RHS1 LOWER 2 UPPER 1
BOUNDS
 BV BND X
ENDATA
"""
UNBOUNDED_LP = """NAME TEST
ROWS
 N OBJ
COLUMNS
 X OBJ -1
RHS
BOUNDS
 LO BND X 0
ENDATA
"""


@pytest.fixture
def client():
    with TestClient(app.app) as connection:
        yield connection


def test_discovery_and_docs(client):
    assert client.get('/health').json() == {'ok': True, 'engine': 'reference'}
    assert len(client.get('/examples').json()['examples']) == 3
    assert client.get('/capabilities').json()['solver']['name'] == 'HiGHS'
    assert client.get('/docs').status_code == 200
    assert '/solve' in client.get('/openapi.json').json()['paths']


def test_real_refinery_and_sensitivity(client):
    plan = client.post('/refinery/plan').json()
    assert plan['status'] == 'optimal'
    assert plan['profit'] == pytest.approx(6.588421476681447)
    assert (plan['rows'], plan['columns']) == (40, 57)
    assert len(plan['names']) == len(plan['primal']) == 57
    low_sulfur = client.post('/solve', json={'example': 'marco_low_sulfur'}).json()
    assert low_sulfur['status'] == 'optimal'
    assert low_sulfur['objective'] == pytest.approx(0)
    sweep = client.post('/refinery/sensitivity', json={'values': [3.4, 3.5, 3.45]}).json()
    assert sweep['complete'] and sweep['monotone']
    assert [p['sulfur_limit'] for p in sweep['curve']] == [3.5, 3.45, 3.4]
    assert [p['profit'] for p in sweep['curve']] == pytest.approx([plan['profit'], 0, 0])
    assert sweep['break_even_between'] == [3.5, 3.45]


def test_real_integer_model_and_relaxation(client):
    integer = client.post('/solve', json={'example': 'production_lotsizing', 'integer': True}).json()
    assert integer['status'] == 'optimal'
    assert integer['objective'] == pytest.approx(762)
    assert integer['gap'] == 0
    assert all(abs(integer['primal'][i] - round(integer['primal'][i])) < 1e-8 for i in range(2, 18, 3))
    relaxed = client.post('/solve', json={'example': 'production_lotsizing'}).json()
    assert relaxed['status'] == 'optimal'
    assert relaxed['objective'] <= integer['objective']
    assert relaxed['message'] == 'integrality relaxed on request'


@pytest.mark.parametrize('model,integer,status', [
    (INFEASIBLE_MIP, True, 'infeasible'),
    (UNBOUNDED_LP, False, 'unbounded'),
    ('not an MPS file', False, 'input_rejected'),
])
def test_nonoptimal_results_are_valid_json(client, model, integer, status):
    response = client.post('/solve', json={'model': model, 'integer': integer})
    assert response.status_code == 200
    result = response.json()
    assert result['status'] == status
    json.dumps(result, allow_nan=False)
    if status != 'unbounded':
        assert result['objective'] is None
        assert result['primal'] == []


@pytest.mark.parametrize('path,body,code', [
    ('/solve', {}, 400),
    ('/solve', {'model': '  '}, 400),
    ('/solve', {'model': 'a', 'example': 'marco_refinery'}, 400),
    ('/solve', {'example': '../secret'}, 400),
    ('/solve', {'example': 'absent'}, 404),
    ('/solve', {'example': 'a' * 300}, 422),
    ('/solve', {'example': 'marco_refinery', 'time_limit': 0}, 422),
    ('/solve', {'example': 'marco_refinery', 'time_limit': -1}, 422),
    ('/refinery/sensitivity', {'values': []}, 422),
    ('/refinery/sensitivity', {'values': [3.5] * 13}, 422),
    ('/refinery/sensitivity', {'values': [-1]}, 422),
])
def test_reject_invalid_inputs(client, path, body, code):
    assert client.post(path, json=body).status_code == code


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity'])
@pytest.mark.parametrize('path,template', [
    ('/solve', '{{"example":"marco_refinery","time_limit":{}}}'),
    ('/refinery/sensitivity', '{{"values":[{}]}}'),
])
def test_nonfinite_input_does_not_crash_error_handler(client, path, template, value):
    response = client.post(path, content=template.format(value), headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    json.dumps(response.json(), allow_nan=False)


def test_upload_limit_counts_utf8_bytes(client, monkeypatch):
    monkeypatch.setattr(app, 'MAX_MODEL_BYTES', 10)
    assert client.post('/solve', json={'model': 'é' * 6}).status_code == 413
    assert client.post('/solve', content=json.dumps({'model': '\ud800'}),
                       headers={'Content-Type': 'application/json'}).status_code == 400


def test_body_limit_before_parsing_and_chunked_upload(client, monkeypatch):
    monkeypatch.setattr(limits, 'MAX_REQUEST_BYTES', 64)
    assert client.post('/solve', content=b'x' * 65).status_code == 413
    response = client.post('/solve', content=iter([b'x' * 32, b'y' * 33]))
    assert response.status_code == 413
    assert client.post('/solve', json={}).status_code == 400  # slot released
    assert client.post('/not-an-endpoint', content=b'x' * 64_001).status_code == 413


def test_busy_response_keeps_health_available_and_releases_slot(client, monkeypatch):
    entered, release = threading.Event(), threading.Event()

    def blocked(*args):
        entered.set()
        assert release.wait(5)
        return solve._empty('reference', 'time_limit', '')

    monkeypatch.setattr(solve, 'solve', blocked)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(client.post, '/refinery/plan')
        assert entered.wait(5)
        try:
            busy = client.post('/refinery/sensitivity', json={'values': [3.5]},
                               headers={'Origin': 'https://frontend.example'})
            assert busy.status_code == 429
            assert busy.headers['Retry-After'] == '2'
            assert busy.headers['Access-Control-Allow-Origin'] == '*'
            assert client.get('/health').status_code == 200
        finally:
            release.set()
        assert pending.result().status_code == 200
    assert client.post('/refinery/plan').status_code == 200


def test_incomplete_sweep_does_not_claim_monotonicity_or_break_even(client, monkeypatch):
    monkeypatch.setattr(app, 'SENSITIVITY_TIME_LIMIT', 0.01)
    response = client.post('/refinery/sensitivity', json={'values': [3.5, 3.4]}).json()
    assert response['complete'] is False
    assert response['monotone'] is None
    assert response['break_even_between'] is None
    assert len(response['curve']) == 2
    assert all(p['status'] == 'time_limit' for p in response['curve'])


def test_cors_preflight(client):
    response = client.options('/solve', headers={'Origin': 'https://frontend.example',
                                               'Access-Control-Request-Method': 'POST',
                                               'Access-Control-Request-Headers': 'content-type'})
    assert response.status_code == 200


def test_negative_zero_sulfur_is_valid(client):
    result = client.post('/refinery/sensitivity', json={'values': [-0.0]}).json()
    assert result['curve'][0]['status'] == 'optimal'


def test_model_dimension_limit_in_real_worker(client, monkeypatch):
    monkeypatch.setenv('MAX_ROWS', '1')
    result = client.post('/refinery/plan').json()
    assert result['status'] == 'input_rejected'
    assert result['profit'] is None


def test_hard_timeout_and_recovery(tmp_path, monkeypatch):
    sleeper = tmp_path / 'sleep.py'
    sleeper.write_text('import time; time.sleep(10)', encoding='utf-8')
    with monkeypatch.context() as patch:
        patch.setattr(solve, 'WORKER', sleeper)
        patch.setattr(solve, 'SOLVE_TIMEOUT_GRACE', 0.05)
        result = solve.solve(app.EXAMPLES / 'marco_refinery.mps', limit=0.01)
        assert result['status'] == 'time_limit'
        assert result['objective'] is None
    assert solve.solve(app.EXAMPLES / 'marco_refinery.mps')['status'] == 'optimal'


@pytest.mark.parametrize('script', ['raise SystemExit(1)', 'print("not json")'])
def test_worker_failure_is_structured(tmp_path, monkeypatch, script):
    worker = tmp_path / 'broken.py'
    worker.write_text(script, encoding='utf-8')
    monkeypatch.setattr(solve, 'WORKER', worker)
    assert solve.solve(app.EXAMPLES / 'marco_refinery.mps')['status'] == 'engine_error'


@pytest.mark.parametrize('engine', ['unknown', 'sovereign'])
def test_bad_engine_configuration_fails_startup(monkeypatch, engine):
    monkeypatch.setattr(solve, 'ENGINE', engine)
    monkeypatch.setattr(solve, 'BINARY', '/not/a/binary')
    with pytest.raises(RuntimeError):
        with TestClient(app.app):
            pass
