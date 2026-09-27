"""Independent exact cut verification using HiGHS only as an MPS reader."""
import json
import sys
from pathlib import Path
from benchmark_lp import ROOT

if not __debug__:raise RuntimeError('Cut verifier requires assertions')

def verify_rows(rows,lows,ups,integer,lower,upper,cuts):
    cache={};checked=0;assignments=0
    for cut in cuts:
        r=cut['source_row'];side=cut['side'];assert type(r) is int and 0<=r<len(rows) and side in (0,1)
        source=rows[r];indices=[j for j,v in source];assert len(set(indices))==len(indices) and 2<=len(indices)<=20
        assert all(integer[j] and lower[j]>=0 and upper[j]<=1 for j in indices)
        terms=dict(cut['row']);assert len(terms)==len(cut['row']) and set(terms)<=set(indices)
        assert all(type(c) in (int,float) and c==int(c) for c in terms.values())
        rhs=cut['rhs'];assert type(rhs) in (int,float) and rhs==int(rhs)
        key=(r,side)
        if key not in cache:
            bound=lows[r] if side else ups[r]
            ratios=[float(v).as_integer_ratio() for j,v in source]+[float(bound).as_integer_ratio()]
            denominator=max(d for v,d in ratios);scaled=[v*(denominator//d) for v,d in ratios]
            activity=[0]*(1<<len(indices));feasible=[]
            for mask in range(len(activity)):
                if mask:
                    bit=mask&-mask;j=bit.bit_length()-1;activity[mask]=activity[mask^bit]+scaled[j]
                if (activity[mask]>=scaled[-1] if side else activity[mask]<=scaled[-1]):feasible.append(mask)
            cache[key]=feasible
        feasible=cache[key];assert cut['assignments']==len(feasible)
        coefficients=[int(terms.get(j,0)) for j in indices];value=[0]*(1<<len(indices))
        for mask in range(1,len(value)):
            bit=mask&-mask;value[mask]=value[mask^bit]+coefficients[bit.bit_length()-1]
        assert all(value[mask]<=rhs for mask in feasible),'Invalid lifted cover'
        checked+=1;assignments+=len(feasible)
    return {'all_pass':True,'cuts_checked':checked,'feasible_assignments_checked':assignments,'source_sides':len(cache),
            'arithmetic':'Python unbounded integers, exact binary64 ratios from independent MPS reader',
            'limitation':'Verifies parsed binary64 rows, not arbitrary-precision original decimal literals; no reference optimizer run.'}

def check(model,result):
    sys.path.insert(0,str(ROOT/'tools/reference/python'));import highspy
    h=highspy.Highs();h.setOptionValue('output_flag',False)
    assert h.readModel(str(model))!=highspy.HighsStatus.kError
    h.ensureRowwise();p=h.getLp();a=p.a_matrix_
    rows=[list(zip(a.index_[a.start_[i]:a.start_[i+1]],a.value_[a.start_[i]:a.start_[i+1]])) for i in range(p.num_row_)]
    integer=[v!=highspy.HighsVarType.kContinuous for v in p.integrality_]
    return verify_rows(rows,p.row_lower_,p.row_upper_,integer,p.col_lower_,p.col_upper_,result.get('lifted_cover_trace',[]))

if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1]),json.loads(Path(sys.argv[2]).read_text())),indent=2))
