#pragma once
#include "mps.hpp"
#include <cmath>

namespace sovereign { namespace detail {
struct FeasibilityEvent {
    std::string kind,status;
    std::size_t node=0,call=0,step=0,mode=0,variable=0,iterations=0,fractional=0;
    bool alternate=false,accepted=false;
    double distance=NAN,violation=NAN;
    std::vector<double> point,target;
};
struct FeasibilityTrace {
    std::size_t events=0,stored_values=0,calls=0;
    std::vector<FeasibilityEvent> samples;
    std::vector<double> rejected_point;
    double rejected_rounded_violation=NAN;
    std::size_t rejected_node=0,rejected_call=0,rejected_step=0;
    void record(bool enabled,const LinearProblem& original,double tolerance,FeasibilityEvent e,
                const std::vector<double>& x={},const std::vector<double>& target={}) {
        if(!enabled)return;
        ++events;if(samples.size()>=512)return;
        const std::size_t n=original.cost.size();
        if(x.size()>=n) {
            std::vector<double> point(x.begin(),x.begin()+n);bool finite=true;
            for(double v:point)finite=finite&&std::isfinite(v);
            if(finite){
                e.distance=0;
                for(std::size_t j=0;j<n;++j)if(original.integer[j]){
                    double d=std::abs(point[j]-std::round(point[j]));e.distance+=d;e.fractional+=d>tolerance;
                }
                e.violation=original_violation(original,point,false);
                if(e.kind=="dive_point"&&!e.accepted&&!e.fractional&&rejected_point.empty()&&n<=2048){
                    // Preserve the first near-integer rejection even if earlier
                    // low-priority vectors filled the bounded trace budget.
                    for(auto it=samples.rbegin();it!=samples.rend()&&stored_values+n>100000;++it){
                        stored_values-=it->point.size()+it->target.size();it->point.clear();it->target.clear();
                    }
                    if(stored_values+n<=100000){
                        rejected_point=point;stored_values+=n;rejected_node=e.node;rejected_call=e.call;rejected_step=e.step;
                        auto rounded=point;for(std::size_t j=0;j<n;++j)if(original.integer[j])rounded[j]=std::round(rounded[j]);
                        rejected_rounded_violation=original_violation(original,rounded,false);
                    }
                }
                if(n<=2048&&stored_values+n<=100000){e.point=std::move(point);stored_values+=n;}
            }
        }
        if(target.size()==n&&n<=2048&&stored_values+n<=100000){e.target=target;stored_values+=n;}
        samples.push_back(std::move(e));
    }
};
}}
