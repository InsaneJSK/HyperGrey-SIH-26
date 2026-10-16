"""Independent Python reader for the continuous quadratic subset used in V1.

This reference-only code shares no parser code with the C++ implementation.
It preserves coefficients below the HiGHS LP-reader filtering threshold.
"""
import math

def read(path,np,sparse):
    values=iter(word for line in path.read_text().splitlines() for word in line.split('#',1)[0].split())
    name,kind,sense=next(values),next(values),next(values)
    if kind[1]!='C' or kind[2] not in 'BLN' or kind[0] not in 'CDQ':raise ValueError('Unsupported reference QPLIB type')
    n=int(next(values));m=int(next(values)) if kind[2]=='L' else 0
    count=int(next(values));ri=[];ci=[];data=[]
    for _ in range(count):
        i,j=int(next(values))-1,int(next(values))-1;v=float(next(values))
        ri.append(i);ci.append(j);data.append(v if i==j else .5*v)
    lower=sparse.coo_matrix((data,(ri,ci)),shape=(n,n)).tocsc()
    h=lower+lower.T-sparse.diags(lower.diagonal())
    def vector(size,bounds=False):
        def numeric():
            v=float(next(values))
            return math.copysign(math.inf,v) if bounds and abs(v)>=infinity else v
        default=numeric();result=np.full(size,default)
        for _ in range(int(next(values))):
            j=int(next(values))-1;result[j]=numeric()
        return result
    c=vector(n);offset=float(next(values));ri=[];ci=[];data=[]
    if m:
        for _ in range(int(next(values))):
            i,j=int(next(values))-1,int(next(values))-1;v=float(next(values))
            ri.append(i);ci.append(j);data.append(v)
    a=sparse.coo_matrix((data,(ri,ci)),shape=(m,n)).tocsc()
    infinity=float(next(values))
    row_lower=vector(m,True) if m else np.empty(0)
    row_upper=vector(m,True) if m else np.empty(0)
    lo=vector(n,True) if kind[2]!='N' else np.full(n,-math.inf)
    up=vector(n,True) if kind[2]!='N' else np.full(n,math.inf)
    vector(n)
    if m:vector(m)
    vector(n)
    for _ in range(int(next(values))):next(values);next(values)
    for _ in range(int(next(values))):next(values);next(values)
    if list(values):raise ValueError('Trailing reference QPLIB content')
    return {'name':name,'hessian':h,'cost':c,'offset':offset,'matrix':a,'row_lower':row_lower,
            'row_upper':row_upper,'lower':lo,'upper':up,'sign':1 if sense=='minimize' else -1}
