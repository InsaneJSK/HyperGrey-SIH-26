#pragma once
#include "mps.hpp"
#include "sparse_lu.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <set>

namespace sovereign { namespace detail {
struct VerifiedCover {
    std::size_t source_row=0;
    int side=0;
    SparseVector row;
    double rhs=0,violation=0;
    std::size_t assignments=0;
};
struct CoverSeparation {
    std::vector<VerifiedCover> cuts;
    std::size_t eligible_rows=0,states=0,checked=0;
    double seconds=0;
    bool interrupted=false;
};
namespace lifted_cover_detail {
// Represent the supplied binary64 values exactly, without decimal rounding.
// Reject a row when its common dyadic scale or absolute-sum envelope is too big.
inline bool integers(const std::vector<double>& values,std::vector<std::int64_t>& out) {
    const std::int64_t limit=std::int64_t(1)<<60;
    std::vector<std::int64_t> mantissa;std::vector<int> powers;int least=2000;
    for(double value:values) {
        if(!std::isfinite(value))return false;
        int exponent=0;double fraction=std::frexp(value,&exponent);
        auto m=static_cast<std::int64_t>(std::ldexp(fraction,53));int power=exponent-53;
        if(m){while(m%2==0){m/=2;++power;}least=std::min(least,power);}
        mantissa.push_back(m);powers.push_back(power);
    }
    std::int64_t envelope=0;out.clear();
    for(std::size_t i=0;i<values.size();++i) {
        auto m=mantissa[i];int shift=powers[i]-least;
        if(m){if(shift<0||shift>60||std::abs(m)>(limit>>shift))return false;m*=std::int64_t(1)<<shift;}
        if(std::abs(m)>limit-envelope)return false;
        envelope+=std::abs(m);out.push_back(m);
    }
    return true;
}
inline unsigned bit_index(std::uint32_t bit){unsigned k=0;while((bit>>k)!=1)++k;return k;}
inline unsigned popcount(std::uint32_t mask){unsigned n=0;for(;mask;mask&=mask-1)++n;return n;}
}

// Full feasible-assignment checks make every exported cut valid for the source
// row over its entire binary cube, not merely the current LP point or node.
inline CoverSeparation separate_lifted_covers(const LinearProblem& p,const std::vector<double>& x,
                                             std::size_t original_rows,double budget) {
    CoverSeparation out;auto start=std::chrono::steady_clock::now();
    auto elapsed=[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();};
    auto stop=[&](){if(elapsed()>=budget){out.interrupted=true;return true;}return false;};
    if(!(budget>0)||!std::isfinite(budget)||x.size()!=p.cost.size())return out;
    for(double v:x)if(!std::isfinite(v))return out;
    for(std::size_t r=0;r<std::min(original_rows,p.rows.size())&&out.cuts.size()<16&&!stop();++r) {
        const auto& source=p.rows[r];const std::size_t n=source.size();
        if(n<2||n>20)continue;
        bool eligible=true;std::set<std::size_t> seen;
        for(auto a:source)if(a.first>=x.size()||!p.integer[a.first]||p.lower[a.first]<0||p.upper[a.first]>1||
            !std::isfinite(a.second)||a.second==0||!seen.insert(a.first).second)eligible=false;
        if(!eligible)continue;
        for(int side=0;side<2&&out.cuts.size()<16&&!stop();++side) {
            double bound=side?-p.row_lower[r]:p.row_upper[r];if(!std::isfinite(bound))continue;
            std::vector<double> raw{bound},z;std::vector<bool> complement;
            for(auto a:source){double v=side?-a.second:a.second;raw.push_back(v);complement.push_back(v<0);z.push_back(v<0?1-x[a.first]:x[a.first]);}
            std::vector<std::int64_t> exact;if(!lifted_cover_detail::integers(raw,exact))continue;
            auto capacity=exact[0];std::vector<std::int64_t> w;
            for(std::size_t j=0;j<n;++j){if(exact[j+1]<0)capacity-=exact[j+1];w.push_back(std::abs(exact[j+1]));}
            if(capacity<0)continue; // General solver handles infeasibility; no cut-based shortcut.
            ++out.eligible_rows;const std::uint32_t count=std::uint32_t(1)<<n;
            std::vector<std::int64_t> weight(count,0);std::vector<double> loss(count,0);
            std::vector<std::uint32_t> feasible;feasible.reserve(count);feasible.push_back(0);
            std::vector<std::pair<double,std::uint32_t>> covers;
            bool interrupted=false;
            for(std::uint32_t mask=1;mask<count;++mask) {
                if((mask&4095)==0&&stop()){interrupted=true;break;}
                auto bit=mask&(~mask+1);auto j=lifted_cover_detail::bit_index(bit);auto previous=mask^bit;
                weight[mask]=weight[previous]+w[j];loss[mask]=loss[previous]+1-z[j];++out.states;
                if(weight[mask]<=capacity)feasible.push_back(mask);
                else {
                    bool minimal=true;
                    for(std::size_t k=0;k<n;++k)if((mask&(1u<<k))&&weight[mask]-w[k]>capacity){minimal=false;break;}
                    if(minimal)covers.push_back({1-loss[mask],mask});
                }
            }
            if(interrupted)break;
            std::sort(covers.rbegin(),covers.rend());
            std::vector<VerifiedCover> candidates;
            for(std::size_t k=0;k<std::min<std::size_t>(8,covers.size())&&!stop();++k) {
                auto cover=covers[k].second;int rhs=static_cast<int>(lifted_cover_detail::popcount(cover))-1;
                std::vector<int> coefficient(n,0),activity;activity.reserve(feasible.size());
                std::vector<std::pair<double,std::size_t>> order;
                for(std::size_t j=0;j<n;++j){if(cover&(1u<<j))coefficient[j]=1;else order.push_back({z[j],j});}
                for(auto mask:feasible)activity.push_back(lifted_cover_detail::popcount(mask&cover));
                std::sort(order.rbegin(),order.rend());
                for(auto item:order) {
                    if(stop()){interrupted=true;break;}
                    auto bit=1u<<item.second;int maximum=-1;
                    for(std::size_t t=0;t<feasible.size();++t)if(feasible[t]&bit)maximum=std::max(maximum,activity[t]);
                    if(maximum<0)continue;
                    int alpha=rhs-maximum;if(alpha<0){interrupted=true;break;}
                    coefficient[item.second]=alpha;
                    for(std::size_t t=0;t<feasible.size();++t)if(feasible[t]&bit)activity[t]+=alpha;
                }
                if(interrupted)break;
                // Recompute all activities from scratch after lifting, not from
                // its incremental scores. No partially checked cut is exported.
                bool valid=true;
                for(std::size_t t=0;t<feasible.size();++t){
                    if((t&4095)==0&&stop()){interrupted=true;break;}
                    int value=0;for(std::size_t j=0;j<n;++j)if(feasible[t]&(1u<<j))value+=coefficient[j];
                    if(value>rhs){valid=false;break;}
                }
                if(interrupted)break;
                if(!valid)continue;
                ++out.checked;VerifiedCover cut;cut.source_row=r;cut.side=side;cut.rhs=rhs;cut.assignments=feasible.size();
                double norm=0;
                for(std::size_t j=0;j<n;++j)if(coefficient[j]){
                    cut.row.push_back({source[j].first,complement[j]?-coefficient[j]:coefficient[j]});
                    if(complement[j])cut.rhs-=coefficient[j];norm+=coefficient[j];
                }
                std::sort(cut.row.begin(),cut.row.end());cut.violation=-cut.rhs;
                for(auto a:cut.row)cut.violation+=a.second*x[a.first];
                if(cut.violation<=1e-7*(1+norm))continue;
                bool duplicate=false;
                for(std::size_t i=0;i<p.rows.size();++i)if(p.rows[i]==cut.row&&p.row_upper[i]==cut.rhs)duplicate=true;
                for(const auto& other:candidates)if(other.row==cut.row&&other.rhs==cut.rhs)duplicate=true;
                if(!duplicate)candidates.push_back(cut);
            }
            std::sort(candidates.begin(),candidates.end(),[](const VerifiedCover& a,const VerifiedCover& b){return a.violation>b.violation;});
            for(std::size_t k=0;k<std::min<std::size_t>(2,candidates.size())&&out.cuts.size()<16;++k)out.cuts.push_back(candidates[k]);
        }
    }
    out.seconds=elapsed();return out;
}
}}
