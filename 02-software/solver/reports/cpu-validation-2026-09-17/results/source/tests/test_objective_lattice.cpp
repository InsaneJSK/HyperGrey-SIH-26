#include "milp.hpp"
#include <iostream>
#include <random>
#include <sstream>
using namespace sovereign;
using detail::detect_objective_lattice;
using detail::round_objective_bound;
void ensure(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
LinearProblem vars(std::size_t n){LinearProblem p;p.names.resize(n);p.cost.assign(n,1);p.lower.assign(n,-2);p.upper.assign(n,2);p.integer.assign(n,true);return p;}
int main(){try{
    auto p=vars(3);p.cost={6,-12,0};p.offset=.25;
    auto l=detect_objective_lattice(p);ensure(l.eligible&&l.step==6&&l.offset==.25,"Direct lattice/offset");
    p.maximize=true;l=detect_objective_lattice(p);ensure(l.offset==-.25&&l.coefficients[0]==-6,"Max normalization");
    p.integer[2]=false;ensure(detect_objective_lattice(p).eligible,"Zero-cost continuous term");
    p.cost[2]=1;ensure(!detect_objective_lattice(p).eligible,"Unsupported continuous objective");
    p.rows={{{0,-5},{1,10},{2,-1}}};p.row_lower=p.row_upper={3};
    l=detect_objective_lattice(p);ensure(l.eligible&&l.step==1&&l.offset==2.75&&l.coefficients[0]==-1&&l.coefficients[1]==2,"Negative-unit definition");
    p.cost={0,0,1};p.maximize=false;l=detect_objective_lattice(p);
    ensure(l.step==5&&l.offset==-2.75&&l.coefficients[0]==-5,"Derived step five");
    p.rows[0].push_back({0,5});p.rows[0].push_back({0,-5});ensure(detect_objective_lattice(p).step==5,"Duplicate integer terms");
    auto valid=p;
    p.row_upper[0]=std::nextafter(3.,4.);ensure(!detect_objective_lattice(p).eligible,"Near equality accepted");p=valid;
    p.rows[0][2].second=-2;ensure(!detect_objective_lattice(p).eligible,"Nonunit accepted");p=valid;
    p.integer[0]=false;ensure(!detect_objective_lattice(p).eligible,"Multiple continuous accepted");p=valid;
    p.rows[0][0].second=-5.0000000001;ensure(!detect_objective_lattice(p).eligible,"Fractional definition accepted");p=valid;
    p.row_lower[0]=p.row_upper[0]=.5;ensure(!detect_objective_lattice(p).eligible,"Fractional RHS accepted");p=valid;
    p.cost[0]=.5;ensure(!detect_objective_lattice(p).eligible,"Fractional cost accepted");p=valid;
    p.offset=.1;ensure(!detect_objective_lattice(p).eligible,"Unsupported offset accepted");p=valid;
    p.cost[0]=std::ldexp(1.,41);ensure(!detect_objective_lattice(p).eligible,"Large coefficient accepted");p=valid;
    p.cost[2]=std::ldexp(1.,40);ensure(!detect_objective_lattice(p).eligible,"Product overflow accepted");p=valid;
    p.offset=std::ldexp(1.,35);ensure(!detect_objective_lattice(p).eligible,"Offset overflow accepted");p=valid;
    p.cost={5,-10,1};ensure(!detect_objective_lattice(p).eligible,"Constant transformed objective not rejected");
    p=vars(2);p.cost={0,0};ensure(!detect_objective_lattice(p).eligible,"Zero constant objective");
    // Multiple independent substitutions, with an unrelated fractional row.
    p=vars(4);p.integer={true,true,false,false};p.cost={0,0,2,-3};p.offset=.5;
    p.rows={{{0,3},{2,1}},{{1,-2},{3,-1}},{{0,.3},{1,.7}}};p.row_lower={4,2,-INFINITY};p.row_upper={4,2,1.5};
    l=detect_objective_lattice(p);ensure(l.eligible&&l.substitutions.size()==2&&l.step==6&&l.offset==14.5,"Multiple definitions");
    p=vars(1);p.cost={5};p.offset=.25;l=detect_objective_lattice(p);
    std::size_t round_checks=0;
    for(int k=-1000;k<=1000;++k){
        const double grid=.25+5*k;
        for(double b:{grid,std::nextafter(grid,INFINITY),std::nextafter(grid,-INFINITY),grid-1.,grid-4.9}){
            double rounded=round_objective_bound(l,b);
            // nextafter ABOVE a grid is deliberately not rounded up: arithmetic guard.
            ensure(rounded>=b&&rounded<=std::max(b,grid),"Unsafe grid rounding");++round_checks;
        }
        ensure(round_objective_bound(l,grid-1.)>grid-1.,"Missed ordinary strengthening");
    }
    ensure(round_objective_bound(l,-INFINITY)==-INFINITY,"Infinite bound changed");
    ensure(std::isnan(round_objective_bound(l,NAN)),"NaN bound changed");
    double huge=std::ldexp(1.,42);ensure(round_objective_bound(l,huge)==huge,"Huge bound changed");
    for(double step:{1.,5.,65537.,std::ldexp(1.,40)})for(int sign:{-1,1}){
        p.cost={step};p.offset=sign*.25;l=detect_objective_lattice(p);ensure(l.eligible,"Large legal step rejected");
        double grid=p.offset+sign*step*std::floor(std::ldexp(1.,39)/step);
        for(double b:{grid,std::nextafter(grid,INFINITY),std::nextafter(grid,-INFINITY),grid-.25})
            ensure(round_objective_bound(l,b)>=b&&round_objective_bound(l,b)<=std::max(grid,b),"Large-grid rounding unsafe");
    }
    std::mt19937 rng(2611912);std::size_t improvements=0;
    for(int test=0;test<300;++test){
        const bool derived=test%3!=0;p=vars(derived?5:4);p.maximize=test%2;p.offset=(int(rng()%9)-4)*.25;
        const int step=1+rng()%7;std::vector<int> target(4),definition(4);std::vector<double> planted(4);
        for(int j=0;j<4;++j){target[j]=step*(int(rng()%11)-5);planted[j]=int(rng()%5)-2;definition[j]=step*(int(rng()%7)-3);p.cost[j]=target[j];}
        if(derived){
            p.integer[4]=false;p.lower[4]=-INFINITY;p.upper[4]=INFINITY;p.cost[4]=(test%4<2)?1:-1;
            SparseVector row;int unit=(test%5<3)?1:-1;
            for(int j=0;j<4;++j){if(definition[j])row.push_back({std::size_t(j),double(definition[j])});}
            row.push_back({4,double(unit)});p.rows.push_back(row);p.row_lower.push_back(test%7-3);p.row_upper=p.row_lower;
        }
        for(int i=0;i<3;++i){SparseVector row;double activity=0;
            for(int j=0;j<4;++j){int a=int(rng()%7)-3;if(a)row.push_back({std::size_t(j),double(a)});activity+=a*planted[j];}
            p.rows.push_back(row);p.row_lower.push_back(-INFINITY);p.row_upper.push_back(activity+.5+(rng()%3));
        }
        double expected=INFINITY;std::vector<double> witness;
        for(int code=0;code<625;++code){int v=code;std::vector<double> x(p.cost.size());for(int j=0;j<4;++j){x[j]=v%5-2;v/=5;}
            if(derived){double rhs=p.row_lower[0];for(int j=0;j<4;++j)rhs-=definition[j]*x[j];x[4]=rhs/p.rows[0].back().second;}
            if(original_violation(p,x,false)>1e-10)continue;
            double value=p.offset;for(std::size_t j=0;j<x.size();++j)value+=p.cost[j]*x[j];value*=p.maximize?-1:1;
            if(value<expected){expected=value;witness=x;}
        }
        ensure(std::isfinite(expected),"Generated model not feasible");
        l=detect_objective_lattice(p);ensure(l.eligible||l.reason=="constant_objective","Generated eligible structure rejected");
        if(l.eligible){
            double transformed=l.offset;for(std::size_t j=0;j<witness.size();++j)transformed+=l.coefficients[j]*witness[j];
            ensure(transformed==expected,"Substitution changed objective");
            for(double slack:{0.,.000001,.1,1.,10.,100.})ensure(round_objective_bound(l,expected-slack)<=expected,"Bound excludes enumerated optimum");
        }
        MilpOptions opt;opt.objective_lattice=true;opt.lp.time_limit_seconds=3;opt.node_limit=10000;
        opt.presolve=test%2;opt.cover_cuts=test%3;opt.heuristics=test%4;opt.lp.compact_equalities=test%3==0;
        auto r=solve_milp(p,opt);improvements+=r.lattice_bound_improvements;
        ensure(r.status=="optimal"||r.status=="gap_limit","Generated solve incomplete");
        ensure(std::abs((p.maximize?-r.objective:r.objective)-expected)<1e-7,"Generated solve disagrees with exhaustive optimum");
        ensure(original_violation(p,r.primal,false)<=1e-7,"Original witness rejected");
        ensure((p.maximize?-r.best_bound:r.best_bound)<=expected+1e-7,"Generated final bound excludes optimum");
        opt.node_limit=1;opt.heuristics=false;auto partial=solve_milp(p,opt);
        ensure((p.maximize?-partial.best_bound:partial.best_bound)<=expected+1e-7,"Partial bound excludes optimum");
        opt.lp.time_limit_seconds=0;auto stopped=solve_milp(p,opt);
        ensure(stopped.status=="time_limit"&&stopped.lattice_bound_calls==0,"Zero time falsely certified");
    }
    ensure(improvements>100,"Generated solves did not exercise bound strengthening");
    // A broad fractional root; no cuts/presolve/heuristics to mask tree behavior.
    p=vars(10);p.lower.assign(10,0);p.upper.assign(10,1);p.maximize=true;p.rows.resize(1);
    for(std::size_t j=0;j<10;++j)p.rows[0].push_back({j,1});p.row_lower={-INFINITY};p.row_upper={3.5};
    MilpOptions opt;opt.presolve=false;opt.heuristics=false;opt.cover_cuts=false;opt.lp.time_limit_seconds=5;
    auto control=solve_milp(p,opt);opt.objective_lattice=true;auto candidate=solve_milp(p,opt);
    ensure(control.objective==3&&candidate.objective==3&&candidate.nodes<control.nodes,"Lattice pruning not effective");
    opt.node_limit=0;auto zero=solve_milp(p,opt);ensure(zero.status=="node_limit"&&zero.lattice_bound_calls==0,"Zero node false completion");
    p=vars(1);p.lower={0};p.upper={1};p.rows={{{0,1}}};p.row_lower=p.row_upper={.5};opt=MilpOptions();opt.objective_lattice=true;
    auto infeasible=solve_milp(p,opt);ensure(infeasible.status=="infeasible"&&infeasible.primal.empty(),"Integer infeasibility misclassified");
    p=vars(1);p.cost={-1};p.lower={0};p.upper={INFINITY};auto unbounded=solve_milp(p,opt);
    ensure(unbounded.status!="optimal"&&unbounded.status!="gap_limit"&&unbounded.status!="infeasible"&&unbounded.lattice_bound_calls==0,"Unbounded LP rounded into a proof");
    std::istringstream marker("NAME MARKER\nROWS\n N OBJ\nCOLUMNS\n M0 'MARKER' 'INTORG'\n X OBJ -1\n M1 'MARKER' 'INTEND'\nENDATA\n");
    auto marked=solve_milp(read_mps(marker),opt);ensure(marked.status=="optimal"&&marked.objective==-1,"Lattice changed marker-only default");
    std::cout<<"300 exhaustive general-integer/mixed min-max models, 600 partial/zero-time outcomes, "<<round_checks
             <<" near-grid checks; improvements="<<improvements<<"; pruning nodes "<<control.nodes<<" -> "<<candidate.nodes<<"\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
