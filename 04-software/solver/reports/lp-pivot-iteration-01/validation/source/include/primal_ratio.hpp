#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

namespace sovereign { namespace detail {
// Refine an existing minimum-ratio choice only when its pivot is weak.
// The two-pass step allowance uses the caller's existing feasibility tolerance;
// all final original-model acceptance checks remain the caller's responsibility.
// Inputs have the current basis dimension and a positive finite tolerance.
inline std::size_t stable_primal_leaving(const std::vector<double>& x,
                                        const std::vector<double>& direction,
                                        const std::vector<std::size_t>& basis,
                                        std::size_t leaving,double tolerance,bool bland) {
    if(bland||leaving>=x.size())return leaving;
    double norm=0;
    for(double value:direction) {
        if(!std::isfinite(value))return leaving;
        norm=std::max(norm,std::abs(value));
    }
    if(direction[leaving]>1e-7*(1+norm))return leaving;
    double expanded=std::numeric_limits<double>::infinity();
    for(std::size_t i=0;i<x.size();++i)if(direction[i]>tolerance)
        expanded=std::min(expanded,(std::max(0.0,x[i])+tolerance)/direction[i]);
    for(std::size_t i=0;i<x.size();++i)if(direction[i]>tolerance&&std::max(0.0,x[i])/direction[i]<=expanded)
        if(direction[i]>direction[leaving]||(direction[i]==direction[leaving]&&basis[i]<basis[leaving]))leaving=i;
    return leaving;
}
}}
