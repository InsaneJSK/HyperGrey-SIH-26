#include "sparse_lp.hpp"
#include "milp.hpp"
#include "reduced_bound_lp.hpp"
#include <fstream>
#include <iostream>
using namespace sovereign;
void require(bool c,const char* m){if(!c)throw std::runtime_error(m);}
int main(int argc,char** argv){try {
    require(argc==2,"Fixture required");std::ifstream f(argv[1]);auto p=read_mps(f);
    Options o;o.refine_basis=true;o.time_limit_seconds=5;
    auto plain=solve_sparse_lp(p,o);o.capture_refinement=true;auto traced=solve_sparse_lp(p,o);
    require(plain.solution.primal==traced.solution.primal&&plain.solution.dual==traced.solution.dual&&plain.solution.iterations==traced.solution.iterations,"Telemetry changed LP arithmetic");
    auto s=traced.refinement;require(s.rhs_calls>0&&s.scans==s.rhs_calls+s.attempts&&s.entries>0,"Missing scans");
    require(s.primal_rhs==s.dual_rhs&&s.rhs_calls==s.primal_rhs+s.dual_rhs,"RHS accounting");
    require(s.attempts==plain.refinement.attempts&&s.accepted==plain.refinement.accepted,"Correction counts changed");
    require(plain.refinement.seconds==0&&plain.refinement.rhs_calls==0,"Disabled telemetry recorded");
    auto original=linear_from_dense({{-1},{},{}}),full=original;full.upper={3};
    auto relaxed=solve_sparse_lp(original,o),restored=solve_sparse_lp(full,o);
    auto fallback=detail::solve_reduced_bound_lp(full,original,o);
    require(fallback.reduced_upper_fallback&&fallback.solution.objective==-3,"Fallback fixture failed");
    require(fallback.refinement.rhs_calls==relaxed.refinement.rhs_calls+restored.refinement.rhs_calls,"Fallback lost refinement work");
    detail::MilpWork work;detail::MilpWorkLedger ledger(work,true);
    {detail::MilpWorkScope outer(ledger,detail::MilpPhase::root_lp);ledger.lp(1,&s);
        {detail::MilpWorkScope inner(ledger,detail::MilpPhase::tree_lp);ledger.lp(2,&s);}}
    ledger.finish();require(work.refinement.rhs_calls==2*s.rhs_calls&&work.phases[1].refinement.rhs_calls==s.rhs_calls,"Nested aggregation");
    const std::vector<SparseVector> identity={{{0,1}}};const std::vector<std::size_t> b={0};const std::vector<double> rhs={1};
    std::vector<double>x={1.1};BasisRefinementStats interrupted;int checks=0;
    refine_basis_values(identity,b,rhs,x,false,[](const std::vector<double>& r){return r;},[&](){return ++checks>=3;},&interrupted,true);
    require(x[0]==1.1&&interrupted.accepted==0&&interrupted.scans>=1,"Interrupted trial mutated values");
    MilpOptions bad;bad.lp.capture_refinement=true;bool rejected=false;
    p.integer.assign(p.cost.size(),true);try{solve_milp(p,bad);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"C++ MILP capture without work ledger accepted");
    std::cout<<"Refinement telemetry, nested ledger, interruption and disabled arithmetic PASS\n";
    return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
