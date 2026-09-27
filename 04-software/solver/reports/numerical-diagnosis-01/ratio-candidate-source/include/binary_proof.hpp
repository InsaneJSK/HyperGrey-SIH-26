#pragma once
#include "mps.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>

namespace sovereign {
struct BinaryProofResult {
    bool eligible=false,completed=false,verified=false,feasible=false;
    std::string status="not_run",reason;
    std::size_t left_states=0,right_states=0,query_nodes=0,work=0;
    double seconds=0;
    std::int64_t objective_minimization=0;
    std::vector<std::int64_t> primal;
    std::vector<std::size_t> binary_indices;
};
namespace detail { namespace exact_binary {
typedef std::int64_t Int;
const Int CAP=Int(1)<<50,INF=Int(1)<<60;
struct Rejected {const char* reason;};
struct InternalFailure {};
inline Int absolute(Int x){return x<0?-x:x;}
inline Int integral(double x){
    if(!std::isfinite(x)||std::abs(x)>static_cast<double>(CAP)||std::trunc(x)!=x)throw Rejected{"nonintegral_or_out_of_range"};
    return static_cast<Int>(x);
}
inline Int bound(double x){return std::isinf(x)?(x<0?-INF:INF):integral(x);}
inline Int add(Int a,Int b){
    if(absolute(a)>CAP||absolute(b)>CAP||(b>0&&a>CAP-b)||(b<0&&a< -CAP-b))throw Rejected{"arithmetic_range"};
    return a+b;
}
inline Int mul(Int a,Int b){
    if(absolute(a)>CAP||absolute(b)>CAP||(b&&absolute(a)>CAP/absolute(b)))throw Rejected{"arithmetic_range"};
    return a*b;
}
inline Int subtract_bound(Int a,Int b){return absolute(a)==INF?a:add(a,-b);}
}

// Exact for this strict integer subset of the PARSED model. No floating-point
// incumbent, tolerance comparison or LP bound enters this independent search.
inline BinaryProofResult binary_proof(const LinearProblem& p,double budget,std::size_t max_work=50000000) {
    using namespace exact_binary;
    BinaryProofResult out;const auto start=std::chrono::steady_clock::now();
    auto elapsed=[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();};
    auto finish=[&](){out.seconds=elapsed();return out;};
    if(!std::isfinite(budget)||budget<=0){out.status="time_limit";return finish();}
    if(!max_work){out.status="work_limit";return finish();}
    try {
        validate_linear_problem(p);
        if(!p.integer_input_literals)throw Rejected{"nonintegral_or_unsafe_literal_input"};
        const std::size_t n=p.cost.size(),m=p.rows.size();
        if(n>128||m>32||!m)throw Rejected{"size_limit"};
        typedef std::array<Int,32> Coordinates;
        std::vector<Int> base(n,0),original_cost(n),lower(n),upper(n);
        std::vector<std::size_t> binaries;std::vector<bool> moving(n,false);
        const Int sign=p.maximize?-1:1;Int original_offset=integral(p.offset),offset=mul(sign,original_offset);
        for(std::size_t j=0;j<n;++j) {
            original_cost[j]=integral(p.cost[j]);lower[j]=bound(p.lower[j]);upper[j]=bound(p.upper[j]);
            if(lower[j]>upper[j])throw Rejected{"inconsistent_domain"};
            if(lower[j]==upper[j])base[j]=lower[j];
            else if(p.integer[j]) {
                if(lower[j]!=0||upper[j]!=1)throw Rejected{"nonbinary_integer"};
                binaries.push_back(j);moving[j]=true;
            } else moving[j]=true;
            offset=add(offset,mul(sign,mul(original_cost[j],base[j])));
        }
        if(binaries.empty()||binaries.size()>36)throw Rejected{"binary_count_limit"};
        std::vector<std::vector<Int> > a(m,std::vector<Int>(n,0));std::vector<std::size_t> occurrences(n,0);
        std::vector<Int> original_lo(m),original_up(m);
        for(std::size_t i=0;i<m;++i){
            original_lo[i]=bound(p.row_lower[i]);original_up[i]=bound(p.row_upper[i]);
            if(original_lo[i]>original_up[i])throw Rejected{"inconsistent_row"};
            for(auto entry:p.rows[i])a[i][entry.first]=add(a[i][entry.first],integral(entry.second));
            for(std::size_t j=0;j<n;++j)if(a[i][j])++occurrences[j];
        }
        for(std::size_t j=0;j<n;++j)if(moving[j]&&!p.integer[j]&&occurrences[j]!=1)throw Rejected{"coupled_continuous"};
        struct Slack {std::size_t row,column;Int coefficient;};std::vector<Slack> slacks;
        Coordinates lo={},hi={};std::vector<Coordinates> coefficients(binaries.size());
        std::vector<Int> cost;for(auto j:binaries)cost.push_back(mul(sign,original_cost[j]));
        for(std::size_t i=0;i<m;++i) {
            Int fixed=0,envelope=0;std::size_t continuous=n;
            for(std::size_t j=0;j<n;++j) {
                Int contribution=mul(a[i][j],base[j]);fixed=add(fixed,contribution);envelope=add(envelope,absolute(contribution));
                if(a[i][j]&&moving[j]&&!p.integer[j]){if(continuous!=n)throw Rejected{"multiple_continuous"};continuous=j;}
            }
            lo[i]=subtract_bound(original_lo[i],fixed);hi[i]=subtract_bound(original_up[i],fixed);
            for(std::size_t k=0;k<binaries.size();++k){coefficients[k][i]=a[i][binaries[k]];envelope=add(envelope,absolute(coefficients[k][i]));}
            if(continuous!=n) {
                if(original_lo[i]!=original_up[i]||absolute(original_lo[i])==INF)throw Rejected{"continuous_requires_equality"};
                const Int rhs=lo[i],c=a[i][continuous];if(absolute(c)!=1)throw Rejected{"nonunit_continuous_coefficient"};
                Int low=c==1?lower[continuous]:-upper[continuous],high=c==1?upper[continuous]:-lower[continuous];
                lo[i]=high==INF?-INF:add(rhs,-high);hi[i]=low== -INF?INF:add(rhs,-low);
                const Int factor=mul(sign,mul(original_cost[continuous],c));
                offset=add(offset,mul(factor,rhs));
                for(std::size_t k=0;k<binaries.size();++k)cost[k]=add(cost[k],-mul(factor,coefficients[k][i]));
                slacks.push_back({i,continuous,c});
            }
        }
        Int objective_envelope=absolute(offset);for(Int c:cost)objective_envelope=add(objective_envelope,absolute(c));
        out.eligible=true;out.binary_indices=binaries;
        bool stopped=false;
        auto step=[&](){
            if(out.work>=max_work){out.status="work_limit";stopped=true;return false;}
            if(elapsed()>=budget){out.status="time_limit";stopped=true;return false;}
            ++out.work;return true;
        };
        struct Point {Coordinates activity;Int cost;std::uint32_t mask;};
        struct Tree {Coordinates low,high;Int minimum;std::size_t begin,end,best;int left=-1,right=-1;};
        const std::size_t half=binaries.size()/2,left_count=std::size_t(1)<<half,right_count=std::size_t(1)<<(binaries.size()-half);
        std::vector<Point> points;points.reserve(left_count);Coordinates activity={};Int value=0;std::uint32_t previous=0;
        auto advance=[&](std::uint32_t current,std::uint32_t before,std::size_t begin,Coordinates& sums,Int& objective){
            auto diff=current^before;if(!diff)return;std::size_t bit=0;while(!((diff>>bit)&1u))++bit;
            Int direction=(current&(std::uint32_t(1)<<bit))?1:-1;
            // The absolute-sum envelopes above bound all subset states by CAP.
            for(std::size_t i=0;i<m;++i)sums[i]+=direction*coefficients[begin+bit][i];
            objective+=direction*cost[begin+bit];
        };
        for(std::size_t k=0;k<left_count;++k){
            if(!step())return finish();auto mask=static_cast<std::uint32_t>(k^(k>>1));advance(mask,previous,0,activity,value);previous=mask;
            points.push_back({activity,value,mask});++out.left_states;
        }
        std::vector<Tree> tree;tree.reserve(left_count/4+1);
        std::function<int(std::size_t,std::size_t)> build=[&](std::size_t begin,std::size_t end){
            if(!step())return -1;
            Tree node;node.begin=begin;node.end=end;node.best=begin;node.low=node.high=points[begin].activity;node.minimum=points[begin].cost;
            for(std::size_t q=begin+1;q<end;++q){node.minimum=std::min(node.minimum,points[q].cost);for(std::size_t i=0;i<m;++i){node.low[i]=std::min(node.low[i],points[q].activity[i]);node.high[i]=std::max(node.high[i],points[q].activity[i]);}}
            int index=static_cast<int>(tree.size());tree.push_back(node);
            if(end-begin>16){
                std::size_t axis=0;for(std::size_t i=1;i<m;++i)if(node.high[i]-node.low[i]>node.high[axis]-node.low[axis])axis=i;
                std::size_t middle=(begin+end)/2;
                std::nth_element(points.begin()+begin,points.begin()+middle,points.begin()+end,[&](const Point& a,const Point& b){return a.activity[axis]<b.activity[axis];});
                tree[index].left=build(begin,middle);if(!stopped)tree[index].right=build(middle,end);
            }
            return index;
        };
        build(0,points.size());if(stopped)return finish();
        // Restore best indices AFTER all in-place descendant partitions.
        for(std::size_t q=tree.size();q-- >0;){
            auto& node=tree[q];if(node.left<0){node.best=node.begin;for(std::size_t k=node.begin+1;k<node.end;++k)if(points[k].cost<points[node.best].cost)node.best=k;}
            else {auto a=tree[node.left].best,b=tree[node.right].best;node.best=points[a].cost<=points[b].cost?a:b;}
            if(points[node.best].cost!=node.minimum)throw InternalFailure{};
        }
        auto consider=[&](const Point& left,std::uint32_t right,Int right_cost){
            auto x=base;for(std::size_t k=0;k<binaries.size();++k)x[binaries[k]]=k<half?((left.mask>>k)&1u):((right>>(k-half))&1u);
            for(auto slack:slacks){Int residual=original_lo[slack.row];for(std::size_t j=0;j<n;++j)if(j!=slack.column)residual=add(residual,-mul(a[slack.row][j],x[j]));x[slack.column]=mul(slack.coefficient,residual);}
            for(std::size_t j=0;j<n;++j)if(x[j]<lower[j]||x[j]>upper[j])throw InternalFailure{};
            for(std::size_t i=0;i<m;++i){Int activity=0;for(std::size_t j=0;j<n;++j)activity=add(activity,mul(a[i][j],x[j]));if(activity<original_lo[i]||activity>original_up[i])throw InternalFailure{};}
            Int objective=original_offset;for(std::size_t j=0;j<n;++j)objective=add(objective,mul(original_cost[j],x[j]));objective=mul(sign,objective);
            if(objective!=offset+left.cost+right_cost)throw InternalFailure{};
            if(!out.feasible||objective<out.objective_minimization){out.feasible=true;out.objective_minimization=objective;out.primal=std::move(x);}
        };
        activity={};value=0;previous=0;
        for(std::size_t k=0;k<right_count;++k){
            if(!step())return finish();auto mask=static_cast<std::uint32_t>(k^(k>>1));advance(mask,previous,half,activity,value);previous=mask;
            Coordinates lower_box={},upper_box={};for(std::size_t i=0;i<m;++i){lower_box[i]=lo[i]== -INF?-INF:lo[i]-activity[i];upper_box[i]=hi[i]==INF?INF:hi[i]-activity[i];}
            std::function<void(int)> query=[&](int index){
                if(stopped||!step())return;++out.query_nodes;const auto& node=tree[index];
                if(out.feasible&&offset+value+node.minimum>=out.objective_minimization)return;
                bool inside=true;for(std::size_t i=0;i<m;++i){if(node.low[i]>upper_box[i]||node.high[i]<lower_box[i])return;if(node.low[i]<lower_box[i]||node.high[i]>upper_box[i])inside=false;}
                if(inside){consider(points[node.best],mask,value);return;}
                if(node.left<0){for(std::size_t q=node.begin;q<node.end;++q){bool fits=true;for(std::size_t i=0;i<m;++i)if(points[q].activity[i]<lower_box[i]||points[q].activity[i]>upper_box[i]){fits=false;break;}if(fits)consider(points[q],mask,value);}}
                else {int a=node.left,b=node.right;if(tree[a].minimum>tree[b].minimum)std::swap(a,b);query(a);query(b);}
            };
            query(0);if(stopped)return finish();++out.right_states;
        }
        // No completion/certificate on interrupted enumeration or tree work.
        if(out.left_states!=left_count||out.right_states!=right_count)throw InternalFailure{};
        out.completed=true;out.verified=true;out.status=out.feasible?"optimal":"infeasible";
    } catch(const Rejected& e){out.status="unsupported";out.reason=e.reason;out.verified=false;out.completed=false;}
      catch(const InternalFailure&){out.status="internal_check_failed";out.verified=false;out.completed=false;out.primal.clear();out.feasible=false;}
      catch(const std::bad_alloc&){out.status="resource_limit";out.verified=false;out.completed=false;}
    return finish();
}
}}
