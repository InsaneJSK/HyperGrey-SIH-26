#include "milp.hpp"
#include <iostream>
using namespace sovereign;
void require(bool yes,const char* message){if(!yes)throw std::runtime_error(message);}
int main(){try{
    LinearProblem p;p.names={"negative","binary","interior","continuous","unbounded"};
    p.cost={7,-3,11,2,1};p.offset=42;p.maximize=true;
    p.lower={-3,0,-2,-10,-INFINITY};p.upper={-2,1,4,10,INFINITY};p.integer={true,true,true,false,true};
    p.rows={{{2,1},{3,1}}};p.row_lower={.4};p.row_upper={.4};
    detail::PumpDistanceModel d;d.start(p,p.lower,p.upper,{-2.1,.1,1.1,-.7,-.1});
    require(d.auxiliaries==2&&!d.model.maximize&&d.model.cost.size()==7,"Wrong private model shape");
    require(d.target==std::vector<double>({-2,0,1,0,0}),"Wrong rounded targets");
    require(p.cost[0]==7&&p.offset==42&&p.maximize&&p.rows.size()==1,"Original model mutated");
    for(double a:{-3.,-2.7,-2.})for(double b:{0.,.2,1.})for(double c:{-2.,.3,1.,4.})for(double e:{-5.,0.,2.}){
        std::vector<double>x={a,b,c,.4-c,e};auto extended=x;extended.push_back(std::abs(c-1));extended.push_back(std::abs(e));
        double z=d.model.offset;for(std::size_t j=0;j<extended.size();++j)z+=d.model.cost[j]*extended[j];
        require(std::abs(z-d.distance(p,x))<1e-12,"L1 objective identity failed");
        require(original_violation(d.model,extended,false)<1e-12,"Valid auxiliary extension rejected");
    }
    Options o;o.time_limit_seconds=5;o.refine_basis=true;o.refine_at_checks=true;
    auto cold=solve_sparse_lp(d.model,o);require(cold.solution.status=="optimal"&&cold.solution.optimality_verified,"Cold private LP failed");
    require(std::abs(cold.solution.objective)<1e-8,"Private LP is not distance minimization");
    auto primary=d.model;primary.upper[2]=0;
    auto left=solve_sparse_lp(primary,o,&cold.basis);require(left.solution.status=="optimal"&&left.solution.optimality_verified,"Private warm LP failed");
    auto alternate=d.model;alternate.lower[2]=2;
    auto right=solve_sparse_lp(alternate,o,&cold.basis);require(right.solution.status=="optimal"&&right.solution.optimality_verified,"Parent-basis alternate failed");
    require(std::abs(left.solution.objective-1)<1e-8&&std::abs(right.solution.objective-1)<1e-8,"Restricted distance wrong");
    o.time_limit_seconds=0;auto zero=solve_sparse_lp(d.model,o);require(zero.solution.status=="time_limit","Zero budget ignored");
    auto lo=p.lower;lo[1]=.2;auto up=p.upper;up[1]=.8;bool rejected=false;
    try{d.start(p,lo,up,{-2,.5,1,0,0});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Empty integer domain accepted");
    LinearProblem q;q.names={"x"};q.cost={5};q.lower={0};q.upper={1};q.integer={true};
    d.start(q,q.lower,q.upper,{.1});require(d.auxiliaries==0&&d.model.rows.empty(),"Unnecessary binary auxiliaries");
    MilpOptions m;m.pump_distance_diving=true;rejected=false;try{solve_milp(q,m);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Missing guidance prerequisite accepted");
    m.pump_guided_diving=true;m.lp.time_limit_seconds=0;auto r=solve_milp(q,m);
    require(r.status=="time_limit"&&r.pump_distance.dives==0,"Zero total budget not inert");
    m.lp.time_limit_seconds=5;m.heuristics=false;r=solve_milp(q,m);require(r.objective==0&&r.pump_distance.dives==0,"Disabled heuristics not inert");
    std::size_t empty_domain_cases=0;
    for(int negative=0;negative<2;++negative)for(int maximum=0;maximum<2;++maximum){
        LinearProblem bad;bad.names={"x","y"};double direction=negative?-1:1;
        bad.cost={direction,10};bad.lower={negative?-.8:.2,0};bad.upper={negative?-.2:.8,1};bad.integer={true,true};
        bad.rows={{{0,direction},{1,1}}};bad.row_lower={.6};bad.row_upper={INFINITY};bad.maximize=maximum;
        if(maximum)for(auto& c:bad.cost)c=-c;
        for(int presolve=0;presolve<2;++presolve)for(int heuristics=0;heuristics<2;++heuristics)for(int distance=0;distance<4;++distance){
            MilpOptions v;v.presolve=presolve;v.heuristics=heuristics;v.cover_cuts=false;
            v.pump_guided_diving=true;v.pump_distance_diving=distance;v.lp.time_limit_seconds=5;
            v.pump_primal_reopt=v.pump_distance_reopt=distance>=2;v.pump_distance_stage=distance==3;
            auto result=solve_milp(bad,v);++empty_domain_cases;
            require(result.status=="infeasible"&&result.primal.empty(),"Empty integer interval was not handled as infeasible");
            require(result.pump_distance.dives==0,"Private distance LP used an empty integer domain");
        }
    }
    require(empty_domain_cases==64,"Missing empty-domain combinations");
    std::cout<<"108 L1 identities; negative/unit/general/unbounded domains; cold/warm/alternate bases; zero budget; 64 empty-domain MIN/MAX/presolve/heuristic/flag combinations PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
