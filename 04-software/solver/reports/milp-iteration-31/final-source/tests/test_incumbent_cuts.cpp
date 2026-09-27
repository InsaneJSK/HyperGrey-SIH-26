#include "milp.hpp"
#include <iostream>
using namespace sovereign;
void require(bool v,const char* m){if(!v)throw std::runtime_error(m);}
LinearProblem model(int pairs,bool maximize){
    LinearProblem p;const int chain=320,n=2*pairs+chain;const double sign=maximize?-1:1;
    p.maximize=maximize;p.names.resize(n);p.cost.assign(n,1000*sign);p.lower.assign(n,0);
    p.upper.assign(n,INFINITY);p.integer.assign(n,false);
    for(int i=0;i<2*pairs;++i){p.integer[i]=true;p.upper[i]=1;p.cost[i]=-100*sign;}
    for(int i=0;i<pairs;++i){p.rows.push_back({{std::size_t(2*i),2},{std::size_t(2*i+1),2}});p.row_lower.push_back(-INFINITY);p.row_upper.push_back(3);}
    for(int i=0;i<chain;++i){SparseVector row={{std::size_t(2*pairs+i),1}};if(i)row.push_back({std::size_t(2*pairs+i-1),-1});
        p.rows.push_back(row);p.row_lower.push_back(1);p.row_upper.push_back(1);}
    return p;
}
int main(){try{
    std::size_t runs=0,protected_rounds=0,known_stops=0;
    for(bool maximize:{false,true})for(int pairs:{40,100}){
        auto p=model(pairs,maximize);const double expected=51360000-100*pairs,sign=maximize?-1:1;
        for(int mode=0;mode<3;++mode){
            MilpOptions o;o.presolve=false;o.heuristics=pairs==100;o.lp.time_limit_seconds=30;o.relative_gap=0;
            o.node_limit=pairs==40?1:2;o.adaptive_cut_rounds=mode>0;o.cut_after_incumbent=mode==2;
            o.capture_cut_rounds=true;o.capture_work=true;
            if(pairs==100){o.late_lifted_covers=true;o.lifted_covers=true;o.restart_by_nodes=true;o.late_cover_restart_nodes=1;}
            auto r=solve_milp(p,o);++runs;
            require(sign*r.best_bound<=expected+1e-6,"Partial bound excludes analytic optimum");
            if(!r.primal.empty()){require(original_violation(p,r.primal,false)<=1e-7,"Invalid analytic point");require(sign*r.objective>=expected-1e-6,"Point beats analytic optimum");}
            for(const auto& t:r.cut_round_trace){
                if(std::string(t.decision)=="no_incumbent"){++protected_rounds;require(!std::isfinite(t.incumbent_objective),"Guard ignores known incumbent");}
                if(mode==2&&std::string(t.decision)=="diminishing_return"){
                    require(std::isfinite(t.incumbent_objective)&&t.restart==1,"Stop without checked restart point");++known_stops;
                    require(original_violation(p,r.cut_restart_primal,false)<=1e-7,"Invalid source incumbent");
                }
            }
            if(pairs==40){
                if(mode==1)require(r.adaptive_cut_stops==1&&r.primal.empty()&&r.status=="node_limit","Ungated branch not exercised");
                else require(!r.primal.empty()&&std::abs(sign*r.objective-expected)<1e-6&&r.gap==0,"Protected first-feasible schedule lost");
            }else if(mode==2)require(r.cut_restarts==1&&r.adaptive_cut_stops>0&&!r.cut_restart_primal.empty(),"Known-incumbent stop not exercised");
            std::cout<<(maximize?"MAX":"MIN")<<" pairs="<<pairs<<" policy="<<mode<<" status="<<r.status<<" stops="<<r.adaptive_cut_stops<<'\n';
        }
    }
    auto p=model(1,false);MilpOptions invalid;invalid.cut_after_incumbent=true;bool rejected=false;
    try{solve_milp(p,invalid);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Invalid policy combination accepted");
    require(protected_rounds>0&&known_stops>=2,"Missing guard integration coverage");
    std::cout<<runs<<" analytic min/max solves; "<<protected_rounds<<" protected rounds; "<<known_stops<<" checked-incumbent stops PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
