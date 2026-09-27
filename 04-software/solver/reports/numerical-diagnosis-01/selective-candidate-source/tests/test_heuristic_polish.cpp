#include "milp.hpp"
#include "heuristic_polish.hpp"
#include <fstream>
#include <iostream>
using namespace sovereign;
void require(bool v,const char* m){if(!v)throw std::runtime_error(m);}
int main(int argc,char** argv){try{
    require(argc==3,"Expected original model and saved rejected point");
    std::ifstream model(argv[1]),saved(argv[2]);require(bool(model)&&bool(saved),"Missing retained fixture inputs");
    auto p=read_mps(model);std::size_t n;saved>>n;std::vector<double>x(n);for(auto& v:x)saved>>v;
    require(bool(saved)&&n==p.cost.size(),"Invalid saved candidate");
    require(original_violation(p,x,false)>1e-7,"Raw failure no longer reproduced");
    Options o;o.refine_basis=true;o.refine_at_checks=true;o.capture_refinement=true;
    for(int sense=0;sense<2;++sense){
        if(sense){p.maximize=!p.maximize;p.offset=-p.offset;for(auto& c:p.cost)c=-c;}
        auto r=detail::polish_heuristic(p,x,o,1e-7,5);
        require(!r.primal.empty()&&original_violation(p,r.primal,false)<=1e-7,"Captured integer fixing not repaired");
        require(r.sparse_called&&r.dense_called,"Captured fallback branch not exercised");
        double z=p.offset;for(std::size_t j=0;j<n;++j){z+=p.cost[j]*r.primal[j];if(p.integer[j])require(r.primal[j]==std::round(x[j]),"Repair changed integer assignment");}
        require(std::abs(z-(sense?-8.788661:8.788661))<1e-7,"Repaired objective wrong");
    }
    auto zero=detail::polish_heuristic(p,x,o,1e-7,0);require(zero.status=="budget"&&!zero.sparse_called&&!zero.dense_called,"Zero budget did LP work");
    auto bad=x;bad[0]=NAN;auto r=detail::polish_heuristic(p,bad,o,1e-7,5);require(r.status=="ineligible"&&!r.sparse_called,"Nonfinite candidate accepted");
    for(std::size_t j=0;j<n;++j)if(p.integer[j]){bad=x;bad[j]=std::round(bad[j])+.1;r=detail::polish_heuristic(p,bad,o,1e-7,5);require(r.status=="ineligible"&&!r.sparse_called,"Fractional candidate fixed");break;}
    MilpOptions invalid;invalid.repair_heuristic_candidates=true;bool rejected=false;try{solve_milp(p,invalid);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Repair flag missing dependency accepted");
    detail::FeasibilityTrace trace;detail::FeasibilityEvent e;e.kind="dive_point";
    for(int i=0;i<400;++i){e.kind="dive_trial";trace.record(true,p,1e-7,e,x,x);}
    e.kind="dive_point";trace.record(true,p,1e-7,e,x);
    require(trace.rejected_point==x&&trace.stored_values<=100000&&trace.rejected_rounded_violation>1e-7,"Priority rejection capture lost or cap exceeded");
    std::cout<<"Cold MIN/MAX captured rejection repair, fixed assignments, budget/input guards and priority capture PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
