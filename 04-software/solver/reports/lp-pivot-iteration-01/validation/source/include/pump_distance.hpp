#pragma once
#include "pump_guidance.hpp"
#include <stdexcept>

namespace sovereign { namespace detail {
// Private L1 projection. No original-objective bound or tree basis lives here.
struct PumpDistanceModel {
    LinearProblem model;
    std::vector<double> target;
    std::size_t columns=0,auxiliaries=0;
    void start(const LinearProblem& p,const std::vector<double>& lo,
               const std::vector<double>& up,const std::vector<double>& seed) {
        columns=p.cost.size();auxiliaries=0;
        if(lo.size()!=columns||up.size()!=columns||seed.size()!=columns)
            throw std::invalid_argument("Distance dive dimension mismatch");
        model=p;model.lower=lo;model.upper=up;model.maximize=false;model.offset=0;
        model.cost.assign(columns,0);model.integer.assign(columns,false);target.assign(columns,0);
        for(std::size_t j=0;j<columns;++j){
            if(!std::isfinite(seed[j])||std::isnan(lo[j])||std::isnan(up[j])||lo[j]>up[j])
                throw std::invalid_argument("Invalid distance dive domain");
            if(!p.integer[j])continue;
            if(std::ceil(lo[j])>std::floor(up[j]))throw std::invalid_argument("Empty distance dive integer domain");
            const double t=std::max(std::ceil(lo[j]),std::min(std::floor(up[j]),std::round(seed[j])));
            target[j]=t;
            // Linearize without auxiliaries only when the entire LP domain is
            // on one side of the target (also handles negative/unit domains).
            if(t<=lo[j]){model.cost[j]=1;model.offset-=t;}
            else if(t>=up[j]){model.cost[j]=-1;model.offset+=t;}
            else {
                const auto a=model.cost.size();++auxiliaries;
                model.names.push_back("__private_distance_"+std::to_string(j));
                model.cost.push_back(1);model.lower.push_back(0);model.upper.push_back(INFINITY);model.integer.push_back(false);
                model.rows.push_back({{j,1},{a,-1}});model.row_lower.push_back(-INFINITY);model.row_upper.push_back(t);
                model.rows.push_back({{j,-1},{a,-1}});model.row_lower.push_back(-INFINITY);model.row_upper.push_back(-t);
            }
        }
    }
    double distance(const LinearProblem& p,const std::vector<double>& x) const {
        if(x.size()!=columns)return INFINITY;
        double d=0;for(std::size_t j=0;j<columns;++j){
            if(!std::isfinite(x[j]))return INFINITY;
            if(p.integer[j])d+=std::abs(x[j]-target[j]);
        }return d;
    }
};
struct PumpDistanceSample {
    std::size_t node=0,auxiliaries=0,lp_calls=0,verified_points=0,warm_starts=0;
    double initial_distance=INFINITY,first_distance=INFINITY,last_distance=INFINITY;
    double first_target_distance=INFINITY,last_target_distance=INFINITY;
};
struct PumpDistanceStats {
    std::size_t dives=0,lp_calls=0,verified_points=0,warm_starts=0;
    std::vector<PumpDistanceSample> samples;
};
}}
