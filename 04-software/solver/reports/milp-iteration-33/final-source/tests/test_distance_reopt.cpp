#include "milp.hpp"
#include "pump_private_basis.hpp"
#include <iostream>
using namespace sovereign;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void same(const LinearProblem& p,const SparseLpResult& r,const SparseLpResult& cold){
    require(r.solution.status==cold.solution.status,"Warm/cold status differs");
    if(r.solution.status=="optimal"){
        require(r.solution.optimality_verified&&cold.solution.optimality_verified,"Unverified optimum");
        require(original_violation(p,r.solution.primal,false)<=1e-7,"Invalid private point");
        require(std::abs(r.solution.objective-cold.solution.objective)<=1e-7,"Warm/cold objective differs");
    }else require(r.solution.status=="infeasible"&&r.solution.infeasibility_verified,"Unexpected private status");
}
int main(){try{
    std::size_t cases=0;
    for(bool scale:{false,true})for(bool compact:{false,true})for(bool maximum:{false,true})for(double shift:{-3.,0.,2.}){
        Options o;o.primal_warm_start=true;o.refine_basis=true;o.refine_at_checks=true;o.scaling=scale;o.compact_equalities=compact;
        auto p=linear_from_dense({{1,2},{{-1,-1}},{-1}});
        p.lower={shift,shift};p.upper={shift+1,shift+1};p.row_upper={-1-2*shift};p.integer={true,true};p.maximize=maximum;
        detail::PumpDistanceModel projection,dive;
        projection.start(p,p.lower,p.upper,{shift+.1,shift+.1});
        auto initial=solve_sparse_lp(projection.model,o);require(initial.solution.optimality_verified,"Missing initial basis");
        detail::PumpPrivateBasis retained;require(retained.select(true,initial.basis),"No seed basis retained");
        const auto columns=retained.basis.columns;const auto tag=retained.basis.structure;
        require(!retained.select(false,LpBasis{})&&retained.basis.columns==columns&&retained.basis.structure==tag,"Non-selected point changed basis");
        dive.start(p,p.lower,p.upper,{shift+.9,shift+.1});
        auto trial=dive.model;trial.upper[0]=shift;
        auto result=solve_sparse_lp(trial,o,&retained.basis);same(trial,result,solve_sparse_lp(trial,o));
        require(result.reopt.compatible==1,"Compatible private structure rejected");
        // Both child infeasibility and auxiliary-layout rejection leave the parent intact.
        auto impossible=trial;impossible.upper[1]=shift;
        auto failed=solve_sparse_lp(impossible,o,&retained.basis);same(impossible,failed,solve_sparse_lp(impossible,o));
        auto alternate=dive.model;alternate.lower[0]=shift+1;
        same(alternate,solve_sparse_lp(alternate,o,&retained.basis),solve_sparse_lp(alternate,o));
        require(retained.basis.columns==columns&&retained.basis.structure==tag,"Failed child mutated parent basis");
        require(!retained.select(true,LpBasis{})&&retained.basis.columns.empty()&&!retained.basis.structure,"New seed kept stale basis");
        for(int bad=0;bad<3;++bad){auto basis=initial.basis;
            if(bad==0)basis.columns[0]=basis.columns[1];
            if(bad==1)basis.columns[0]=std::numeric_limits<std::size_t>::max();
            if(bad==2){auto s=std::make_shared<LpBasisStructure>(*basis.structure);s->mapping[0][0].second=-s->mapping[0][0].second;basis.structure=s;}
            auto r=solve_sparse_lp(trial,o,&basis);same(trial,r,solve_sparse_lp(trial,o));require(!r.warm_started,"Invalid private basis used");
        }
        o.time_limit_seconds=0;auto limited=solve_sparse_lp(trial,o,&initial.basis);require(limited.solution.status=="time_limit"&&!limited.solution.optimality_verified,"Zero time ignored");
        ++cases;
    }
    // Same dimensions but DIFFERENT general-integer auxiliaries are not interchangeable.
    LinearProblem p;p.names={"a","b","free"};p.cost={4,-2,1};p.lower={-2,-2,-INFINITY};p.upper={2,2,INFINITY};p.integer={true,true,false};
    p.rows={{{0,1},{1,1},{2,1}}};p.row_lower={.3};p.row_upper={.3};
    Options o;o.primal_warm_start=true;o.refine_basis=true;o.refine_at_checks=true;
    detail::PumpDistanceModel a,b;a.start(p,p.lower,p.upper,{0,2,0});b.start(p,p.lower,p.upper,{2,0,0});
    auto first=solve_sparse_lp(a.model,o);require(first.solution.optimality_verified,"General/free projection failed");
    require(a.model.cost.size()==b.model.cost.size()&&a.model.rows.size()==b.model.rows.size(),"Not equal-shape fixture");
    auto r=solve_sparse_lp(b.model,o,&first.basis);same(b.model,r,solve_sparse_lp(b.model,o));require(r.reopt.compatible==0&&!r.warm_started,"Changed auxiliary identity accepted");
    b.start(p,p.lower,p.upper,{2,2,0});r=solve_sparse_lp(b.model,o,&first.basis);same(b.model,r,solve_sparse_lp(b.model,o));require(r.reopt.compatible==0,"Changed auxiliary count accepted");
    MilpOptions m;m.pump_distance_reopt=true;bool rejected=false;
    try{solve_milp(p,m);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Missing prerequisites accepted");
    m.pump_guided_diving=m.pump_distance_diving=m.pump_primal_reopt=true;m.lp.time_limit_seconds=0;
    auto z=solve_milp(p,m);require(z.status=="time_limit"&&z.distance_reopt.calls==0&&z.distance_seed_updates==0,"Zero global budget not inert");
    std::cout<<cases<<" private handoff/bound/alternate/bad-basis/budget cases; changed auxiliary count/identity and free/equality guards PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
