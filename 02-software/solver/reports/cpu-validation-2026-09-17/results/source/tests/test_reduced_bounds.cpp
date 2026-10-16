#include "milp.hpp"
#include "reduced_bound_lp.hpp"
#include <iostream>
#include <random>
using namespace sovereign;
void require(bool x,const char* message){if(!x)throw std::runtime_error(message);}
LinearProblem variables(std::size_t n){LinearProblem p;p.names.resize(n);p.cost.assign(n,-1);p.lower.assign(n,0);p.upper.assign(n,INFINITY);p.integer.assign(n,false);return p;}
int main(){try{
    Options o;o.compact_equalities=true;o.time_limit_seconds=5;
    auto original=variables(2);original.lower[1]=1;original.upper[1]=3;original.cost[1]=0;
    original.rows={{{0,1},{1,1}}};original.row_lower={-INFINITY};original.row_upper={5};
    auto full=original;full.upper[0]=4;
    auto reduced=detail::solve_reduced_bound_lp(full,original,o);
    auto control=solve_sparse_lp(full,o);
    require(reduced.solution.status=="optimal"&&reduced.solution.objective==-4&&reduced.reduced_upper_accepted&&!reduced.reduced_upper_fallback,"Valid reduced bound failed");
    require(reduced.canonical_rows+1==control.canonical_rows&&reduced.reduced_upper_candidates==1,"Finite original bound removed or no row saved");
    auto warm=detail::solve_reduced_bound_lp(full,original,o,&reduced.basis);
    require(warm.warm_started&&warm.solution.objective==-4,"Reduced warm start failed");
    auto crossed=detail::solve_reduced_bound_lp(full,original,o,&control.basis);
    require(!crossed.warm_started&&crossed.solution.objective==-4,"Full basis crossed into reduced mode");
    full.upper[0]=2;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="optimal"&&reduced.solution.objective==-2&&reduced.reduced_upper_fallback&&!reduced.reduced_upper_accepted,"Missing FULL-node primal gate");
    original=variables(1);full=original;full.upper[0]=3;
    reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="optimal"&&reduced.solution.objective==-3&&reduced.reduced_upper_fallback&&!reduced.solution.unboundedness_verified,"Relaxed ray certified original node unbounded");
    original.upper[0]=3;full.upper[0]=2;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.objective==-2&&reduced.reduced_upper_candidates==0,"Original finite domain removed");
    original.upper[0]=INFINITY;original.integer[0]=true;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.objective==-2&&reduced.reduced_upper_candidates==0,"Integer domain removed");
    original.integer[0]=false;original.lower[0]=full.lower[0]=-INFINITY;
    reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.objective==-2&&reduced.reduced_upper_fallback,"Free-column fallback failed");
    original=variables(1);original.cost[0]=1;original.rows={{{0,1}}};original.row_lower={4};original.row_upper={INFINITY};
    full=original;full.upper[0]=3;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="infeasible"&&reduced.solution.infeasibility_verified&&reduced.reduced_upper_fallback,"Empty full node accepted from nonempty relaxation");
    original.row_lower={-INFINITY};original.row_upper={-1};full=original;full.upper[0]=3;
    reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="infeasible"&&reduced.solution.infeasibility_verified&&reduced.reduced_upper_accepted,"Empty relaxation was mishandled");
    original=variables(2);full=original;full.upper[0]=2;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="unbounded"&&reduced.solution.unboundedness_verified&&reduced.reduced_upper_fallback&&std::abs(reduced.solution.unbounded_ray[0])<1e-9,"Full ray fallback did not restore bounds");
    o.time_limit_seconds=0;reduced=detail::solve_reduced_bound_lp(full,original,o);
    require(reduced.solution.status=="time_limit"&&!reduced.solution.optimality_verified&&!reduced.solution.unboundedness_verified,"Zero time certified reduced solve");o.time_limit_seconds=5;
    std::mt19937 rng(2611910);std::size_t accepted=0;
    for(int test=0;test<200;++test){
        auto p=variables(5);p.maximize=test%2;p.offset=int(rng()%7)-3;
        std::vector<double> planted={double(rng()%2),double(rng()%2),double(rng()%2),2,3};
        for(std::size_t j=0;j<5;++j){p.cost[j]=int(rng()%15)-7;if(j<3){p.integer[j]=true;p.upper[j]=1;}}
        p.rows={{{3,1}},{{4,1}}};p.row_lower={-INFINITY,-INFINITY};p.row_upper={5,6};
        for(int i=0;i<4;++i){SparseVector row;double rhs=0;for(std::size_t j=0;j<5;++j){double a=int(rng()%7)-3;if(a){row.push_back({j,a});rhs+=a*planted[j];}}
            p.rows.push_back(row);p.row_lower.push_back(i?rhs-3:rhs);p.row_upper.push_back(i?rhs+4:rhs);
        }
        MilpOptions m;m.lp=o;m.node_limit=10000;auto before=solve_milp(p,m);m.reduced_bound_lp=true;auto after=solve_milp(p,m);
        require((before.status=="optimal"||before.status=="gap_limit")&&(after.status=="optimal"||after.status=="gap_limit"),"Generated MILP status failed");
        require(std::abs(before.objective-after.objective)<1e-6*(1+std::abs(before.objective))&&original_violation(p,after.primal,false)<=1e-7,"Generated MILP objective/feasibility mismatch");
        accepted+=after.reduced_bound_lp_accepted;
    }
    require(accepted>=100,"Generated cases did not exercise reduction");
    auto p=variables(9);for(int j=0;j<8;++j){p.integer[j]=true;p.upper[j]=1;}p.cost[8]=0;
    p.rows={{{0,1},{1,1},{2,1},{3,1},{4,1},{5,1},{6,1},{7,1},{8,1}},{{8,1}}};p.row_lower={-INFINITY,0};p.row_upper={3.5,0};
    for(int maximize=0;maximize<2;++maximize){
        p.maximize=maximize;for(int j=0;j<8;++j)p.cost[j]=maximize?1:-1;
        MilpOptions late;late.late_reduced_bound_lp=true;late.heuristics=false;late.lp.time_limit_seconds=5;late.node_limit=1000;late.late_cover_restart_nodes=6;
        auto result=solve_milp(p,late);
        require((result.status=="optimal"||result.status=="gap_limit")&&std::abs(result.objective-(maximize?3:-3))<1e-6,"Delayed reduced LP lost optimum");
        require(result.cut_restarts==1&&result.reduced_bound_lp_accepted>0&&result.root_reduced_upper_bounds==1,"Delayed reduction not exercised");
        late.node_limit=6;result=solve_milp(p,late);require(result.cut_restarts==0&&result.reduced_bound_lp_calls==0,"Reduction activated before restart");
        late.node_limit=1000;late.cover_cuts=false;result=solve_milp(p,late);require(result.reduced_bound_lp_calls==0,"No-cuts allowed late reduction");
    }
    std::cout<<"200 generated MILP comparisons and reduced/full-node/domain/ray/warm/delayed guards passed; accepted reduced LPs="<<accepted<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
