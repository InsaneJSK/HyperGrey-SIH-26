#include "milp.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <sstream>
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
double objective(const sovereign::LinearProblem& p,const std::vector<double>& x){double v=p.offset;for(std::size_t j=0;j<x.size();++j)v+=p.cost[j]*x[j];return v;}
int main(){try{
    std::uint32_t seed=73126119;auto random=[&](int n){seed=1664525u*seed+1013904223u;return int(seed%std::uint32_t(n));};
    for(int test=0;test<600;++test){
        const bool recourse=test%3!=0;const std::size_t bits=8,rows=4,fixed=bits+(recourse?rows:0);
        sovereign::LinearProblem p;p.names.resize(fixed+1);p.cost.resize(fixed+1);p.lower.assign(fixed+1,0);p.upper.assign(fixed+1,1);p.integer.assign(fixed+1,true);
        p.rows.resize(rows);p.row_lower.resize(rows);p.row_upper.resize(rows);p.maximize=test%2;p.offset=random(11)-5;p.lower[fixed]=p.upper[fixed]=-2;
        for(auto& c:p.cost)c=random(17)-8;
        std::vector<double> planted(fixed+1,0);planted[fixed]=-2;for(std::size_t j=0;j<bits;++j)planted[j]=random(2);
        for(std::size_t i=0;i<rows;++i){
            double rhs=-2;for(std::size_t j=0;j<bits;++j){double a=random(11)-5;p.rows[i].push_back({j,a});rhs+=a*planted[j];}p.rows[i].push_back({fixed,1});
            if(recourse){std::size_t j=bits+i;p.integer[j]=false;p.lower[j]=-3;p.upper[j]=5;double c=i%2?-1:1;p.rows[i].push_back({j,c});rhs+=c*2;p.row_lower[i]=p.row_upper[i]=rhs;}
            else {p.row_lower[i]=rhs-random(5);p.row_upper[i]=rhs+random(5);}
        }
        if(test%15==0){p.rows[0].clear();for(std::size_t j=0;j<bits;++j)p.rows[0].push_back({j,2});p.row_lower[0]=p.row_upper[0]=1;}
        bool feasible=false;double best=INFINITY,sign=p.maximize?-1:1;
        for(int mask=0;mask<256;++mask){auto x=planted;for(std::size_t j=0;j<bits;++j)x[j]=(mask>>j)&1;
            if(recourse)for(std::size_t i=0;i<rows;++i){double residual=p.row_lower[i];for(auto a:p.rows[i])if(a.first!=bits+i)residual-=a.second*x[a.first];x[bits+i]=residual/(i%2?-1:1);}
            if(sovereign::original_violation(p,x,false)==0){feasible=true;best=std::min(best,sign*objective(p,x));}
        }
        auto result=sovereign::detail::binary_proof(p,2);
        require(result.eligible&&result.completed&&result.verified,"Exact test failed to complete");
        require(result.feasible==feasible,"False exact feasibility/infeasibility");
        require(result.left_states==16&&result.right_states==16,"Incomplete state coverage certified");
        if(feasible){std::vector<double> x(result.primal.begin(),result.primal.end());require(sovereign::original_violation(p,x,false)==0,"Exact witness fails original rows");require(result.objective_minimization==best&&sign*objective(p,x)==best,"Exact proof disagrees with enumeration");}
        else require(result.status=="infeasible"&&result.primal.empty(),"Infeasibility result contains a witness");
    }
    auto simple=sovereign::linear_from_dense({{-1,-2},{{1,1}},{1}});simple.upper={1,1};simple.integer={true,true};
    auto reject=[&](const sovereign::LinearProblem& p){auto r=sovereign::detail::binary_proof(p,1);require(!r.verified&&!r.completed&&r.status=="unsupported","Unsupported arithmetic/domain certified");};
    auto p=simple;p.rows[0][0].second=1+1e-10;reject(p);p=simple;p.cost[0]=.5;reject(p);
    p=simple;p.offset=.5;reject(p);p=simple;p.lower[0]=-.1;reject(p);p=simple;p.upper[0]=2;reject(p);
    p=simple;p.integer[1]=false;p.row_lower=p.row_upper;p.rows[0][1].second=2;reject(p);
    p=simple;p.integer[1]=false;reject(p);
    p=simple;p.integer[1]=false;p.rows.push_back(p.rows[0]);p.row_lower.push_back(-INFINITY);p.row_upper.push_back(1);reject(p);
    p=simple;p.rows[0][0].second=p.rows[0][1].second=std::ldexp(1.,50);reject(p);
    p=simple;p.rows[0]={{0,std::ldexp(1.,50)},{0,std::ldexp(1.,50)},{0,-std::ldexp(1.,50)}};reject(p);
    p=simple;p.names.resize(37);p.cost.resize(37);p.lower.resize(37,0);p.upper.resize(37,1);p.integer.resize(37,true);reject(p);
    p=simple;p.rows.resize(33);p.row_lower.resize(33,-INFINITY);p.row_upper.resize(33,1);reject(p);
    // A literal fractional part can disappear during double conversion. It must
    // not silently turn into integer-proof eligibility.
    const std::string prefix="NAME LITERAL\nROWS\n N O\n L R\nCOLUMNS\n X O 1 R ";
    const std::string suffix="\nRHS\n B R 1\nBOUNDS\n BV B X\nENDATA\n";
    for(const std::string token:{"1.00000000000000000000000000001","0.5","1e-3","1e20"}){
        std::istringstream input(prefix+token+suffix);auto parsed=sovereign::read_mps(input);
        require(!parsed.integer_input_literals,"Nonintegral source literal lost");reject(parsed);
    }
    for(const std::string token:{"1.000","100D-2","0.000E-9","1E0"}){
        std::istringstream input(prefix+token+suffix);auto parsed=sovereign::read_mps(input);
        require(parsed.integer_input_literals&&sovereign::detail::binary_proof(parsed,1).verified,"Exact integral decimal literal rejected");
    }
    std::istringstream cancellation(prefix+"1125899906842624\n X R 1125899906842624\n X R -1125899906842624"+suffix);
    auto cancelled=sovereign::read_mps(cancellation);require(!cancelled.integer_input_literals,"Unsafe source accumulation lost");reject(cancelled);
    auto stopped=sovereign::detail::binary_proof(simple,1,1);require(!stopped.completed&&!stopped.verified&&stopped.status=="work_limit","Work interruption certified");
    stopped=sovereign::detail::binary_proof(simple,0);require(!stopped.completed&&!stopped.verified&&stopped.work==0,"Zero budget ignored");
    stopped=sovereign::detail::binary_proof(simple,1e-12);require(!stopped.completed&&!stopped.verified,"Deadline interruption certified");
    // Exact algorithm remains active with heuristics disabled, but respects
    // global zero-time/node limits and falls back without bounds on work=0.
    auto hard=sovereign::linear_from_dense({{5,2,1,5,-3,-6,-2},{{-3,3,-2,-2,5,0,-3},{3,4,2,-1,-3,2,6},{1,2,1,4,6,0,4}},{5,11,9}});
    hard.upper.assign(7,1);hard.integer.assign(7,true);
    sovereign::MilpOptions opt;opt.binary_proof=true;opt.heuristics=false;opt.node_limit=1;opt.lp.time_limit_seconds=5;
    auto exact=sovereign::solve_milp(hard,opt);require(exact.status=="optimal"&&exact.objective==-9&&exact.best_bound==-9&&exact.gap==0&&exact.binary_proof.verified,"Exact proof integration failed");
    for(auto& c:hard.cost)c=-c;hard.maximize=true;exact=sovereign::solve_milp(hard,opt);require(exact.status=="optimal"&&exact.objective==9&&exact.best_bound==9&&exact.gap==0,"Exact max-sense proof failed");
    opt.binary_proof_work=0;auto incomplete=sovereign::solve_milp(hard,opt);opt.binary_proof=false;auto control=sovereign::solve_milp(hard,opt);
    require(!incomplete.binary_proof.verified&&incomplete.status==control.status&&incomplete.best_bound==control.best_bound&&incomplete.primal==control.primal,"Incomplete proof changed ordinary results");
    opt.binary_proof=true;opt.binary_proof_work=50000000;opt.lp.time_limit_seconds=0;require(sovereign::solve_milp(hard,opt).binary_proof_attempts==0,"Proof ignored zero time");
    opt.lp.time_limit_seconds=5;opt.node_limit=0;require(sovereign::solve_milp(hard,opt).binary_proof_attempts==0,"Proof ignored zero nodes");
    std::cout<<"600 exhaustive exact-proof models plus arithmetic/domain/resource/integration regressions passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
