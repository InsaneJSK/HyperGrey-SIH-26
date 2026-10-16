#pragma once
#include "mps.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>

namespace sovereign { namespace detail {
struct BinaryMeetResult {
    bool eligible=false,completed=false;
    std::size_t left_states=0,right_states=0,query_nodes=0;
    double seconds=0;
    std::vector<double> primal;
};
// Bounded incumbent heuristic, NOT a proof engine. No local objective or
// exhausted enumeration is returned as a bound/infeasibility certificate.
inline BinaryMeetResult binary_meet(const LinearProblem& p,double budget,double incumbent) {
    BinaryMeetResult out;
    const auto start=std::chrono::steady_clock::now();
    auto elapsed=[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();};
    auto finish=[&](){out.seconds=elapsed();return out;};
    const std::size_t n=p.cost.size(),m=p.rows.size();
    if(budget<=0||n>128||m>8||!m)return finish();
    typedef std::array<double,8> Coordinates;
    std::vector<std::size_t> binaries;
    std::vector<double> base(n,0);std::vector<bool> movable(n,false);
    for(std::size_t j=0;j<n;++j) {
        if(p.lower[j]==p.upper[j]&&std::isfinite(p.lower[j])) {
            if(p.integer[j]&&p.lower[j]!=std::round(p.lower[j]))return finish();
            base[j]=p.lower[j];
        }
        else if(p.integer[j]) {
            if(std::ceil(p.lower[j])!=0||std::floor(p.upper[j])!=1)return finish();
            binaries.push_back(j);movable[j]=true;
        } else movable[j]=true;
    }
    if(binaries.empty()||binaries.size()>36)return finish();
    std::vector<std::vector<double> > a(m,std::vector<double>(n,0));
    std::vector<std::size_t> occurrences(n,0);
    for(std::size_t i=0;i<m;++i)for(auto entry:p.rows[i])a[i][entry.first]+=entry.second;
    for(std::size_t i=0;i<m;++i)for(std::size_t j=0;j<n;++j)if(a[i][j]!=0) {
        if(!std::isfinite(a[i][j])||std::abs(a[i][j])>1e9)return finish();
        ++occurrences[j];
    }
    for(std::size_t j=0;j<n;++j)if(movable[j]&&!p.integer[j]&&occurrences[j]!=1)return finish();
    struct Slack {std::size_t row,column;double coefficient;};std::vector<Slack> slacks;
    Coordinates lo={},hi={};double sign=p.maximize?-1:1,offset=sign*p.offset;
    for(std::size_t j=0;j<n;++j)offset+=sign*p.cost[j]*base[j];
    std::vector<double> cost;for(auto j:binaries)cost.push_back(sign*p.cost[j]);
    std::vector<Coordinates> coefficients(binaries.size());
    for(std::size_t i=0;i<m;++i) {
        long double fixed=0;std::size_t continuous=n;
        for(std::size_t j=0;j<n;++j) {
            fixed+=static_cast<long double>(a[i][j])*base[j];
            if(a[i][j]!=0&&movable[j]&&!p.integer[j]) {
                if(continuous!=n)return finish();continuous=j;
            }
        }
        lo[i]=p.row_lower[i]-static_cast<double>(fixed);hi[i]=p.row_upper[i]-static_cast<double>(fixed);
        for(std::size_t k=0;k<binaries.size();++k)coefficients[k][i]=a[i][binaries[k]];
        if(continuous!=n) {
            if(!std::isfinite(p.row_lower[i])||p.row_lower[i]!=p.row_upper[i])return finish();
            const double rhs=lo[i],c=a[i][continuous];
            const double low=c*p.lower[continuous],high=c*p.upper[continuous];
            lo[i]=rhs-std::max(low,high);hi[i]=rhs-std::min(low,high);
            const double factor=sign*p.cost[continuous]/c;
            offset+=factor*rhs;
            for(std::size_t k=0;k<binaries.size();++k)cost[k]-=factor*coefficients[k][i];
            slacks.push_back({i,continuous,c});
        }
        if(std::isnan(lo[i])||std::isnan(hi[i])||lo[i]>hi[i])return finish();
        if((std::isfinite(lo[i])&&std::abs(lo[i])>1e12)||(std::isfinite(hi[i])&&std::abs(hi[i])>1e12))return finish();
    }
    if(!std::isfinite(offset)||std::abs(offset)>1e15)return finish();
    for(double c:cost)if(!std::isfinite(c)||std::abs(c)>1e12)return finish();
    out.eligible=true;if(elapsed()>=budget)return finish();
    struct Point {Coordinates activity;double cost;std::uint32_t mask;};
    struct TreeNode {Coordinates low,high;double minimum;std::size_t begin,end,best;int left=-1,right=-1;};
    const std::size_t half=binaries.size()/2,left_count=std::size_t(1)<<half;
    const std::size_t right_count=std::size_t(1)<<(binaries.size()-half);
    // <=2^18 points (~21 MiB) plus a bounded, leaf-blocked search tree.
    std::vector<Point> points;points.reserve(left_count);Coordinates activity={};double value=0;
    std::uint32_t previous=0;
    auto advance=[&](std::uint32_t current,std::uint32_t before,std::size_t begin,Coordinates& sums,double& objective) {
        const auto diff=current^before;if(!diff)return;
        std::size_t bit=0;while(!((diff>>bit)&1u))++bit;
        const double direction=(current&(std::uint32_t(1)<<bit))?1.:-1.;
        for(std::size_t i=0;i<m;++i)sums[i]+=direction*coefficients[begin+bit][i];
        objective+=direction*cost[begin+bit];
    };
    for(std::size_t k=0;k<left_count;++k) {
        if(k%256==0&&elapsed()>=budget)return finish();
        const auto mask=static_cast<std::uint32_t>(k^(k>>1));advance(mask,previous,0,activity,value);previous=mask;
        points.push_back({activity,value,mask});++out.left_states;
    }
    std::vector<TreeNode> tree;tree.reserve(left_count/4+1);bool stopped=false;
    std::function<int(std::size_t,std::size_t)> build=[&](std::size_t begin,std::size_t end) {
        if(elapsed()>=budget){stopped=true;return -1;}
        TreeNode node;node.begin=begin;node.end=end;node.best=begin;node.low=node.high=points[begin].activity;node.minimum=points[begin].cost;
        for(std::size_t k=begin+1;k<end;++k) {
            if(points[k].cost<node.minimum){node.minimum=points[k].cost;node.best=k;}
            for(std::size_t i=0;i<m;++i){node.low[i]=std::min(node.low[i],points[k].activity[i]);node.high[i]=std::max(node.high[i],points[k].activity[i]);}
        }
        const int index=static_cast<int>(tree.size());tree.push_back(node);
        if(end-begin>16) {
            std::size_t axis=0;for(std::size_t i=1;i<m;++i)if(node.high[i]-node.low[i]>node.high[axis]-node.low[axis])axis=i;
            const std::size_t middle=(begin+end)/2;
            std::nth_element(points.begin()+begin,points.begin()+middle,points.begin()+end,[&](const Point& a,const Point& b){return a.activity[axis]<b.activity[axis];});
            // nth_element permutes the former best index; recompute it locally.
            tree[index].best=begin;for(std::size_t k=begin+1;k<end;++k)if(points[k].cost<points[tree[index].best].cost)tree[index].best=k;
            tree[index].left=build(begin,middle);if(!stopped)tree[index].right=build(middle,end);
        }
        return index;
    };
    build(0,points.size());if(stopped)return finish();
    // Recursive child partitioning also changes ancestor best indices. Restore
    // all indices after the entire point partition is final.
    for(auto& node:tree){node.best=node.begin;for(std::size_t k=node.begin+1;k<node.end;++k)if(points[k].cost<points[node.best].cost)node.best=k;}
    auto consider=[&](std::uint32_t left,std::uint32_t right) {
        auto x=base;
        for(std::size_t k=0;k<binaries.size();++k)x[binaries[k]]=k<half?((left>>k)&1u):((right>>(k-half))&1u);
        for(auto slack:slacks) {
            long double residual=p.row_lower[slack.row];
            for(std::size_t j=0;j<n;++j)if(j!=slack.column)residual-=static_cast<long double>(a[slack.row][j])*x[j];
            x[slack.column]=static_cast<double>(residual/slack.coefficient);
        }
        for(double xj:x)if(!std::isfinite(xj))return;
        if(original_violation(p,x,false)>1e-7)return;
        long double objective=p.offset;for(std::size_t j=0;j<n;++j)objective+=static_cast<long double>(p.cost[j])*x[j];
        const double normalized=sign*static_cast<double>(objective);
        if(std::isfinite(normalized)&&normalized<incumbent){incumbent=normalized;out.primal=std::move(x);}
    };
    activity={};value=0;previous=0;
    for(std::size_t k=0;k<right_count;++k) {
        if(elapsed()>=budget)return finish();
        const auto mask=static_cast<std::uint32_t>(k^(k>>1));advance(mask,previous,half,activity,value);previous=mask;
        Coordinates lower={},upper={};for(std::size_t i=0;i<m;++i){lower[i]=lo[i]-activity[i];upper[i]=hi[i]-activity[i];}
        std::function<void(int)> query=[&](int index) {
            if(stopped)return;
            if((++out.query_nodes)%1024==0&&elapsed()>=budget){stopped=true;return;}
            const auto& node=tree[index];
            double estimate=offset+value+node.minimum;
            // Conservative numerical margins improve recall but are NOT a proof.
            if(std::isfinite(incumbent)&&estimate>incumbent+1e-7*(1+std::abs(incumbent)))return;
            bool inside=true;
            for(std::size_t i=0;i<m;++i) {
                const double margin=1e-7*(1+std::abs(activity[i])+std::abs(node.low[i])+std::abs(node.high[i]));
                if(node.low[i]>upper[i]+margin||node.high[i]<lower[i]-margin)return;
                if(node.low[i]<lower[i]||node.high[i]>upper[i])inside=false;
            }
            if(inside){consider(points[node.best].mask,mask);return;}
            if(node.left<0) {
                for(std::size_t q=node.begin;q<node.end;++q) {
                    bool fits=true;for(std::size_t i=0;i<m;++i)if(points[q].activity[i]<lower[i]-1e-7||points[q].activity[i]>upper[i]+1e-7){fits=false;break;}
                    if(fits)consider(points[q].mask,mask);
                }
            } else {
                int first=node.left,second=node.right;if(tree[first].minimum>tree[second].minimum)std::swap(first,second);
                query(first);query(second);
            }
        };
        query(0);if(stopped)return finish();++out.right_states;
    }
    out.completed=true;return finish();
}
}}
