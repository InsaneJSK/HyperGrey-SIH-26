#pragma once
#include <vector>
#include <map>
#include <set>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <functional>

namespace sovereign {
using SparseVector = std::vector<std::pair<std::size_t, double> >;

// Sparse Gaussian elimination with partial row pivoting. No explicit inverse.
// Fill is retained (no magnitude-based coefficient dropping).
class SparseLU {
    std::vector<std::size_t> order_;
    std::vector<SparseVector> lower_, upper_;
public:
    std::size_t nonzeros = 0;
    bool factor(const std::vector<SparseVector>& columns, std::size_t max_fill = 16000000,const std::function<bool()>& cancelled = {}) {
        const std::size_t n = columns.size();
        std::vector<std::map<std::size_t,double> > rows(n);
        std::vector<std::set<std::size_t> > incidence(n);
        std::vector<SparseVector> lower_rows(n);
        std::vector<bool> used(n, false);
        for (std::size_t j=0;j<n;++j) for(auto a:columns[j]) {
            if(a.first>=n||!std::isfinite(a.second)) return false;
            rows[a.first][j]+=a.second;
        }
        std::size_t fill=0;
        for(std::size_t i=0;i<n;++i) for(auto a:rows[i]) {
            incidence[a.first].insert(i); ++fill;
        }
        order_.resize(n);lower_.assign(n,{});upper_.assign(n,{});nonzeros=0;
        for(std::size_t k=0;k<n;++k) {
            if(cancelled&&cancelled())return false;
            std::size_t pivot=n;double largest=0;
            for(auto i:incidence[k]) if(!used[i]) {
                const double a=std::abs(rows[i].at(k));
                if(a>largest) {largest=a;pivot=i;}
            }
            if(pivot==n||largest<1e-14||!std::isfinite(largest)) return false;
            // Threshold partial pivoting with a sparsity preference limits fill.
            for(auto i:incidence[k])if(!used[i]&&std::abs(rows[i].at(k))>=.1*largest&&rows[i].size()<rows[pivot].size())pivot=i;
            used[pivot]=true;order_[k]=pivot;lower_[k]=std::move(lower_rows[pivot]);
            for(auto a:rows[pivot]) if(a.first>=k) upper_[k].push_back(a);
            const double diagonal=rows[pivot].at(k);
            std::vector<std::size_t> affected(incidence[k].begin(),incidence[k].end());
            for(auto i:affected) if(!used[i]) {
                if(cancelled&&cancelled())return false;
                double multiplier=rows[i].at(k)/diagonal;
                if(multiplier!=0) lower_rows[i].push_back({k,multiplier});
                rows[i].erase(k);--fill;
                for(auto a:upper_[k]) if(a.first>k) {
                    auto found=rows[i].find(a.first);
                    double value=(found==rows[i].end()?0:found->second)-multiplier*a.second;
                    if(!std::isfinite(value)) return false;
                    if(found==rows[i].end()) {
                        if(value!=0) {rows[i][a.first]=value;incidence[a.first].insert(i);++fill;}
                    } else if(value==0) {
                        rows[i].erase(found);incidence[a.first].erase(i);--fill;
                    } else found->second=value;
                }
            }
            incidence[k].clear();
            nonzeros+=upper_[k].size()+lower_[k].size();
            if(fill+nonzeros>max_fill) throw std::runtime_error("resource_limit: sparse LU fill budget");
        }
        return true;
    }
    std::vector<double> solve(const std::vector<double>& b, bool transpose=false) const {
        const std::size_t n=order_.size();
        if(b.size()!=n) throw std::invalid_argument("LU RHS dimension");
        std::vector<double> x(n);
        if(!transpose) {
            for(std::size_t i=0;i<n;++i) {
                long double value=b[order_[i]];
                for(auto a:lower_[i]) value-=static_cast<long double>(a.second)*x[a.first];
                x[i]=static_cast<double>(value);
            }
            for(std::size_t i=n;i-->0;) {
                long double value=x[i];double diagonal=0;
                for(auto a:upper_[i]) {
                    if(a.first==i) diagonal=a.second;
                    else value-=static_cast<long double>(a.second)*x[a.first];
                }
                x[i]=static_cast<double>(value/diagonal);
            }
        } else {
            x=b;
            for(std::size_t i=0;i<n;++i) {
                double diagonal=upper_[i].front().second;x[i]/=diagonal;
                for(auto a:upper_[i]) if(a.first>i) x[a.first]-=a.second*x[i];
            }
            for(std::size_t i=n;i-->0;) for(auto a:lower_[i]) x[a.first]-=a.second*x[i];
            std::vector<double> permuted(n);
            for(std::size_t i=0;i<n;++i) permuted[order_[i]]=x[i];
            x.swap(permuted);
        }
        return x;
    }
};
}
