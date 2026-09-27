#pragma once
#include <cmath>
#include <limits>
#include <queue>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace sovereign { namespace detail {
// A node's ranking need not equal its proof bound. In that case a separate
// ordered index MUST supply the minimum over every queued proof bound.
// T exposes bound, search_bound, depth and id. IDs identify one queued copy.
template<class T> class MilpFrontier {
    struct Order {
        bool raw;
        explicit Order(bool r=false):raw(r){}
        bool operator()(const T& a,const T& b)const {
            double av=raw?a.search_bound:a.bound,bv=raw?b.search_bound:b.bound;
            if(av!=bv)return av>bv;
            if(a.depth!=b.depth)return a.depth<b.depth;
            return a.id>b.id;
        }
    };
    bool raw_;
    std::priority_queue<T,std::vector<T>,Order> queue_;
    std::multiset<std::pair<double,std::size_t> > bounds_;
public:
    explicit MilpFrontier(bool raw=false):raw_(raw),queue_(Order(raw)){}
    bool empty()const{return queue_.empty();}
    std::size_t size()const{return queue_.size();}
    const T& top()const{return queue_.top();}
    void push(T node){
        if(std::isnan(node.bound)||std::isnan(node.search_bound))throw std::logic_error("NaN MILP frontier key");
        auto key=std::make_pair(node.bound,node.id);
        if(!raw_){queue_.push(std::move(node));return;}
        auto inserted=bounds_.insert(key);
        try{queue_.push(std::move(node));}catch(...){bounds_.erase(inserted);throw;}
    }
    T pop(){
        if(empty())throw std::logic_error("Empty MILP frontier pop");
        T node=queue_.top();
        if(raw_){
            auto found=bounds_.find({node.bound,node.id});
            if(found==bounds_.end())throw std::logic_error("MILP frontier proof index mismatch");
            bounds_.erase(found);
        }
        queue_.pop();return node;
    }
    double minimum_bound()const{
        if(empty())return std::numeric_limits<double>::infinity();
        if(!raw_)return queue_.top().bound;
        if(bounds_.size()!=queue_.size())throw std::logic_error("MILP frontier proof index size mismatch");
        return bounds_.begin()->first;
    }
    void clear(){queue_=decltype(queue_)(Order(raw_));bounds_.clear();}
};
}}
