#pragma once
#include <array>
#include <chrono>
#include <cstddef>
#include "basis_refinement.hpp"

namespace sovereign { namespace detail {
enum class MilpPhase { other,root_lp,cut_lp,tree_lp,pump,pump_fix,pump_projection,
    dive,neighborhood,repair,branch_probe,lp_recovery,presolve,cut_separation,
    validation,restart,binary,count };
inline const char* phase_name(std::size_t i){
    static const char* names[]={"other","root_lp","cut_lp","tree_lp","pump","pump_fix","pump_projection",
        "dive","neighborhood","repair","branch_probe","lp_recovery","presolve","cut_separation","validation","restart","binary"};
    return names[i];
}
struct MilpPhaseWork { double seconds=0;std::size_t lp_calls=0,iterations=0;BasisRefinementStats refinement; };
struct MilpWork {
    std::array<MilpPhaseWork,static_cast<std::size_t>(MilpPhase::count)> phases;
    double seconds=0;
    BasisRefinementStats refinement;
};
// Exclusive wall-time attribution: entering a child pauses the parent's clock.
// Counters describe reported iterations of MILP-visible LP calls, not FLOPs.
class MilpWorkLedger {
    using Clock=std::chrono::steady_clock;
    MilpWork& work_;bool enabled_,finished_=false;
    MilpPhase active_=MilpPhase::other;Clock::time_point last_;
    void charge(){
        if(!enabled_||finished_)return;
        auto now=Clock::now();double dt=std::chrono::duration<double>(now-last_).count();last_=now;
        work_.phases[static_cast<std::size_t>(active_)].seconds+=dt;work_.seconds+=dt;
    }
public:
    MilpWorkLedger(MilpWork& w,bool enabled):work_(w),enabled_(enabled),last_(enabled?Clock::now():Clock::time_point{}){}
    MilpPhase enter(MilpPhase phase){auto previous=active_;charge();active_=phase;return previous;}
    void lp(std::size_t iterations,const BasisRefinementStats* refinement=nullptr){if(enabled_){auto& p=work_.phases[static_cast<std::size_t>(active_)];++p.lp_calls;p.iterations+=iterations;if(refinement){p.refinement.add(*refinement);work_.refinement.add(*refinement);}}}
    void finish(){charge();finished_=true;}
};
class MilpWorkScope {
    MilpWorkLedger& ledger_;MilpPhase previous_;
public:
    MilpWorkScope(MilpWorkLedger& ledger,MilpPhase phase):ledger_(ledger),previous_(ledger.enter(phase)){}
    ~MilpWorkScope(){ledger_.enter(previous_);}
    MilpWorkScope(const MilpWorkScope&)=delete;MilpWorkScope& operator=(const MilpWorkScope&)=delete;
};
}}
