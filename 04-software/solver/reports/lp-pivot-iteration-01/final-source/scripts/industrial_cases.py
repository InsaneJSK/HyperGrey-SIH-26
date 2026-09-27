"""Generate literature-based LP cases and a labelled synthetic planning MILP.

Numerical inputs: GAMS MARCO and TRNSPORT model-library pages, retrieved 2026-09-14.
The equations are independently assembled here; no GAMS or solver is used.
"""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

class MpsModel:
    def __init__(self,name): self.name=name;self.vars={};self.rows=[]
    def var(self,name,cost=0,lower=0,upper=None,integer=False):
        self.vars[name]=(cost,lower,upper,integer);return name
    def row(self,coefficients,sense,rhs): self.rows.append((coefficients,sense,rhs))
    def write(self,path):
        lines=[f'NAME {self.name}','ROWS',' N OBJ']+[f' {sense} R{i}' for i,(_,sense,_) in enumerate(self.rows)]+['COLUMNS']
        for name,(cost,_,_,_) in self.vars.items():
            lines.append(f' {name} OBJ {cost:.17g}')
            for i,(row,_,_) in enumerate(self.rows):
                if row.get(name,0):lines.append(f' {name} R{i} {row[name]:.17g}')
        lines+=['RHS']+[f' B R{i} {rhs:.17g}' for i,(_,_,rhs) in enumerate(self.rows)]+['BOUNDS']
        for name,(_,lo,up,integer) in self.vars.items():
            if integer and lo==0 and up==1:lines.append(f' BV B {name}')
            else:
                if lo is None:lines.append(f' MI B {name}')
                else:lines.append(f' {"LI" if integer else "LO"} B {name} {lo:.17g}')
                if up is not None:lines.append(f' {"UI" if integer else "UP"} B {name} {up:.17g}')
        lines+=['ENDATA'];path.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def refinery(sulfur=3.5):
    model=MpsModel('MARCO_REFORMULATED')
    crude=['mid','west'];process=['dist','reform','crackdist','crackoil','hydro']
    intermediates=['butane','gas','naphtha','distillate','gasoil','resid','reformgas','fuelgas','crackgas','crackoil','hydrores']
    allowed={'premium':['butane','gas','reformgas','crackgas','naphtha'],'regular':['butane','gas','reformgas','crackgas','naphtha'],
             'distillate':['distillate','naphtha','gasoil','crackoil'],'fueloil':['gasoil','resid','crackoil','hydrores'],'fuelgas':['fuelgas']}
    yields={
      ('mid','dist'):{'gas':.236,'naphtha':.223,'distillate':.087,'gasoil':.111,'resid':.315,'fuelgas':.029},
      ('west','dist'):{'gas':.180,'naphtha':.196,'distillate':.073,'gasoil':.091,'resid':.443,'fuelgas':.017},
      ('mid','reform'):{'naphtha':-1,'reformgas':.807,'fuelgas':.129},
      ('west','reform'):{'naphtha':-1,'reformgas':.836,'fuelgas':.099},
      ('mid','crackdist'):{'distillate':-1,'fuelgas':.30,'crackgas':.59,'crackoil':.21},
      ('west','crackdist'):{'distillate':-1,'fuelgas':.36,'crackgas':.58,'crackoil':.15},
      ('mid','crackoil'):{'gasoil':-1,'fuelgas':.31,'crackgas':.59,'crackoil':.22},
      ('west','crackoil'):{'gasoil':-1,'fuelgas':.38,'crackgas':.60,'crackoil':.15},
      ('mid','hydro'):{},('west','hydro'):{'resid':-1,'hydrores':.97}}
    op=dict(zip(process,[.1,.15,.8,.08,.1]));prices={'premium':10.5,'regular':9.1,'distillate':7.7,'fueloil':6.65,'fuelgas':1.5}
    for cr,price in zip(crude,[7.5,6.5]):
        model.var(f'u_{cr}',price,upper=200);model.var(f'butane_{cr}',6.75)
        for pr in process:model.var(f'z_{cr}_{pr}',op[pr])
        model.row({f'u_{cr}':1,f'z_{cr}_dist':-1},'G',0)
        for cf,streams in allowed.items():
            for ci in streams:model.var(f'w_{cr}_{ci}_{cf}')
        for ci in intermediates:
            row={f'z_{cr}_{pr}':yields[cr,pr].get(ci,0) for pr in process}
            if ci=='butane':row[f'butane_{cr}']=1
            row.update({f'w_{cr}_{ci}_{cf}':-1 for cf,streams in allowed.items() if ci in streams})
            model.row(row,'G',0)
    for prs,capacity in [(['dist'],100),(['reform'],20),(['crackdist','crackoil'],30)]:
        model.row({f'z_{cr}_{pr}':1 for cr in crude for pr in prs},'L',capacity)
    for cf,streams in allowed.items():
        model.var(f'sale_{cf}',-prices[cf]);row={f'sale_{cf}':1}
        row.update({f'w_{cr}_{ci}_{cf}':-1 for cr in crude for ci in streams});model.row(row,'E',0)
    octane={'gas':78.5,'naphtha':65,'reformgas':104,'crackgas':93.7,'butane':91.8}
    vapor={'gas':18.4,'naphtha':6.54,'reformgas':2.57,'crackgas':6.9,'butane':199.2}
    density={'mid':{'naphtha':272,'distillate':292,'gasoil':295,'crackoil':294.4,'resid':343},
             'west':{'naphtha':272,'distillate':297.6,'gasoil':303.3,'crackoil':299.1,'resid':365,'hydrores':365}}
    sulfur_data={'mid':{'naphtha':.283,'distillate':.526,'gasoil':.980,'crackoil':.353,'resid':4.7},
                 'west':{'naphtha':1.48,'distillate':2.83,'gasoil':5.05,'crackoil':1.31,'resid':11,'hydrores':6}}
    for cf,minimum in [('premium',90),('regular',86)]:
        for attributes,sense,limit in [(octane,'G',minimum),(vapor,'L',12.7)]:
            row={f'w_{cr}_{ci}_{cf}':attributes[ci] for cr in crude for ci in allowed[cf]};row[f'sale_{cf}']=-limit;model.row(row,sense,0)
    for cf,density_limit,sulfur_limit in [('distillate',306,.5),('fueloil',352,sulfur)]:
        for attributes,limit in [(density,density_limit),(sulfur_data,sulfur_limit)]:
            row={f'w_{cr}_{ci}_{cf}':attributes[cr].get(ci,0) for cr in crude for ci in allowed[cf]};row[f'sale_{cf}']=-limit;model.row(row,'L',0)
    return model

def transportation():
    model=MpsModel('DANTZIG_TRANSPORT')
    for i,distances in enumerate([[2.5,1.7,1.8],[2.5,1.8,1.4]]):
        for j,d in enumerate(distances):model.var(f'x{i}_{j}',.09*d)
        model.row({f'x{i}_{j}':1 for j in range(3)},'L',[350,600][i])
    for j,demand in enumerate([325,300,275]):model.row({f'x{i}_{j}':1 for i in range(2)},'G',demand)
    return model

def lotsizing():
    model=MpsModel('SYNTHETIC_MULTIPERIOD_PRODUCTION')
    demand=[18,32,24,40,16,30];capacity=50
    for t in range(6):model.var(f'produce{t}',[4,5,3,6,4,5][t],upper=capacity);model.var(f'inventory{t}',.5,upper=100);model.var(f'on{t}',25,upper=1,integer=True)
    for t in range(6):
        row={f'produce{t}':1,f'inventory{t}':-1}
        if t:row[f'inventory{t-1}']=1
        model.row(row,'E',demand[t]);model.row({f'produce{t}':1,f'on{t}':-capacity},'L',0)
    model.row({'inventory5':1},'E',0);return model

def main():
    folder=ROOT/'examples/industrial';folder.mkdir(parents=True,exist_ok=True)
    cases=[('marco_refinery',refinery(),False,'https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html'),
           ('marco_low_sulfur',refinery(3.4),False,'https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html'),
           ('transport_dantzig',transportation(),False,'https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_trnsport.html'),
           ('production_lotsizing',lotsizing(),True,None)]
    records=[]
    for name,model,milp,source in cases:
        path=folder/(name+'.mps');model.write(path)
        records.append({'name':name,'milp':milp,'source':source,'synthetic_data':source is None,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'variables':list(model.vars),'rows':len(model.rows)})
    (folder/'manifest.json').write_text(json.dumps(records,indent=2)+'\n');print('Generated',len(records),'industrial cases')

if __name__=='__main__':main()
