#pragma once
#include "mps.hpp"
#include <algorithm>
#include <cmath>

namespace sovereign { namespace detail {
inline double integer_distance(const LinearProblem& p,const std::vector<double>& x) {
    if(x.size()!=p.cost.size())return INFINITY;
    double d=0;
    for(std::size_t j=0;j<x.size();++j){
        if(!std::isfinite(x[j]))return INFINITY;
        if(p.integer[j])d+=std::abs(x[j]-std::round(x[j]));
    }
    return d;
}
// A heuristic point ONLY. Deliberately has no LP basis, objective bound or proof status.
struct PumpDiveSeed {
    std::vector<double> point;
    double initial_distance=INFINITY,best_distance=INFINITY;
    std::size_t candidates=0,rejected=0,improvements=0;
    void start(const LinearProblem& p,const std::vector<double>& initial) {
        point.clear();candidates=rejected=improvements=0;
        initial_distance=best_distance=integer_distance(p,initial);
    }
    bool consider(const LinearProblem& p,const std::vector<double>& lo,const std::vector<double>& up,
                  const std::vector<double>& x,bool verified) {
        ++candidates;
        double d=integer_distance(p,x);
        if(!verified||!std::isfinite(d)||!std::isfinite(initial_distance)||lo.size()!=x.size()||up.size()!=x.size()){
            ++rejected;return false;
        }
        for(std::size_t j=0;j<x.size();++j)if(std::isnan(lo[j])||std::isnan(up[j])||lo[j]>up[j]||x[j]<lo[j]-1e-7||x[j]>up[j]+1e-7){
            ++rejected;return false;
        }
        if(original_violation(p,x,false)>1e-7){++rejected;return false;}
        if(d+1e-12*(1+best_distance)>=best_distance)return false;
        point=x;best_distance=d;++improvements;return true;
    }
};
inline bool pump_target_up(double value,double guide,double lo,double up,bool fallback) {
    if(!std::isfinite(value)||!std::isfinite(guide)||std::isnan(lo)||std::isnan(up)||std::ceil(lo)>std::floor(up))return fallback;
    const double target=std::max(std::ceil(lo),std::min(std::floor(up),std::round(guide)));
    return target>=std::ceil(value);
}
struct PumpGuidanceSample {
    std::size_t node=0,candidates=0,rejected=0,improvements=0,steps=0;
    double initial_distance=INFINITY,best_distance=INFINITY;
    bool selected=false,used=false;
    std::vector<double> initial,point;
};
struct PumpGuidanceStats {
    std::size_t calls=0,candidates=0,rejected=0,improvements=0,dives=0,steps=0,stored_values=0;
    std::vector<PumpGuidanceSample> samples;
};
}}
