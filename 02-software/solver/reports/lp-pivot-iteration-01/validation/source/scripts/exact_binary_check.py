"""Independent literal-MPS / Python-integer proof check. No solver is called.

This is a recomputation checker, not a compact proof-trace format. Unsupported
syntax or nonintegral literal data are rejected, never rounded into eligibility.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

if not __debug__:raise RuntimeError('Exact verification must not run with Python optimization disabling checks')


def number(token):
    value=Fraction(token.replace('D','E').replace('d','e'))
    if value.denominator!=1:raise ValueError('Nonintegral literal MPS value: '+token)
    return value.numerator


def parse_mps(text):
    rows={};columns={};rhs={};ranges={};sets={};bound_columns=set();section=None;objective=None;previous=None;integer=False;maximize=False;ended=False
    for raw in text.splitlines():
        if not raw.strip() or raw.startswith('*'):continue
        t=raw.split('$',1)[0].split()
        if not t:continue
        if ended:raise ValueError('Data after ENDATA')
        if t[0]=='NAME' and section is None:section='NAME';continue
        if t==['ENDATA']:ended=True;continue
        if t[0] in ('ROWS','COLUMNS','RHS','RANGES','BOUNDS','OBJSENSE') and len(t)==1:section=t[0];continue
        if t[0]=='OBJSENSE' and len(t)==2:section='OBJSENSE';t=t[1:]
        if section=='OBJSENSE':
            if len(t)!=1 or t[0] not in ('MIN','MAX'):raise ValueError('Unsupported objective sense')
            maximize=t[0]=='MAX'
        elif section=='ROWS':
            if len(t)!=2 or t[0] not in ('N','L','E','G') or t[1] in rows or t[1]==objective:raise ValueError('Invalid row')
            if t[0]=='N':
                if objective is not None:raise ValueError('Multiple objective rows')
                objective=t[1]
            else:rows[t[1]]=t[0]
        elif section=='COLUMNS':
            if len(t)==3 and t[1]=="'MARKER'":
                if t[2] not in ("'INTORG'","'INTEND'"):raise ValueError('Invalid marker')
                value=t[2]=="'INTORG'"
                if integer==value:raise ValueError('Invalid marker scope')
                integer=value;continue
            if len(t) in (2,4):
                if previous is None:raise ValueError('Missing column name')
                t=[previous]+t
            if len(t) not in (3,5):raise ValueError('Invalid column record')
            name=t[0];previous=name
            if name not in columns:columns[name]={'integer':integer,'lower':0,'upper':None,'cost':0,'rows':{}}
            col=columns[name]
            if col['integer']!=integer:raise ValueError('Inconsistent column markers')
            for key,token in zip(t[1::2],t[2::2]):
                value=number(token)
                if key==objective:col['cost']+=value
                elif key in rows:col['rows'][key]=col['rows'].get(key,0)+value
                else:raise ValueError('Unknown row')
        elif section in ('RHS','RANGES'):
            if len(t) in (2,4):t=['__blank__']+t
            if len(t) not in (3,5):raise ValueError('Invalid RHS/range')
            if sets.setdefault(section,t[0])!=t[0]:raise ValueError('Multiple RHS/range sets')
            target=rhs if section=='RHS' else ranges
            for key,token in zip(t[1::2],t[2::2]):
                if key in target or key not in rows and not(section=='RHS' and key==objective):raise ValueError('Invalid RHS/range row')
                target[key]=number(token)
        elif section=='BOUNDS':
            if len(t) not in (3,4) or t[2] not in columns:raise ValueError('Invalid bound')
            kind,group,name=t[:3];col=columns[name]
            bound_columns.add(name)
            if sets.setdefault(section,group)!=group:raise ValueError('Multiple bound sets')
            valued=kind in ('LO','UP','FX','LI','UI')
            if len(t)!=(4 if valued else 3):raise ValueError('Invalid bound value')
            value=number(t[3]) if valued else None
            if kind in ('LO','LI'):col['lower']=value
            elif kind in ('UP','UI'):col['upper']=value
            elif kind=='FX':col['lower']=col['upper']=value
            elif kind=='BV':col.update(lower=0,upper=1,integer=True)
            elif kind=='FR':col.update(lower=None,upper=None)
            elif kind=='MI':col['lower']=None
            elif kind=='PL':col['upper']=None
            else:raise ValueError('Unsupported bound type')
            if kind in ('LI','UI'):col['integer']=True
        else:raise ValueError('Unsupported MPS syntax')
    if not ended or integer or not columns or objective is None:raise ValueError('Incomplete MPS')
    # Marker-only integers with no bound record have the MPS binary default.
    # Explicit LO/LI-only columns keep their unspecified upper side unbounded.
    for name,col in columns.items():
        if col['integer'] and name not in bound_columns:col['upper']=1
    names=list(columns);rnames=list(rows);matrix=[];lower=[];upper=[]
    for row,sense in rows.items():
        b=rhs.get(row,0);lo=b if sense in ('G','E') else None;up=b if sense in ('L','E') else None
        if row in ranges:
            r=ranges[row]
            if sense=='L':lo=b-abs(r)
            elif sense=='G':up=b+abs(r)
            elif r>=0:up=b+r
            else:lo=b+r
        lower.append(lo);upper.append(up);matrix.append([columns[name]['rows'].get(row,0) for name in names])
    return {'names':names,'rows':matrix,'row_lower':lower,'row_upper':upper,'maximize':maximize,'offset':-rhs.get(objective,0),
            **{key:[columns[name][key] for name in names] for key in ('cost','lower','upper','integer')}}


def reduce_model(p):
    n=len(p['names']);m=len(p['rows']);assert n<=128 and 1<=m<=32
    base=[0]*n;bits=[];continuous=[]
    for j,(lo,up,integer) in enumerate(zip(p['lower'],p['upper'],p['integer'])):
        assert lo is None or up is None or lo<=up
        if lo is not None and lo==up:base[j]=lo
        elif integer:
            assert (lo,up)==(0,1);bits.append(j)
        else:continuous.append(j)
    assert 1<=len(bits)<=36
    for j in continuous:assert sum(row[j]!=0 for row in p['rows'])==1
    sign=-1 if p['maximize'] else 1
    offset=sign*(p['offset']+sum(c*x for c,x in zip(p['cost'],base)));cost=[sign*p['cost'][j] for j in bits]
    matrix=[];lower=[];upper=[]
    for i,row in enumerate(p['rows']):
        fixed=sum(a*x for a,x in zip(row,base));lo=p['row_lower'][i];up=p['row_upper'][i]
        lo=None if lo is None else lo-fixed;up=None if up is None else up-fixed
        free=[j for j in continuous if row[j]];assert len(free)<=1
        coeff=[row[j] for j in bits]
        if free:
            j=free[0];c=row[j];assert c in (-1,1) and lo is not None and lo==up
            rhs=lo;yl,yu=p['lower'][j],p['upper'][j]
            low,high=(yl,yu) if c==1 else (None if yu is None else -yu,None if yl is None else -yl)
            lo=None if high is None else rhs-high;up=None if low is None else rhs-low
            factor=sign*p['cost'][j]*c;offset+=factor*rhs;cost=[v-factor*a for v,a in zip(cost,coeff)]
        matrix.append(coeff);lower.append(lo);upper.append(up)
    return {'base':base,'bits':bits,'continuous':continuous,'a':matrix,'lo':lower,'up':upper,'cost':cost,'offset':offset,'sign':sign}


def witness(p,x):
    assert len(x)==len(p['names']) and all(type(v) is int for v in x)
    for v,lo,up in zip(x,p['lower'],p['upper']):assert (lo is None or v>=lo) and (up is None or v<=up)
    for row,lo,up in zip(p['rows'],p['row_lower'],p['row_upper']):
        value=sum(a*v for a,v in zip(row,x));assert (lo is None or value>=lo) and (up is None or value<=up)
    return p['offset']+sum(c*v for c,v in zip(p['cost'],x))


def halves(a,cost,indices):
    states=[(tuple(0 for _ in a),0,0)]
    for bit in indices:
        column=tuple(row[bit] for row in a)
        states += [(tuple(x+y for x,y in zip(weights,column)),value+cost[bit],mask|(1<<bit)) for weights,value,mask in states]
    return states


def zero_objective_exclusion(p,reduced,claim):
    # Separate hash-join argument: a nonnegative INTEGER objective below1 must
    # be0. Positive-cost variables must therefore be zero. This is structural,
    # not a named-model/known-answer shortcut. Unit recourse implies integrality.
    if claim!=1 or p['maximize'] or p['offset']!=0 or any(c<0 for c in p['cost']):return None
    if any(lo is None or lo<0 for lo in p['lower']):return None
    if any(p['cost'][j]<=0 for j in reduced['continuous']):return None
    if any(lo is None or lo!=up for lo,up in zip(p['row_lower'],p['row_upper'])):return None
    if any(c>0 and lo>0 for c,lo in zip(p['cost'],p['lower'])):return {'method':'nonnegative_integral_objective_lower_bound','zero_excluded':True}
    base=reduced['base'];bits=[j for j in reduced['bits'] if p['cost'][j]==0]
    a=[[row[j] for j in bits] for row in p['rows']];rhs=tuple(b-sum(v*x for v,x in zip(row,base)) for row,b in zip(p['rows'],p['row_lower']))
    left=halves(a,[0]*len(bits),range(0,len(bits),2));right=halves(a,[0]*len(bits),range(1,len(bits),2));keys={row for row,_,_ in left}
    for row,_,_ in right:
        assert tuple(b-v for b,v in zip(rhs,row)) not in keys,'Found a zero-objective assignment contradicting claimed optimum1'
    return {'method':'nonnegative_integer_objective_plus_exact_equality_hash_join','zero_excluded':True,'left_states':len(left),'right_states':len(right)}


def range_join(reduced,claim):
    # Independent immutable Python tree, different half split and leaf size.
    # All arithmetic uses unbounded Python integers, not the core's int64 engine.
    a,cost=reduced['a'],reduced['cost'];n=len(cost);m=len(a)
    left=halves(a,cost,range(0,n,2));right=halves(a,cost,range(1,n,2));visited=0
    def tree(points,depth=0):
        axes=list(zip(*(p[0] for p in points)));low=tuple(map(min,axes));high=tuple(map(max,axes));best=min(points,key=lambda p:p[1])
        if len(points)<=64:return low,high,best,points,None,None
        axis=max(range(m),key=lambda i:high[i]-low[i]);points.sort(key=lambda p:p[0][axis]);middle=len(points)//2
        return low,high,best,None,tree(points[:middle],depth+1),tree(points[middle:],depth+1)
    root=tree(left)
    def better(node,weights,value):
        nonlocal visited
        visited+=1;low,high,best,points,lchild,rchild=node
        if claim is not None and reduced['offset']+value+best[1]>=claim:return False
        for i,(lo,up) in enumerate(zip(reduced['lo'],reduced['up'])):
            if lo is not None and high[i]+weights[i]<lo or up is not None and low[i]+weights[i]>up:return False
        if points is not None:
            for lhs,c,_ in points:
                if claim is not None and reduced['offset']+value+c>=claim:continue
                if all((lo is None or x+y>=lo) and (up is None or x+y<=up) for x,y,lo,up in zip(lhs,weights,reduced['lo'],reduced['up'])):return True
            return False
        return better(lchild,weights,value) or better(rchild,weights,value)
    for weights,value,_ in right:assert not better(root,weights,value),'Independent integer search found a contradictory feasible point'
    return {'method':'independent_python_integer_range_join','left_states':len(left),'right_states':len(right),'query_nodes':visited}


def check(p,ours):
    proof=ours['binary_proof'];assert ours['binary_proof_enabled'] and ours['binary_proof_attempts']==1
    assert proof['version']==1 and proof['arithmetic']=='checked_int64'
    assert proof['eligible'] is True and proof['verified'] is True and proof['completed'] is True
    reduced=reduce_model(p);assert proof['binary_indices']==reduced['bits']
    count=len(reduced['bits']);assert proof['left_states']==1<<(count//2) and proof['right_states']==1<<(count-count//2)
    assert 0<=proof['query_nodes']<=proof['work']<=proof['work_limit'] and ours['nodes']==1 and ours['lp_iterations']==0
    if proof['feasible']:
        assert proof['status']==ours['status']=='optimal' and proof['primal']==ours['primal']
        value=witness(p,proof['primal']);claim=reduced['sign']*value
        assert value==ours['objective']==ours['best_bound'] and ours['gap']==0 and claim==proof['objective_minimization']
        result=zero_objective_exclusion(p,reduced,claim) or range_join(reduced,claim)
    else:
        assert proof['status']==ours['status']=='infeasible' and not proof['primal'] and not ours['primal'] and ours['objective'] is None
        claim=None;result=range_join(reduced,None)
    return {**result,'normalized_objective':claim,'literal_integer_model_verified':True,'all_checks_pass':True}


def main(args):
    start=time.perf_counter();p=parse_mps(args.model.read_text());ours=json.loads(args.result.read_text());result=check(p,ours)
    result.update(model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),result_sha256=hashlib.sha256(args.result.read_bytes()).hexdigest(),
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.perf_counter()-start)
    if args.output:
        with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('model',type=Path);parser.add_argument('result',type=Path);parser.add_argument('--output',type=Path)
    main(parser.parse_args())
