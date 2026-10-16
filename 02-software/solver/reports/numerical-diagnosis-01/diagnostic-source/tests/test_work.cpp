#include "milp.hpp"
#include <cmath>
#include <iostream>
#include <random>
using namespace sovereign;
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
void accounting(const MilpResult& r){
    double sum=0;std::size_t iterations=0;
    for(const auto& p:r.work.phases){require(std::isfinite(p.seconds)&&p.seconds>=0,"Invalid phase time");sum+=p.seconds;iterations+=p.iterations;}
    require(std::abs(sum-r.work.seconds)<=1e-8*(1+r.work.seconds),"Double-counted phase time");
    require(iterations==r.lp_iterations,"Missing LP work");
}
int main(){try{
    using namespace detail;
    MilpWork w;MilpWorkLedger ledger(w,true);
    {MilpWorkScope a(ledger,MilpPhase::root_lp);ledger.lp(7);
     {MilpWorkScope b(ledger,MilpPhase::cut_lp);ledger.lp(3);}ledger.lp(2);}
    ledger.finish();require(w.phases[1].iterations==9&&w.phases[2].iterations==3,"Nested phase restoration");
    MilpWork off;MilpWorkLedger disabled(off,false);{MilpWorkScope a(disabled,MilpPhase::root_lp);disabled.lp(99);}disabled.finish();
    require(off.seconds==0&&off.phases[1].iterations==0,"Disabled telemetry recorded work");
    std::mt19937 rng(2611914);std::size_t solves=0,partials=0,restarts=0;
    for(int test=0;test<120;++test){
        LinearProblem p;p.names.resize(5);p.cost.resize(5);p.lower.assign(5,-1);p.upper.assign(5,2);p.integer.assign(5,true);
        p.integer[4]=false;p.lower[4]=-INFINITY;p.upper[4]=INFINITY;p.maximize=test%2;p.offset=(test%5-2)*.25;
        double definition[4],planted[4];SparseVector equality;
        for(std::size_t j=0;j<4;++j){definition[j]=int(rng()%7)-3;planted[j]=int(rng()%4)-1;p.cost[j]=int(rng()%13)-6;if(definition[j])equality.push_back({j,-definition[j]});}
        p.cost[4]=test%3?1:-1;equality.push_back({4,1});p.rows.push_back(equality);p.row_lower={1};p.row_upper={1};
        for(int i=0;i<4;++i){SparseVector row;double rhs=.5+rng()%3;for(std::size_t j=0;j<4;++j){double a=int(rng()%9)-4;if(a)row.push_back({j,a});rhs+=a*planted[j];}
            p.rows.push_back(row);p.row_lower.push_back(-INFINITY);p.row_upper.push_back(rhs);}
        double expected=INFINITY;
        for(int code=0;code<256;++code){int v=code;std::vector<double>x(5);x[4]=1;
            for(int j=0;j<4;++j){x[j]=v%4-1;v/=4;x[4]+=definition[j]*x[j];}
            if(original_violation(p,x,false)>1e-8)continue;double z=p.offset;for(int j=0;j<5;++j)z+=p.cost[j]*x[j];expected=std::min(expected,p.maximize?-z:z);}
        for(std::size_t rounds:{0u,1u,5u}){
            MilpOptions o;o.root_cut_rounds=rounds;o.capture_work=true;o.capture_frontier=true;o.raw_lp_priority=true;o.objective_lattice=true;
            o.heuristics=test%3==0;o.presolve=test%4==0;o.lp.time_limit_seconds=5;
            o.late_lifted_covers=true;o.lifted_covers=true;o.restart_by_nodes=true;o.late_cover_restart_nodes=2;
            auto r=solve_milp(p,o);++solves;restarts+=r.cut_restarts;accounting(r);
            require((r.status=="optimal"||r.status=="gap_limit")&&std::abs((p.maximize?-r.objective:r.objective)-expected)<1e-7,"Wrong enumerated optimum");
            require(original_violation(p,r.primal,false)<=1e-7,"Invalid incumbent");
            require(r.work.phases[static_cast<std::size_t>(MilpPhase::cut_lp)].lp_calls<=rounds*(1+r.cut_restarts),"Cut round cap exceeded");
            o.heuristics=false;o.node_limit=3;r=solve_milp(p,o);++partials;accounting(r);
            require((p.maximize?-r.best_bound:r.best_bound)<=expected+1e-7,"Partial bound excludes optimum");
            o.lp.time_limit_seconds=0;r=solve_milp(p,o);++partials;accounting(r);
            require(r.status=="time_limit"&&r.nodes==0,"Zero time falsely completed");
        }
    }
    require(restarts>10,"Restart coverage absent");
    LinearProblem p;p.names={"x"};p.cost={1};p.lower={0};p.upper={1};p.integer={true};
    MilpOptions bad;bad.root_cut_rounds=6;bool rejected=false;try{solve_milp(p,bad);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Invalid round option accepted");
    std::cout<<solves<<" solves on120 exhaustive models; "<<partials<<" partial/zero-time checks; "<<restarts<<" counter restarts; phase accounting PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
