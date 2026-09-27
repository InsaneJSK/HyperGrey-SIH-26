#include "milp.hpp"
#include "milp_neighborhood.hpp"
#include "milp_meet.hpp"
#include "reduced_bound_lp.hpp"
#include "milp_frontier.hpp"
#include "heuristic_polish.hpp"
#include "pump_private_basis.hpp"
#include "private_dive_ranking.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <queue>
#include <set>
#include <stdexcept>

namespace sovereign {
namespace {
const double inf=std::numeric_limits<double>::infinity();
struct Node {
    std::vector<double> lower,upper;
    double bound,search_bound;
    std::size_t id,depth;
    LpBasis basis;
    std::size_t parent_variable;
    bool branch_up;
    double parent_lp_bound,branch_distance;
};
bool propagate(const LinearProblem& p,std::vector<double>& lo,std::vector<double>& up,std::size_t& changes) {
    for(std::size_t j=0;j<lo.size();++j) {
        if(p.integer[j]){lo[j]=std::ceil(lo[j]);up[j]=std::floor(up[j]);}
        if(lo[j]>up[j])return false;
    }
    std::vector<std::pair<double,double> > proposed; // Reused across rows and passes.
    for(int pass=0;pass<10;++pass) {
        bool changed=false;
        for(std::size_t i=0;i<p.rows.size();++i) {
            const auto& row=p.rows[i];
            long double minimum=0,maximum=0;int min_inf=0,max_inf=0;
            for(auto a:row) {
                if(a.second==0)continue;
                double low=a.second>0?lo[a.first]:up[a.first],high=a.second>0?up[a.first]:lo[a.first];
                if(std::isfinite(low))minimum+=static_cast<long double>(a.second)*low;else ++min_inf;
                if(std::isfinite(high))maximum+=static_cast<long double>(a.second)*high;else ++max_inf;
            }
            long double margin=1e-9L*(1+std::abs(minimum)+std::abs(maximum));
            if((!min_inf&&minimum>p.row_upper[i]+margin)||(!max_inf&&maximum<p.row_lower[i]-margin))return false;
            proposed.clear();
            for(auto a:row) {
                const std::size_t j=a.first;
                double low=a.second>0?lo[j]:up[j],high=a.second>0?up[j]:lo[j];
                double nl=lo[j],nu=up[j];
                auto tighten=[&](long double value,bool upper) {
                    double slack=1e-9*(1+std::abs(static_cast<double>(value)));
                    if(upper)nu=std::min(nu,static_cast<double>(value)+slack);else nl=std::max(nl,static_cast<double>(value)-slack);
                };
                if(a.second!=0&&std::isfinite(p.row_upper[i])&&min_inf-(!std::isfinite(low))==0) {
                    long double other=minimum-(std::isfinite(low)?static_cast<long double>(a.second)*low:0);
                    tighten((p.row_upper[i]-other)/a.second,a.second>0);
                }
                if(a.second!=0&&std::isfinite(p.row_lower[i])&&max_inf-(!std::isfinite(high))==0) {
                    long double other=maximum-(std::isfinite(high)?static_cast<long double>(a.second)*high:0);
                    tighten((p.row_lower[i]-other)/a.second,a.second<0);
                }
                if(p.integer[j]){nl=std::ceil(nl);nu=std::floor(nu);}
                if(nl>nu)return false;
                proposed.push_back({nl,nu});
            }
            // Apply together: all implied bounds were derived from the same row sums.
            for(std::size_t k=0;k<row.size();++k) {
                auto j=row[k].first;
                if(proposed[k].first>lo[j]+1e-10||proposed[k].second<up[j]-1e-10){changed=true;++changes;}
                lo[j]=proposed[k].first;up[j]=proposed[k].second;
            }
        }
        if(!changed)break;
    }
    return true;
}
std::size_t add_covers(LinearProblem& p,const std::vector<double>& x) {
    std::size_t added=0,original_rows=p.rows.size();
    for(std::size_t i=0;i<original_rows&&added<16;++i)for(int side=0;side<2&&added<16;++side) {
        double bound=side?p.row_lower[i]:p.row_upper[i],sign=side?-1:1;
        if(!std::isfinite(bound))continue;
        bound*=sign;
        struct Item {std::size_t j;double weight,z;bool complement;};std::vector<Item> items;bool valid=true;
        for(auto a:p.rows[i]) {
            if(a.second==0)continue;
            if(!p.integer[a.first]||p.lower[a.first]<0||p.upper[a.first]>1){valid=false;break;}
            double weight=sign*a.second;bool complement=weight<0;
            if(complement)bound-=weight;
            items.push_back({a.first,std::abs(weight),complement?1-x[a.first]:x[a.first],complement});
        }
        if(!valid||items.empty())continue;
        std::sort(items.begin(),items.end(),[](const Item& a,const Item& b){return a.z==b.z?a.weight>b.weight:a.z>b.z;});
        double sum=0,activity=0;std::size_t count=0;
        while(count<items.size()&&sum<=bound+1e-8*(1+std::abs(bound))) {sum+=items[count].weight;activity+=items[count].z;++count;}
        if(sum<=bound+1e-8*(1+std::abs(bound))||activity<=static_cast<double>(count)-1+1e-7)continue;
        SparseVector cut;double rhs=static_cast<double>(count)-1;
        for(std::size_t k=0;k<count;++k){cut.push_back({items[k].j,items[k].complement?-1.0:1.0});if(items[k].complement)rhs-=1;}
        std::sort(cut.begin(),cut.end());bool duplicate=false;
        for(std::size_t r=0;r<p.rows.size();++r)if(p.rows[r]==cut&&p.row_upper[r]==rhs)duplicate=true;
        if(!duplicate){p.rows.push_back(cut);p.row_lower.push_back(-inf);p.row_upper.push_back(rhs);++added;}
    }
    return added;
}
}
MilpResult solve_milp(const LinearProblem& original,const MilpOptions& requested) {
    MilpOptions opt=requested;
    if(opt.late_reduced_bound_lp){opt.reduced_bound_lp=false;opt.late_compact_equalities=true;}
    if(opt.late_compact_equalities){opt.lp.compact_equalities=false;opt.lifted_covers=true;opt.late_lifted_covers=true;}
    validate_linear_problem(original);
    if(opt.root_cut_rounds>5)throw std::invalid_argument("MILP root cut rounds must be in [0,5]");
    if(opt.cut_after_incumbent&&!opt.adaptive_cut_rounds)throw std::invalid_argument("cut-after-incumbent requires adaptive-cut-rounds");
    if(opt.lp.capture_refinement&&!opt.capture_work)throw std::invalid_argument("capture-refinement requires capture-work for MILP");
    if(opt.lp.refine_at_checks&&!opt.lp.refine_basis)throw std::invalid_argument("refine-at-checks requires refine-basis");
    if(opt.repair_heuristic_candidates&&!opt.repair_candidates)throw std::invalid_argument("repair-heuristic-candidates requires repair-candidates");
    if(opt.pump_distance_diving&&!opt.pump_guided_diving)throw std::invalid_argument("pump-distance-diving requires pump-guided-diving");
    if(opt.pump_distance_reopt&&(!opt.pump_distance_diving||!opt.pump_primal_reopt))
        throw std::invalid_argument("pump-distance-reopt requires pump-distance-diving and pump-primal-reopt");
    if(opt.pump_distance_stage&&!opt.pump_distance_reopt)throw std::invalid_argument("pump-distance-stage requires pump-distance-reopt");
    if(opt.private_dual_certificate&&!opt.pump_distance_reopt)throw std::invalid_argument("private-dual-certificate requires pump-distance-reopt");
    if(opt.lp.warm_infeasibility_certificate)throw std::invalid_argument("Use private-dual-certificate for private MILP certificates");
    if(opt.pump_distance_alternate_reserve&&!opt.pump_distance_diving)throw std::invalid_argument("pump-distance-alternate-reserve requires pump-distance-diving");
    if(opt.pump_distance_stable_ranking&&!opt.pump_distance_diving)throw std::invalid_argument("pump-distance-stable-ranking requires pump-distance-diving");
    if(opt.lp.primal_warm_start)throw std::invalid_argument("Use pump-primal-reopt for private MILP reoptimization");
    if(opt.integer_tolerance<=0||!std::isfinite(opt.integer_tolerance)||opt.relative_gap<0||!std::isfinite(opt.relative_gap))
        throw std::invalid_argument("Invalid MILP tolerances");
    if(opt.branching!="fractionality"&&opt.branching!="reliability")throw std::invalid_argument("MILP branching must be fractionality or reliability");
    if(opt.neighborhood!="guided"&&opt.neighborhood!="diversified"&&opt.neighborhood!="reserved")throw std::invalid_argument("MILP neighborhood must be guided, diversified or reserved");
    MilpResult out;LinearProblem p=original;auto start=std::chrono::steady_clock::now();
    using Phase=detail::MilpPhase;using WorkScope=detail::MilpWorkScope;
    detail::MilpWorkLedger work(out.work,opt.capture_work);
    auto propagate_checked=[&](const LinearProblem& model,std::vector<double>& lo,std::vector<double>& up,std::size_t& changes){
        WorkScope scope(work,Phase::presolve);return propagate(model,lo,up,changes);
    };
    if(opt.objective_lattice)out.objective_lattice=detail::detect_objective_lattice(original);
    auto validated_bound=[&](double raw,Node& node){
        double before=raw-100*opt.lp.tolerance*(1+std::abs(raw));
        node.search_bound=std::max(node.search_bound,before);
        if(!out.objective_lattice.eligible)return before;
        ++out.lattice_bound_calls;
        double after=detail::round_objective_bound(out.objective_lattice,before);
        if(after>before){
            ++out.lattice_bound_improvements;
            if(out.lattice_bound_trace.size()<4096)out.lattice_bound_trace.push_back({node.id,before,after});
        }
        return after;
    };
    for(auto& row:p.rows){std::map<std::size_t,double> a;for(auto v:row)a[v.first]+=v.second;row.clear();for(auto v:a)if(v.second!=0)row.push_back(v);}
    double sign=p.maximize?-1:1,incumbent=inf;
    auto remaining=[&](){return std::max(0.0,opt.lp.time_limit_seconds-std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());};
    auto accept=[&](std::vector<double> x) {
        WorkScope scope(work,Phase::validation);
        if(x.size()!=p.cost.size())return false;
        for(double value:x)if(!std::isfinite(value))return false;
        for(std::size_t j=0;j<x.size();++j)if(p.integer[j]) {
            if(std::abs(x[j]-std::round(x[j]))>opt.integer_tolerance)return false;
            x[j]=std::round(x[j]);
        }
        if(original_violation(original,x,false)>1e-7)return false;
        double value=sign*p.offset;for(std::size_t j=0;j<x.size();++j)value+=sign*p.cost[j]*x[j];
        if(std::isfinite(value)&&value<incumbent){
            if(out.primal.empty())out.first_incumbent_seconds=opt.lp.time_limit_seconds-remaining();
            incumbent=value;out.primal=x;out.objective=sign*value;
            out.incumbent_trace.push_back({opt.lp.time_limit_seconds-remaining(),out.objective});
        }
        return std::isfinite(value);
    };
    // The scaled copy of p is rebuilt whenever its rows change (p_version).
    std::size_t p_version=0,prepared_version=std::numeric_limits<std::size_t>::max();
    std::shared_ptr<const BoundedLpModel> prepared_p;
    auto bounded_model=[&](const LinearProblem& base){
        if(&base==&p){
            if(!prepared_p||prepared_version!=p_version){prepared_p=prepare_bounded_lp(p,opt.lp.scaling);prepared_version=p_version;++out.bounded_lp.prepared;}
            return prepared_p;
        }
        ++out.bounded_lp.prepared;return prepare_bounded_lp(base,opt.lp.scaling);
    };
    // A cutoff result proves the LP bound reaches the incumbent plus the margin
    // validated_bound later subtracts; such a node cannot hold a better point.
    auto lp_cutoff=[&](){return std::isfinite(incumbent)?incumbent+200*opt.lp.tolerance*(1+std::abs(incumbent)):inf;};
    auto relax_model=[&](const Node& node,bool heuristic,double budget,const LinearProblem& base,bool private_reopt=false) {
        const double stop=remaining()-std::min(remaining(),budget);
        if(opt.bounded_lp&&!private_reopt){
            Options o=opt.lp;o.time_limit_seconds=std::max(0.0,remaining()-stop);
            auto prepared=bounded_model(base);
            auto r=solve_bounded_lp(base,*prepared,node.lower,node.upper,o,node.basis.bounded.get(),lp_cutoff(),&out.bounded_lp);
            work.lp(r.solution.iterations);out.lp_iterations+=r.solution.iterations;
            const auto& status=r.solution.status;
            if((status=="optimal"&&r.solution.optimality_verified)||(status=="infeasible"&&r.solution.infeasibility_verified)||
               status=="cutoff"||status=="time_limit"){
                out.warm_starts+=r.warm_started;
                if(heuristic)++out.heuristic_solves;
                if(!heuristic&&node.depth==0)out.root_lp_rows=base.rows.size();
                return r;
            }
            ++out.bounded_lp_fallbacks; // Unverified: the existing engine decides this LP.
        }
        LinearProblem model=base;model.lower=node.lower;model.upper=node.upper;
        std::fill(model.integer.begin(),model.integer.end(),false);
        Options o=opt.lp;o.time_limit_seconds=std::max(0.0,remaining()-stop);
        o.primal_warm_start=private_reopt;
        o.warm_infeasibility_certificate=heuristic&&private_reopt&&opt.private_dual_certificate;
        const LpBasis* warm=node.basis.columns.empty()?nullptr:&node.basis;
        auto r=opt.reduced_bound_lp&&!heuristic?detail::solve_reduced_bound_lp(model,original,o,warm):solve_sparse_lp(model,o,warm&&warm->reduced_upper_bounds?nullptr:warm);
        out.private_certificate_attempts+=r.reopt.certificate_attempts;
        out.private_certificate_accepted+=r.reopt.certificate_accepted;
        work.lp(r.solution.iterations,opt.lp.capture_refinement?&r.refinement:nullptr);
        if(opt.reduced_bound_lp&&!heuristic){
            ++out.reduced_bound_lp_calls;out.reduced_bound_lp_fallbacks+=r.reduced_upper_fallback;
            out.reduced_bound_lp_accepted+=r.reduced_upper_accepted;out.reduced_upper_candidates+=r.reduced_upper_candidates;
        }
        if(o.compact_equalities){++out.compact_lp_calls;out.compact_lp_fallbacks+=r.compact_fallback;}
        if(!heuristic&&node.depth==0){out.root_lp_rows=r.canonical_rows;out.root_compact_equalities=r.compact_equality_rows;out.root_reduced_upper_bounds=r.reduced_upper_accepted?r.reduced_upper_candidates:0;}
        std::size_t spent_iterations=r.solution.iterations;
        const bool failed=r.solution.status=="iteration_limit"||r.solution.status=="numerical_error"||r.solution.status=="numerical_stall";
        if(!heuristic&&failed&&opt.capture_lp_failure&&out.first_lp_failure.status.empty()) {
            auto& f=out.first_lp_failure;f.status=r.solution.status;f.node=node.id;f.depth=node.depth;f.iterations=r.solution.iterations;f.parent_bound=node.bound;
            std::size_t entries=0;for(const auto& row:model.rows)entries+=row.size();
            if(entries<=200000&&model.cost.size()<=10000){f.model=model;f.input_basis=node.basis;f.captured=true;}
        }
        const bool recover=!heuristic&&failed&&opt.lp_recovery;
        const double allowance=std::max(0.0,std::min(30.0,.2*opt.lp.time_limit_seconds)-out.lp_recovery_seconds);
        const double recovery_stop=remaining()-std::max(0.0,std::min(remaining()-stop,std::min(5.0,allowance)));
        auto recovery_start=std::chrono::steady_clock::now();
        if(recover&&remaining()>recovery_stop) {
            WorkScope scope(work,Phase::lp_recovery);
            // Restart from a fresh factorization/cold Phase I, not the same
            // stalled warm basis with a silently increased iteration limit.
            ++out.lp_recovery_attempts;
            o.time_limit_seconds=std::max(0.0,std::min(2.0,remaining()-recovery_stop));
            r=solve_sparse_lp(model,o);
            work.lp(r.solution.iterations,opt.lp.capture_refinement?&r.refinement:nullptr);
            spent_iterations+=r.solution.iterations;
        }
        if((!recover&&(r.solution.status=="numerical_error"||r.solution.status=="numerical_stall"))||
           (recover&&remaining()>recovery_stop&&r.solution.status!="optimal"&&!(r.solution.status=="infeasible"&&r.solution.infeasibility_verified))) {
            WorkScope scope(work,Phase::lp_recovery);
            // Independent algorithmic recovery on small, difficult bases.
            try {
                auto standard=standardize(model,o.max_tableau_cells);o.time_limit_seconds=std::max(0.0,remaining()-(recover?recovery_stop:stop));
                auto dense=solve(standard.model,o);spent_iterations+=dense.iterations;
                work.lp(dense.iterations);
                if(dense.status=="optimal"&&dense.optimality_verified) {
                    long double dual=0;for(std::size_t i=0;i<dense.dual.size();++i)dual+=standard.model.rhs[i]*dense.dual[i];
                    r.best_bound=static_cast<double>(dual)+sign*standard.objective_offset;
                    dense.primal=standard.recover(dense.primal);dense.objective=model.offset;
                    for(std::size_t j=0;j<dense.primal.size();++j)dense.objective+=model.cost[j]*dense.primal[j];
                    r.solution=dense;r.basis={};
                } else if(dense.status=="infeasible"&&dense.infeasibility_verified){r.solution=dense;r.basis={};}
            } catch(const std::runtime_error&) { /* Preserve the original failure if recovery exceeds its resource budget. */ }
        }
        if(recover){out.lp_recovery_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-recovery_start).count();if((r.solution.status=="optimal"&&r.solution.optimality_verified)||(r.solution.status=="infeasible"&&r.solution.infeasibility_verified))++out.lp_recovery_successes;}
        out.lp_iterations+=spent_iterations;out.warm_starts+=r.warm_started;
        if(heuristic)++out.heuristic_solves;
        return r;
    };
    auto relax=[&](const Node& node,bool heuristic,double budget){return relax_model(node,heuristic,budget,p);};
    std::set<std::vector<double> > repaired_heuristic_assignments;
    auto repair_heuristic=[&](const std::vector<double>& raw,const Node& node,double stop){
        if(!opt.repair_heuristic_candidates||out.heuristic_repair_attempts>=16||raw.size()!=p.cost.size())return false;
        const double allowance=std::min(15.0,.1*opt.lp.time_limit_seconds)-out.candidate_repair_seconds;
        const double budget=std::min(2.0,std::min(remaining()-stop,allowance));
        if(budget<=.001)return false;
        std::vector<double> key;
        for(std::size_t j=0;j<raw.size();++j){
            if(!std::isfinite(raw[j]))return false;
            if(p.integer[j]){double v=std::round(raw[j]);if(std::abs(raw[j]-v)>opt.integer_tolerance||v<original.lower[j]||v>original.upper[j])return false;key.push_back(v);}
        }
        if(!repaired_heuristic_assignments.insert(key).second){++out.heuristic_repair_duplicates;return false;}
        WorkScope scope(work,Phase::repair);auto began=std::chrono::steady_clock::now();++out.heuristic_repair_attempts;
        auto repaired=detail::polish_heuristic(original,raw,opt.lp,opt.integer_tolerance,budget);
        if(repaired.sparse_called){++out.heuristic_repair_sparse_calls;++out.heuristic_solves;out.lp_iterations+=repaired.sparse_iterations;work.lp(repaired.sparse_iterations,opt.lp.capture_refinement?&repaired.refinement:nullptr);}
        if(repaired.dense_called){++out.heuristic_repair_dense_calls;++out.heuristic_solves;out.lp_iterations+=repaired.dense_iterations;work.lp(repaired.dense_iterations);}
        const bool accepted=!repaired.primal.empty()&&accept(repaired.primal);
        out.heuristic_repair_successes+=accepted;
        double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
        out.heuristic_repair_seconds+=seconds;out.candidate_repair_seconds+=seconds;
        if(opt.capture_feasibility){
            detail::FeasibilityEvent e;e.kind="heuristic_repair";e.status=repaired.status;e.node=node.id;e.call=++out.feasibility.calls;e.accepted=accepted;
            out.feasibility.record(true,original,opt.integer_tolerance,e,repaired.primal);
        }
        return accepted;
    };
    // Fix-and-propagate first-point search: fix integers one at a time
    // (policy 0: nearest-integral LP values first, rounded; 1: toward lower
    // bounds; 2: toward upper bounds), propagating after each fixing, then solve
    // the LP over the remaining continuous columns. The point still passes
    // accept(); nothing here tightens the tree or exports a bound.
    auto fix_propagate=[&](const Node& node,const std::vector<double>& x,int policy,double budget){
        if(!opt.fix_propagate||!out.primal.empty()||budget<=.001||remaining()<=0)return false;
        WorkScope scope(work,Phase::dive);
        const auto began=std::chrono::steady_clock::now();
        auto spent=[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();};
        ++out.fix_propagate_calls;
        const bool accepted=[&](){
            Node fixed=node;
            if(opt.presolve&&!propagate_checked(p,fixed.lower,fixed.upper,out.bound_tightenings))return false;
            std::vector<std::pair<double,std::size_t> > order;
            for(std::size_t j=0;j<p.cost.size();++j)if(p.integer[j]){
                const double key=policy==0&&j<x.size()&&std::isfinite(x[j])?std::abs(x[j]-std::round(x[j])):0.;
                order.push_back({key,j});
            }
            std::stable_sort(order.begin(),order.end(),[](const std::pair<double,std::size_t>& a,const std::pair<double,std::size_t>& b){return a.first<b.first;});
            std::vector<double> lo,up;
            // Bounded chronological backtracking: the last frames keep the
            // untried value and the bounds before their fixing.
            struct Frame {std::size_t index,column;double alternative;bool tried;std::vector<double> lower,upper;};
            std::vector<Frame> stack;std::size_t backtracks=0;
            auto place=[&](std::size_t j,double v){
                lo=fixed.lower;up=fixed.upper;lo[j]=up[j]=v;
                ++out.fix_propagate_fixings;
                if(opt.presolve&&!propagate_checked(p,lo,up,out.bound_tightenings))return false;
                fixed.lower.swap(lo);fixed.upper.swap(up);return true;
            };
            for(std::size_t k=0;k<order.size();){
                if((k&15)==0&&(spent()>budget||remaining()<=0))return false;
                const std::size_t j=order[k].second;
                const double lower=std::ceil(fixed.lower[j]-1e-9),upper=std::floor(fixed.upper[j]+1e-9);
                if(lower>=upper){++k;continue;}
                double first,second;
                if(policy==0){
                    const double value=j<x.size()&&std::isfinite(x[j])?x[j]:lower;
                    first=std::max(lower,std::min(upper,std::round(value)));
                    second=(value>first||(value==first&&first+1<=upper))?first+1:first-1;
                } else if(policy==1){first=std::isfinite(lower)?lower:upper;second=first+1;}
                else {first=std::isfinite(upper)?upper:lower;second=first-1;}
                auto usable=[&](double v){return std::isfinite(v)&&v>=lower&&v<=upper;};
                std::vector<double> before_lower=fixed.lower,before_upper=fixed.upper;
                bool placed=false;double alternative=std::numeric_limits<double>::quiet_NaN();
                if(usable(first)&&place(j,first)){placed=true;if(usable(second))alternative=second;}
                else if(usable(second)){fixed.lower=before_lower;fixed.upper=before_upper;placed=place(j,second);}
                if(placed){
                    if(stack.size()>=16)stack.erase(stack.begin());
                    stack.push_back({k,j,alternative,!std::isfinite(alternative),std::move(before_lower),std::move(before_upper)});
                    ++k;continue;
                }
                fixed.lower=before_lower;fixed.upper=before_upper;
                bool resumed=false;
                while(!resumed){
                    while(!stack.empty()&&stack.back().tried)stack.pop_back();
                    if(stack.empty()||++backtracks>32||spent()>budget)return false;
                    Frame& frame=stack.back();frame.tried=true;
                    fixed.lower=frame.lower;fixed.upper=frame.upper;
                    if(place(frame.column,frame.alternative)){k=frame.index+1;resumed=true;}
                }
            }
            for(std::size_t j=0;j<p.cost.size();++j)if(p.integer[j]&&fixed.lower[j]<fixed.upper[j])return false;
            const double left=std::max(0.0,std::min(remaining(),budget-spent()));
            if(left<=0)return false;
            auto r=relax_model(fixed,true,left,p);
            ++out.fix_propagate_lps;
            if(r.solution.status!="optimal"||!r.solution.optimality_verified)return false;
            return accept(r.solution.primal);
        }();
        if(accepted)++out.fix_propagate_successes;
        out.fix_propagate_seconds+=spent();
        return accepted;
    };
    std::size_t next_neighborhood_node=0,neighborhood_stalls=0;
    std::size_t next_tree_dive_node=0,tree_dive_interval=32;
    std::size_t next_fix_propagate_node=100,fix_propagate_interval=100,fix_propagate_round=0;
    double next_neighborhood_time=0;
    std::size_t guided_calls=0,strong_calls=0;
    double guided_seconds=0,last_neighborhood_value=inf,last_strong_value=inf,last_strong_time=0;
    auto improve=[&](const Node& current,const std::vector<double>& relaxation) {
        if(!opt.heuristics||!opt.improve_incumbent||out.primal.empty()||out.nodes<next_neighborhood_node||out.neighborhood_calls>=16)return;
        WorkScope scope(work,Phase::neighborhood);
        if(opt.pace_neighborhood&&opt.lp.time_limit_seconds-remaining()<next_neighborhood_time)return;
        double allowance=std::min(30.0,.15*opt.lp.time_limit_seconds)-out.neighborhood_seconds;
        const bool reserved=opt.neighborhood=="reserved";
        if(reserved&&detail::material_gain(last_neighborhood_value,incumbent))neighborhood_stalls=0;
        auto plan=detail::reserved_neighborhood_plan(opt.lp.time_limit_seconds,opt.lp.time_limit_seconds-remaining(),
            out.neighborhood_seconds,guided_seconds,guided_calls,strong_calls,neighborhood_stalls,last_strong_time,
            detail::material_gain(last_strong_value,incumbent));
        const bool strong=reserved&&plan.strong;
        const bool diversify=(opt.neighborhood=="diversified"&&neighborhood_stalls>=4)||strong;
        // Preserve productive guided sequences. Once four calls fail to improve,
        // spend a larger slice on a different subproblem, not a larger total budget.
        double budget=reserved?plan.budget:std::min(diversify?4.0:2.0,std::min(.2*remaining(),allowance));if(budget<=.001)return;
        next_neighborhood_node=out.nodes+128;
        auto began=std::chrono::steady_clock::now();const double stop=remaining()-budget;double before=incumbent;
        MilpResult::NeighborhoodSample sample;sample.node=current.id;sample.start_seconds=opt.lp.time_limit_seconds-remaining();
        // Keep cheap root-region calls from using the entire call allowance
        // before the global tree supplies materially better incumbents.
        if(opt.pace_neighborhood)next_neighborhood_time=sample.start_seconds+std::min(5.0,.02*opt.lp.time_limit_seconds);
        sample.budget=budget;sample.objective_before=sign*before;sample.stalls_before=neighborhood_stalls;sample.selection="guided";
        sample.strong=strong;
        ++out.neighborhood_calls;
        if(strong){++strong_calls;last_strong_time=sample.start_seconds;last_strong_value=before;}
        else ++guided_calls;
        // A restricted original-model search: keep continuous variables free;
        // fix most integers to the incumbent and release the largest LP disagreements.
        // Its local bounds are never exported to the global proof queue.
        std::vector<std::pair<double,std::size_t> > order;auto center=out.primal;
        for(std::size_t j=0;j<p.cost.size();++j)if(p.integer[j]&&p.lower[j]<p.upper[j]) {
            double perturb=double((j*1664525u+out.neighborhood_calls*1013904223u)%1009)/1009;
            double distance=std::abs(relaxation[j]-center[j])/(1+std::abs(center[j]));
            order.push_back({distance+.05*perturb,j});
        }
        std::sort(order.rbegin(),order.rend());
        std::size_t free_count=std::min(order.size(),std::min<std::size_t>(48,std::max<std::size_t>(8,order.size()/5)));
        if(diversify&&free_count<order.size()) {
            // After four unproductive calls, vary the restricted integer domain.
            // Some moves need lower-ranked variables that LP distance alone
            // repeatedly fixes. No instance names or reference values enter here.
            bool expand=neighborhood_stalls%2!=0;
            if(expand)free_count=std::min(order.size(),2*free_count);
            std::size_t guided=free_count*2/3;
            auto key=[&](std::size_t j) {
                std::uint64_t z=static_cast<std::uint64_t>(j)+0x9e3779b97f4a7c15ULL*out.neighborhood_calls;
                z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);
            };
            std::sort(order.begin()+guided,order.end(),[&](const std::pair<double,std::size_t>& a,const std::pair<double,std::size_t>& b){
                auto ka=key(a.second),kb=key(b.second);return ka==kb?a.second<b.second:ka>kb;
            });
            sample.selection=expand?"expanded_diverse":"diverse";
        }
        LinearProblem local_model;
        std::vector<std::size_t> binary_free;
        if(strong){
            local_model=p;sample.radius=strong_calls%2?4:8;
            binary_free=detail::binary_neighborhood(local_model,center,sample.radius);
            if(binary_free.empty()){local_model=p;sample.radius=0;}
            else sample.selection="local_branching";
        }
        const auto& search_model=binary_free.empty()?p:local_model;
        Node root=current;root.lower=search_model.lower;root.upper=search_model.upper;root.bound=-inf;
        if(binary_free.empty()){
            for(std::size_t k=free_count;k<order.size();++k){auto j=order[k].second;root.lower[j]=root.upper[j]=center[j];}
            if(opt.capture_neighborhood)for(std::size_t k=0;k<free_count;++k)sample.free_variables.push_back(order[k].second);
        } else {
            root.basis={}; // Extra private row changes basis dimensions.
            if(opt.capture_neighborhood){sample.free_variables=binary_free;if(center.size()<=10000)sample.center_primal=center;}
        }
        std::vector<Node> stack;stack.push_back(root);std::size_t explored=0;
        while(!stack.empty()&&explored<(strong?512u:(diversify?128u:64u))&&remaining()>stop) {
            Node local=std::move(stack.back());stack.pop_back();++explored;++out.neighborhood_nodes;
            if(opt.presolve&&!propagate_checked(search_model,local.lower,local.upper,out.bound_tightenings))continue;
            auto result=relax_model(local,true,std::max(0.0,remaining()-stop),search_model);
            if(result.solution.status!="optimal"||!result.solution.optimality_verified){
                if(!(result.solution.status=="infeasible"&&result.solution.infeasibility_verified)&&result.solution.status!="cutoff")++sample.lp_failures;
                continue;
            }
            if(result.best_bound-100*opt.lp.tolerance*(1+std::abs(result.best_bound))>=incumbent)continue;
            auto x=result.solution.primal;accept(x);local.basis=result.basis;
            std::size_t j=p.cost.size();double fraction=opt.integer_tolerance;
            for(std::size_t k=0;k<x.size();++k)if(p.integer[k]&&std::abs(x[k]-std::round(x[k]))>fraction){j=k;fraction=std::abs(x[k]-std::round(x[k]));}
            if(j==p.cost.size())continue;
            Node down=local,up=local;down.upper[j]=std::floor(x[j]);up.lower[j]=std::ceil(x[j]);
            // Explore the branch nearest the local LP solution first.
            if(x[j]-std::floor(x[j])<.5){stack.push_back(std::move(up));stack.push_back(std::move(down));}
            else {stack.push_back(std::move(down));stack.push_back(std::move(up));}
        }
        sample.improved=incumbent<before;
        sample.material_improved=detail::material_gain(before,incumbent);
        if(sample.improved)++out.neighborhood_improvements;
        if(reserved?sample.material_improved:sample.improved)neighborhood_stalls=0;else ++neighborhood_stalls;
        last_neighborhood_value=incumbent;
        sample.seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
        sample.nodes=explored;sample.frontier_exhausted=stack.empty();sample.objective_after=out.objective;
        out.neighborhood_seconds+=sample.seconds;
        if(!strong)guided_seconds+=sample.seconds;
        if(opt.capture_neighborhood&&out.neighborhood_trace.size()<32){
            if(sample.improved&&out.primal.size()<=10000)sample.improved_primal=out.primal;
            out.neighborhood_trace.push_back(std::move(sample));
        }
    };
    // Independently implemented L1 feasibility pump (Fischetti, Glover, Lodi).
    // These LP objectives are distances, NEVER valid objective bounds for the tree.
    auto pump=[&](const Node& node,const std::vector<double>& initial,detail::PumpDiveSeed* seed,detail::PumpPrivateBasis* private_seed) {
        WorkScope scope(work,Phase::pump);
        const std::size_t trace_call=opt.capture_feasibility?++out.feasibility.calls:0;
        auto trace=[&](const char* kind,const char* status,std::size_t step,const std::vector<double>& point,
                       const std::vector<double>& target,std::size_t iterations=0,bool accepted=false){
            if(!opt.capture_feasibility)return;
            detail::FeasibilityEvent e;e.kind=kind;e.status=status;e.node=node.id;e.call=trace_call;e.step=step;
            e.iterations=iterations;e.accepted=accepted;
            out.feasibility.record(true,original,opt.integer_tolerance,e,point,target);
        };
        trace("pump_start","start",0,initial,{});
        const double stop=std::max(0.0,remaining()-5.0);
        if(seed)seed->start(p,initial);
        const std::size_t n=p.cost.size();
        auto px=initial;
        const std::size_t no_aux=std::numeric_limits<std::size_t>::max();
        std::vector<std::size_t> integers,aux(n,no_aux);
        LinearProblem projection=p;
        projection.lower=node.lower;projection.upper=node.upper;
        projection.maximize=false;projection.offset=0;
        std::fill(projection.integer.begin(),projection.integer.end(),false);
        std::fill(projection.cost.begin(),projection.cost.end(),0);
        for(std::size_t j=0;j<n;++j)if(p.integer[j]&&node.lower[j]<node.upper[j]) {
            integers.push_back(j);
            // Keep general-integer distance columns and rows structurally stable
            // between iterations, so basis reuse remains safe when targets change.
            if(node.upper[j]-node.lower[j]>1) {
                aux[j]=projection.cost.size();
                projection.names.push_back("pump_distance_"+std::to_string(j));
                projection.cost.push_back(1);projection.lower.push_back(0);
                projection.upper.push_back(inf);projection.integer.push_back(false);
                projection.rows.push_back({{j,1},{aux[j],-1}});
                projection.rows.push_back({{j,-1},{aux[j],-1}});
                projection.row_lower.push_back(-inf);projection.row_lower.push_back(-inf);
                projection.row_upper.push_back(0);projection.row_upper.push_back(0);
            }
        }
        if(integers.empty())return;
        LpBasis basis=projection.cost.size()==n?node.basis:LpBasis{};
        std::set<std::vector<double> > visited;
        std::uint32_t rng=26119;
        auto random=[&](){rng=1664525u*rng+1013904223u;return double(rng)/4294967296.0;};
        for(int iteration=0;iteration<40&&remaining()>stop;++iteration) {
            std::vector<double> target(n,0),key;
            for(std::size_t j=0;j<n;++j)if(p.integer[j])
                target[j]=std::max(std::ceil(node.lower[j]),std::min(std::floor(node.upper[j]),std::round(px[j])));
            for(auto j:integers)key.push_back(target[j]);
            if(opt.capture_feasibility)trace("pump_round",visited.count(key)?"repeat":"new",iteration,px,target);
            if(visited.count(key)) {
                ++out.pump_restarts;
                std::vector<std::pair<double,std::size_t> > order;
                for(auto j:integers)order.push_back({std::abs(px[j]-target[j])+.35*random(),j});
                std::sort(order.rbegin(),order.rend());
                const std::size_t flips=std::min(order.size(),1+out.pump_restarts%8);
                for(std::size_t k=0;k<flips;++k) {
                    auto j=order[k].second;
                    double direction=px[j]>target[j]?1:(px[j]<target[j]?-1:(random()<.5?-1:1));
                    double value=target[j]+direction;
                    if(value<node.lower[j]||value>node.upper[j])value=target[j]-direction;
                    target[j]=std::max(std::ceil(node.lower[j]),std::min(std::floor(node.upper[j]),value));
                }
                key.clear();for(auto j:integers)key.push_back(target[j]);
            }
            if(opt.capture_feasibility)trace("pump_target",visited.count(key)?"repeat":"new",iteration,px,target);
            visited.insert(key);
            // Optimize continuous variables with exact integer fixings. Propagation
            // can reject a rounded target cheaply, but can never certify feasibility.
            Node fixed=node;
            for(std::size_t j=0;j<n;++j)if(p.integer[j])fixed.lower[j]=fixed.upper[j]=target[j];
            bool propagated=!opt.presolve||propagate_checked(p,fixed.lower,fixed.upper,out.bound_tightenings);
            trace("pump_propagation",propagated?"pass":"rejected",iteration,{},{});
            if(propagated&&remaining()>stop) {
                WorkScope scope(work,Phase::pump_fix);
                LinearProblem polished=p;polished.lower=fixed.lower;polished.upper=fixed.upper;
                std::fill(polished.integer.begin(),polished.integer.end(),false);
                Options o=opt.lp;o.tolerance=std::min(o.tolerance,1e-11);
                o.time_limit_seconds=std::max(0.0,remaining()-stop);
                auto r=solve_sparse_lp(polished,o);
                work.lp(r.solution.iterations,opt.lp.capture_refinement?&r.refinement:nullptr);
                ++out.heuristic_solves;out.lp_iterations+=r.solution.iterations;
                double previous=incumbent;
                bool accepted=accept(r.solution.primal);
                trace("pump_fix",r.solution.status.c_str(),iteration,r.solution.primal,{},r.solution.iterations,accepted);
                if(accepted) {
                    if(incumbent<previous)++out.pump_incumbents;
                    return;
                }
            }
            std::size_t row=p.rows.size();
            for(auto j:integers) {
                if(aux[j]!=no_aux) {
                    projection.row_upper[row++]=target[j];
                    projection.row_upper[row++]=-target[j];
                } else projection.cost[j]=target[j]==node.lower[j]?1:-1;
            }
            Options o=opt.lp;o.time_limit_seconds=std::max(0.0,remaining()-stop);
            o.primal_warm_start=opt.pump_primal_reopt;
            if(o.time_limit_seconds<=0)break;
            WorkScope projection_scope(work,Phase::pump_projection);
            auto r=solve_sparse_lp(projection,o,basis.columns.empty()?nullptr:&basis);
            out.pump_reopt.add(r.reopt);
            if(opt.capture_feasibility&&r.reopt.primal&&out.pump_reopt_replay.status.empty()){
                auto& replay=out.pump_reopt_replay;replay.status=r.solution.status;replay.node=node.id;replay.iterations=r.solution.iterations;
                std::size_t entries=0;for(const auto& row:projection.rows)entries+=row.size();
                if(entries<=200000&&projection.cost.size()<=10000&&projection.rows.size()<=20000){replay.model=projection;replay.input_basis=basis;replay.captured=true;}
            }
            work.lp(r.solution.iterations,opt.lp.capture_refinement?&r.refinement:nullptr);
            ++out.pump_projections;++out.heuristic_solves;out.lp_iterations+=r.solution.iterations;
            out.warm_starts+=r.warm_started;
            trace("pump_projection",r.solution.status.c_str(),iteration,r.solution.primal,{},r.solution.iterations);
            if(r.solution.status!="optimal"||!r.solution.optimality_verified)break;
            basis=r.basis;px=r.solution.primal;px.resize(n);
            if(seed){
                const bool selected=seed->consider(p,node.lower,node.upper,px,original_violation(original,px,false)<=1e-7);
                if(private_seed&&private_seed->select(selected,basis,opt.pump_distance_stage?&projection:nullptr))++out.distance_seed_updates;
            }
            double previous=incumbent;
            if(accept(px)) {if(incumbent<previous)++out.pump_incumbents;return;}
        }
    };
    struct Pseudo {double sum[2]={0,0};std::size_t count[2]={0,0};};
    std::vector<Pseudo> pseudo(p.cost.size());double pseudo_total=0;std::size_t pseudo_count=0;
    auto learn=[&](std::size_t j,bool up,double distance,double child,double parent) {
        if(distance<=opt.integer_tolerance||!std::isfinite(child)||!std::isfinite(parent))return;
        double value=std::max(0.0,child-parent)/distance;
        if(!std::isfinite(value))return;
        pseudo[j].sum[up]+=value;++pseudo[j].count[up];pseudo_total+=value;++pseudo_count;++out.pseudocost_updates;
    };
    auto choose_branch=[&](const Node& node,const std::vector<double>& x,double parent_bound) {
        WorkScope scope(work,Phase::branch_probe);
        struct Candidate {std::size_t j;double score,down,up;};std::vector<Candidate> candidates;
        const double average=pseudo_count?std::max(1e-8,pseudo_total/pseudo_count):1;
        auto score=[](double down,double up){return .9*std::min(down,up)+.1*std::max(down,up);};
        for(std::size_t j=0;j<x.size();++j)if(p.integer[j]) {
            double fraction=x[j]-std::floor(x[j]);if(std::min(fraction,1-fraction)<=opt.integer_tolerance)continue;
            double down=fraction*(pseudo[j].count[0]?pseudo[j].sum[0]/pseudo[j].count[0]:average);
            double up=(1-fraction)*(pseudo[j].count[1]?pseudo[j].sum[1]/pseudo[j].count[1]:average);
            candidates.push_back({j,score(down,up),down,up});
        }
        if(candidates.empty())return p.cost.size();
        std::sort(candidates.begin(),candidates.end(),[](const Candidate& a,const Candidate& b){return a.score==b.score?a.j<b.j:a.score>b.score;});
        // Trial LPs only inform branch selection. Their estimates NEVER replace
        // tree proof bounds, prune a branch, or manufacture an incumbent.
        double allowance=std::min(15.0,.15*opt.lp.time_limit_seconds)-out.strong_branch_seconds;
        double budget=std::max(0.0,std::min(allowance,std::min(node.depth==0?2.0:.5,.1*remaining())));
        auto begin=std::chrono::steady_clock::now();
        auto probe_left=[&](){return std::max(0.0,std::min(remaining(),budget-std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()));};
        for(std::size_t k=0;k<std::min<std::size_t>(4,candidates.size())&&probe_left()>0&&out.strong_branch_probes<128;++k) {
            auto& candidate=candidates[k];auto j=candidate.j;
            for(int side=0;side<2&&probe_left()>0&&out.strong_branch_probes<128;++side) {
                if(pseudo[j].count[side]>=2)continue;
                Node trial=node;double distance=side?std::ceil(x[j])-x[j]:x[j]-std::floor(x[j]);
                if(side)trial.lower[j]=std::ceil(x[j]);else trial.upper[j]=std::floor(x[j]);
                double gain=side?candidate.up:candidate.down;
                if(opt.presolve&&!propagate_checked(p,trial.lower,trial.upper,out.bound_tightenings))gain=1e30;
                else {
                    LinearProblem model=p;model.lower=trial.lower;model.upper=trial.upper;std::fill(model.integer.begin(),model.integer.end(),false);
                    Options o=opt.lp;o.time_limit_seconds=std::min(.5,probe_left());o.iteration_limit=std::min<std::size_t>(250,o.iteration_limit);
                    auto solved=opt.bounded_lp?solve_bounded_lp(p,*bounded_model(p),trial.lower,trial.upper,o,trial.basis.bounded.get(),inf,&out.bounded_lp)
                                              :solve_sparse_lp(model,o,trial.basis.columns.empty()?nullptr:&trial.basis);
                    work.lp(solved.solution.iterations,opt.lp.capture_refinement?&solved.refinement:nullptr);
                    ++out.strong_branch_probes;out.lp_iterations+=solved.solution.iterations;out.warm_starts+=solved.warm_started;
                    if(solved.solution.status=="optimal"&&solved.solution.optimality_verified) {
                        learn(j,side!=0,distance,solved.best_bound,parent_bound);gain=std::max(0.0,solved.best_bound-parent_bound);
                        accept(solved.solution.primal);
                    } else if(solved.solution.status=="infeasible"&&solved.solution.infeasibility_verified)gain=1e30;
                }
                if(side)candidate.up=gain;else candidate.down=gain;
            }
            candidate.score=score(candidate.down,candidate.up);
        }
        out.strong_branch_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
        return std::max_element(candidates.begin(),candidates.end(),[](const Candidate& a,const Candidate& b){return a.score==b.score?a.j>b.j:a.score<b.score;})->j;
    };
    detail::MilpFrontier<Node> queue(opt.raw_lp_priority);
    std::vector<Node> deferred;double deferred_bound=inf;
    auto frontier_event=[&](const char* operation,std::size_t id,std::size_t depth,double proof,double rank){
        if(!opt.capture_frontier)return;
        ++out.frontier_events;
        if(out.frontier_trace.size()<20000)out.frontier_trace.push_back({operation,id,depth,queue.size(),deferred.size(),proof,rank});
    };
    auto push=[&](Node node){
        auto id=node.id,depth=node.depth;double proof=node.bound,rank=node.search_bound;
        queue.push(std::move(node));out.frontier_max_queued=std::max(out.frontier_max_queued,queue.size());
        frontier_event("push",id,depth,proof,rank);
    };
    auto global_bound=[&](){return std::min(incumbent,std::min(queue.minimum_bound(),deferred_bound));};
    auto checkpoint=[&](){frontier_event("checkpoint",0,0,global_bound(),incumbent);};
    auto defer=[&](Node node){
        auto id=node.id,depth=node.depth;double proof=node.bound,rank=node.search_bound;
        deferred_bound=std::min(deferred_bound,proof);deferred.push_back(std::move(node));++out.deferred_nodes;
        frontier_event("defer",id,depth,proof,rank);
    };
    // Conservative per-node estimate: two bound vectors, the node record, the
    // bounded basis (shared by siblings) and frontier bookkeeping.
    const double open_node_bytes=sizeof(Node)+16.*p.cost.size()+.5*(p.cost.size()+p.rows.size()+64)+160;
    Node root={p.lower,p.upper,-inf,-inf,0,0,{},0,false,0,0};push(root);std::size_t serial=1;
    out.status="optimal";
    while(!queue.empty()) {
        checkpoint();
        if(remaining()<=0){out.status="time_limit";break;}
        if(out.nodes>=opt.node_limit){out.status="node_limit";break;}
        if(opt.bounded_lp&&queue.size()>=64&&queue.size()*open_node_bytes>opt.open_node_memory_mib*1048576.){
            // Fast relaxations can grow the frontier past the process budget.
            out.status="node_limit";out.message="Open-node memory guard";break;
        }
        if(std::isfinite(incumbent)&&global_bound()>=incumbent-opt.relative_gap*(1+std::abs(incumbent))){out.status="gap_limit";break;}
        if(opt.late_lifted_covers&&opt.lifted_covers&&opt.cover_cuts&&out.cut_restarts==0&&
           (opt.restart_by_nodes?out.nodes>=opt.late_cover_restart_nodes:
            (remaining()<=.5*opt.lp.time_limit_seconds||out.nodes>=opt.late_cover_restart_nodes))) {
            WorkScope scope(work,Phase::restart);
            // Restart over the ENTIRE original domain, not merely a promising
            // branch. This covers every old live/deferred node. Carry only the
            // already valid global minimum bound and original-checked incumbent.
            double global=global_bound();
            out.cut_restart_bound=sign*global;out.cut_restart_objective=out.objective;
            out.cut_restart_seconds=opt.lp.time_limit_seconds-remaining();out.cut_restart_nodes=out.nodes;
            if(out.primal.size()<=10000)out.cut_restart_primal=out.primal;
            ++out.cut_restarts;
            if(opt.late_compact_equalities)opt.lp.compact_equalities=true;
            if(opt.late_reduced_bound_lp)opt.reduced_bound_lp=true;
            frontier_event("reset",0,0,global,incumbent);
            queue.clear();deferred.clear();deferred_bound=inf;
            Node restarted=root;restarted.bound=global;restarted.id=serial++;push(std::move(restarted));
            // Global time, total nodes and all heuristic budgets remain spent.
        }
        if(queue.top().bound!=queue.minimum_bound())++out.frontier_priority_mismatches;
        Node node=queue.pop();++out.nodes;
        frontier_event("pop",node.id,node.depth,node.bound,node.search_bound);
        if(opt.binary_proof&&out.nodes==1) {
            WorkScope scope(work,Phase::binary);
            out.binary_proof_budget=std::min(5.,std::min(.1*opt.lp.time_limit_seconds,remaining()));
            ++out.binary_proof_attempts;
            out.binary_proof=detail::binary_proof(original,out.binary_proof_budget,opt.binary_proof_work);
            const auto& proof=out.binary_proof;
            if(proof.verified&&proof.completed) {
                out.message="Complete checked-integer small-binary proof for the parsed model";
                if(proof.feasible){
                    // Publish the exact witness, not a possibly lower, tolerance-
                    // feasible incumbent inherited from a floating-point method.
                    out.primal.assign(proof.primal.begin(),proof.primal.end());
                    out.objective=sign*static_cast<double>(proof.objective_minimization);
                    out.best_bound=out.objective;out.gap=0;out.status="optimal";
                    out.first_incumbent_seconds=opt.lp.time_limit_seconds-remaining();
                    out.incumbent_trace.push_back({out.first_incumbent_seconds,out.objective});
                } else {out.status="infeasible";out.best_bound=sign*inf;}
                work.finish();return out;
            }
            if(proof.feasible)accept(std::vector<double>(proof.primal.begin(),proof.primal.end()));
        }
        if(node.bound>=incumbent)continue;
        if(opt.presolve&&!propagate_checked(p,node.lower,node.upper,out.bound_tightenings))continue;
        SparseLpResult lp;
        const auto root_work_before=out.lp_iterations;
        {WorkScope scope(work,node.depth==0?Phase::root_lp:Phase::tree_lp);lp=relax(node,false,remaining());}
        const auto root_iterations=out.lp_iterations-root_work_before;
        if(lp.solution.status=="cutoff"){++out.bounded_lp_cutoff_nodes;continue;}
        if(lp.solution.status=="infeasible"&&lp.solution.infeasibility_verified)continue;
        if(lp.solution.status!="optimal"||!lp.solution.optimality_verified) {
            if(opt.lp_recovery&&remaining()>0&&lp.solution.status!="unbounded") {
                defer(std::move(node));continue;
            }
            push(node);out.status=lp.solution.status=="unbounded"?"unbounded_relaxation":lp.solution.status;
            out.message="LP relaxation did not pass its numerical checks";break;
        }
        if(opt.branching=="reliability"&&node.depth>0)learn(node.parent_variable,node.branch_up,node.branch_distance,lp.best_bound,node.parent_lp_bound);
        node.basis=lp.basis;node.bound=std::max(node.bound,validated_bound(lp.best_bound,node));
        if(node.depth==0)out.root_bound_before_cuts=sign*node.bound;
        if(node.depth==0&&opt.cover_cuts) {
            // Reserve a full pump allowance. Repeated root cut solves must not
            // shrink the first-incumbent search to a fraction of the last second.
            const double cut_stop=opt.heuristics&&opt.feasibility_pump?std::min(5.0,remaining()):0;
            for(std::size_t pass=0;pass<opt.root_cut_rounds&&remaining()>cut_stop;++pass) {
                WorkScope scope(work,Phase::cut_separation);
                const std::size_t old_rows=p.rows.size();
                const auto old_trace=out.lifted_cover_trace.size();
                std::size_t added=0;
                if(opt.lifted_covers&&(!opt.late_lifted_covers||out.cut_restarts)){
                    double budget=std::max(0.,std::min(2.,std::min(remaining()-cut_stop,std::min(5.,.05*opt.lp.time_limit_seconds)-out.lifted_cover_seconds)));
                    detail::CoverSeparation separated;
                    try {separated=detail::separate_lifted_covers(p,lp.solution.primal,original.rows.size(),budget);}
                    catch(const std::bad_alloc&) { /* Optional separator: retain the original model and ordinary cover fallback. */ }
                    out.lifted_cover_seconds+=separated.seconds;out.lifted_cover_states+=separated.states;out.lifted_cover_checked+=separated.checked;
                    for(const auto& cut:separated.cuts){p.rows.push_back(cut.row);p.row_lower.push_back(-inf);p.row_upper.push_back(cut.rhs);out.lifted_cover_trace.push_back(cut);++added;}
                }
                if(!added)added=add_covers(p,lp.solution.primal);
                out.cuts+=added;if(!added)break;
                ++p_version;
                auto previous=lp;
                const auto round_work_before=out.lp_iterations;
                const double before_cut_bound=lp.best_bound;
                {LpBasis kept;kept.bounded=node.basis.bounded;node.basis=kept;} // Bounded bases extend to the new rows.
                {WorkScope scope(work,Phase::cut_lp);lp=relax(node,false,std::max(0.0,remaining()-cut_stop));}
                const auto round_iterations=out.lp_iterations-round_work_before;
                auto record_round=[&](const char* decision){
                    if(opt.capture_cut_rounds||opt.adaptive_cut_rounds)
                        out.cut_round_trace.push_back({node.id,out.cut_restarts,pass+1,root_iterations,round_iterations,before_cut_bound,lp.best_bound,sign*original.offset,decision,out.objective});
                };
                if(lp.solution.status=="cutoff"){record_round("cutoff");break;}
                if(lp.solution.status=="infeasible"&&lp.solution.infeasibility_verified&&out.primal.empty()){record_round("infeasible");break;}
                if(lp.solution.status!="optimal"||!lp.solution.optimality_verified) {
                    record_round("rollback");
                    // A cut attempt is optional. If its LP misses the budget/checks,
                    // restore both model and validated pre-cut basis/relaxation.
                    p.rows.resize(old_rows);p.row_lower.resize(old_rows);p.row_upper.resize(old_rows);++p_version;
                    out.lifted_cover_trace.resize(old_trace);
                    out.cuts-=added;++out.cut_rollbacks;lp=std::move(previous);node.basis=lp.basis;
                    break;
                }
                // Only accept() can supply a finite incumbent here. Allocation
                // never imports a point or uses the cut relaxation as an incumbent.
                const char* decision=detail::guarded_cut_continuation(opt.adaptive_cut_rounds,opt.cut_after_incumbent,
                    std::isfinite(incumbent),pass+1,opt.root_cut_rounds,root_iterations,round_iterations,
                    before_cut_bound,lp.best_bound,sign*original.offset);
                record_round(decision);
                if(std::string(decision)=="diminishing_return"){++out.adaptive_cut_stops;break;}
            }
            if(lp.solution.status=="cutoff"){++out.bounded_lp_cutoff_nodes;continue;}
            if(lp.solution.status=="infeasible"&&lp.solution.infeasibility_verified)continue;
            if(lp.solution.status!="optimal"||!lp.solution.optimality_verified){push(node);out.status=lp.solution.status;break;}
        }
        node.basis=lp.basis;node.bound=std::max(node.bound,validated_bound(lp.best_bound,node));
        if(node.depth==0)out.root_bound_after_cuts=sign*node.bound;
        if(node.bound>=incumbent)continue;
        auto x=lp.solution.primal;accept(x);
        if(opt.heuristics&&opt.binary_meet&&out.nodes==1&&remaining()>0) {
            WorkScope scope(work,Phase::binary);
            // The structural detector and private range search never contribute
            // a proof bound. Even a completed enumeration exports only a point.
            out.binary_meet_budget=std::min(5.,std::min(.05*opt.lp.time_limit_seconds,.1*remaining()));
            ++out.binary_meet_attempts;const double before=incumbent;
            auto meet=detail::binary_meet(original,out.binary_meet_budget,incumbent);
            out.binary_meet_eligible=meet.eligible;out.binary_meet_completed=meet.completed;
            out.binary_meet_seconds=meet.seconds;out.binary_meet_left_states=meet.left_states;
            out.binary_meet_right_states=meet.right_states;out.binary_meet_query_nodes=meet.query_nodes;
            accept(meet.primal);out.binary_meet_improved=incumbent<before;
            if(out.binary_meet_improved)out.binary_meet_primal=out.primal;
        }
        if(opt.heuristics&&opt.fix_propagate&&out.primal.empty()&&(node.depth==0||out.nodes>=next_fix_propagate_node)){
            // A bounded share of time; the root tries all three value policies,
            // and repeated failures in the tree back off geometrically.
            const bool root=node.depth==0;
            const double share=root?std::min(3.0,.1*remaining()):std::min(.5,.02*remaining());
            bool found=false;
            for(int policy=0;policy<(root?3:1)&&!found;++policy)
                found=fix_propagate(node,x,root?policy:static_cast<int>(fix_propagate_round%3),share/(root?3:1));
            if(!root){
                ++fix_propagate_round;
                fix_propagate_interval=found?100:std::min<std::size_t>(6400,2*fix_propagate_interval);
                next_fix_propagate_node=out.nodes+fix_propagate_interval;
            }
        }
        detail::PumpDiveSeed pump_seed;
        detail::PumpPrivateBasis pump_private_seed;
        std::size_t seed_record=std::numeric_limits<std::size_t>::max();
        if(opt.heuristics&&opt.feasibility_pump&&node.depth==0&&out.primal.empty()) {
            pump(node,x,opt.pump_guided_diving?&pump_seed:nullptr,opt.pump_distance_reopt?&pump_private_seed:nullptr);
            if(opt.pump_guided_diving){
                auto& g=out.pump_guidance;++g.calls;g.candidates+=pump_seed.candidates;
                g.rejected+=pump_seed.rejected;g.improvements+=pump_seed.improvements;
                if(g.samples.size()<8){
                    detail::PumpGuidanceSample s;s.node=node.id;s.candidates=pump_seed.candidates;
                    s.rejected=pump_seed.rejected;s.improvements=pump_seed.improvements;
                    s.initial_distance=pump_seed.initial_distance;s.best_distance=pump_seed.best_distance;s.selected=!pump_seed.point.empty();
                    if(opt.capture_feasibility&&s.selected&&x.size()<=10000&&g.stored_values+2*x.size()<=20000){
                        s.initial=x;s.point=pump_seed.point;g.stored_values+=s.initial.size()+s.point.size();
                    }
                    seed_record=g.samples.size();g.samples.push_back(std::move(s));
                }
            }
        }
        // Periodic tree dives after the first incumbent: at most about a tenth of
        // elapsed time, spaced adaptively, with an extra incumbent-guided mode.
        const bool tree_dive=opt.tree_dives&&opt.heuristics&&out.nodes>1&&!out.primal.empty()&&out.nodes>=next_tree_dive_node&&
            out.tree_dive_seconds<=.1*(opt.lp.time_limit_seconds-remaining())+.05;
        if(opt.heuristics&&(out.nodes==1||(out.primal.empty()&&out.nodes%100==0)||tree_dive)) {
            WorkScope scope(work,Phase::dive);
            const auto dive_began=std::chrono::steady_clock::now();const double dive_before=incumbent;
            const std::size_t trace_call=opt.capture_feasibility?++out.feasibility.calls:0;
            auto trace=[&](const char* kind,const char* status,std::size_t step,int mode,std::size_t variable,
                           bool alternate,const std::vector<double>& point,std::size_t iterations=0,bool accepted=false){
                if(!opt.capture_feasibility)return;
                detail::FeasibilityEvent e;e.kind=kind;e.status=status;e.node=node.id;e.call=trace_call;e.step=step;e.mode=mode;
                e.variable=variable;e.alternate=alternate;e.iterations=iterations;e.accepted=accepted;
                out.feasibility.record(true,original,opt.integer_tolerance,e,point);
            };
            double budget=tree_dive?std::min(1.0,remaining()*.05):std::min(2.0,remaining()*.2),until=remaining()-budget;
            // Mode 2 (tree dives only) rounds toward the current incumbent.
            const int dive_modes=tree_dive?3:2;const std::size_t dive_steps=tree_dive?256:64;
            for(int mode=0;mode<dive_modes&&remaining()>until;++mode) {
                const bool guided=mode==0&&!pump_seed.point.empty()&&out.primal.empty();
                if(guided&&opt.pump_distance_diving&&!opt.presolve){
                    // Without presolve a valid input can have an empty integer
                    // interval. Skip this private heuristic, not the global node;
                    // the existing original-model tree still decides infeasibility.
                    bool empty=false;
                    for(std::size_t j=0;j<p.cost.size();++j)if(p.integer[j]&&std::ceil(node.lower[j])>std::floor(node.upper[j])){empty=true;break;}
                    if(empty)continue;
                }
                // Keep the original-objective root basis; projection bases can have auxiliary columns.
                Node dive=node;auto dx=guided?pump_seed.point:x;
                if(guided){++out.pump_guidance.dives;if(seed_record<out.pump_guidance.samples.size())out.pump_guidance.samples[seed_record].used=true;}
                const bool distance_guided=guided&&opt.pump_distance_diving;
                detail::PumpDistanceModel distance_model;LpBasis distance_basis;
                bool stage_ready=false;
                detail::PumpDistanceSample distance_sample;distance_sample.node=node.id;
                if(distance_guided){
                    // Construction is inside the unchanged shared two-second dive slice.
                    // An offered private basis is not presumed compatible: the LP
                    // reoptimizer checks exact canonical rows/mapping and feasibility.
                    distance_model.start(p,node.lower,node.upper,pump_seed.point);
                    if(opt.pump_distance_reopt)distance_basis=pump_private_seed.basis;
                    distance_sample.auxiliaries=distance_model.auxiliaries;
                    distance_sample.initial_distance=detail::integer_distance(p,dx);
                    ++out.pump_distance.dives;
                }
                trace("dive_start",distance_guided?"pump_distance":guided?"pump_guided":"start",0,mode,0,false,dx);
                auto capture_private=[&](MilpLpFailure& replay,const LinearProblem& model,const LpBasis& input,const SparseLpResult& r){
                    if(!opt.capture_feasibility||!replay.status.empty())return;
                    replay.status=r.solution.status;replay.node=node.id;replay.iterations=r.solution.iterations;
                    std::size_t entries=0;for(const auto& row:model.rows)entries+=row.size();
                    if(entries<=200000&&model.cost.size()<=10000&&model.rows.size()<=20000){
                        replay.model=model;replay.input_basis=input;replay.captured=true;
                    }
                };
                if(distance_guided&&opt.pump_distance_stage){
                    auto began=std::chrono::steady_clock::now();auto& stats=out.distance_stage;
                    detail::DistanceStageSample sample;sample.node=node.id;sample.available_seconds=std::max(0.0,remaining()-until);
                    ++stats.considered;sample.eligible=pump_private_seed.same_parent_domain(distance_model.model);
                    stats.eligible+=sample.eligible;
                    if(sample.eligible&&remaining()>until){
                        sample.attempted=true;++stats.attempts;
                        Node parent=node;parent.lower=distance_model.model.lower;parent.upper=distance_model.model.upper;parent.basis=distance_basis;
                        auto staged=relax_model(parent,true,std::max(0.0,remaining()-until),distance_model.model,true);
                        stats.reopt.add(staged.reopt);sample.iterations=staged.solution.iterations;sample.status=staged.solution.status;
                        capture_private(out.distance_stage_replay,distance_model.model,distance_basis,staged);
                        if(staged.solution.status=="optimal"&&staged.solution.optimality_verified&&staged.solution.primal.size()==distance_model.model.cost.size()){
                            auto point=staged.solution.primal;point.resize(p.cost.size());
                            // A checked private optimum is still only a heuristic point.
                            const bool finite=std::all_of(staged.solution.primal.begin(),staged.solution.primal.end(),[](double v){return std::isfinite(v);});
                            if(finite&&original_violation(distance_model.model,staged.solution.primal,false)<=1e-7&&original_violation(original,point,false)<=1e-7&&original_violation(p,point,false)<=1e-7){
                                sample.verified=true;++stats.verified;stage_ready=true;
                                distance_basis=staged.basis;dx=std::move(point);
                                sample.accepted=accept(dx);stats.incumbents+=sample.accepted;
                            }else sample.status="point_rejected";
                        }
                        trace("distance_stage",sample.status.c_str(),0,mode,0,false,sample.verified?dx:std::vector<double>{},sample.iterations,sample.accepted);
                    }else if(sample.eligible)sample.status="budget";
                    sample.seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
                    if(stats.samples.size()<8)stats.samples.push_back(std::move(sample));
                    // Failed staging leaves the seed point/basis intact. Any
                    // remaining branch work spends ONLY the original shared slice.
                }
                for(std::size_t step=0;step<dive_steps&&remaining()>until;++step) {
                    std::size_t branch=p.cost.size();double fraction=opt.integer_tolerance;
                    if(mode==2){
                        // Closest fractional coordinate to the incumbent; larger fractionality breaks ties.
                        double closest=inf;
                        for(std::size_t j=0;j<dx.size();++j)if(p.integer[j]){
                            const double f=std::abs(dx[j]-std::round(dx[j]));if(f<=opt.integer_tolerance)continue;
                            const double gapj=std::abs(dx[j]-out.primal[j]);
                            if(gapj<closest||(gapj==closest&&f>fraction)){closest=gapj;fraction=f;branch=j;}
                        }
                    }else if(distance_guided&&opt.pump_distance_stable_ranking){
                        const auto choice=detail::private_dive_choice(p.integer,dx,opt.integer_tolerance);
                        branch=choice.column;++out.private_ranking_calls;
                        out.private_ranking_ties+=choice.ties>1;
                        out.private_ranking_changes+=choice.column!=choice.strict_column;
                    }else for(std::size_t j=0;j<dx.size();++j)if(p.integer[j]&&std::abs(dx[j]-std::round(dx[j]))>fraction) {
                        branch=j;fraction=std::abs(dx[j]-std::round(dx[j]));
                    }
                    if(branch==p.cost.size()){if(!accept(dx))repair_heuristic(dx,dive,until);break;}
                    bool up=mode==2?out.primal[branch]>dx[branch]:(mode?sign*p.cost[branch]<0:dx[branch]-std::floor(dx[branch])>=.5);
                    if(guided){
                        up=detail::pump_target_up(dx[branch],pump_seed.point[branch],dive.lower[branch],dive.upper[branch],up);
                        ++out.pump_guidance.steps;if(seed_record<out.pump_guidance.samples.size())++out.pump_guidance.samples[seed_record].steps;
                    }
                    Node alternate=dive;
                    if(up){dive.lower[branch]=std::ceil(dx[branch]);alternate.upper[branch]=std::floor(dx[branch]);}
                    else {dive.upper[branch]=std::floor(dx[branch]);alternate.lower[branch]=std::ceil(dx[branch]);}
                    bool alternate_attempt=false;
                    auto attempt=[&](Node& d){
                        if(remaining()<=until||(opt.presolve&&!propagate_checked(p,d.lower,d.upper,out.bound_tightenings))){
                            trace("dive_trial",remaining()<=until?"budget":"propagation_rejected",step,mode,branch,alternate_attempt,{});
                            SparseLpResult bad;bad.solution.status="infeasible";return bad;
                        }
                        SparseLpResult trial;
                        if(distance_guided){
                            Node private_node=d;private_node.basis=distance_basis;
                            private_node.lower.resize(distance_model.model.cost.size(),0);
                            private_node.upper.resize(distance_model.model.cost.size(),INFINITY);
                            const bool first_offer=opt.pump_distance_reopt&&distance_sample.verified_points==0&&!private_node.basis.columns.empty();
                            const bool seed_offer=first_offer&&!stage_ready;
                            double available=std::max(0.0,remaining()-until);
                            if(opt.pump_distance_alternate_reserve){
                                if(alternate_attempt)++out.private_reserve_alternate;
                                else {available*=.5;++out.private_reserve_primary;}
                            }
                            const auto private_work_before=out.lp_iterations;
                            auto private_start=opt.capture_private_dive?std::chrono::steady_clock::now():std::chrono::steady_clock::time_point{};
                            trial=relax_model(private_node,true,available,distance_model.model,opt.pump_distance_reopt);
                            const double private_seconds=opt.capture_private_dive?std::chrono::duration<double>(std::chrono::steady_clock::now()-private_start).count():0;
                            if(opt.capture_private_dive){
                                auto capture=[&](PrivateDiveReplay& f){
                                    if(!f.lp.status.empty())return;
                                    f.step=step;f.branch=branch;f.total_iterations=out.lp_iterations-private_work_before;f.alternate=alternate_attempt;f.available_seconds=available;f.seconds=private_seconds;f.reopt=trial.reopt;
                                    f.lp.status=trial.solution.status;f.lp.node=node.id;f.lp.depth=node.depth;f.lp.iterations=trial.solution.iterations;
                                    std::size_t entries=0;for(const auto& row:distance_model.model.rows)entries+=row.size();
                                    if(entries<=200000&&distance_model.model.cost.size()<=10000&&distance_model.model.rows.size()<=20000){
                                        f.lp.model=distance_model.model;f.lp.model.lower=private_node.lower;f.lp.model.upper=private_node.upper;
                                        f.lp.input_basis=private_node.basis;f.lp.captured=true;
                                    }
                                };
                                if(out.lp_iterations-private_work_before>=256)capture(out.private_dive_expensive);
                                const auto& expensive=out.private_dive_expensive;
                                const bool duplicate=!expensive.lp.status.empty()&&expensive.lp.node==node.id&&expensive.step==step&&expensive.branch==branch&&expensive.alternate==alternate_attempt;
                                if(!duplicate&&(trial.solution.status!="optimal"||!trial.solution.optimality_verified))capture(out.private_dive_failed);
                            }
                            out.distance_reopt.add(trial.reopt);
                            if(first_offer&&stage_ready){
                                auto& stats=out.distance_stage;++stats.child_offers;
                                stats.child_compatible+=trial.reopt.compatible>0;stats.child_verified+=trial.reopt.verified>0;
                                if(opt.capture_feasibility&&out.distance_stage_child_replay.status.empty()){
                                    auto model=distance_model.model;model.lower=private_node.lower;model.upper=private_node.upper;
                                    capture_private(out.distance_stage_child_replay,model,private_node.basis,trial);
                                }
                            }
                            if(seed_offer){
                                ++out.distance_seed_offers;
                                out.distance_seed_compatible+=trial.reopt.compatible>0;
                                out.distance_seed_verified+=trial.reopt.verified>0;
                                if(opt.capture_feasibility&&out.distance_reopt_replay.status.empty()){
                                    auto& replay=out.distance_reopt_replay;replay.status=trial.solution.status;
                                    replay.node=node.id;replay.iterations=trial.solution.iterations;
                                    std::size_t entries=0;for(const auto& row:distance_model.model.rows)entries+=row.size();
                                    if(entries<=200000&&distance_model.model.cost.size()<=10000&&distance_model.model.rows.size()<=20000){
                                        replay.model=distance_model.model;replay.model.lower=private_node.lower;replay.model.upper=private_node.upper;
                                        replay.input_basis=private_node.basis;replay.captured=true;
                                    }
                                }
                            }
                            ++distance_sample.lp_calls;++out.pump_distance.lp_calls;
                            distance_sample.warm_starts+=trial.warm_started;out.pump_distance.warm_starts+=trial.warm_started;
                            if(trial.solution.status=="optimal"&&trial.solution.primal.size()!=distance_model.model.cost.size()){
                                trial.solution.status="numerical_error";trial.solution.optimality_verified=false;
                            }
                            // Only a successful private LP may advance its private basis.
                            // A failed primary branch leaves the parent's basis for the alternate.
                            if(trial.solution.status=="optimal"&&trial.solution.optimality_verified){
                                distance_basis=trial.basis;
                            }
                            if(trial.solution.primal.size()==distance_model.model.cost.size())trial.solution.primal.resize(p.cost.size());
                            else trial.solution.primal.clear();
                            // Explicit point-only boundary: never export distance bounds,
                            // certificates, auxiliary vectors, or bases to the original tree.
                            trial.best_bound=-inf;trial.solution.objective=NAN;trial.solution.infeasibility_verified=false;
                            trial.solution.dual.clear();trial.solution.unbounded_ray.clear();trial.solution.unboundedness_verified=false;
                            trial.basis={};trial.canonical_primal.clear();trial.canonical_dual.clear();trial.row_dual.clear();
                        } else trial=relax(d,true,std::max(0.0,remaining()-until));
                        trace("dive_trial",trial.solution.status.c_str(),step,mode,branch,alternate_attempt,trial.solution.primal,trial.solution.iterations);
                        return trial;
                    };
                    auto trial=attempt(dive);
                    if(trial.solution.status!="optimal"){dive=alternate;alternate_attempt=true;trial=attempt(dive);}
                    if(trial.solution.status!="optimal"||!trial.solution.optimality_verified)break;
                    dive.basis=trial.basis;dx=trial.solution.primal;bool accepted=accept(dx);
                    if(distance_guided){
                        ++distance_sample.verified_points;++out.pump_distance.verified_points;
                        distance_sample.last_distance=detail::integer_distance(p,dx);
                        distance_sample.last_target_distance=distance_model.distance(p,dx);
                        if(distance_sample.verified_points==1){distance_sample.first_distance=distance_sample.last_distance;distance_sample.first_target_distance=distance_sample.last_target_distance;}
                    }
                    trace("dive_point","accepted_candidate",step,mode,branch,alternate_attempt,dx,0,accepted);
                    if(!accepted)repair_heuristic(dx,dive,until);
                }
                if(distance_guided&&out.pump_distance.samples.size()<8)out.pump_distance.samples.push_back(distance_sample);
            }
            if(tree_dive){
                ++out.tree_dive_calls;
                const bool improved=incumbent<dive_before;out.tree_dive_improvements+=improved;
                out.tree_dive_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-dive_began).count();
                tree_dive_interval=improved?std::max<std::size_t>(16,tree_dive_interval/2):std::min<std::size_t>(1024,2*tree_dive_interval);
                next_tree_dive_node=out.nodes+tree_dive_interval;
            }
        }
        improve(node,x);
        std::size_t branch=p.cost.size();double score=opt.integer_tolerance;
        for(std::size_t j=0;j<x.size();++j)if(p.integer[j]) {
            double fractional=std::abs(x[j]-std::round(x[j]));
            if(fractional>score){score=fractional;branch=j;}
        }
        if(branch!=p.cost.size()&&opt.branching=="reliability")branch=choose_branch(node,x,lp.best_bound);
        if(branch==p.cost.size()) {
            if(!accept(x)) {
                WorkScope scope(work,Phase::repair);
                ++out.rejected_integer_candidates;
                LinearProblem fixed=original;
                for(std::size_t j=0;j<x.size();++j)if(p.integer[j])fixed.lower[j]=fixed.upper[j]=std::round(x[j]);
                std::fill(fixed.integer.begin(),fixed.integer.end(),false);
                Options polish_options=opt.lp;polish_options.tolerance=std::min(1e-11,opt.lp.tolerance);polish_options.time_limit_seconds=remaining();
                auto polished=solve_sparse_lp(fixed,polish_options);out.lp_iterations+=polished.solution.iterations;++out.heuristic_solves;
                work.lp(polished.solution.iterations,opt.lp.capture_refinement?&polished.refinement:nullptr);
                bool repaired=polished.solution.status=="optimal"&&accept(polished.solution.primal);
                std::vector<double> fallback_primal;std::string fallback_status;bool fallback_accepted=false;
                double repair_allowance=std::min(15.0,.1*opt.lp.time_limit_seconds)-out.candidate_repair_seconds;
                double repair_budget=std::min(2.0,std::min(.2*remaining(),repair_allowance));
                if(!repaired&&opt.repair_candidates&&repair_budget>.001) {
                    ++out.candidate_repair_attempts;auto began=std::chrono::steady_clock::now();
                    const double stop=remaining()-repair_budget;
                    try {
                        auto standard=standardize(fixed,opt.lp.max_tableau_cells);
                        Options options=polish_options;options.time_limit_seconds=std::max(0.0,remaining()-stop);
                        auto dense=solve(standard.model,options);out.lp_iterations+=dense.iterations;
                        work.lp(dense.iterations);
                        fallback_status=dense.status;
                        if(dense.status=="optimal"&&dense.optimality_verified) {
                            fallback_primal=standard.recover(dense.primal);
                            // Feasibility is checked again on the ORIGINAL MILP.
                            // No dense fixing-LP bound can prune the whole node.
                            fallback_accepted=accept(fallback_primal);repaired=fallback_accepted;
                            if(repaired)++out.candidate_repair_successes;
                        }
                    } catch(const std::runtime_error&) {fallback_status="resource_or_numerical_error";}
                    out.candidate_repair_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
                }
                if(opt.capture_rejected_candidates&&out.rejected_candidates.size()<4) {
                    MilpResult::RejectedCandidate sample;auto& f=sample.fixing;
                    f.status=polished.solution.status;f.node=node.id;f.depth=node.depth;f.iterations=polished.solution.iterations;f.parent_bound=node.bound;
                    std::size_t entries=0;for(const auto& row:fixed.rows)entries+=row.size();
                    if(entries<=200000&&fixed.cost.size()<=10000) {
                        f.captured=true;f.model=fixed;sample.relaxation=x;sample.rounded=x;
                        for(std::size_t j=0;j<x.size();++j)if(p.integer[j])sample.rounded[j]=std::round(x[j]);
                        sample.repair_primal=polished.solution.primal;sample.node_lower=node.lower;sample.node_upper=node.upper;
                        sample.relaxation_violation=original_violation(original,x,false);sample.rounded_violation=original_violation(original,sample.rounded,false);
                        sample.repair_violation=sample.repair_primal.size()==x.size()?original_violation(original,sample.repair_primal,false):inf;
                    }
                    sample.repair_infeasibility_verified=polished.solution.infeasibility_verified;sample.repair_optimality_verified=polished.solution.optimality_verified;
                    sample.repair_accepted=repaired&&!fallback_accepted;sample.fallback_primal=fallback_primal;sample.fallback_status=fallback_status;sample.fallback_accepted=fallback_accepted;
                    out.rejected_candidates.push_back(std::move(sample));
                }
                if(repaired||opt.repair_candidates) {
                    // A tiny integer displacement can have a large objective
                    // effect. Repair supplies an incumbent, NOT proof for the
                    // whole node. Branch even below the acceptance tolerance
                    // when both integer-domain children strictly tighten bounds.
                    double tiny=0;
                    for(std::size_t j=0;j<x.size();++j)if(p.integer[j]) {
                        double delta=std::abs(x[j]-std::round(x[j]));
                        if(delta>tiny&&std::floor(x[j])>=node.lower[j]&&std::ceil(x[j])<=node.upper[j]&&
                           std::floor(x[j])<node.upper[j]&&std::ceil(x[j])>node.lower[j]){tiny=delta;branch=j;}
                    }
                    if(branch!=p.cost.size())++out.repair_branch_nodes;
                }
                if(branch==p.cost.size()&&(opt.lp_recovery||opt.repair_candidates||repaired)&&remaining()>0) {
                    // Almost integral is not feasible. Keep this node's checked
                    // relaxation bound unresolved, just as for an LP failure;
                    // do not let a failed repair abort all other tree work.
                    defer(std::move(node));continue;
                }
                if(branch==p.cost.size()) {
                    for(std::size_t j=0;j<x.size();++j)if(p.integer[j])x[j]=std::round(x[j]);
                    push(node);out.status=remaining()<=0?"time_limit":"numerical_error";
                    out.message="Rounded integer candidate violation "+std::to_string(original_violation(original,x,false));break;
                }
            }
            if(branch==p.cost.size())continue;
        }
        Node down=node,up=node;down.upper[branch]=std::floor(x[branch]);up.lower[branch]=std::ceil(x[branch]);
        down.parent_variable=up.parent_variable=branch;down.branch_up=false;up.branch_up=true;
        down.parent_lp_bound=up.parent_lp_bound=lp.best_bound;
        down.branch_distance=x[branch]-std::floor(x[branch]);up.branch_distance=std::ceil(x[branch])-x[branch];
        down.depth=up.depth=node.depth+1;down.id=serial++;up.id=serial++;
        if(down.lower[branch]<=down.upper[branch])push(std::move(down));
        if(up.lower[branch]<=up.upper[branch])push(std::move(up));
    }
    checkpoint();
    for(const auto& node:deferred)if(node.bound<incumbent)++out.unresolved_nodes;
    if(queue.empty()&&out.unresolved_nodes==0) {
        if(out.primal.empty())out.status="infeasible";
        out.best_bound=out.primal.empty()?sign*inf:out.objective;out.gap=out.primal.empty()?inf:0;
    } else {
        double bound=global_bound();out.best_bound=sign*bound;
        if(std::isfinite(incumbent)&&std::isfinite(bound))out.gap=std::max(0.0,incumbent-bound)/(1+std::abs(incumbent));
        if(queue.empty()){out.status=out.gap<=opt.relative_gap?"gap_limit":"unresolved_relaxations";out.message="Unresolved LP nodes retained in the global bound";}
    }
    work.finish();return out;
}
}
