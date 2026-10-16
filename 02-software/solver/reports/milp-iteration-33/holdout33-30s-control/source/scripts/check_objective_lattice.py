"""Independent exact algebra/rounding audit of emitted numerical lattice data.

HiGHS only reads the original model. Fraction arithmetic verifies the claimed
substitutions and every saved strengthening event, NOT the input LP bounds.
"""
from fractions import Fraction as F
from functools import reduce
import math
from pathlib import Path
import sys
from benchmark_lp import ROOT


def read(model):
    sys.path.insert(0, str(ROOT/'tools/reference/python'))
    import highspy
    h = highspy.Highs(); h.setOptionValue('output_flag', False)
    assert h.readModel(str(model)) != highspy.HighsStatus.kError
    h.ensureColwise(); lp = h.getLp()
    # The C++ MPS vector contract is first column occurrence. Check the
    # independent reader retained that order before comparing index telemetry.
    names, section, seen_names = [], None, set()
    for line in Path(model).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('*'): continue
        fields = line.split()
        if fields[0] in ('NAME','OBJSENSE','OBJNAME','ROWS','COLUMNS','RHS','RANGES','BOUNDS','ENDATA') and not line[0].isspace():
            section = fields[0]; continue
        if section == 'COLUMNS' and len(fields) > 1 and fields[1].strip("'\"") != 'MARKER' and fields[0] not in seen_names:
            names.append(fields[0]); seen_names.add(fields[0])
    assert names == list(lp.col_names_), 'Independent column order differs'
    rows = [dict() for _ in range(lp.num_row_)]
    a = lp.a_matrix_
    # Bind these Python lists once; each binding-property access can copy the
    # complete sparse array. This does not change coefficient order/arithmetic.
    starts, indices, values = a.start_, a.index_, a.value_
    for j in range(lp.num_col_):
        for k in range(starts[j], starts[j+1]):
            i = indices[k]; rows[i][j] = rows[i].get(j,F(0)) + F(float(values[k]))
    integer = [t == highspy.HighsVarType.kInteger for t in lp.integrality_]
    if not integer: integer = [False]*lp.num_col_
    return {'cost':[F(float(c)) for c in lp.col_cost_], 'offset':F(float(lp.offset_)),
            'sign':-1 if lp.sense_ == highspy.ObjSense.kMaximize else 1,
            'integer':integer, 'rows':rows, 'lower':list(lp.row_lower_), 'upper':list(lp.row_upper_)}


def verify(data, result):
    l = result['objective_lattice']; trace = l['trace']
    assert l['bound_calls'] >= l['bound_improvements'] >= len(trace)
    assert l['trace_truncated'] == (l['bound_improvements'] > len(trace))
    if not l['eligible']:
        assert not trace and not l['bound_calls'] and not l['substitutions']
        return {'eligible':False, 'reason':l['reason'], 'events_checked':0, 'all_checks_pass':True}
    assert l['enabled']
    costs = [data['sign']*c for c in data['cost']]
    assert all(c.denominator == 1 for c in costs)
    offset = data['sign']*data['offset']; coeff = costs.copy(); eliminated = set()
    for substitution in l['substitutions']:
        j,i = substitution['column'],substitution['row']
        assert 0 <= j < len(costs) and 0 <= i < len(data['rows'])
        assert j not in eliminated and not data['integer'][j] and costs[j]
        eliminated.add(j); row = data['rows'][i]; unit = row.get(j,F(0))
        assert abs(unit) == 1 and math.isfinite(data['lower'][i]) and data['lower'][i] == data['upper'][i]
        rhs = F(float(data['lower'][i])); assert rhs.denominator == 1
        for k,a in row.items():
            assert a.denominator == 1
            if k != j and a: assert data['integer'][k]
        factor = costs[j]/unit; offset += factor*rhs; coeff[j] = F(0)
        for k,a in row.items():
            if k != j: coeff[k] -= factor*a
    assert all(data['integer'][j] or coeff[j] == 0 for j in range(len(coeff)))
    assert all(c.denominator == 1 for c in coeff)
    step = reduce(math.gcd,(abs(int(c)) for c in coeff),0)
    assert step > 0 and F(l['step']) == step
    assert F(l['offset_minimization']) == offset
    assert list(map(F,l['coefficients_minimization'])) == coeff
    for event in trace:
        b,a = F(event['before_minimization']),F(event['after_minimization'])
        # Exact next possible value from the reported INPUT bound. Floating
        # implementation may publish less due to its conservative guards.
        next_grid = offset + step*math.ceil((b-offset)/step)
        assert b < a <= next_grid, (b,a,next_grid)
    return {'eligible':True, 'step':step, 'offset':str(offset), 'substitutions_checked':len(eliminated),
            'events_checked':len(trace), 'trace_truncated':l['trace_truncated'], 'all_checks_pass':True,
            'scope':'Exact parsed-model algebra and saved rounding events; LP input bounds remain numerical.'}


def check(model, result):
    return verify(read(model),result)
