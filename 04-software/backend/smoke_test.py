"""Check a deployed EC2 API, or a local run, using only Python's standard library.

Verifies the numbers and not just the status codes: the refinery plan must be
optimal with a positive profit, tightening the sulfur specification must never
raise profit, and an integer model must come back solved.

    python smoke_test.py https://api.example.com
    python smoke_test.py http://localhost:8000

Prints ALL PASS and exits 0 when the service is healthy.
"""
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000').rstrip('/')
TIMEOUT = 45
failures = []


def check(label, condition, detail=''):
    print(f'  {"PASS" if condition else "FAIL"}  {label}' + (f'  {detail}' if detail else ''))
    if not condition:
        failures.append(label)


class Response:
    def __init__(self, status, body):
        self.status_code = status
        self.body = body

    def json(self):
        return json.loads(self.body)


def request(path, body=None):
    payload = json.dumps(body).encode() if body is not None else None
    req = Request(BASE + path, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=TIMEOUT) as result:
            return Response(result.status, result.read())
    except HTTPError as error:
        return Response(error.code, error.read())
    except (URLError, TimeoutError) as error:
        sys.exit(f'  FAIL  cannot reach {BASE + path}: {error}')


def get(path):
    return request(path)


def post(path, body=None):
    return request(path, body or {})


print(f'Checking {BASE}\n')
r = get('/health')

check('/health answers', r.status_code == 200, f'HTTP {r.status_code}')
body = r.json() if r.status_code == 200 else {}
check('/health reports ok', body.get('ok') is True, str(body))
check('engine is the reference engine', body.get('engine') == 'reference', repr(body.get('engine')))
r = get('/capabilities')
check('capabilities identify HiGHS', r.status_code == 200 and r.json().get('solver', {}).get('name') == 'HiGHS')
check('interactive documentation is available', get('/docs').status_code == 200)

r = get('/examples')
names = r.json().get('examples', []) if r.status_code == 200 else []
check('three examples are bundled', len(names) == 3, str(names))

r = post('/refinery/plan')
plan = r.json() if r.status_code == 200 else {}
check('refinery plan solves to optimal', plan.get('status') == 'optimal', repr(plan.get('status')))
check('refinery plan has a positive profit', isinstance(plan.get('profit'), (int, float)) and plan['profit'] > 0,
      repr(plan.get('profit')))
check('refinery model is the expected size', (plan.get('rows'), plan.get('columns')) == (40, 57),
      f"{plan.get('rows')}x{plan.get('columns')}")

r = post('/refinery/sensitivity', {'values': [3.5, 3.45, 3.4]})
sweep = r.json() if r.status_code == 200 else {}
curve = sweep.get('curve', [])
check('sensitivity returns one point per value', len(curve) == 3, f'{len(curve)} points')
check('profit never rises as the specification tightens', sweep.get('monotone') is True,
      f"monotone={sweep.get('monotone')}")
for point in curve:
    print(f'        sulfur {point["sulfur_limit"]:<6} profit {point["profit"]!r:>20}  {point["status"]}')

r = post('/solve', {'example': 'production_lotsizing', 'integer': True})
solved = r.json() if r.status_code == 200 else {}
check('integer model solves', solved.get('status') == 'optimal', repr(solved.get('status')))
check('integer model returns the expected objective', abs(solved.get('objective', 0) - 762) < 1e-6 if solved.get('objective') is not None else False, repr(solved.get('objective')))

check('a bad example name is refused', post('/solve', {'example': '../../etc/passwd'}).status_code == 400)
check('an empty request is refused', post('/solve', {}).status_code == 400)
check('a negative time limit is refused', post('/solve', {'example': 'marco_refinery', 'time_limit': -1}).status_code == 422)
check('a missing example returns 404', post('/solve', {'example': 'not_here'}).status_code == 404)

print()
if failures:
    print(f'{len(failures)} CHECK(S) FAILED: ' + '; '.join(failures))
    sys.exit(1)
print('ALL PASS')
