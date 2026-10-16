#pragma once
#include "sparse_lp.hpp"
#include <chrono>

namespace sovereign { namespace detail {
struct HeuristicPolishResult {
    std::vector<double> primal; // A checked point only, NEVER a bound or node certificate.
    std::string status="ineligible";
    bool sparse_called=false,dense_called=false;
    std::size_t sparse_iterations=0,dense_iterations=0;
    BasisRefinementStats refinement;
};
inline HeuristicPolishResult polish_heuristic(const LinearProblem& original,const std::vector<double>& raw,
                                             Options options,double integer_tolerance,double budget) {
    HeuristicPolishResult out;
    const auto start=std::chrono::steady_clock::now();
    if(raw.size()!=original.cost.size())return out;
    LinearProblem fixed=original;
    for(std::size_t j=0;j<raw.size();++j){
        if(!std::isfinite(raw[j]))return out;
        if(original.integer[j]){
            double v=std::round(raw[j]);
            if(std::abs(raw[j]-v)>integer_tolerance||v<original.lower[j]||v>original.upper[j])return out;
            fixed.lower[j]=fixed.upper[j]=v;
        }
    }
    if(!std::isfinite(budget)||budget<=0){out.status="budget";return out;}
    auto remaining=[&](){return std::max(0.0,budget-std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());};
    if(remaining()<=0){out.status="budget";return out;}
    auto usable=[&](std::vector<double> x){
        if(x.size()!=raw.size())return false;
        for(std::size_t j=0;j<x.size();++j){
            if(!std::isfinite(x[j]))return false;
            if(original.integer[j]){
                if(std::abs(x[j]-fixed.lower[j])>integer_tolerance)return false;
                x[j]=fixed.lower[j];
            }
        }
        if(original_violation(original,x,false)>1e-7)return false;
        out.primal=std::move(x);return true;
    };
    std::fill(fixed.integer.begin(),fixed.integer.end(),false);
    options.tolerance=std::min(options.tolerance,1e-11);
    // Reserve half this SAME allowance for independent-algorithm dense recovery.
    options.time_limit_seconds=.5*remaining();out.sparse_called=true;
    auto sparse=solve_sparse_lp(fixed,options);out.sparse_iterations=sparse.solution.iterations;out.refinement=sparse.refinement;
    out.status="sparse_"+sparse.solution.status;
    if(sparse.solution.status=="optimal"&&sparse.solution.optimality_verified&&usable(sparse.solution.primal))return out;
    if(remaining()<=0)return out;
    try {
        auto standard=standardize(fixed,options.max_tableau_cells);
        options.time_limit_seconds=remaining();if(options.time_limit_seconds<=0)return out;
        out.dense_called=true;auto dense=solve(standard.model,options);out.dense_iterations=dense.iterations;
        out.status="dense_"+dense.status;
        if(dense.status=="optimal"&&dense.optimality_verified)usable(standard.recover(dense.primal));
    }catch(const std::runtime_error&){out.status="dense_resource_or_numerical_error";}
    return out;
}
}}
