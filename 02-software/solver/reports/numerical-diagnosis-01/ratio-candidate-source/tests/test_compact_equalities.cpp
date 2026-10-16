#include "milp.hpp"
#include <iostream>
#include <random>
using namespace sovereign;
void ensure(bool condition,const char* msg){if(!condition)throw std::runtime_error(msg);}
LinearProblem vars(std::size_t n){LinearProblem p;p.names.resize(n);p.cost.assign(n,1);p.lower.assign(n,0);p.upper.assign(n,INFINITY);p.integer.assign(n,false);return p;}
int main(){try{
    Options o;o.compact_equalities=true;o.time_limit_seconds=5;auto ordinary=o;ordinary.compact_equalities=false;
    auto p=vars(1);p.rows={{{0,1}}};p.row_lower=p.row_upper={2};
    auto r=solve_sparse_lp(p,o);ensure(r.solution.status=="optimal"&&r.solution.optimality_verified&&r.solution.objective==2,"Positive equality failed");
    ensure(r.compact_equality_rows==1&&r.canonical_rows==1&&r.canonical_dual[0]>0,"Equality multiplier incorrectly clamped");
    auto old=solve_sparse_lp(p,ordinary);ensure(old.canonical_rows==2,"Control equality encoding changed");
    auto warm=solve_sparse_lp(p,o,&r.basis);ensure(warm.warm_started&&warm.solution.objective==2,"Compact warm basis failed");
    auto crossed=solve_sparse_lp(p,o,&old.basis);ensure(!crossed.warm_started&&crossed.solution.objective==2,"Cross-mode warm basis accepted");
    auto bad=r.basis;bad.columns[0]=1;auto rejected=solve_sparse_lp(p,o,&bad);ensure(!rejected.warm_started&&rejected.solution.objective==2,"Artificial warm column admitted");
    p.maximize=true;r=solve_sparse_lp(p,o);ensure(r.solution.status=="optimal"&&r.solution.objective==2&&r.best_bound==-2,"Max equality sign failed");
    p.maximize=false;p.row_lower=p.row_upper={-2};p.lower={-INFINITY};r=solve_sparse_lp(p,o);
    ensure(r.solution.status=="optimal"&&r.solution.objective==-2,"Free variable negative equality failed");
    p.lower={0};r=solve_sparse_lp(p,o);ensure(r.solution.status=="infeasible"&&r.solution.infeasibility_verified,"Negative equality infeasibility failed");
    p.row_lower=p.row_upper={1};p.rows.push_back(p.rows[0]);p.row_lower.push_back(1);p.row_upper.push_back(1);
    r=solve_sparse_lp(p,o);ensure(r.solution.status=="optimal"&&r.solution.objective==1&&r.compact_fallback,"Dependent equality fallback failed");
    p.row_lower[1]=p.row_upper[1]=2;r=solve_sparse_lp(p,o);ensure(r.solution.status=="infeasible"&&r.solution.infeasibility_verified,"Inconsistent equalities accepted");
    p=vars(2);p.cost={-1,-1};p.rows={{{0,1},{1,-1}}};p.row_lower=p.row_upper={0};r=solve_sparse_lp(p,o);
    ensure(r.solution.status=="unbounded"&&r.solution.unboundedness_verified&&std::abs(r.solution.unbounded_ray[0]-r.solution.unbounded_ray[1])<1e-9,"Equality-violating ray accepted");
    p=vars(1);p.rows={{{0,1}}};p.row_lower={0};p.row_upper={1e-12};r=solve_sparse_lp(p,o);ensure(r.compact_equality_rows==0,"Near equality silently collapsed");
    o.time_limit_seconds=0;r=solve_sparse_lp(p,o);ensure(!r.solution.optimality_verified&&r.solution.status=="time_limit","Zero time certified solve");o.time_limit_seconds=5;
    std::mt19937 rng(2611909);std::size_t fallback=0;
    for(int test=0;test<300;++test){
        p=vars(6);p.lower.assign(6,-3);p.upper.assign(6,4);p.offset=int(rng()%15)-7;p.maximize=test%2;
        std::vector<double> planted;for(std::size_t j=0;j<6;++j){planted.push_back(int(rng()%7)-3);p.cost[j]=int(rng()%15)-7;}
        for(int i=0;i<4;++i){SparseVector row;double activity=0;for(std::size_t j=0;j<6;++j){double a=int(rng()%7)-3;if(a){row.push_back({j,a});activity+=a*planted[j];}}
            p.rows.push_back(row);p.row_lower.push_back(i<2?activity:activity-3);p.row_upper.push_back(i<2?activity:activity+4);
        }
        auto a=solve_sparse_lp(p,ordinary),b=solve_sparse_lp(p,o);fallback+=b.compact_fallback;
        ensure(a.solution.status=="optimal"&&b.solution.status=="optimal"&&b.solution.optimality_verified,"Generated LP failed");
        ensure(std::abs(a.solution.objective-b.solution.objective)<1e-7*(1+std::abs(a.solution.objective))&&original_violation(p,b.solution.primal,false)<1e-7,"Generated LP objective/primal disagreement");
        if(test<80){
            for(int j=0;j<3;++j)p.integer[j]=true;
            MilpOptions m;m.lp=o;m.node_limit=10000;auto solved=solve_milp(p,m);m.lp=ordinary;auto control=solve_milp(p,m);
            ensure((solved.status=="optimal"||solved.status=="gap_limit")&&(control.status=="optimal"||control.status=="gap_limit"),"Generated MILP failed");
            ensure(std::abs(solved.objective-control.objective)<1e-6*(1+std::abs(control.objective))&&original_violation(p,solved.primal,false)<1e-7,"Generated MILP disagreement");
        }
    }
    p=vars(9);p.upper.assign(9,1);p.integer.assign(9,true);p.integer[8]=false;p.upper[8]=0;
    p.rows={{{0,1},{1,1},{2,1},{3,1},{4,1},{5,1},{6,1},{7,1},{8,1}},{{8,1}}};
    p.row_lower={-INFINITY,0};p.row_upper={3.5,0};
    for(int maximize=0;maximize<2;++maximize){
        p.maximize=maximize;p.cost.assign(9,maximize?1:-1);p.cost[8]=0;
        MilpOptions late;late.late_compact_equalities=true;late.late_cover_restart_nodes=6;
        late.presolve=false;late.heuristics=false;late.lp.time_limit_seconds=5;late.node_limit=1000;
        auto solved=solve_milp(p,late);
        ensure((solved.status=="optimal"||solved.status=="gap_limit")&&std::abs(solved.objective-(maximize?3:-3))<1e-6,"Delayed compact lost optimum");
        ensure(solved.cut_restarts==1&&solved.cut_restart_nodes==6&&solved.compact_lp_calls>0&&solved.root_compact_equalities==1,"Delayed compact activation failed");
        ensure(solved.cut_restart_objective==solved.objective&&!solved.cut_restart_primal.empty(),"Delayed compact lost incumbent");
        ensure(maximize?solved.cut_restart_bound>=3:solved.cut_restart_bound<=-3,"Delayed compact imported local bound");
        late.node_limit=6;solved=solve_milp(p,late);ensure(solved.cut_restarts==0&&solved.compact_lp_calls==0,"Compact active before restart");
        late.node_limit=1000;late.cover_cuts=false;solved=solve_milp(p,late);ensure(solved.cut_restarts==0&&solved.compact_lp_calls==0,"No-cuts did not disable delayed compact");
        late.cover_cuts=true;late.lp.time_limit_seconds=0;solved=solve_milp(p,late);ensure(solved.cut_restarts==0&&solved.compact_lp_calls==0,"Zero-time compact activation");
    }
    std::cout<<"300 equality LP comparisons and80 mixed MILP comparisons passed; LP fallbacks="<<fallback<<"; analytical/artificial/dual/ray/warm/domain and delayed min/max activation guards passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
