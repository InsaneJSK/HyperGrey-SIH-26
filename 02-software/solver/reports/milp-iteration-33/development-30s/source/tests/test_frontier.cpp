#include "milp.hpp"
#include "milp_frontier.hpp"
#include <algorithm>
#include <iostream>
#include <map>
#include <random>
#include <tuple>
using namespace sovereign;
void need(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
struct Item {double bound,search_bound;std::size_t id,depth;};
LinearProblem vars(std::size_t n){LinearProblem p;p.names.resize(n);p.cost.assign(n,1);p.lower.assign(n,-1);p.upper.assign(n,2);p.integer.assign(n,true);return p;}
int main(){try{
    detail::MilpFrontier<Item> q(true);q.push({10,0,1,0});q.push({1,.5,2,0});
    need(q.top().bound==10&&q.minimum_bound()==1,"Search top was used as proof minimum");
    need(q.pop().id==1&&q.minimum_bound()==1,"Pop removed wrong proof entry");
    q.clear();q.push({10,0,1,0});q.push({1,.5,2,0});need(q.pop().id==1,"Clear changed priority policy");
    bool rejected=false;try{q.push({NAN,0,3,0});}catch(const std::logic_error&){rejected=true;}
    need(rejected&&q.size()==1&&q.minimum_bound()==1,"NaN corrupted frontier");
    std::mt19937 rng(2611913);std::size_t operations=0;
    for(bool raw:{false,true}){
        detail::MilpFrontier<Item> frontier(raw);std::map<std::size_t,Item> live;std::size_t serial=0;
        for(int k=0;k<50000;++k){
            auto action=rng()%100;
            if(action<2){frontier.clear();live.clear();}
            else if(live.empty()||action<58){
                Item item={double(int(rng()%41)-20),double(int(rng()%61)-30),serial++,rng()%10};
                if(k%71==0)item.bound=-INFINITY;if(k%73==0)item.bound=INFINITY;
                frontier.push(item);live.emplace(item.id,item);
            }else{
                auto expected=std::min_element(live.begin(),live.end(),[&](const std::pair<const std::size_t,Item>& a,const std::pair<const std::size_t,Item>& b){
                    const auto& x=a.second;const auto& y=b.second;
                    return std::make_tuple(raw?x.search_bound:x.bound,-int(x.depth),x.id)<std::make_tuple(raw?y.search_bound:y.bound,-int(y.depth),y.id);
                });
                need(frontier.pop().id==expected->first,"Priority selection differs from independent scan");live.erase(expected);
            }
            double minimum=INFINITY;for(auto entry:live)minimum=std::min(minimum,entry.second.bound);
            need(frontier.minimum_bound()==minimum&&frontier.size()==live.size()&&frontier.empty()==live.empty(),"Proof index differs from independent scan");++operations;
        }
    }
    std::size_t restarts=0,partial=0,solves=0;
    for(int test=0;test<240;++test){
        bool derived=test%2;auto p=vars(derived?6:5);p.maximize=test%3==0;p.offset=(test%9-4)*.25;
        std::vector<double> planted(5),definition(5);for(int j=0;j<5;++j){p.cost[j]=int(rng()%15)-7;planted[j]=int(rng()%4)-1;definition[j]=2*(int(rng()%7)-3);}
        if(derived){
            p.integer[5]=false;p.lower[5]=-INFINITY;p.upper[5]=INFINITY;p.cost[5]=test%4<2?1:-1;
            SparseVector row;for(std::size_t j=0;j<5;++j)if(definition[j])row.push_back({j,definition[j]});row.push_back({5,test%5<2?1.:-1.});
            p.rows.push_back(row);p.row_lower={double(test%7-3)};p.row_upper=p.row_lower;
        }
        for(int i=0;i<4;++i){SparseVector row;double b=.5+(rng()%3);
            for(std::size_t j=0;j<5;++j){double a=int(rng()%9)-4;if(a)row.push_back({j,a});b+=a*planted[j];}
            p.rows.push_back(row);p.row_lower.push_back(-INFINITY);p.row_upper.push_back(b);
        }
        double expected=INFINITY;for(int code=0;code<1024;++code){
            int v=code;std::vector<double> x(p.cost.size());for(int j=0;j<5;++j){x[j]=v%4-1;v/=4;}
            if(derived){double rhs=p.row_lower[0];for(int j=0;j<5;++j)rhs-=definition[j]*x[j];x[5]=rhs/p.rows[0].back().second;}
            if(original_violation(p,x,false)>1e-10)continue;
            double z=p.offset;for(std::size_t j=0;j<x.size();++j)z+=p.cost[j]*x[j];expected=std::min(expected,p.maximize?-z:z);
        }
        need(std::isfinite(expected),"Unplanted generated model");
        for(int profile=0;profile<3;++profile){
            MilpOptions o;o.objective_lattice=profile>0;o.raw_lp_priority=profile==2;o.capture_frontier=true;
            o.lp.time_limit_seconds=3;o.heuristics=test%4==0;o.presolve=test%3==0;o.cover_cuts=test%2==0;
            if(test%6==0){o.late_lifted_covers=true;o.lifted_covers=true;o.late_compact_equalities=true;o.late_reduced_bound_lp=true;o.late_cover_restart_nodes=2;}
            auto result=solve_milp(p,o);++solves;restarts+=result.cut_restarts;
            need(result.status=="optimal"||result.status=="gap_limit","Generated completion missing");
            need(std::abs((p.maximize?-result.objective:result.objective)-expected)<=1e-7&&original_violation(p,result.primal,false)<=1e-7,"Exhaustive optimum/witness mismatch");
            o.node_limit=3;o.heuristics=false;result=solve_milp(p,o);++partial;
            need((p.maximize?-result.best_bound:result.best_bound)<=expected+1e-7,"Partial bound excludes optimum");
            if(!result.primal.empty())need(original_violation(p,result.primal,false)<=1e-7,"Partial incumbent infeasible");
            o.lp.time_limit_seconds=0;result=solve_milp(p,o);++partial;
            need(result.status=="time_limit"&&result.nodes==0,"Zero time was certified");
        }
    }
    need(restarts>10,"Restart coverage not exercised");
    auto p=vars(8);p.upper.assign(8,1);p.lower.assign(8,0);p.cost.assign(8,-1);p.rows={};
    for(int i=0;i<7;++i){p.rows.push_back({{std::size_t(i),1},{std::size_t(i+1),1}});p.row_lower.push_back(-INFINITY);p.row_upper.push_back(1.5);}
    MilpOptions o;o.objective_lattice=true;o.raw_lp_priority=true;o.capture_frontier=true;o.presolve=false;o.heuristics=false;o.cover_cuts=false;o.lp.iteration_limit=1;
    auto stopped=solve_milp(p,o);need(stopped.status!="optimal"&&stopped.status!="gap_limit"&&stopped.best_bound<=-4,"LP limit exported an unsafe bound");
    o.lp_recovery=true;auto deferred=solve_milp(p,o);need(deferred.best_bound<=-4,"Deferred LP bound excluded feasible point");
    need(deferred.deferred_nodes>0,"Deferred path not exercised");
    std::cout<<operations<<" queue operations; "<<solves<<" solves on 240 exhaustive models; "<<partial
             <<" partial/zero-time checks; "<<restarts<<" forced restarts; LP-limit and deferred coverage\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
