#pragma once
#include "sparse_lp.hpp"
namespace sovereign { namespace detail {
struct DistanceStageSample {
    std::size_t node=0,iterations=0;
    bool eligible=false,attempted=false,verified=false,accepted=false;
    double available_seconds=0,seconds=0;
    std::string status="ineligible";
};
struct DistanceStageStats {
    std::size_t considered=0,eligible=0,attempts=0,verified=0,incumbents=0;
    std::size_t child_offers=0,child_compatible=0,child_verified=0;
    LpReoptStats reopt;
    std::vector<DistanceStageSample> samples;
};
}}
