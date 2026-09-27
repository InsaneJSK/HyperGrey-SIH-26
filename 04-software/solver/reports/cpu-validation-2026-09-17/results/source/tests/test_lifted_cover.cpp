#include "milp.hpp"
#include <iostream>
#include <random>

using namespace sovereign;
void ensure(bool yes,const char* message){if(!yes)throw std::runtime_error(message);}
LinearProblem model(std::size_t n){LinearProblem p;p.names.resize(n);p.cost.assign(n,-1);p.lower.assign(n,0);p.upper.assign(n,1);p.integer.assign(n,true);return p;}
std::size_t verify(const LinearProblem& p,const detail::CoverSeparation& result){
    for(const auto& cut:result.cuts){
        for(std::size_t mask=0;mask<(1u<<p.cost.size());++mask){
            long double original=0;for(auto a:p.rows[cut.source_row])if(mask&(1u<<a.first))original+=a.second;
            bool feasible=cut.side?original>=p.row_lower[cut.source_row]:original<=p.row_upper[cut.source_row];
            if(feasible){long double value=0;for(auto a:cut.row)if(mask&(1u<<a.first))value+=a.second;ensure(value<=cut.rhs,"Exported invalid cut");}
        }
    }
    return result.cuts.size();
}
int main(){try{
    std::mt19937 rng(2611908);std::size_t count=0;
    for(int test=0;test<400;++test){
        auto p=model(10);SparseVector row;std::vector<double> x;
        for(std::size_t j=0;j<10;++j){double a=(1+rng()%60)/8.;if(rng()%3==0)a=-a;row.push_back({j,a});x.push_back((rng()%101)/100.);}
        p.rows={row};p.row_lower={test%2?double(int(rng()%100)-40)/8.:-INFINITY};p.row_upper={test%2?INFINITY:double(int(rng()%100)-20)/8.};
        auto cuts=detail::separate_lifted_covers(p,x,1,5);ensure(!cuts.interrupted,"Small-case timeout");count+=verify(p,cuts);
    }
    ensure(count>100,"Exhaustive test generated too few cuts");
    auto p=model(3);p.rows={{{0,2},{1,2},{2,3}}};p.row_lower={-INFINITY};p.row_upper={4};
    auto cuts=detail::separate_lifted_covers(p,{.7,.7,.7},1,5);ensure(!cuts.cuts.empty(),"No basic separating cut");verify(p,cuts);
    auto run=MilpOptions();run.lifted_covers=true;run.heuristics=false;run.lp.time_limit_seconds=5;run.node_limit=1000;
    for(int maximize=0;maximize<2;++maximize){p.maximize=maximize;p.cost=maximize?std::vector<double>{1,1,2}:std::vector<double>{-1,-1,-2};
        auto solved=solve_milp(p,run);ensure((solved.status=="optimal"||solved.status=="gap_limit")&&std::abs(solved.objective-(maximize?2:-2))<1e-6,"Integrated objective wrong");
        ensure(!solved.lifted_cover_trace.empty(),"Integrated separator not exercised");
        run.cover_cuts=false;auto disabled=solve_milp(p,run);ensure(disabled.lifted_cover_trace.empty()&&disabled.lifted_cover_states==0,"No-cuts not honored");run.cover_cuts=true;
    }
    auto q=p;q.integer[1]=false;ensure(detail::separate_lifted_covers(q,{.7,.7,.7},1,1).cuts.empty(),"Continuous row accepted");
    q=p;q.upper[1]=2;ensure(detail::separate_lifted_covers(q,{.7,.7,.7},1,1).cuts.empty(),"General integer accepted");
    q=p;q.rows[0].push_back({0,1});ensure(detail::separate_lifted_covers(q,{.7,.7,.7},1,1).cuts.empty(),"Duplicate column accepted");
    ensure(detail::separate_lifted_covers(p,{.7,.7,.7},1,0).cuts.empty(),"Zero budget exports cut");
    ensure(detail::separate_lifted_covers(p,{.7,NAN,.7},1,1).cuts.empty(),"NaN point accepted");
    ensure(detail::separate_lifted_covers(p,{.7,.7,.7},1,NAN).cuts.empty(),"NaN budget accepted");
    ensure(detail::separate_lifted_covers(p,{.7,.7,.7},1,1e-100).cuts.empty(),"Expired budget exports cut");
    q=model(21);q.rows.resize(1);for(std::size_t j=0;j<21;++j)q.rows[0].push_back({j,1});q.row_lower={-INFINITY};q.row_upper={5};
    ensure(detail::separate_lifted_covers(q,std::vector<double>(21,.9),1,1).cuts.empty(),"Oversized row accepted");
    std::vector<std::int64_t> exact;
    ensure(detail::lifted_cover_detail::integers({.1,.2,.3},exact),"Ordinary dyadic decimals rejected");
    ensure(!detail::lifted_cover_detail::integers({1e100,1e-100},exact),"Unsafe common scale accepted");
    ensure(!detail::lifted_cover_detail::integers({INFINITY,1},exact),"Infinity accepted");
    ensure(detail::lifted_cover_detail::integers({0,0},exact)&&exact[0]==0,"All-zero conversion failed");
    q=model(2);q.rows={{{0,1},{1,1}}};q.row_lower={-INFINITY};q.row_upper={std::nextafter(2.,0.)};
    auto edge=detail::separate_lifted_covers(q,{1,1},1,1);ensure(!edge.cuts.empty(),"Adjacent-double bound rounded");verify(q,edge);
    q.row_upper={2};ensure(detail::separate_lifted_covers(q,{1,1},1,1).cuts.empty(),"Exact boundary cut feasible point");
    // Force a restart at a deterministic node count while the full-domain
    // frontier is live; never reset consumed nodes/time or import a local bound.
    auto restart_model=model(9);restart_model.integer[8]=false;restart_model.upper[8]=0;
    restart_model.rows={{{0,1},{1,1},{2,1},{3,1},{4,1},{5,1},{6,1},{7,1},{8,1}}};
    restart_model.row_lower={-INFINITY};restart_model.row_upper={3.5};
    for(int maximize=0;maximize<2;++maximize){
        restart_model.maximize=maximize;restart_model.cost.assign(9,maximize?1:-1);restart_model.cost[8]=0;
        MilpOptions late;late.lifted_covers=true;late.late_lifted_covers=true;late.late_cover_restart_nodes=6;late.heuristics=false;late.presolve=false;late.lp.time_limit_seconds=5;late.node_limit=1000;
        // A fixed continuous column makes this row ineligible for either cover
        // helper, so the frontier stays live after the first integer incumbent.
        auto result=solve_milp(restart_model,late);
        ensure((result.status=="optimal"||result.status=="gap_limit")&&std::abs(result.objective-(maximize?3:-3))<1e-6,"Late restart lost original optimum");
        ensure(result.cut_restarts==1&&result.cut_restart_nodes==6&&!result.cut_restart_primal.empty()&&result.cut_restart_objective==result.objective,"Restart did not preserve same-run incumbent");
        ensure(maximize?result.cut_restart_bound>=3:result.cut_restart_bound<=-3,"Restart imported invalid local bound");
        late.late_cover_restart_nodes=0;late.node_limit=1;auto forced=solve_milp(restart_model,late);
        ensure(forced.cut_restarts==1&&forced.nodes==1&&forced.cut_restart_nodes==0,"Restart resets or exceeds node accounting");
        late.node_limit=0;ensure(solve_milp(restart_model,late).cut_restarts==0,"Zero node limit allowed restart");
        late.node_limit=1000;late.lp.time_limit_seconds=0;ensure(solve_milp(restart_model,late).cut_restarts==0,"Zero time limit allowed restart");
        late.lp.time_limit_seconds=5;late.cover_cuts=false;ensure(solve_milp(restart_model,late).cut_restarts==0,"No-cuts allowed restart");
    }
    std::cout<<"400 exhaustive signed/dyadic row cases passed; "<<count<<" cuts checked, plus integration/domain/budget/boundary guards\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
