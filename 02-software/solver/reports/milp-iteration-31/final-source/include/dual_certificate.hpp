#pragma once
#include "mps.hpp"
#include "sparse_matrix.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <cstdint>
#include <cfenv>

namespace sovereign { namespace detail {
// Deliberately narrow certificate domain. Coefficients and multipliers must
// admit exact bounded integer arithmetic; uncertainty rejects the shortcut.
// This is independent of pivot tolerances and does not relax feasibility.
namespace dual_certificate {
const std::int64_t operand_limit=std::int64_t(1)<<26;
const std::int64_t sum_limit=std::int64_t(1)<<52;
inline bool integer(double x,std::int64_t& value) {
    if(!std::isfinite(x)||std::abs(x)>operand_limit||std::trunc(x)!=x)return false;
    value=static_cast<std::int64_t>(x);return true;
}
inline bool accumulate(std::int64_t& sum,std::int64_t a,std::int64_t b) {
    const auto term=a*b; // each operand is at most 2^26
    if((term>0&&sum>sum_limit-term)||(term<0&&sum<-sum_limit-term))return false;
    sum+=term;return true;
}
struct Interval {
    double lo,hi;
    explicit Interval(double x=0):lo(x),hi(x){}
    Interval(double l,double h):lo(l),hi(h){}
    bool finite()const{return std::isfinite(lo)&&std::isfinite(hi)&&lo<=hi;}
};
inline double down(double x){return std::nextafter(x,-INFINITY);}
inline double up(double x){return std::nextafter(x,INFINITY);}
inline Interval add(Interval a,Interval b) {
    if(a.lo==0&&a.hi==0)return b;
    if(b.lo==0&&b.hi==0)return a;
    return Interval(down(a.lo+b.lo),up(a.hi+b.hi));
}
inline Interval product(double a,double b) {
    if(a==0||b==0)return Interval();
    if(a==1)return Interval(b);
    if(b==1)return Interval(a);
    if(a==-1)return Interval(-b);
    if(b==-1)return Interval(-a);
    return Interval(down(a*b),up(a*b));
}
inline Interval negative(Interval a){return Interval(-a.hi,-a.lo);}
inline bool contradiction(Interval rhs,Interval minimum,Interval magnitude,double tolerance) {
    const auto gap=add(minimum,negative(rhs));
    magnitude=add(magnitude,Interval(std::max(std::abs(minimum.lo),std::abs(minimum.hi))));
    const auto factor=product(10.,tolerance), threshold=product(factor.hi,magnitude.hi);
    return rhs.finite()&&minimum.finite()&&magnitude.finite()&&gap.finite()&&threshold.finite()&&gap.lo>threshold.hi;
}
}

template<class Expired>
bool verify_dual_row(const LinearProblem& p,const std::vector<SparseVector>& columns,
    const std::vector<double>& rhs,const std::vector<bool>& equality,std::size_t structural,
    const std::vector<std::pair<std::size_t,double> >& origin,const std::vector<double>& scale,
    const std::vector<double>& row,double tolerance,Expired expired) {
    using namespace dual_certificate;
    // Outward enclosures assume IEEE binary64 with gradual underflow and
    // normal rounding; builds must not use fast-math / flush-to-zero.
    if(!std::numeric_limits<double>::is_iec559||std::fegetround()!=FE_TONEAREST||
       !std::isfinite(tolerance)||tolerance<=0||expired())return false;
    volatile double smallest_normal=std::numeric_limits<double>::min();
    if(smallest_normal*.5!=std::numeric_limits<double>::min()/2)return false;
    const auto m=rhs.size(),n=p.cost.size();
    if(row.size()!=m||equality.size()!=m||origin.size()!=m||scale.size()!=m||columns.size()<structural+m)return false;
    std::vector<std::int64_t> y(m),raw(m);
    Interval b,mag(1);
    for(std::size_t i=0;i<m;++i) {
        if((i%256==0&&expired())||!integer(row[i],y[i])||(!equality[i]&&y[i]<0)||!std::isfinite(rhs[i]))return false;
        std::int64_t divisor=1;
        if(y[i]&&(!integer(scale[i],divisor)||divisor<=0||y[i]%divisor))return false;
        raw[i]=y[i]?y[i]/divisor:0;
        const auto term=product(static_cast<double>(y[i]),rhs[i]);
        b=add(b,term);mag=add(mag,Interval(std::max(std::abs(term.lo),std::abs(term.hi))));
    }
    for(std::size_t j=0;j<structural+m;++j) {
        if(j%256==0&&expired())return false;
        if(j>=structural&&equality[j-structural])continue; // artificial equality slack
        std::int64_t dot=0;
        std::size_t work=0;
        for(auto a:columns[j]) {
            if(++work%256==0&&expired())return false;
            if(a.first>=m||!std::isfinite(a.second))return false;
            if(!y[a.first])continue;
            std::int64_t coefficient;
            if(!integer(a.second,coefficient)||!accumulate(dot,coefficient,y[a.first]))return false;
        }
        if(dot<0)return false; // check basic, nonbasic and true slack columns
    }
    if(!contradiction(b,Interval(),mag,tolerance))return false;
    // Reconstruct the same row combination using ORIGINAL coefficients and
    // domains. This guards against canonical scaling/shift rounding errors.
    std::vector<std::int64_t> g(n,0);std::size_t bounded=0;
    b=Interval();mag=Interval(1);
    for(std::size_t i=0;i<m;++i) {
        if(i%256==0&&expired())return false;
        const auto index=origin[i].first;const double direction=origin[i].second;
        if(index>p.rows.size()||(direction!=1&&direction!=-1))return false;
        double bound;
        if(index==p.rows.size()) {
            while(bounded<n&&(!std::isfinite(p.lower[bounded])||!std::isfinite(p.upper[bounded])))++bounded;
            if(bounded==n||direction!=1)return false;
            if(!accumulate(g[bounded],raw[i],1))return false;
            bound=p.upper[bounded++];
        } else {
            if(!raw[i])continue;
            const auto multiplier=raw[i]*static_cast<std::int64_t>(direction);
            std::size_t work=0;
            for(auto a:p.rows[index]) {
                if(++work%256==0&&expired())return false;
                std::int64_t coefficient;
                if(a.first>=n||!integer(a.second,coefficient)||!accumulate(g[a.first],coefficient,multiplier))return false;
            }
            bound=direction>0?p.row_upper[index]:-p.row_lower[index];
        }
        if(!std::isfinite(bound))return false;
        const auto term=product(static_cast<double>(raw[i]),bound);
        b=add(b,term);mag=add(mag,Interval(std::max(std::abs(term.lo),std::abs(term.hi))));
    }
    Interval minimum;
    for(std::size_t j=0;j<n;++j) {
        if(j%256==0&&expired())return false;
        if(!g[j])continue;
        const double bound=g[j]>0?p.lower[j]:p.upper[j];
        if(!std::isfinite(bound))return false;
        minimum=add(minimum,product(static_cast<double>(g[j]),bound));
    }
    return !expired()&&contradiction(b,minimum,mag,tolerance);
}
}}
