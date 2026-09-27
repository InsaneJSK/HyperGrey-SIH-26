// Validity of the tableau Gomory mixed-integer cuts, by enumeration.
//
// Every model here is small enough that all of its integer points can be
// listed, so each returned cut is checked against every feasible point rather
// than against a reference solver's opinion. The strengthened relaxation is
// also re-solved and must not pass the enumerated integer optimum, which
// catches an invalid cut through the bound even when it removes no point of
// this particular box.
#include "bounded_simplex.hpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using namespace sovereign;
namespace {
const double inf=std::numeric_limits<double>::infinity();
std::uint64_t state=2611903;
double uniform(){state^=state<<13;state^=state>>7;state^=state<<17;return static_cast<double>(state>>11)/9007199254740992.0;}
int pick(int n){return static_cast<int>(uniform()*n)%n;}
void check(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}

// All variables integer inside a small explicit box, mixed row senses, and a
// quarter of the coefficients half-integral so the cuts are not exercised on
// integral data alone.
LinearProblem random_integer_problem(int n,int m) {
    LinearProblem p;
    p.names.resize(n);p.cost.resize(n);p.lower.resize(n);p.upper.resize(n);p.integer.assign(n,true);
    for(int j=0;j<n;++j){
        p.names[j]="x"+std::to_string(j);
        p.cost[j]=pick(21)-10;
        const double lo=pick(3)-1;
        p.lower[j]=lo;p.upper[j]=lo+1+pick(3);
    }
    p.rows.resize(m);p.row_lower.assign(m,-inf);p.row_upper.assign(m,inf);
    for(int i=0;i<m;++i){
        double lowest=0,highest=0;
        for(int j=0;j<n;++j){
            if(uniform()>=.6)continue;
            double a=pick(9)-4;
            if(uniform()<.25)a+=.5;
            if(a==0)continue;
            p.rows[i].push_back({static_cast<std::size_t>(j),a});
            lowest+=a>0?a*p.lower[j]:a*p.upper[j];
            highest+=a>0?a*p.upper[j]:a*p.lower[j];
        }
        if(p.rows[i].empty()){
            const int j=pick(n);
            p.rows[i].push_back({static_cast<std::size_t>(j),1});
            lowest=p.lower[j];highest=p.upper[j];
        }
        const double middle=lowest+(highest-lowest)*(.3+.4*uniform());
        const int kind=pick(6);
        if(kind<3)p.row_upper[i]=std::floor(middle*2)/2;
        else if(kind<5)p.row_lower[i]=std::ceil(middle*2)/2;
        else {p.row_lower[i]=std::ceil(middle*2)/2-1;p.row_upper[i]=p.row_lower[i]+1+pick(3);}
    }
    p.maximize=uniform()<.4;p.offset=pick(5)-2;
    return p;
}
double activity(const std::vector<std::pair<std::size_t,double> >& row,const std::vector<double>& x,double& magnitude) {
    double sum=0;magnitude=0;
    for(auto a:row){const double t=a.second*x[a.first];sum+=t;magnitude+=std::abs(t);}
    return sum;
}

// Mixed model with continuous columns, all bounds finite so that maximizing a
// cut over a fixed integer assignment is always bounded.
LinearProblem random_mixed_problem(int integers,int continuous,int m) {
    const int n=integers+continuous;
    LinearProblem p;
    p.names.resize(n);p.cost.resize(n);p.lower.resize(n);p.upper.resize(n);p.integer.assign(n,false);
    for(int j=0;j<n;++j){
        p.names[j]="x"+std::to_string(j);
        p.cost[j]=pick(21)-10;
        if(j<integers){p.integer[j]=true;const double lo=pick(3)-1;p.lower[j]=lo;p.upper[j]=lo+1+pick(2);}
        else {p.lower[j]=pick(3)-1;p.upper[j]=p.lower[j]+1+3*uniform();}
    }
    p.rows.resize(m);p.row_lower.assign(m,-inf);p.row_upper.assign(m,inf);
    for(int i=0;i<m;++i){
        double lowest=0,highest=0;
        for(int j=0;j<n;++j){
            if(uniform()>=.7)continue;
            double a=pick(9)-4;
            if(uniform()<.4)a+=.5;
            if(a==0)continue;
            p.rows[i].push_back({static_cast<std::size_t>(j),a});
            lowest+=a>0?a*p.lower[j]:a*p.upper[j];
            highest+=a>0?a*p.upper[j]:a*p.lower[j];
        }
        if(p.rows[i].empty()){
            const int j=pick(n);
            p.rows[i].push_back({static_cast<std::size_t>(j),1});
            lowest=p.lower[j];highest=p.upper[j];
        }
        const double middle=lowest+(highest-lowest)*(.3+.4*uniform());
        const int kind=pick(6);
        if(kind<3)p.row_upper[i]=std::floor(middle*2)/2;
        else if(kind<5)p.row_lower[i]=std::ceil(middle*2)/2;
        else {p.row_lower[i]=std::ceil(middle*2)/2-1;p.row_upper[i]=p.row_lower[i]+1+pick(3);}
    }
    p.maximize=uniform()<.4;p.offset=pick(5)-2;
    return p;
}

// Largest value the cut's own row can reach over the mixed feasible region
// with the integer variables fixed: the exact test of a cut on that assignment.
// Returns false when no feasible completion exists.
bool cut_maximum(const LinearProblem& p,const std::vector<std::pair<std::size_t,double> >& row,
                 const std::vector<double>& assignment,int integers,const Options& o,double& value) {
    LinearProblem q=p;
    q.maximize=true;q.offset=0;
    std::fill(q.cost.begin(),q.cost.end(),0.0);
    for(auto a:row)q.cost[a.first]=a.second;
    for(int j=0;j<integers;++j)q.lower[j]=q.upper[j]=assignment[j];
    auto r=solve_bounded_lp(q,o,nullptr,nullptr);
    if(r.solution.status=="infeasible"&&r.solution.infeasibility_verified)return false;
    if(r.solution.status!="optimal"||!r.solution.optimality_verified)return false;
    value=r.solution.objective;
    return true;
}
}

int main() {
    try {
        Options o;o.time_limit_seconds=5;o.tolerance=1e-9;
        const std::size_t trials=3000;
        std::size_t solved=0,with_cuts=0,total_cuts=0,strict=0,points=0,bounds=0,feasible_models=0;
        GomoryStats totals;
        for(std::size_t trial=0;trial<trials;++trial) {
            const int n=2+pick(5),m=1+pick(4);
            auto p=random_integer_problem(n,m);
            auto model=prepare_bounded_lp(p);
            auto relaxation=solve_bounded_lp(p,*model,p.lower,p.upper,o,nullptr,inf,nullptr);
            if(relaxation.solution.status!="optimal"||!relaxation.solution.optimality_verified)continue;
            ++solved;
            auto cuts=separate_gomory(p,*model,p.lower,p.upper,o,*relaxation.basis.bounded,8,1.0,nullptr,&totals);
            if(cuts.empty())continue;
            ++with_cuts;total_cuts+=cuts.size();
            for(const auto& cut:cuts){
                double magnitude=0;
                const double value=activity(cut.row,relaxation.solution.primal,magnitude);
                check(value>cut.rhs-1e-7*(1+magnitude),"Cut does not remove the relaxation point, trial "+std::to_string(trial));
                if(value>cut.rhs)++strict;
                check(cut.efficacy>0&&std::isfinite(cut.rhs),"Cut reports no efficacy, trial "+std::to_string(trial));
            }
            // Enumerate the box: every integer point must satisfy every cut.
            std::vector<double> x=p.lower;
            double best=inf;bool any=false;
            for(;;){
                bool feasible=true;
                for(std::size_t i=0;i<p.rows.size()&&feasible;++i){
                    double magnitude=0;const double value=activity(p.rows[i],x,magnitude);
                    const double tolerance=1e-9*(1+magnitude);
                    feasible=value>=p.row_lower[i]-tolerance&&value<=p.row_upper[i]+tolerance;
                }
                if(feasible){
                    any=true;++points;
                    double value=p.offset;
                    for(std::size_t j=0;j<x.size();++j)value+=p.cost[j]*x[j];
                    best=std::min(best,p.maximize?-value:value);
                    for(const auto& cut:cuts){
                        double magnitude=0;const double reached=activity(cut.row,x,magnitude);
                        check(reached<=cut.rhs+1e-6*(1+magnitude+std::abs(cut.rhs)),
                              "Cut removes a feasible integer point, trial "+std::to_string(trial));
                    }
                }
                std::size_t j=0;
                for(;j<x.size();++j){x[j]+=1;if(x[j]<=p.upper[j]+.5)break;x[j]=p.lower[j];}
                if(j==x.size())break;
            }
            if(!any)continue;
            ++feasible_models;
            LinearProblem strengthened=p;
            for(const auto& cut:cuts){
                strengthened.rows.push_back(cut.row);
                strengthened.row_lower.push_back(-inf);
                strengthened.row_upper.push_back(cut.rhs);
            }
            auto after=solve_bounded_lp(strengthened,o,nullptr,nullptr);
            check(!(after.solution.status=="infeasible"&&after.solution.infeasibility_verified),
                  "Cuts made a model with an integer point infeasible, trial "+std::to_string(trial));
            if(after.solution.status=="optimal"&&after.solution.optimality_verified){
                const double bound=p.maximize?-after.solution.objective:after.solution.objective;
                check(bound<=best+1e-6*(1+std::abs(best)),
                      "Cut relaxation passes the integer optimum, trial "+std::to_string(trial));
                ++bounds;
            }
        }
        std::cout<<"trials "<<trials<<" solved "<<solved<<" with_cuts "<<with_cuts<<" cuts "<<total_cuts
                 <<" strictly_violated "<<strict<<" integer_points "<<points<<" bound_checks "<<bounds
                 <<" feasible_models "<<feasible_models
                 <<" | candidates "<<totals.candidates<<" attempts "<<totals.attempts
                 <<" consistency "<<totals.skipped_consistency<<" dynamism "<<totals.skipped_dynamism
                 <<" efficacy "<<totals.skipped_efficacy<<" drop "<<totals.skipped_drop
                 <<" free "<<totals.skipped_free<<" support "<<totals.skipped_support
                 <<" basis "<<totals.basis_rejected<<'\n';
        // Mixed models: the cut is maximized over the continuous variables with
        // the integer variables fixed, one LP per assignment, so a continuous
        // coefficient with the wrong sign or shift cannot pass unnoticed.
        std::size_t mixed_models=0,mixed_cuts=0,assignments=0,completions=0;
        GomoryStats mixed_totals;
        for(std::size_t trial=0;trial<400;++trial) {
            const int integers=2+pick(2),continuous=1+pick(3),m=2+pick(3);
            auto p=random_mixed_problem(integers,continuous,m);
            auto model=prepare_bounded_lp(p);
            auto relaxation=solve_bounded_lp(p,*model,p.lower,p.upper,o,nullptr,inf,nullptr);
            if(relaxation.solution.status!="optimal"||!relaxation.solution.optimality_verified)continue;
            auto cuts=separate_gomory(p,*model,p.lower,p.upper,o,*relaxation.basis.bounded,4,1.0,nullptr,&mixed_totals);
            if(cuts.empty())continue;
            ++mixed_models;mixed_cuts+=cuts.size();
            std::vector<double> assignment(p.lower.begin(),p.lower.begin()+integers);
            for(;;){
                ++assignments;
                for(const auto& cut:cuts){
                    double reached=0;
                    if(!cut_maximum(p,cut.row,assignment,integers,o,reached))continue;
                    ++completions;
                    check(reached<=cut.rhs+1e-6*(1+std::abs(reached)+std::abs(cut.rhs)),
                          "Cut removes a mixed feasible point, trial "+std::to_string(trial));
                }
                int j=0;
                for(;j<integers;++j){assignment[j]+=1;if(assignment[j]<=p.upper[j]+.5)break;assignment[j]=p.lower[j];}
                if(j==integers)break;
            }
        }
        std::cout<<"mixed_models "<<mixed_models<<" mixed_cuts "<<mixed_cuts<<" assignments "<<assignments
                 <<" feasible_completions "<<completions
                 <<" | candidates "<<mixed_totals.candidates<<" attempts "<<mixed_totals.attempts
                 <<" consistency "<<mixed_totals.skipped_consistency<<" dynamism "<<mixed_totals.skipped_dynamism
                 <<" efficacy "<<mixed_totals.skipped_efficacy<<" drop "<<mixed_totals.skipped_drop
                 <<" free "<<mixed_totals.skipped_free<<" support "<<mixed_totals.skipped_support<<'\n';
        check(mixed_models>50,"Too few mixed models produced a cut");
        check(completions>500,"Too few mixed feasible completions were checked");
        check(with_cuts>200,"Too few models produced a cut");
        check(bounds>100,"Too few strengthened-bound checks");
        check(points>10000,"Too few enumerated integer points");
        check(strict*4>total_cuts*3,"Most cuts should strictly remove the relaxation point");
        check(totals.skipped_consistency*100<totals.attempts+100,"Too many cuts failed their own rebuild check");
        return 0;
    } catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
