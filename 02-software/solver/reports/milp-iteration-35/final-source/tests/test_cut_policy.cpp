#include "milp.hpp"
#include <iostream>
#include <random>
#include <set>
using namespace sovereign;
void need(bool v,const char* m){if(!v)throw std::runtime_error(m);}
int main(){try{
    auto decision=[](std::size_t round,std::size_t root,std::size_t work,double b,double a,double o=0){return std::string(detail::cut_continuation(round,root,work,b,a,o));};
    need(decision(1,100,1000,0,0)=="minimum_rounds","Minimum rounds");
    need(decision(2,100,255,0,0)=="cheap_round","Cheap-round floor");
    need(decision(2,0,256,0,0)=="missing_root_work","Zero work guard");
    need(decision(2,256,256,0,0)=="diminishing_return","Stagnation decision");
    need(decision(2,256,256,0,.001)=="diminishing_return","Inclusive boundary");
    need(decision(2,256,256,0,std::nextafter(.001,INFINITY))=="productive_round","Above boundary");
    need(decision(2,256,256,0,std::nextafter(.001,0.))=="diminishing_return","Below boundary");
    need(decision(2,256,1024,0,.003)=="diminishing_return","Work normalization");
    need(decision(2,1024,256,0,.003)=="productive_round","Cheap relative work");
    need(decision(2,256,256,50,51)==decision(2,256,256,150,151,100),"Exact offset translation");
    for(double x:{INFINITY,-INFINITY,NAN})need(decision(2,256,256,x,0)=="invalid_metric","Nonfinite before");
    need(decision(2,256,256,0,INFINITY)=="invalid_metric","Nonfinite after");
    need(decision(2,256,256,0,0,NAN)=="invalid_metric","Nonfinite offset");
    double large=std::numeric_limits<double>::max();
    need(decision(2,256,256,large,-large)=="invalid_metric","Negative overflow");
    need(decision(2,256,256,-large,large)=="invalid_metric","Positive overflow");
    need(decision(2,256,256,large,large,-large)=="invalid_metric","Scale overflow");
    for(bool enabled:{false,true})for(bool required:{false,true})for(bool known:{false,true}){
        auto d=std::string(detail::guarded_cut_continuation(enabled,required,known,2,5,300,300,10,10,0));
        need(d==(!enabled?"disabled":required&&!known?"no_incumbent":"diminishing_return"),"Incumbent guard");
        need(std::string(detail::guarded_cut_continuation(enabled,required,known,1,1,300,300,10,10,0))==
            (enabled?"round_cap":"disabled"),"Explicit cap before guard");
    }
    std::mt19937 rng(2611915);std::size_t solves=0,partial=0,rounds=0,restarts=0;
    std::set<std::string> observed;
    for(int test=0;test<120;++test){
        const bool binary=test%2==0;const int base=binary?2:4;const int lower=binary?0:-1;
        LinearProblem p;p.names.resize(5);p.cost.resize(5);p.lower.assign(5,lower);p.upper.assign(5,lower+base-1);p.integer.assign(5,true);
        p.integer[4]=false;p.lower[4]=-INFINITY;p.upper[4]=INFINITY;p.maximize=test%3==0;p.offset=(test%7-3)*.25;
        int definition[4],planted[4];SparseVector equality;
        for(int j=0;j<4;++j){definition[j]=int(rng()%5)-2;planted[j]=int(rng()%base)+lower;p.cost[j]=int(rng()%15)-7;if(definition[j])equality.push_back({std::size_t(j),-double(definition[j])});}
        p.cost[4]=test%3?1:-1;equality.push_back({4,1});p.rows.push_back(equality);p.row_lower={1};p.row_upper={1};
        for(int i=0;i<5;++i){SparseVector row;double rhs=.5+rng()%3;for(int j=0;j<4;++j){double a=int(rng()%11)-5;if(a)row.push_back({std::size_t(j),a});rhs+=a*planted[j];}
            p.rows.push_back(row);p.row_lower.push_back(-INFINITY);p.row_upper.push_back(rhs);}
        double expected=INFINITY;
        for(int code=0;code<base*base*base*base;++code){int v=code;std::vector<double>x(5);x[4]=1;
            for(int j=0;j<4;++j){x[j]=v%base+lower;v/=base;x[4]+=definition[j]*x[j];}
            if(original_violation(p,x,false)>1e-8)continue;double z=p.offset;for(int j=0;j<5;++j)z+=p.cost[j]*x[j];expected=std::min(expected,p.maximize?-z:z);}
        for(int policy=0;policy<3;++policy)for(std::size_t cap:{0u,1u,5u}){
            bool adaptive=policy>0;
            MilpOptions o;o.adaptive_cut_rounds=adaptive;o.capture_cut_rounds=true;o.capture_work=true;o.root_cut_rounds=cap;
            o.cut_after_incumbent=policy==2;
            o.objective_lattice=true;o.raw_lp_priority=true;o.capture_frontier=true;o.heuristics=false;o.presolve=test%4==0;
            o.late_lifted_covers=true;o.lifted_covers=true;o.restart_by_nodes=true;o.late_cover_restart_nodes=2;o.lp.time_limit_seconds=5;
            auto r=solve_milp(p,o);++solves;restarts+=r.cut_restarts;
            need((r.status=="optimal"||r.status=="gap_limit")&&std::abs((p.maximize?-r.objective:r.objective)-expected)<1e-7,"Enumerated optimum mismatch");
            need(original_violation(p,r.primal,false)<=1e-7,"Invalid point");
            need(r.cut_round_trace.size()<=cap*(1+r.cut_restarts),"Round cap exceeded");
            std::size_t stops=0;for(const auto& t:r.cut_round_trace){++rounds;observed.insert(t.decision);stops+=std::string(t.decision)=="diminishing_return";
                if(std::string(t.decision)!="rollback"&&std::string(t.decision)!="infeasible")
                    need(std::string(t.decision)==detail::guarded_cut_continuation(adaptive,o.cut_after_incumbent,
                        std::isfinite(t.incumbent_objective),t.round,cap,t.root_iterations,t.iterations,t.before,t.after,t.offset),"Policy trace mismatch");}
            need(stops==r.adaptive_cut_stops,"Stop count mismatch");
            o.node_limit=2;r=solve_milp(p,o);++partial;need((p.maximize?-r.best_bound:r.best_bound)<=expected+1e-7,"Partial bound excludes optimum");
            o.lp.time_limit_seconds=0;r=solve_milp(p,o);++partial;need(r.status=="time_limit"&&r.nodes==0&&r.cut_round_trace.empty(),"Zero-time policy ran");
        }
    }
    need(rounds>0&&restarts>0&&observed.count("minimum_rounds"),"No integration coverage");
    std::cout<<"Policy boundaries/invalid metrics PASS; "<<solves<<" solves on120 exhaustive models; "<<partial<<" partial/zero checks; "<<rounds<<" traced rounds; "<<restarts<<" restarts\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
