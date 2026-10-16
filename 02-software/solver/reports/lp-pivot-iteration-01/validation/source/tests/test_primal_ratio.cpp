#include "primal_ratio.hpp"
#include "sparse_lp.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
int main(int argc,char** argv) {
    using sovereign::detail::stable_primal_leaving;
    try {
        const double tol=1e-9;
        require(stable_primal_leaving({0,0},{2e-9,1},{0,1},0,tol,false)==1,"Weak zero-step pivot retained");
        require(stable_primal_leaving({0,1e-10},{2e-9,1},{0,1},0,tol,false)==1,"Feasible expanded-step candidate ignored");
        require(stable_primal_leaving({0,1},{2e-9,1},{0,1},0,tol,false)==0,"Strong pivot exceeded feasibility allowance");
        require(stable_primal_leaving({0,0},{2e-9,1},{0,1},0,tol,true)==0,"Bland choice changed");
        require(stable_primal_leaving({0,0},{1,2},{0,1},0,tol,false)==0,"Strong original choice changed");
        require(stable_primal_leaving({0,0,0},{2e-9,1,1},{0,8,3},0,tol,false)==2,"Equal-pivot tie is unstable");
        require(stable_primal_leaving({0,0},{-1,-2},{0,1},2,tol,false)==2,"Missing leaving row changed");
        require(stable_primal_leaving({},{},{},0,tol,false)==0,"Empty basis mishandled");
        require(stable_primal_leaving({0},{2e-9},{0},0,tol,false)==0,"Genuine sole small pivot discarded");
        require(stable_primal_leaving({0,0},{2e-9,INFINITY},{0,1},0,tol,false)==0,"Nonfinite direction used for stability selection");
        for(unsigned k=0;k<512;++k) {
            std::vector<double> x={0,(k%7)*tol/4,((k*13)%11)*tol/5};
            std::vector<double> d={2e-9,1.0+(k%5),.5+(k%3)};
            std::vector<std::size_t> basis={5,3,1};
            const auto row=stable_primal_leaving(x,d,basis,0,tol,false);
            long double step=static_cast<long double>(x[row])/d[row];
            for(std::size_t i=0;i<x.size();++i)
                require(static_cast<long double>(x[i])-step*d[i]>=-1.0000001L*tol,"Chosen step exceeds existing tolerance");
        }
        require(argc==2,"Provide retained bandm fixture path");
        std::ifstream stream(argv[1]);require(bool(stream),"Fixture missing");
        auto original=sovereign::read_mps(stream);
        for(unsigned mode=0;mode<4;++mode) {
            auto model=original;sovereign::Options options;options.stable_primal_ratio=true;options.time_limit_seconds=10;
            if(mode==1){options.refine_basis=true;options.refine_at_checks=true;}
            if(mode==2){model.maximize=true;for(auto& c:model.cost)c=-c;model.offset=-model.offset;}
            if(mode==3){options.compact_equalities=true;options.refine_basis=true;options.refine_at_checks=true;}
            auto result=sovereign::solve_sparse_lp(model,options);
            require(result.solution.status=="optimal"&&result.solution.optimality_verified,"Retained weak-pivot LP did not complete");
            const double expected=mode==2?158.62801845012078:-158.62801845012078;
            require(std::abs(result.solution.objective-expected)<1e-6,"Retained objective changed");
            require(sovereign::original_violation(model,result.solution.primal,true)<=1e-8,"Original-model feasibility failed");
            options.time_limit_seconds=0;
            auto expired=sovereign::solve_sparse_lp(model,options);
            require(expired.solution.status=="time_limit"&&!expired.solution.optimality_verified,"Zero deadline reported completion");
            options.time_limit_seconds=10;options.iteration_limit=0;
            auto capped=sovereign::solve_sparse_lp(model,options);
            require(capped.solution.status=="iteration_limit"&&!capped.solution.optimality_verified,"Zero pivot cap reported completion");
        }
        std::cout<<"Primal ratio: selection edges, 512 feasibility checks and four retained LP modes passed\n";
        return 0;
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
