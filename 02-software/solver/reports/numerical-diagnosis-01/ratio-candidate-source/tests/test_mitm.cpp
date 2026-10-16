#include "milp.hpp"
#include "milp_meet.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>

void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
double objective(const sovereign::LinearProblem& p,const std::vector<double>& x){double value=p.offset;for(std::size_t j=0;j<x.size();++j)value+=p.cost[j]*x[j];return value;}
int main(){try {
    // 180 independently enumerated small models: signed costs/rows, ranged rows,
    // positive/negative slack coefficients, offsets, fixed variables, min and max.
    std::uint32_t state=26119;auto random=[&](int n){state=1664525u*state+1013904223u;return int(state%std::uint32_t(n));};
    for(int test=0;test<180;++test) {
        const bool recourse=test%3!=0;const std::size_t bits=7,rows=3,fixed=bits+(recourse?rows:0);
        sovereign::LinearProblem p;p.cost.resize(fixed+1);p.lower.assign(fixed+1,0);p.upper.assign(fixed+1,1);
        p.integer.assign(fixed+1,true);p.names.resize(fixed+1);p.rows.resize(rows);p.row_lower.resize(rows);p.row_upper.resize(rows);
        p.maximize=test%2;p.offset=random(9)-4;p.lower[fixed]=p.upper[fixed]=2;
        for(auto& c:p.cost)c=random(13)-6;
        std::vector<double> planted(fixed+1,0);planted[fixed]=2;for(std::size_t j=0;j<bits;++j)planted[j]=random(2);
        for(std::size_t i=0;i<rows;++i) {
            double value=0;for(std::size_t j=0;j<bits;++j){double a=random(9)-4;p.rows[i].push_back({j,a});value+=a*planted[j];}
            p.rows[i].push_back({fixed,1});value+=2;
            if(recourse){auto j=bits+i;p.integer[j]=false;p.lower[j]=-3;p.upper[j]=6;double a=i%2?-2:1;p.rows[i].push_back({j,a});value+=a*.5;p.row_lower[i]=p.row_upper[i]=value;}
            else {p.row_lower[i]=value-random(5);p.row_upper[i]=value+random(5);}
        }
        double best=INFINITY,sign=p.maximize?-1:1;
        for(int mask=0;mask<128;++mask) {
            auto x=planted;for(std::size_t j=0;j<bits;++j)x[j]=(mask>>j)&1;
            if(recourse)for(std::size_t i=0;i<rows;++i){double remaining=p.row_lower[i];for(auto a:p.rows[i])if(a.first!=bits+i)remaining-=a.second*x[a.first];x[bits+i]=remaining/(i%2?-2:1);}
            if(sovereign::original_violation(p,x,false)<=1e-9)best=std::min(best,sign*objective(p,x));
        }
        auto result=sovereign::detail::binary_meet(p,2.,INFINITY);
        require(result.eligible&&result.completed&&!result.primal.empty(),"Small structural search failed");
        require(sovereign::original_violation(p,result.primal,false)<=1e-7,"Meet point violates original model");
        require(std::abs(sign*objective(p,result.primal)-best)<1e-8,"Meet point disagrees with exhaustive enumeration");
        require(result.left_states==8&&result.right_states==16,"Incorrect half enumeration count");
    }
    auto p=sovereign::linear_from_dense({{1,2},{{1,1}},{1}});p.upper={1,1};p.integer={true,true};
    auto zero=sovereign::detail::binary_meet(p,0,INFINITY);require(!zero.eligible&&zero.primal.empty()&&zero.left_states==0,"Zero budget ignored");
    auto wide=p;wide.upper[0]=2;require(!sovereign::detail::binary_meet(wide,1,INFINITY).eligible,"General integer not rejected");
    auto shared=p;shared.integer[1]=false;shared.rows.push_back(shared.rows[0]);shared.row_lower.push_back(-INFINITY);shared.row_upper.push_back(1);
    require(!sovereign::detail::binary_meet(shared,1,INFINITY).eligible,"Coupled continuous recourse not rejected");
    auto inequality=p;inequality.integer[1]=false;require(!sovereign::detail::binary_meet(inequality,1,INFINITY).eligible,"Non-equality recourse not rejected");
    auto big=p;big.cost.resize(37);big.names.resize(37);big.lower.resize(37,0);big.upper.resize(37,1);big.integer.resize(37,true);
    require(!sovereign::detail::binary_meet(big,1,INFINITY).eligible,"Half-state memory cap ignored");
    auto impossible=p;impossible.row_lower={.5};impossible.row_upper={.5};
    auto no_point=sovereign::detail::binary_meet(impossible,1,INFINITY);
    require(no_point.eligible&&no_point.completed&&no_point.primal.empty(),"Infeasible binary equality returned a point");
    auto coupled=sovereign::linear_from_dense({{5,2,1,5,-3,-6,-2},{{-3,3,-2,-2,5,0,-3},{3,4,2,-1,-3,2,6},{1,2,1,4,6,0,4}},{5,11,9}});
    coupled.upper.assign(7,1);coupled.integer.assign(7,true);
    sovereign::MilpOptions opt;opt.node_limit=1;opt.cover_cuts=false;opt.lp.time_limit_seconds=5;
    auto control=sovereign::solve_milp(coupled,opt);opt.binary_meet=true;auto improved=sovereign::solve_milp(coupled,opt);
    require(improved.objective==-9&&improved.binary_meet_improved&&improved.binary_meet_primal==improved.primal,"Integrated meet improvement missing");
    require(improved.status=="node_limit"&&improved.best_bound==control.best_bound&&improved.gap>.1,"Meet enumeration leaked a global proof");
    for(auto& c:coupled.cost)c=-c;coupled.maximize=true;auto maximum=sovereign::solve_milp(coupled,opt);
    require(maximum.objective==9&&maximum.best_bound>10.49&&maximum.status=="node_limit","Meet maximization bound is unsafe");
    opt.heuristics=false;require(sovereign::solve_milp(coupled,opt).binary_meet_attempts==0,"Meet ignored no-heuristics");
    opt.heuristics=true;opt.lp.time_limit_seconds=0;require(sovereign::solve_milp(coupled,opt).binary_meet_attempts==0,"Meet ignored zero time");
    opt.lp.time_limit_seconds=5;opt.node_limit=0;require(sovereign::solve_milp(coupled,opt).binary_meet_attempts==0,"Meet ignored zero nodes");
    std::cout<<"180 exhaustive structural cases plus domain, budget and proof-bound regressions passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
