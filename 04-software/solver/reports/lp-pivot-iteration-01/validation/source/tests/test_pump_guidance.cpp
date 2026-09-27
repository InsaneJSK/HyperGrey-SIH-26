#include "milp.hpp"
#include <iostream>
#include <cstdint>
using namespace sovereign;
void require(bool yes,const char* message){if(!yes)throw std::runtime_error(message);}
int main(){try{
    LinearProblem p;p.names={"a","b","c"};p.cost={1,2,3};p.lower={-2,0,-10};p.upper={3,1,10};p.integer={true,true,false};
    p.rows={{{0,1},{1,1},{2,1}}};p.row_lower={-10};p.row_upper={1.5};
    detail::PumpDiveSeed s;s.start(p,{.4,.4,0});
    require(s.consider(p,p.lower,p.upper,{.1,.2,.5},true),"Valid progress lost");
    require(std::abs(s.initial_distance-.8)<1e-12&&std::abs(s.best_distance-.3)<1e-12,"Wrong integer distance");
    require(!s.consider(p,p.lower,p.upper,{.3,.3,0},true),"Worse point replaced best");
    require(!s.consider(p,p.lower,p.upper,{.1,.2,.5},true),"Tie replaced best");
    const auto saved=s.point;
    require(!s.consider(p,p.lower,p.upper,{.01,.01,0},false),"Unverified projection accepted");
    require(!s.consider(p,p.lower,p.upper,{NAN,0,0},true),"Nonfinite seed accepted");
    require(!s.consider(p,p.lower,p.upper,{.01,0},true),"Wrong dimension accepted");
    require(!s.consider(p,p.lower,p.upper,{3.01,0,0},true),"Original bound violation accepted");
    require(!s.consider(p,p.lower,p.upper,{2.01,0,0},true),"Original row violation accepted");
    auto lo=p.lower;lo[0]=.5;
    require(!s.consider(p,lo,p.upper,{.01,.01,0},true),"Node bound violation accepted");
    require(s.point==saved&&s.rejected==6&&s.improvements==1,"Rejected seed changed incumbent hint");
    require(s.consider(p,p.lower,p.upper,{-.01,.01,0},true),"Negative integer-domain progress lost");
    s.start(p,{INFINITY,0,0});require(!s.consider(p,p.lower,p.upper,{0,0,0},true),"Invalid initial metric accepted");
    require(detail::pump_target_up(.3,.9,0,1,false),"Binary up direction wrong");
    require(!detail::pump_target_up(.8,.1,0,1,true),"Binary down direction wrong");
    require(!detail::pump_target_up(2.2,-1.9,1,4,true),"Lower clipping wrong");
    require(detail::pump_target_up(-2.2,8,-4,-1,false),"Upper clipping wrong");
    require(detail::pump_target_up(.2,NAN,0,1,true),"Fallback on invalid guide wrong");
    require(!detail::pump_target_up(.2,.8,1,0,false),"Empty integer domain did not fall back");
    std::uint32_t rng=26120;auto next=[&](){rng=1664525u*rng+1013904223u;return rng;};
    std::size_t guided_dives=0,seed_calls=0;
    for(int k=0;k<40;++k){
        LinearProblem q;q.names.resize(8);q.cost.resize(8);q.lower.assign(8,0);q.upper.assign(8,1);q.integer.assign(8,true);
        q.maximize=k%2;q.offset=k-20;const unsigned witness=next()%256;
        for(int j=0;j<8;++j){q.names[j]="x"+std::to_string(j);q.cost[j]=int(next()%19)-9;}
        for(int i=0;i<4;++i){SparseVector row;double rhs=0;
            for(int j=0;j<8;++j){double a=int(next()%11)-5;if(a){row.push_back({std::size_t(j),a});rhs+=a*((witness>>j)&1);}}
            q.rows.push_back(row);q.row_lower.push_back(rhs-2.4);q.row_upper.push_back(rhs+3.7);
        }
        double expected=q.maximize?-INFINITY:INFINITY;
        for(unsigned mask=0;mask<256;++mask){std::vector<double>x(8);double z=q.offset;
            for(int j=0;j<8;++j){x[j]=(mask>>j)&1;z+=q.cost[j]*x[j];}
            if(original_violation(q,x,false)<=1e-7)expected=q.maximize?std::max(expected,z):std::min(expected,z);
        }
        for(int enabled=0;enabled<3;++enabled){
            MilpOptions o;o.lp.time_limit_seconds=5;o.cover_cuts=false;o.lp.refine_basis=true;o.lp.refine_at_checks=true;
            o.repair_candidates=true;o.repair_heuristic_candidates=true;o.pump_guided_diving=enabled;o.capture_feasibility=true;
            o.pump_distance_diving=enabled==2;
            auto r=solve_milp(q,o);
            require(r.status=="optimal"||r.status=="gap_limit","Generated model not completed");
            require(std::abs(r.objective-expected)<1e-7,"Wrong exhaustive optimum");
            require(original_violation(q,r.primal,true)<=1e-7,"Invalid final candidate");
            for(double v:r.primal)require(std::abs(v-std::round(v))<=o.integer_tolerance,"Fractional final candidate");
            require(q.maximize?r.best_bound>=expected-1e-7:r.best_bound<=expected+1e-7,"Guidance corrupted proof bound");
            if(!enabled)require(r.pump_guidance.calls==0&&r.pump_guidance.dives==0,"Disabled guidance not inert");
            guided_dives+=r.pump_guidance.dives;seed_calls+=r.pump_guidance.calls;
            for(const auto& e:r.pump_guidance.samples)if(e.selected){
                require(e.best_distance<e.initial_distance,"No strict seed improvement");
                require(!e.point.empty()&&original_violation(q,e.point,false)<=1e-7,"Invalid retained seed");
                require(std::abs(detail::integer_distance(q,e.point)-e.best_distance)<1e-10,"Seed metric mismatch");
            }
        }
    }
    require(seed_calls>0,"Pump selection path not exercised");
    std::cout<<"40 exhaustive MIN/MAX models, 120 solves; "<<seed_calls<<" seed calls; "<<guided_dives<<" guided dives; eligibility and clipping PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
