#pragma once
#include "sparse_lu.hpp"
#include <limits>
#include <chrono>

namespace sovereign {
struct BasisRefinementStats {
    std::size_t attempts=0,accepted=0,rhs_calls=0,primal_rhs=0,dual_rhs=0,scans=0,entries=0;
    double seconds=0;
    void add(const BasisRefinementStats& s) {
        attempts+=s.attempts;accepted+=s.accepted;rhs_calls+=s.rhs_calls;
        primal_rhs+=s.primal_rhs;dual_rhs+=s.dual_rhs;scans+=s.scans;entries+=s.entries;seconds+=s.seconds;
    }
};
// Optional telemetry, with no changes to arithmetic or acceptance decisions.
struct BasisRefinementClock {
    using Clock=std::chrono::steady_clock;
    BasisRefinementStats* stats;Clock::time_point start;
    BasisRefinementClock(BasisRefinementStats* s,bool capture,bool transpose):stats(capture?s:nullptr),start(stats?Clock::now():Clock::time_point{}) {
        if(stats){++stats->rhs_calls;if(transpose)++stats->dual_rhs;else ++stats->primal_rhs;}
    }
    ~BasisRefinementClock(){if(stats)stats->seconds+=std::chrono::duration<double>(Clock::now()-start).count();}
};
struct BasisRefinementScan {
    BasisRefinementStats* stats;std::size_t& visited;
    BasisRefinementScan(BasisRefinementStats* s,std::size_t& n):stats(s),visited(n){if(stats)++stats->scans;}
    ~BasisRefinementScan(){if(stats)stats->entries+=visited;}
};

// Correct a basis RHS using the current LU + eta solve, not a new pivot or
// factorization. Residuals use the actual current basis (not its factors).
// The RHS-relative infinity norm avoids hiding errors in small equations
// behind an unrelated large-bound slack. It is NOT a feasibility tolerance.
template<class Solve,class Cancelled>
void refine_basis_values(const std::vector<SparseVector>& columns,
                         const std::vector<std::size_t>& basis,
                         const std::vector<double>& rhs,std::vector<double>& x,
                         bool transpose,const Solve& solve,const Cancelled& cancelled,
                         BasisRefinementStats* stats=nullptr,bool capture=false) {
    const std::size_t n=basis.size();
    if(rhs.size()!=n||x.size()!=n)throw std::invalid_argument("Basis refinement dimension");
    BasisRefinementClock trace(stats,capture,transpose);
    auto residual=[&](const std::vector<double>& point,std::vector<double>& r)->double {
        std::vector<long double> wide(rhs.begin(),rhs.end());
        std::size_t work=0;
        BasisRefinementScan scan(trace.stats,work);
        for(std::size_t j=0;j<n;++j) {
            if((j%256==0&&cancelled())||!std::isfinite(point[j]))return INFINITY;
            for(auto a:columns[basis[j]]) {
                if(++work%4096==0&&cancelled())return INFINITY;
                if(transpose)wide[j]-=static_cast<long double>(a.second)*point[a.first];
                else wide[a.first]-=static_cast<long double>(a.second)*point[j];
            }
        }
        double error=0;r.resize(n);
        for(std::size_t i=0;i<n;++i) {
            r[i]=static_cast<double>(wide[i]);
            if(!std::isfinite(r[i])||!std::isfinite(rhs[i]))return INFINITY;
            error=std::max(error,static_cast<double>(std::abs(wide[i])/(1+std::abs(static_cast<long double>(rhs[i])))));
        }
        return error;
    };
    std::vector<double> r;double error=residual(x,r);
    // A small fixed arithmetic-work cap, within the existing LP wall budget.
    // Never accept a nonfinite or non-improving correction. The usual full
    // primal/dual certificate is still required by the caller.
    for(unsigned k=0;k<2&&std::isfinite(error)&&error>64*std::numeric_limits<double>::epsilon();++k) {
        if(cancelled())return;
        if(stats)++stats->attempts;
        auto correction=solve(r);
        if(correction.size()!=n)return;
        std::vector<double> trial(n),next;
        for(std::size_t i=0;i<n;++i)trial[i]=static_cast<double>(static_cast<long double>(x[i])+correction[i]);
        const double improved=residual(trial,next);
        if(cancelled()||!std::isfinite(improved)||improved>=error)return;
        x.swap(trial);r.swap(next);error=improved;
        if(stats)++stats->accepted;
    }
}
}
