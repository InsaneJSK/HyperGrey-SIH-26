#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>

namespace sovereign { namespace detail {
// Allocation heuristic ONLY. Its decision never publishes a proof bound.
inline const char* cut_continuation(std::size_t round,std::size_t root_iterations,
                                    std::size_t iterations,double before,double after,double offset){
    if(!std::isfinite(before)||!std::isfinite(after)||!std::isfinite(offset))return "invalid_metric";
    if(round<2)return "minimum_rounds";
    if(iterations<256)return "cheap_round";
    if(root_iterations==0)return "missing_root_work";
    const double scale=std::max({1.,std::abs(before-offset),std::abs(after-offset)});
    const double delta=after-before;
    const double gain=std::max(0.,delta)/scale;
    const double effort=std::max(1.,static_cast<double>(iterations)/static_cast<double>(root_iterations));
    const double threshold=.001*effort;
    if(!std::isfinite(delta)||!std::isfinite(scale)||!std::isfinite(gain)||!std::isfinite(effort)||!std::isfinite(threshold))return "invalid_metric";
    return gain<=threshold?"diminishing_return":"productive_round";
}
inline const char* guarded_cut_continuation(bool enabled,bool require_incumbent,bool has_incumbent,
    std::size_t round,std::size_t cap,std::size_t root_iterations,std::size_t iterations,
    double before,double after,double offset){
    if(!enabled)return "disabled";
    if(round>=cap)return "round_cap";
    if(require_incumbent&&!has_incumbent)return "no_incumbent";
    return cut_continuation(round,root_iterations,iterations,before,after,offset);
}
struct CutRound {
    std::size_t node,restart,round,root_iterations,iterations;
    double before,after,offset;
    const char* decision;
    double incumbent_objective; // Original objective sense; NaN means absent.
};
}}
