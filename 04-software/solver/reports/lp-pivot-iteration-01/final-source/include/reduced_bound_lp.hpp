#pragma once
#include "sparse_lp.hpp"
#include <chrono>

namespace sovereign { namespace detail {
// A relaxation-and-check procedure, not an unchecked redundancy claim.
// Original finite upper bounds and every integer bound remain in the LP.
inline SparseLpResult solve_reduced_bound_lp(const LinearProblem& full,
        const LinearProblem& original, const Options& options, const LpBasis* warm=nullptr) {
    validate_linear_problem(full);validate_linear_problem(original);
    if(full.cost.size()!=original.cost.size())throw std::invalid_argument("Reduced-bound domain dimension mismatch");
    auto started=std::chrono::steady_clock::now();
    LinearProblem relaxed=full;std::size_t omitted=0;
    for(std::size_t j=0;j<full.cost.size();++j)
        if(!original.integer[j]&&original.upper[j]==std::numeric_limits<double>::infinity()&&std::isfinite(full.upper[j])) {
            relaxed.upper[j]=std::numeric_limits<double>::infinity();++omitted;
        }
    if(!omitted)return solve_sparse_lp(full,options,warm&&warm->reduced_upper_bounds?nullptr:warm);
    auto result=solve_sparse_lp(relaxed,options,warm&&warm->reduced_upper_bounds?warm:nullptr);
    result.reduced_upper_candidates=omitted;
    if(result.solution.status=="optimal"&&result.solution.optimality_verified) {
        double absolute=original_violation(full,result.solution.primal,false);
        double scaled=original_violation(full,result.solution.primal,true);
        if(absolute<=1e-7&&scaled<=10*options.tolerance) {
            // The relaxed dual extends with zero multipliers on omitted bounds.
            // The FULL-node primal check completes the numerical certificate.
            result.solution.max_violation=absolute;result.solution.scaled_primal_violation=scaled;
            result.reduced_upper_accepted=true;result.basis.reduced_upper_bounds=true;return result;
        }
    } else if(result.solution.status=="infeasible"&&result.solution.infeasibility_verified) {
        // Empty relaxation implies empty full node. Never use the converse.
        result.reduced_upper_accepted=true;return result;
    }
    double left=options.time_limit_seconds-std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
    if(left>0) {
        Options fallback=options;fallback.time_limit_seconds=left;
        auto restored=solve_sparse_lp(full,fallback);
        restored.solution.iterations+=result.solution.iterations;
        restored.refinement.add(result.refinement);
        restored.reduced_upper_candidates=omitted;restored.reduced_upper_fallback=true;return restored;
    }
    // An unbounded RELAXATION is not a ray for the full node.
    result.solution.status="time_limit";result.solution.optimality_verified=false;
    result.solution.infeasibility_verified=false;result.solution.unboundedness_verified=false;
    result.solution.primal.clear();result.solution.unbounded_ray.clear();result.basis={};
    result.best_bound=-std::numeric_limits<double>::infinity();return result;
}
}}
