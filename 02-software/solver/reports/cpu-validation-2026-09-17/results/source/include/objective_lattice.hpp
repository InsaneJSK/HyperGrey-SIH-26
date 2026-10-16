#pragma once
#include "mps.hpp"
#include <cmath>
#include <cstdint>
#include <map>

namespace sovereign { namespace detail {
struct ObjectiveLattice {
    bool eligible=false;
    std::string reason="disabled";
    double offset=0,step=0; // All data and bounds in minimization sense.
    std::vector<std::int64_t> coefficients;
    std::vector<std::pair<std::size_t,std::size_t> > substitutions; // column,row
};
namespace lattice_integer {
typedef std::int64_t Int;
const Int CAP=Int(1)<<40,OFFSET_CAP=Int(1)<<50,SCALE=Int(1)<<16;
struct Rejected {const char* reason;};
inline Int absolute(Int a){return a<0?-a:a;}
inline Int integral(double x,Int cap=CAP){
    if(!std::isfinite(x)||std::abs(x)>double(cap)||std::trunc(x)!=x)
        throw Rejected{"nonintegral_or_out_of_range"};
    return static_cast<Int>(x);
}
inline Int add(Int a,Int b,Int cap=CAP){
    if(absolute(a)>cap||absolute(b)>cap||(b>0&&a>cap-b)||(b<0&&a< -cap-b))
        throw Rejected{"arithmetic_range"};
    return a+b;
}
inline Int mul(Int a,Int b,Int cap=CAP){
    if(absolute(a)>cap||absolute(b)>cap||(b&&absolute(a)>cap/absolute(b)))
        throw Rejected{"arithmetic_range"};
    return a*b;
}
inline Int gcd(Int a,Int b){a=absolute(a);b=absolute(b);while(b){Int r=a%b;a=b;b=r;}return a;}
}

// Exact algebra for the PARSED binary64 model, not a source-decimal or LP
// certificate. Fixed continuous variables and fractional objective coefficients
// deliberately have no special treatment. Eligibility must come from original
// global equations, never a heuristic fixing or a node-local restriction.
inline ObjectiveLattice detect_objective_lattice(const LinearProblem& p){
    using namespace lattice_integer;
    ObjectiveLattice out;
    try {
        validate_linear_problem(p);
        const std::size_t n=p.cost.size();const Int sign=p.maximize?-1:1;
        Int shifted=integral(sign*p.offset*double(SCALE),OFFSET_CAP);
        std::vector<Int> cost(n),effective(n,0);
        for(std::size_t j=0;j<n;++j){cost[j]=mul(sign,integral(p.cost[j]));if(p.integer[j])effective[j]=cost[j];}
        struct Definition {std::size_t row;Int rhs,unit;std::map<std::size_t,Int> terms;};
        std::map<std::size_t,Definition> definitions;
        for(std::size_t i=0;i<p.rows.size();++i){
            if(!std::isfinite(p.row_lower[i])||p.row_lower[i]!=p.row_upper[i])continue;
            // A rejected row does not invalidate a different valid definition.
            try {
                Int rhs=integral(p.row_lower[i]);std::map<std::size_t,Int> terms;
                for(auto e:p.rows[i])terms[e.first]=add(terms[e.first],integral(e.second));
                std::size_t continuous=n;bool multiple=false;
                for(auto e:terms)if(e.second&&!p.integer[e.first]){
                    if(continuous!=n){multiple=true;break;}continuous=e.first;
                }
                if(multiple||continuous==n||!cost[continuous]||absolute(terms[continuous])!=1||definitions.count(continuous))continue;
                Definition d;d.row=i;d.rhs=rhs;d.unit=terms[continuous];d.terms=std::move(terms);
                definitions.emplace(continuous,std::move(d));
            }catch(const Rejected&){}
        }
        for(std::size_t j=0;j<n;++j)if(!p.integer[j]&&cost[j]){
            auto it=definitions.find(j);if(it==definitions.end())throw Rejected{"continuous_objective_without_unit_definition"};
            const auto& d=it->second;Int factor=mul(cost[j],d.unit);
            shifted=add(shifted,mul(mul(factor,d.rhs),SCALE,OFFSET_CAP),OFFSET_CAP);
            for(auto e:d.terms)if(e.first!=j&&e.second)
                effective[e.first]=add(effective[e.first],-mul(factor,e.second));
            out.substitutions.push_back({j,d.row});
        }
        Int step=0;for(Int c:effective)step=gcd(step,c);
        if(!step)throw Rejected{"constant_objective"};
        out.offset=double(shifted)/double(SCALE);out.step=double(step);
        out.coefficients=std::move(effective);out.eligible=true;out.reason="checked_parsed_model_lattice";
    }catch(const lattice_integer::Rejected& e){out=ObjectiveLattice();out.reason=e.reason;}
    return out;
}

// Caller must supply a validated numerical lower bound (already outward safety
// adjusted). Subtracting a further margin before ceil prevents an arithmetic
// error at a grid point from skipping that point. Publish one double ULP down.
// Large/nonfinite data and unsupported lattices fall back to the old bound.
inline double round_objective_bound(const ObjectiveLattice& lattice,double bound){
    const double cap=double(lattice_integer::CAP);
    if(!lattice.eligible||!std::isfinite(bound)||std::abs(bound)>cap||
       !std::isfinite(lattice.offset)||std::abs(lattice.offset)>cap||
       !std::isfinite(lattice.step)||lattice.step<1||lattice.step>cap)return bound;
    const long double b=bound,o=lattice.offset,s=lattice.step;
    const long double margin=64*std::numeric_limits<double>::epsilon()*(1+std::abs(b)+std::abs(o)+s);
    const long double q=std::ceil((b-o-margin)/s);
    const long double candidate=o+s*q;
    if(!std::isfinite(candidate)||std::abs(candidate)>cap)return bound;
    const double outward=std::nextafter(static_cast<double>(candidate),-std::numeric_limits<double>::infinity());
    return std::max(bound,outward);
}
}}
