#include "sparse_lp.hpp"
#include <fstream>
#include <iostream>
#include <iomanip>

using namespace sovereign;
void check(bool good,const char* why){if(!good)throw std::runtime_error(why);}
static void corrected_point(const LinearProblem& p,const SparseLpResult& r,double expected) {
    const auto& s=r.solution;
    check(s.status=="optimal"&&s.optimality_verified,"Missing numerical optimality check");
    check(original_violation(p,s.primal,false)<=1e-7,"Original absolute feasibility failed");
    check(std::abs(s.objective-expected)<=1e-8*(1+std::abs(expected)),"Transformed objective wrong");
    check(s.relative_gap<=1e-8&&s.scaled_primal_violation<=1e-8&&s.scaled_dual_violation<=1e-8,"Certificate thresholds changed");
}
int main(int argc,char** argv){try {
    check(argc==3||(argc==4&&std::string(argv[3])=="--checks"),"Expected fixture and basis paths, optionally --checks");
    std::ifstream input(argv[1]),saved(argv[2]);check(bool(input)&&bool(saved),"Missing retained fixture");
    LinearProblem p=read_mps(input);LpBasis warm;std::size_t count;
    saved>>warm.structural_columns>>count;warm.columns.resize(count);for(auto& j:warm.columns)saved>>j;
    check(bool(saved),"Malformed retained warm basis");
    Options o;o.time_limit_seconds=5;
    const double expected=10515.606014154164;
    auto cold_control=solve_sparse_lp(p,o),warm_control=solve_sparse_lp(p,o,&warm);
    std::cout<<std::setprecision(17)<<"cold_control="<<cold_control.solution.status<<" warm_control="<<warm_control.solution.status<<"\n";
    // This regression intentionally keeps the failing control visible.
    check(cold_control.solution.status=="numerical_error","Retained cold failure no longer reproduced");
    o.refine_basis=true;
    o.refine_at_checks=argc==4;
    auto cold=solve_sparse_lp(p,o),hot=solve_sparse_lp(p,o,&warm);
    corrected_point(p,cold,expected);corrected_point(p,hot,expected);
    check(cold.refinement.accepted>0&&hot.refinement.accepted>0,"Correction not exercised");
    check(hot.warm_started,"Saved warm basis silently replaced by cold replay");
    std::cout<<"cold_refined pivots="<<cold.solution.iterations<<" violation="<<cold.solution.max_violation<<" attempts="<<cold.refinement.attempts<<" accepted="<<cold.refinement.accepted<<"\n";
    std::cout<<"warm_refined pivots="<<hot.solution.iterations<<" violation="<<hot.solution.max_violation<<" attempts="<<hot.refinement.attempts<<" accepted="<<hot.refinement.accepted<<"\n";
    // Machine-readable points for an independent checker, not solver input.
    for(const auto& labelled:std::vector<std::pair<const char*,const SparseLpResult*> >{{"cold",&cold},{"warm",&hot}}) {
        const auto& result=labelled.second->solution;
        std::cout<<"POINT {\"label\":\""<<labelled.first<<"\",\"status\":\""<<result.status<<"\",\"objective\":"<<result.objective<<",\"primal\":[";
        for(std::size_t j=0;j<result.primal.size();++j){if(j)std::cout<<',';std::cout<<result.primal[j];}
        std::cout<<"]}\n";
    }
    unsigned equivalents=0;
    for(bool maximize:{false,true})for(double variable_scale:{.5,2.})for(double row_scale:{.001,1.,1000.}) {
        LinearProblem q=p;long double shift_objective=0;
        std::vector<double> shifts(p.cost.size());
        for(std::size_t j=0;j<p.cost.size();++j){
            shifts[j]=j%2?-.25:.25;shift_objective+=static_cast<long double>(p.cost[j])*shifts[j];
            q.cost[j]=(maximize?-1:1)*variable_scale*p.cost[j];
            q.lower[j]=(p.lower[j]-shifts[j])/variable_scale;q.upper[j]=(p.upper[j]-shifts[j])/variable_scale;
        }
        for(std::size_t i=0;i<p.rows.size();++i){
            long double shift=0;for(auto a:p.rows[i])shift+=static_cast<long double>(a.second)*shifts[a.first];
            for(auto& a:q.rows[i])a.second*=variable_scale*row_scale;
            q.row_lower[i]=static_cast<double>((p.row_lower[i]-shift)*row_scale);
            q.row_upper[i]=static_cast<double>((p.row_upper[i]-shift)*row_scale);
        }
        q.maximize=maximize;q.offset=(maximize?-1:1)*static_cast<double>(shift_objective)+123456.;
        auto r=solve_sparse_lp(q,o);corrected_point(q,r,(maximize?-1:1)*expected+123456.);++equivalents;
    }
    for(bool compact:{false,true}) {
        o.compact_equalities=compact;
        auto degenerate=linear_from_dense({{1,0},{{-1,0},{-2,0},{1,0}},{-1,-2,1}});
        degenerate.upper={2,0};corrected_point(degenerate,solve_sparse_lp(degenerate,o),1);
        auto infeasible=linear_from_dense({{1},{{1},{-1}},{0,-1}});
        auto bad=solve_sparse_lp(infeasible,o);check(bad.solution.status=="infeasible"&&bad.solution.infeasibility_verified,"Infeasibility certificate lost");
        auto unbounded=linear_from_dense({{-1},{{-1}},{-2}});auto ray=solve_sparse_lp(unbounded,o);
        check(ray.solution.status=="unbounded"&&ray.solution.unboundedness_verified,"Unbounded certificate lost");
    }
    o.compact_equalities=false;o.time_limit_seconds=0;
    auto stopped=solve_sparse_lp(p,o,&warm);check(stopped.solution.status=="time_limit"&&!stopped.solution.optimality_verified&&stopped.refinement.attempts==0,"Zero time budget ignored");
    o.time_limit_seconds=5;o.iteration_limit=0;
    stopped=solve_sparse_lp(p,o);check(stopped.solution.status=="iteration_limit"&&!stopped.solution.optimality_verified,"Zero pivot budget ignored");
    o.iteration_limit=10000;o.max_tableau_cells=1;bool limited=false;
    try{solve_sparse_lp(p,o);}catch(const std::runtime_error& e){limited=std::string(e.what()).find("resource_limit")!=std::string::npos;}
    check(limited,"Fill budget bypassed");
    SparseLU singular;check(!singular.factor({{{0,1},{1,2}},{{0,1},{1,2}}}),"Singular basis accepted");
    // Direct guard tests: reject damage/NaN/stagnation and preserve cancellation.
    const std::vector<SparseVector> identity={{{0,1}},{{1,1}}};const std::vector<std::size_t> basis={0,1};
    const std::vector<double> rhs={1,2},initial={1.01,1.99};BasisRefinementStats stats;
    for(int mode=0;mode<4;++mode){auto x=initial;stats={};
        refine_basis_values(identity,basis,rhs,x,false,[&](const std::vector<double>& r){
            auto d=r;for(auto& v:d)v=mode==0?-v:(mode==1?NAN:0);return d;
        },[&](){return mode==3;},&stats);
        check(x==initial&&stats.accepted==0,"Rejected correction altered values");
    }
    for(bool transpose:{false,true}){auto x=initial;stats={};
        refine_basis_values(identity,basis,rhs,x,transpose,[](const std::vector<double>& r){return r;},[](){return false;},&stats);
        check(x==rhs&&stats.attempts==1&&stats.accepted==1,"Exact residual correction failed");
    }
    auto x=initial;stats={};
    refine_basis_values(identity,basis,rhs,x,false,[](const std::vector<double>& r){auto d=r;for(auto& v:d)v*=.5;return d;},[](){return false;},&stats);
    check(stats.attempts==2&&stats.accepted==2,"Arithmetic correction cap changed");
    std::cout<<"PASS retained cold+saved warm; "<<equivalents<<" transformed LPs; certificates, budgets and correction guards\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}}
