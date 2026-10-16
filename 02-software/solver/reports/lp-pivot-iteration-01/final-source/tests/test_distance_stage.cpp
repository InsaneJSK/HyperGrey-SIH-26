#include "milp.hpp"
#include "pump_private_basis.hpp"
#include <iostream>
using namespace sovereign;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void optimal(const LinearProblem& p,const SparseLpResult& r,double expected){
    require(r.solution.status=="optimal"&&r.solution.optimality_verified,"Unverified private optimum");
    require(original_violation(p,r.solution.primal,false)<=1e-7,"Private absolute infeasibility");
    require(std::abs(r.solution.objective-expected)<=1e-7,"Wrong private objective");
}
int main(){try{
    std::size_t cases=0;
    for(bool scaling:{false,true})for(bool compact:{false,true})for(bool maximum:{false,true})for(double shift:{-3.,0.,2.}){
        auto p=linear_from_dense({{1,2},{{-1,-1}},{-1}});p.lower={shift,shift};p.upper={shift+1,shift+1};p.row_upper={-1-2*shift};p.integer={true,true};p.maximize=maximum;
        detail::PumpDistanceModel a,b;a.start(p,p.lower,p.upper,{shift+.1,shift+.9});b.start(p,p.lower,p.upper,{shift+.9,shift+.1});
        Options o;o.primal_warm_start=true;o.refine_basis=true;o.refine_at_checks=true;o.scaling=scaling;o.compact_equalities=compact;
        auto initial=solve_sparse_lp(a.model,o);optimal(a.model,initial,0);
        detail::PumpPrivateBasis saved;require(saved.select(true,initial.basis,&a.model),"Missing parent snapshot");
        auto tag=saved.basis.structure;auto parent=saved.parent;
        require(saved.same_parent_domain(b.model),"Objective-only parent rejected");
        require(!saved.select(false,LpBasis{},nullptr)&&saved.parent==parent,"Non-selected point changed parent");
        auto altered=a.model;altered.lower[0]=shift+.5;require(!saved.same_parent_domain(altered),"Changed parent bounds accepted");
        altered=a.model;altered.row_upper[0]+=.1;require(!saved.same_parent_domain(altered),"Changed parent RHS accepted");
        altered=a.model;altered.rows[0][0].second=-2;require(!saved.same_parent_domain(altered),"Changed parent matrix accepted");
        a.model.lower[0]=shift+.25;require(saved.parent->lower[0]==shift,"Parent aliases mutable projection");
        auto staged=solve_sparse_lp(b.model,o,&saved.basis);optimal(b.model,staged,0);
        require(staged.reopt.primal==1&&staged.reopt.phase_one_iterations==0,"Objective-only stage did not primal-reoptimize");
        auto child=b.model;child.upper[0]=shift;
        auto warm=solve_sparse_lp(child,o,&staged.basis);optimal(child,warm,2);
        auto cold=solve_sparse_lp(child,o);optimal(child,cold,2);
        require(warm.reopt.dual==1&&warm.reopt.phase_one_iterations==0,"Bound-only child did not dual-reoptimize");
        auto impossible=child;impossible.upper[1]=shift;
        auto failed=solve_sparse_lp(impossible,o,&staged.basis);require(failed.solution.status=="infeasible"&&failed.solution.infeasibility_verified,"Failed child not checked");
        auto alternate=b.model;alternate.lower[0]=shift+1;optimal(alternate,solve_sparse_lp(alternate,o,&staged.basis),0);
        require(saved.parent==parent&&saved.basis.structure==tag,"Child changed selected seed ownership");
        for(int bad=0;bad<3;++bad){auto basis=staged.basis;
            if(bad==0)basis.columns[0]=basis.columns[1];else if(bad==1)basis.columns[0]=std::numeric_limits<std::size_t>::max();else basis.reduced_upper_bounds=true;
            auto r=solve_sparse_lp(child,o,&basis);optimal(child,r,2);require(!r.warm_started,"Invalid staged basis accepted");
        }
        o.time_limit_seconds=0;auto limited=solve_sparse_lp(b.model,o,&saved.basis);require(limited.solution.status=="time_limit"&&!limited.solution.optimality_verified,"Zero time ignored");
        o.time_limit_seconds=5;o.iteration_limit=0;limited=solve_sparse_lp(b.model,o,&saved.basis);require(limited.solution.status=="iteration_limit"&&!limited.solution.optimality_verified,"Zero pivots ignored");
        require(saved.select(true,saved.basis,saved.parent.get())&&saved.parent->lower[0]==shift,"Self-alias replacement lost parent");
        require(!saved.select(true,LpBasis{})&&!saved.parent&&saved.basis.columns.empty(),"Stale selected parent retained");
        ++cases;
    }
    LinearProblem p;p.names={"general","free"};p.cost={2,1};p.lower={-2,-INFINITY};p.upper={2,INFINITY};p.integer={true,false};
    p.rows={{{0,1},{1,1}}};p.row_lower={.2};p.row_upper={.2};
    detail::PumpDistanceModel a,b;a.start(p,p.lower,p.upper,{.1,.1});b.start(p,p.lower,p.upper,{1.1,-.9});
    Options o;o.primal_warm_start=true;auto first=solve_sparse_lp(a.model,o);optimal(a.model,first,0);
    detail::PumpPrivateBasis saved;saved.select(true,first.basis,&a.model);
    require(!saved.same_parent_domain(b.model),"Changed auxiliary RHS accepted for objective-only stage");
    b.start(p,p.lower,p.upper,{2,-1.8});require(!saved.same_parent_domain(b.model),"Changed auxiliary layout accepted");
    auto free=a.model;free.upper[1]=3;require(!saved.same_parent_domain(free),"Changed free-variable orientation accepted");
    MilpOptions m;m.pump_distance_stage=true;bool rejected=false;try{solve_milp(p,m);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Missing stage prerequisite accepted");
    m.pump_guided_diving=m.pump_distance_diving=m.pump_primal_reopt=m.pump_distance_reopt=true;m.lp.time_limit_seconds=0;
    auto z=solve_milp(p,m);require(z.status=="time_limit"&&z.distance_stage.attempts==0,"Zero MILP budget not inert");
    std::cout<<cases<<" staged primal/dual/alternate/domain/ownership/invalid-basis/resource cases; general-integer auxiliary/free guards PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
