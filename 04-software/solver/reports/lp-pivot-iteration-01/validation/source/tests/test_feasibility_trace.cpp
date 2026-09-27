#include "milp.hpp"
#include <iostream>
using namespace sovereign;
void require(bool v,const char* m){if(!v)throw std::runtime_error(m);}
int main(){try{
    std::size_t events=0;
    for(int k=0;k<40;++k){
        LinearProblem p;p.names={"a","b","c","d","e"};p.lower.assign(5,0);p.upper.assign(5,1);p.integer.assign(5,true);
        p.cost={1.,2.,3.,4.,5.};p.maximize=k%2;p.offset=k-20;
        p.rows={{{0,1},{1,1},{2,1},{3,1},{4,1}}};p.row_lower={2.+(k%8+1)/10.};p.row_upper={3.9};
        MilpOptions o;o.lp.time_limit_seconds=5;o.cover_cuts=false;o.lp.refine_basis=true;o.lp.refine_at_checks=true;
        auto a=solve_milp(p,o);o.capture_feasibility=true;auto b=solve_milp(p,o);
        require(a.status==b.status&&a.objective==b.objective&&a.best_bound==b.best_bound&&a.primal==b.primal&&a.nodes==b.nodes&&a.lp_iterations==b.lp_iterations,"Telemetry changed untimed semantic result");
        require(a.feasibility.events==0&&a.feasibility.samples.empty(),"Disabled trace recorded");
        require(b.status=="optimal"||b.status=="gap_limit","Small model not complete");
        double expected=p.maximize?-INFINITY:INFINITY;
        for(unsigned mask=0;mask<32;++mask){std::vector<double>x(5);double z=p.offset;for(int j=0;j<5;++j){x[j]=(mask>>j)&1;z+=x[j]*p.cost[j];}
            if(original_violation(p,x,false)<=1e-7)expected=p.maximize?std::max(expected,z):std::min(expected,z);}
        require(std::abs(expected-b.objective)<1e-7,"Wrong exhaustive optimum");events+=b.feasibility.events;
        for(const auto& e:b.feasibility.samples)if(!e.point.empty()){
            double d=0;std::size_t f=0;for(double x:e.point){double v=std::abs(x-std::round(x));d+=v;f+=v>o.integer_tolerance;}
            require(std::abs(d-e.distance)<1e-12&&f==e.fractional,"Wrong distance trace");
        }
    }
    require(events>100,"Feasibility trace not exercised");
    LinearProblem p;p.names.assign(2048,"x");p.cost.assign(2048,0);p.lower.assign(2048,0);p.upper.assign(2048,1);p.integer.assign(2048,true);
    detail::FeasibilityTrace t;detail::FeasibilityEvent e;e.kind="test";std::vector<double>x(2048,.25);
    for(int i=0;i<600;++i)t.record(true,p,1e-7,e,x,x);
    require(t.events==600&&t.samples.size()==512&&t.stored_values<=100000,"Trace resource cap broken");
    std::cout<<"40 min/max exhaustive models, 80 trace parity solves; "<<events<<" events; bounded trace PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
