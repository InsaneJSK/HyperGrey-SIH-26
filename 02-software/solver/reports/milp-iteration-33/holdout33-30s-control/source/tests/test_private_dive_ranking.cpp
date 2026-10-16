#include "milp.hpp"
#include "private_dive_ranking.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <numeric>
using namespace sovereign;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
int main(int argc,char** argv){try{
    // Saved vectors are diagnostic inputs to the ranking helper only, never MILP seeds.
    if(argc==2){
        std::ifstream in(argv[1]);std::size_t n;require(bool(in>>n),"Missing ranking fixture");
        std::vector<bool> integer(n);std::vector<double> x(n);
        for(std::size_t j=0;j<n;++j){int t;require(bool(in>>t>>x[j]),"Invalid ranking fixture");integer[j]=t;}
        const auto c=detail::private_dive_choice(integer,x,1e-7);
        std::cout<<c.strict_column<<' '<<c.column<<' '<<c.ties<<'\n';return 0;
    }
    auto pick=[](const std::vector<double>& x){return detail::private_dive_choice(std::vector<bool>(x.size(),true),x,1e-7);};
    auto c=pick({.25,.25+2e-16});require(c.column==0&&c.strict_column==1&&c.ties==2,"Near tie unstable");
    c=pick({.25,.25+2e-12});require(c.column==1&&c.ties==1,"Outside tie ignored");
    c=pick({.25,.25+0.75e-12,.25+1.5e-12});require(c.column==1&&c.ties==2,"Pairwise tie chain used");
    require(pick({1e-7,1e-7+5e-13}).column==1,"Ranking relaxed integrality eligibility");
    require(pick({0,1,-2}).column==3&&pick({}).column==0,"Integral/empty vector selection");
    require(detail::private_dive_choice({false,true},{.5,.25},1e-7).column==1,"Continuous variable selected");
    for(double shift:{-100.,-3.,0.,7.,100.})for(double perturb:{-2e-14,0.,2e-14}){
        c=pick({shift+.25,shift+.25+perturb,shift+.1});require(c.column==0&&c.ties==2,"Translated perturbation unstable");
        c=pick({shift-.25,shift-.25+perturb,shift-.1});require(c.column==0&&c.ties==2,"Negative perturbation unstable");
    }
    std::vector<double> x={.25,.1,.25+2e-14,.25-2e-14};std::vector<int> order={0,1,2,3};
    do{
        std::vector<double> permuted;std::size_t first=4;
        for(std::size_t j=0;j<4;++j){permuted.push_back(x[order[j]]);if(order[j]!=1&&first==4)first=j;}
        c=pick(permuted);require(c.column==first&&c.ties==3,"Permutation violated anchored tie set/order");
    }while(std::next_permutation(order.begin(),order.end()));
    for(double v:{NAN,INFINITY,-INFINITY}){
        bool rejected=false;try{pick({.25,v});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Nonfinite point accepted");
    }
    for(double tol:{0.,-1.,double(NAN),double(INFINITY)}){
        bool rejected=false;try{detail::private_dive_choice({true},{.25},tol);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Invalid tolerance accepted");
    }
    bool rejected=false;try{detail::private_dive_choice({true},{},1e-7);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Dimension mismatch accepted");
    for(bool maximum:{false,true})for(double shift:{-3.,0.,2.}){
        auto p=linear_from_dense({{1,2},{{-1,-1}},{-1}});p.lower={shift,shift};p.upper={shift+1,shift+1};p.row_upper={-1-2*shift};p.integer={true,true};p.maximize=maximum;
        require(detail::private_dive_choice(p.integer,{shift+.25,shift+.25+2e-14},1e-7).column==0,"Sense/domain changed ranking");
        MilpOptions o;o.pump_distance_stable_ranking=true;rejected=false;
        try{solve_milp(p,o);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"Missing prerequisite accepted");
        o.pump_guided_diving=o.pump_distance_diving=o.pump_primal_reopt=o.pump_distance_reopt=o.pump_distance_stage=true;
        o.lp.time_limit_seconds=0;auto r=solve_milp(p,o);require(r.status=="time_limit"&&r.private_ranking_calls==0,"Zero time not inert");
        o.lp.time_limit_seconds=5;o.lp.iteration_limit=0;r=solve_milp(p,o);require(r.primal.empty()&&r.private_ranking_calls==0,"Exhausted LP budget advances ranking");
        o.lp.iteration_limit=10000;p.lower[0]=shift+.2;p.upper[0]=shift+.8;
        for(bool presolve:{false,true}){o.presolve=presolve;r=solve_milp(p,o);require(r.status=="infeasible"&&r.primal.empty()&&r.private_ranking_calls==0,"Empty integer domain not guarded");}
    }
    std::cout<<"Private ranking ties, anchored set, perturbations, domains, MIN/MAX, permutations, nonfinite and resource guards PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
