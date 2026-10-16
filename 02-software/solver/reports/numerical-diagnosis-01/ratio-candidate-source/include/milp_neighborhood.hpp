#pragma once
#include "mps.hpp"
#include <algorithm>
#include <cmath>

namespace sovereign { namespace detail {
// Scheduling only: never use this threshold to accept points or prune the tree.
inline bool material_gain(double before,double after) {
    return std::isfinite(after)&&(!std::isfinite(before)||before-after>1e-6*(1+std::abs(before)));
}
struct NeighborhoodPlan { bool strong=false; double budget=0; };
inline NeighborhoodPlan reserved_neighborhood_plan(double limit,double elapsed,double spent,
        double guided_spent,std::size_t guided_calls,std::size_t strong_calls,
        std::size_t stalls,double last_strong_time,bool fresh_center) {
    NeighborhoodPlan plan;
    const double total=std::min(30.,.15*limit),remaining=std::max(0.,limit-elapsed);
    plan.strong=strong_calls>0||stalls>=4||guided_calls>=12||guided_spent>=.8*total-.001;
    if(plan.strong) {
        // At most one wide attempt before 40% of the global budget; retain
        // another for after 65%. A better center can bypass only the spacing,
        // never these quotas or the cumulative time allowance.
        const std::size_t released=elapsed<.4*limit?1:(elapsed<.65*limit?3:4);
        if(strong_calls>=released||(strong_calls&&!fresh_center&&elapsed<last_strong_time+.1*limit))return plan;
        plan.budget=std::min(4.,std::max(0.,total-spent)/(4-strong_calls));
    } else plan.budget=std::min(2.,std::max(0.,.8*total-guided_spent));
    plan.budget=std::max(0.,std::min(plan.budget,std::min(.2*remaining,total-spent)));
    return plan;
}
// Local-branching restriction (Fischetti and Lodi, 2003). This model is PRIVATE
// heuristic work: its row and its bounds must never enter the global proof queue.
inline std::vector<std::size_t> binary_neighborhood(LinearProblem& model,
        const std::vector<double>& center,std::size_t radius) {
    std::vector<std::size_t> free;SparseVector row;double rhs=static_cast<double>(radius);
    for(std::size_t j=0;j<model.cost.size();++j)if(model.integer[j]&&model.lower[j]<model.upper[j]) {
        if(std::ceil(model.lower[j])==0&&std::floor(model.upper[j])==1) {
            free.push_back(j);row.push_back({j,center[j]==0?1.:-1.});
            if(center[j]==1)rhs-=1;
        } else model.lower[j]=model.upper[j]=center[j];
    }
    if(!free.empty()) {
        model.rows.push_back(row);model.row_lower.push_back(-std::numeric_limits<double>::infinity());
        model.row_upper.push_back(rhs);
    }
    return free;
}
}}
