#include "bounded_simplex.hpp"
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

using namespace sovereign;
namespace {
const double inf=std::numeric_limits<double>::infinity();
std::uint64_t state=26119;
double uniform(){state^=state<<13;state^=state>>7;state^=state<<17;return static_cast<double>(state>>11)/9007199254740992.0;}
int pick(int n){return static_cast<int>(uniform()*n)%n;}
void check(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}

// Random bounded LP around a known point; `shift` pushes some rows away so a
// fraction of instances are infeasible. Integral data keeps both engines honest.
LinearProblem random_problem(int n,int m,bool shift) {
    LinearProblem p;p.names.resize(n);p.cost.resize(n);p.lower.resize(n);p.upper.resize(n);p.integer.assign(n,false);
    std::vector<double> x0(n);
    for(int j=0;j<n;++j){
        p.names[j]="x"+std::to_string(j);
        p.cost[j]=pick(21)-10;
        const int kind=pick(10);
        double lo=pick(7)-3,width=pick(6);
        if(kind<6){p.lower[j]=lo;p.upper[j]=lo+width;}
        else if(kind==6){p.lower[j]=lo;p.upper[j]=inf;}
        else if(kind==7){p.lower[j]=-inf;p.upper[j]=lo+width;}
        else if(kind==8){p.lower[j]=p.upper[j]=lo;}
        else {p.lower[j]=-inf;p.upper[j]=inf;}
        const double a=std::isfinite(p.lower[j])?p.lower[j]:(std::isfinite(p.upper[j])?p.upper[j]-3:-2);
        const double b=std::isfinite(p.upper[j])?p.upper[j]:a+4;
        x0[j]=a+(b-a)*uniform();
    }
    p.rows.resize(m);p.row_lower.resize(m);p.row_upper.resize(m);
    for(int i=0;i<m;++i){
        double activity=0;
        for(int j=0;j<n;++j)if(uniform()<.35){double a=pick(13)-6;if(a!=0){p.rows[i].push_back({static_cast<std::size_t>(j),a});activity+=a*x0[j];}}
        const int kind=pick(8);const double base=std::floor(activity);
        if(kind<3){p.row_lower[i]=-inf;p.row_upper[i]=base+pick(4);}
        else if(kind<5){p.row_lower[i]=base-pick(4);p.row_upper[i]=inf;}
        else if(kind<6){p.row_lower[i]=base-pick(3);p.row_upper[i]=base+1+pick(3);}
        else if(kind<7){p.row_lower[i]=p.row_upper[i]=activity;}
        else {p.row_lower[i]=-inf;p.row_upper[i]=inf;}
        if(shift&&uniform()<.3&&std::isfinite(p.row_upper[i])){p.row_upper[i]-=40;if(std::isfinite(p.row_lower[i]))p.row_lower[i]=std::min(p.row_lower[i],p.row_upper[i]);}
    }
    // Every unbounded direction gets an explicit bounding row to keep most LPs bounded.
    SparseVector box;for(int j=0;j<n;++j)if(!std::isfinite(p.lower[j])||!std::isfinite(p.upper[j]))box.push_back({static_cast<std::size_t>(j),1});
    if(!box.empty()&&uniform()<.8){
        for(auto& a:box){SparseVector row{a};p.rows.push_back(row);p.row_lower.push_back(-60);p.row_upper.push_back(60);}
    }
    p.maximize=uniform()<.3;p.offset=pick(5)-2;
    return p;
}
double minimization(const LinearProblem& p,double objective){return p.maximize?-objective:objective;}
bool optimal(const SparseLpResult& r){return r.solution.status=="optimal"&&r.solution.optimality_verified;}
bool infeasible(const SparseLpResult& r){return r.solution.status=="infeasible"&&r.solution.infeasibility_verified;}
}

int main() {
    try {
        Options o;o.time_limit_seconds=10;o.iteration_limit=100000;
        std::size_t compared=0,infeasible_agreed=0,warm_checked=0,cutoff_checked=0,row_warm=0,bound_checked=0,unverified=0,trials=0;
        BoundedLpStats stats;
        for(int trial=0;trial<3000;++trial){
            const int n=1+pick(30),m=pick(25);
            LinearProblem p=random_problem(n,m,trial%4==0);
            ++trials;
            auto reference=solve_sparse_lp(p,o);
            auto ours=solve_bounded_lp(p,o,nullptr,&stats);
            if(optimal(ours)){
                check(!infeasible(reference),"Bounded engine optimal where reference proves infeasible (trial "+std::to_string(trial)+")");
                check(reference.solution.status!="unbounded"||!reference.solution.unboundedness_verified,"Bounded engine optimal on verified unbounded LP");
                const double viol=original_violation(p,ours.solution.primal,true);
                check(viol<=1e-8,"Reported primal violation not reproduced");
                check(ours.best_bound<=minimization(p,ours.solution.objective)+1e-7*(1+std::abs(ours.solution.objective)),"Safe bound above own objective");
                ++bound_checked;
            }
            if(infeasible(ours))check(!optimal(reference),"Bounded engine infeasible where reference is optimal (trial "+std::to_string(trial)+")");
            if(optimal(ours)&&optimal(reference)){
                const double a=ours.solution.objective,b=reference.solution.objective;
                check(std::abs(a-b)<=1e-6*(1+std::abs(b)),"Objective mismatch trial "+std::to_string(trial)+": "+std::to_string(a)+" vs "+std::to_string(b));
                ++compared;
            } else if(infeasible(ours)&&infeasible(reference))++infeasible_agreed;
            else if(!optimal(ours)&&!infeasible(ours)){
                // Unbounded LPs are reported without a claim; count only unexplained failures.
                const bool reference_unbounded=reference.solution.status=="unbounded";
                if(!(ours.solution.status=="unbounded"&&(reference_unbounded||!optimal(reference))))++unverified;
                if(std::getenv("BOUNDED_DEBUG"))std::cerr<<"trial "<<trial<<" ours "<<ours.solution.status<<" reference "<<reference.solution.status<<"\n";
            }
            if(!optimal(ours))continue;
            // Branching-like bound change: warm and cold must agree.
            const double opt_min=minimization(p,ours.solution.objective);
            LinearProblem child=p;const int j=pick(n);
            const double v=ours.solution.primal[j];
            if(uniform()<.5)child.upper[j]=std::max(child.lower[j],std::floor(v-.5));
            else child.lower[j]=std::min(child.upper[j],std::ceil(v+.5));
            auto cold=solve_bounded_lp(child,o,nullptr,&stats);
            auto warm=solve_bounded_lp(child,o,ours.basis.bounded.get(),&stats);
            if(optimal(cold)&&optimal(warm)){
                check(std::abs(cold.solution.objective-warm.solution.objective)<=1e-6*(1+std::abs(cold.solution.objective)),"Warm/cold objective mismatch trial "+std::to_string(trial));
                ++warm_checked;
            }
            if(infeasible(warm))check(!optimal(cold),"Warm infeasible, cold optimal trial "+std::to_string(trial));
            if(infeasible(cold))check(!optimal(warm),"Cold infeasible, warm optimal trial "+std::to_string(trial));
            // Cutoff: below the optimum a cutoff must never fire; above-optimum cutoffs must bound correctly.
            auto model=prepare_bounded_lp(p);
            auto high=solve_bounded_lp(p,*model,p.lower,p.upper,o,nullptr,opt_min+1,&stats);
            check(high.solution.status!="cutoff","Cutoff fired although the optimum is below it (trial "+std::to_string(trial)+")");
            if(optimal(cold)){
                const double child_min=minimization(child,cold.solution.objective);
                if(child_min>opt_min+1e-6){
                    const double cut=(opt_min+child_min)/2;
                    auto cmodel=prepare_bounded_lp(child);
                    auto stop=solve_bounded_lp(child,*cmodel,child.lower,child.upper,o,ours.basis.bounded.get(),cut,&stats);
                    if(stop.solution.status=="cutoff"){
                        check(stop.best_bound>=cut&&stop.best_bound<=child_min+1e-7*(1+std::abs(child_min)),"Invalid cutoff bound trial "+std::to_string(trial));
                        ++cutoff_checked;
                    } else if(optimal(stop))check(std::abs(stop.solution.objective-cold.solution.objective)<=1e-6*(1+std::abs(child_min)),"Cutoff-mode optimum mismatch");
                }
            }
            // Added row (cut-like): warm start extends the basis with a basic logical.
            LinearProblem cut=p;SparseVector row;double activity=0;
            for(int k=0;k<n;++k)if(uniform()<.5){double a=pick(5)-2;if(a!=0){row.push_back({static_cast<std::size_t>(k),a});activity+=a*ours.solution.primal[k];}}
            if(!row.empty()){
                cut.rows.push_back(row);cut.row_lower.push_back(-inf);cut.row_upper.push_back(std::floor(activity)-1);
                auto rc=solve_bounded_lp(cut,o,nullptr,&stats);
                auto rw=solve_bounded_lp(cut,o,ours.basis.bounded.get(),&stats);
                auto rr=solve_sparse_lp(cut,o);
                if(optimal(rc)&&optimal(rw)){check(std::abs(rc.solution.objective-rw.solution.objective)<=1e-6*(1+std::abs(rc.solution.objective)),"Row warm/cold mismatch");++row_warm;}
                if(optimal(rw)&&optimal(rr))check(std::abs(rr.solution.objective-rw.solution.objective)<=1e-6*(1+std::abs(rr.solution.objective)),"Row warm/reference mismatch");
                if(infeasible(rw))check(!optimal(rr)&&!optimal(rc),"Row warm infeasible but optimum exists");
            }
        }
        std::cout<<"trials "<<trials<<" compared "<<compared<<" infeasible_agreed "<<infeasible_agreed<<" unverified "<<unverified
                 <<" warm "<<warm_checked<<" cutoff "<<cutoff_checked<<" row_warm "<<row_warm<<" bounds "<<bound_checked
                 <<" farkas_rejected "<<stats.farkas_rejected<<" verification_rejected "<<stats.verification_rejected
                 <<" failures "<<stats.failures<<" cleanups "<<stats.cleanups<<'\n';
        check(compared>1000,"Too few optimal comparisons");
        check(warm_checked>500&&row_warm>300,"Too few warm-start comparisons");
        check(unverified*50<trials,"Too many unverified bounded-engine outcomes");
        return 0;
    } catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
