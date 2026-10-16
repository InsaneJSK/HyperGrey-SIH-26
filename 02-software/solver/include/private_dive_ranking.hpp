#pragma once
#include <cmath>
#include <cstddef>
#include <stdexcept>
#include <vector>

namespace sovereign { namespace detail {
// Ranking only: never use this slack to accept a point or certify a bound.
// Anchor the tie set to the true maximum, avoiding order-dependent chains.
// Ties use original column order; permutations may change the tied winner.
struct PrivateDiveChoice {
    std::size_t column, strict_column, ties;
};
inline PrivateDiveChoice private_dive_choice(const std::vector<bool>& integer,
                                            const std::vector<double>& x,
                                            double integer_tolerance) {
    if(integer.size()!=x.size()||!std::isfinite(integer_tolerance)||integer_tolerance<=0)
        throw std::invalid_argument("Invalid private dive ranking input");
    PrivateDiveChoice result={x.size(),x.size(),0};
    double maximum=integer_tolerance;
    for(std::size_t j=0;j<x.size();++j){
        if(!std::isfinite(x[j]))throw std::invalid_argument("Nonfinite private dive point");
        const double score=std::abs(x[j]-std::round(x[j]));
        if(integer[j]&&score>maximum){maximum=score;result.strict_column=j;}
    }
    if(result.strict_column==x.size())return result;
    for(std::size_t j=0;j<x.size();++j){
        const double score=std::abs(x[j]-std::round(x[j]));
        if(integer[j]&&score>integer_tolerance&&maximum-score<=1e-12){
            if(result.column==x.size())result.column=j;
            ++result.ties;
        }
    }
    return result;
}
}}
