#include "sparse_lp.hpp"
#include "dual_certificate.hpp"
#include <chrono>
#include <numeric>

namespace sovereign {
namespace {
const double inf=std::numeric_limits<double>::infinity();
struct Canonical {
    std::vector<SparseVector> columns, rows, mapping;
    std::vector<double> cost, rhs, shift, scale;
    std::vector<std::pair<std::size_t,double> > origin;
    std::vector<bool> equality;
    double cost_scale=1, sign=1, offset=0;
};
Canonical canonicalize(const LinearProblem& p, bool scaling,bool compact) {
    Canonical s;s.sign=p.maximize?-1:1;s.offset=s.sign*p.offset;
    s.shift.resize(p.cost.size());s.mapping.resize(p.cost.size());
    for(std::size_t j=0;j<p.cost.size();++j) {
        if(p.integer[j]) throw std::invalid_argument("Integer model requires --milp");
        double sign=std::isfinite(p.lower[j])?1:-1;
        s.shift[j]=std::isfinite(p.lower[j])?p.lower[j]:(std::isfinite(p.upper[j])?p.upper[j]:0);
        s.mapping[j].push_back({s.cost.size(),sign});s.cost.push_back(s.sign*p.cost[j]*sign);
        if(!std::isfinite(p.lower[j])&&!std::isfinite(p.upper[j])) {
            s.mapping[j].push_back({s.cost.size(),1});s.cost.push_back(s.sign*p.cost[j]);
        }
        s.offset+=s.sign*p.cost[j]*s.shift[j];
    }
    auto add=[&](SparseVector row,double rhs,std::size_t original,double direction,bool equality) {
        double scale=0;for(auto a:row)scale=std::max(scale,std::abs(a.second));
        if(!scaling||scale==0)scale=1;
        for(auto& a:row)a.second/=scale;
        s.rows.push_back(std::move(row));s.rhs.push_back(rhs/scale);s.scale.push_back(scale);
        s.origin.push_back({original,direction});
        s.equality.push_back(equality);
    };
    for(std::size_t i=0;i<p.rows.size();++i) {
        std::map<std::size_t,double> aggregate;long double shift=0;
        for(auto a:p.rows[i]) {
            shift+=static_cast<long double>(a.second)*s.shift[a.first];
            for(auto term:s.mapping[a.first])aggregate[term.first]+=a.second*term.second;
        }
        SparseVector row;for(auto a:aggregate)if(a.second!=0)row.push_back(a);
        bool equality=compact&&std::isfinite(p.row_upper[i])&&p.row_lower[i]==p.row_upper[i];
        if(std::isfinite(p.row_upper[i])) add(row,static_cast<double>(p.row_upper[i]-shift),i,1,equality);
        if(!equality&&std::isfinite(p.row_lower[i])) {
            for(auto& a:row)a.second=-a.second;
            add(row,static_cast<double>(shift-p.row_lower[i]),i,-1,false);
        }
    }
    for(std::size_t j=0;j<p.cost.size();++j)if(std::isfinite(p.lower[j])&&std::isfinite(p.upper[j]))
        add({{s.mapping[j][0].first,1}},p.upper[j]-p.lower[j],p.rows.size(),1,false);
    if(scaling) {s.cost_scale=0;for(double c:s.cost)s.cost_scale=std::max(s.cost_scale,std::abs(c));if(!s.cost_scale)s.cost_scale=1;}
    for(double& c:s.cost)c/=s.cost_scale;
    s.columns.resize(s.cost.size());
    for(std::size_t i=0;i<s.rows.size();++i)for(auto a:s.rows[i])s.columns[a.first].push_back({i,a.second});
    return s;
}
double dot(const SparseVector& a,const std::vector<double>& x) {
    long double sum=0;for(auto v:a)sum+=static_cast<long double>(v.second)*x[v.first];return static_cast<double>(sum);
}
struct Eta {std::size_t row;std::vector<double> column;};
struct ReoptClock {
    double* target;std::chrono::steady_clock::time_point start;
    explicit ReoptClock(double* p):target(p){if(target)start=std::chrono::steady_clock::now();}
    ~ReoptClock(){if(target)*target+=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();}
};
struct Engine {
    const Options& opt; Canonical& s;
    std::chrono::steady_clock::time_point start=std::chrono::steady_clock::now();
    SparseLU lu;std::vector<Eta> updates;
    BasisRefinementStats* refinement=nullptr;
    LpReoptStats* reopt=nullptr;
    const LinearProblem* certificate_model=nullptr;
    bool allow_certificate=false;
    std::vector<std::size_t> basis;std::vector<double> x,pi,reduced,ray;
    std::size_t iterations=0,factorizations=0,n,m,original;
    Engine(const Options& o,Canonical& model):opt(o),s(model),n(s.cost.size()),m(s.rhs.size()),original(n+m) {
        for(std::size_t i=0;i<m;++i)s.columns.push_back({{i,1}});
    }
    bool expired() const {return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit_seconds;}
    bool artificial(std::size_t j) const {return j>=original||(j>=n&&s.equality[j-n]);}
    bool refactor() {
        ReoptClock clock(reopt?&reopt->factor_seconds:nullptr);
        if(reopt)++reopt->factorizations;
        std::vector<SparseVector> b(m);
        for(std::size_t i=0;i<m;++i)b[i]=s.columns[basis[i]];
        ++factorizations;updates.clear();return lu.factor(b,opt.max_tableau_cells,[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit_seconds;});
    }
    std::vector<double> ftran(std::vector<double> b) const {
        b=lu.solve(b);
        for(const auto& e:updates) {
            double value=b[e.row]/e.column[e.row];
            for(std::size_t i=0;i<m;++i)if(i!=e.row)b[i]-=e.column[i]*value;
            b[e.row]=value;
        }
        return b;
    }
    std::vector<double> btran(std::vector<double> b) const {
        for(auto it=updates.rbegin();it!=updates.rend();++it) {
            long double value=b[it->row];
            for(std::size_t i=0;i<m;++i)if(i!=it->row)value-=static_cast<long double>(it->column[i])*b[i];
            b[it->row]=static_cast<double>(value/it->column[it->row]);
        }
        return lu.solve(b,true);
    }
    std::vector<double> direction(std::size_t j) const {
        std::vector<double> a(m,0);for(auto v:s.columns[j])a[v.first]=v.second;return ftran(a);
    }
    bool pivot(std::size_t row,std::size_t col,std::vector<double> d) {
        if(std::abs(d[row])<1e-12)return false;
        basis[row]=col;updates.push_back({row,std::move(d)});++iterations;
        if(updates.size()>=100)return refactor();
        return true;
    }
    void refine_current(const std::vector<double>& cb) {
        refine_basis_values(s.columns,basis,s.rhs,x,false,[&](const std::vector<double>& r){return ftran(r);},[&](){return expired();},refinement,opt.capture_refinement);
        refine_basis_values(s.columns,basis,cb,pi,true,[&](const std::vector<double>& r){return btran(r);},[&](){return expired();},refinement,opt.capture_refinement);
    }
    void reprice(const std::vector<double>& cost) {
        ReoptClock clock(reopt?&reopt->pricing_seconds:nullptr);
        reduced.resize(cost.size());
        for(std::size_t j=0;j<cost.size();++j)reduced[j]=cost[j]-dot(s.columns[j],pi);
    }
    void values(const std::vector<double>& cost) {
        x=ftran(s.rhs);std::vector<double> cb(m);
        for(std::size_t i=0;i<m;++i)cb[i]=cost[basis[i]];
        pi=btran(cb);
        if(opt.refine_basis&&!opt.refine_at_checks)refine_current(cb);
        reprice(cost);
    }
    std::string optimize(const std::vector<double>& cost,std::size_t allowed,bool dual=false,bool phase_one=false) {
        std::set<std::vector<std::size_t> > seen;bool bland=false;
        for(;;) {
            if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit_seconds)return "time_limit";
            values(cost);
            bool checked=false,recorded=false;
            auto repair=[&](){
                if(!opt.refine_at_checks||checked)return false;
                checked=true;std::vector<double> cb(m);
                for(std::size_t i=0;i<m;++i)cb[i]=cost[basis[i]];
                refine_current(cb);reprice(cost);return true;
            };
            // Re-evaluate decisions on the corrected SAME basis. Never reload
            // its uncorrected values or count this as another pivot/cycle.
recheck_values:
            if(opt.refine_basis&&expired())return "time_limit";
            for(double v:x)if(!std::isfinite(v)){if(repair())goto recheck_values;return "numerical_error";}
            for(double v:reduced)if(!std::isfinite(v)){if(repair())goto recheck_values;return "numerical_error";}
            std::vector<bool> basic(cost.size(),false);for(auto j:basis)basic[j]=true;
            std::size_t entering=allowed,leaving=m;
            if(dual) {
                for(std::size_t j=0;j<allowed;++j)if(!basic[j]&&(phase_one||!artificial(j))&&reduced[j]<-20*opt.tolerance){if(repair())goto recheck_values;return "warm_start_rejected";}
                for(std::size_t i=0;i<m;++i)if(x[i]<-10*opt.tolerance&&(leaving==m||x[i]<x[leaving]))leaving=i;
                if(leaving==m){if(repair())goto recheck_values;return "optimal";}
                std::vector<double> unit(m,0);unit[leaving]=1;auto row=btran(unit);double ratio=inf;
                for(std::size_t j=0;j<allowed;++j)if(!basic[j]&&(phase_one||!artificial(j))) {
                    double a=dot(s.columns[j],row);
                    if(a<-opt.tolerance) {double r=std::max(0.0,reduced[j])/(-a);if(r<ratio){ratio=r;entering=j;}}
                }
                if(entering==allowed){
                    if(repair())goto recheck_values;
                    if(allow_certificate&&certificate_model){
                        ++reopt->certificate_attempts;
                        const bool verified=detail::verify_dual_row(*certificate_model,s.columns,s.rhs,s.equality,n,s.origin,s.scale,row,opt.tolerance,[&](){return expired();});
                        if(expired())return "time_limit";
                        if(verified){++reopt->certificate_accepted;return "infeasible";}
                    }
                    return "warm_start_rejected";
                }
            } else {
                for(double v:x)if(v<-100*opt.tolerance){if(repair())goto recheck_values;return "numerical_error";}
                for(std::size_t j=0;j<allowed;++j)if(!basic[j]&&(phase_one||!artificial(j))&&reduced[j]<-opt.tolerance) {
                    if(entering==allowed||reduced[j]<reduced[entering])entering=j;
                    if(bland)break;
                }
                if(entering==allowed){if(repair())goto recheck_values;return "optimal";}
            }
            if(iterations>=opt.iteration_limit)return "iteration_limit";
            if(!recorded){auto key=basis;std::sort(key.begin(),key.end());recorded=true;
                if(!seen.insert(key).second) {if(bland)return "numerical_stall";bland=true;seen.clear();}}
            auto d=direction(entering);
            if(!dual) {
                double ratio=inf;
                for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance) {
                    double r=std::max(0.0,x[i])/d[i];
                    if(r<ratio||(r==ratio&&leaving<m&&basis[i]<basis[leaving])){ratio=r;leaving=i;}
                }
                if(leaving==m) {
                    if(repair())goto recheck_values;
                    ray.assign(n,0);if(entering<n)ray[entering]=1;
                    for(std::size_t i=0;i<m;++i)if(basis[i]<n)ray[basis[i]]=-d[i];
                    return "unbounded";
                }
            }
            if(!pivot(leaving,entering,std::move(d)))return expired()?"time_limit":"numerical_error";
        }
    }
};
}
LinearProblem linear_from_dense(const Model& m) {
    LinearProblem p;p.cost=m.cost;p.lower.assign(m.cost.size(),0);p.upper.assign(m.cost.size(),inf);
    p.integer.assign(m.cost.size(),false);p.names.resize(m.cost.size());
    for(std::size_t j=0;j<p.names.size();++j)p.names[j]="x"+std::to_string(j);
    if(m.rows.size()!=m.rhs.size())throw std::invalid_argument("Invalid dense row count");
    p.row_lower.assign(m.rows.size(),-inf);p.row_upper=m.rhs;p.rows.resize(m.rows.size());
    for(std::size_t i=0;i<m.rows.size();++i) {
        if(m.rows[i].size()!=m.cost.size())throw std::invalid_argument("Invalid dense row width");
        for(std::size_t j=0;j<m.cost.size();++j)if(m.rows[i][j]!=0)p.rows[i].push_back({j,m.rows[i][j]});
    }
    return p;
}
static SparseLpResult solve_sparse_lp_impl(const LinearProblem& p,const Options& opt,const LpBasis* warm) {
    const auto call_start=std::chrono::steady_clock::now();
    validate_linear_problem(p);
    if(!std::isfinite(opt.tolerance)||opt.tolerance<=0||!std::isfinite(opt.time_limit_seconds)||opt.time_limit_seconds<0)
        throw std::invalid_argument("Invalid LP options");
    if(opt.refine_at_checks&&!opt.refine_basis)throw std::invalid_argument("refine-at-checks requires refine-basis");
    if(opt.warm_infeasibility_certificate&&!opt.primal_warm_start)throw std::invalid_argument("warm infeasibility certificate requires primal warm start");
    SparseLpResult out;auto& r=out.solution;
    for(std::size_t j=0;j<p.cost.size();++j)if(p.lower[j]>p.upper[j]){r.status="infeasible";r.infeasibility_verified=true;return out;}
    for(std::size_t i=0;i<p.rows.size();++i)if(p.row_lower[i]>p.row_upper[i]){r.status="infeasible";r.infeasibility_verified=true;return out;}
    Canonical s;
    {ReoptClock clock(opt.primal_warm_start?&out.reopt.canonical_seconds:nullptr);s=canonicalize(p,opt.scaling,opt.compact_equalities);}
    Engine e(opt,s);const std::size_t n=e.n,m=e.m,original=e.original;
    if(opt.primal_warm_start){out.reopt.calls=1;e.reopt=&out.reopt;e.start=call_start;}
    e.refinement=&out.refinement;
    out.canonical_rows=m;out.compact_equality_rows=std::count(s.equality.begin(),s.equality.end(),true);
    std::vector<double> cost(original,0);for(std::size_t j=0;j<n;++j)cost[j]=s.cost[j];
    bool solved=false;
    if(warm&&warm->structural_columns==n&&warm->columns.size()==m&&warm->compact_equalities==opt.compact_equalities) {
        e.basis=warm->columns;bool valid=true;std::set<std::size_t> distinct;
        for(auto j:e.basis)if(e.artificial(j)||!distinct.insert(j).second)valid=false;
        // A primal restart is permitted only for an exact, non-hashed structural
        // match. Untagged legacy bases keep their existing dual-only behavior.
        bool compatible=opt.primal_warm_start&&warm->structure&&!warm->reduced_upper_bounds
            &&warm->structure->rows==s.rows&&warm->structure->mapping==s.mapping&&warm->structure->equality==s.equality;
        if(opt.primal_warm_start&&warm->structure&&!compatible)valid=false;
        if(valid&&compatible)++out.reopt.compatible;
        if(valid&&e.refactor()) {
            bool use_primal=false,eligible=true;
            if(compatible){
                e.values(cost);
                if(opt.refine_at_checks){std::vector<double> cb(m);for(std::size_t i=0;i<m;++i)cb[i]=cost[e.basis[i]];e.refine_current(cb);e.reprice(cost);}
                bool primal=true,dual=true;std::vector<bool> basic(original,false);for(auto j:e.basis)basic[j]=true;
                // Conservative selection thresholds; the existing optimizer and
                // full numerical certificate checks still decide acceptance.
                for(double v:e.x)if(!std::isfinite(v)||v<-opt.tolerance)primal=false;
                for(std::size_t j=0;j<original;++j)if(!basic[j]&&!e.artificial(j)&&(!std::isfinite(e.reduced[j])||e.reduced[j]<-opt.tolerance))dual=false;
                use_primal=!dual&&primal;eligible=dual||primal;
                if(eligible){if(use_primal)++out.reopt.primal;else ++out.reopt.dual;}
                else ++out.reopt.rejected;
            }
            e.allow_certificate=compatible&&opt.warm_infeasibility_certificate;
            e.certificate_model=&p;
            r.status=eligible?e.optimize(cost,original,!use_primal):"warm_start_rejected";
            e.allow_certificate=false;
            if(r.status=="infeasible"&&out.reopt.certificate_accepted){
                r.infeasibility_verified=true;r.iterations=e.iterations;out.factorizations=e.factorizations;return out;
            }
            solved=r.status=="optimal";out.warm_started=solved;
            if(r.status=="time_limit"||r.status=="iteration_limit"){r.iterations=e.iterations;return out;}
        }
    }
    if(!solved) {
        e.basis.resize(m);std::vector<double> phase(original,0);bool need_phase=false;
        for(std::size_t i=0;i<m;++i) {
            e.basis[i]=n+i;
            if(s.equality[i]){phase[n+i]=1;need_phase=true;}
            if(s.rhs[i]<0){e.basis[i]=s.columns.size();s.columns.push_back({{i,-1}});phase.push_back(1);need_phase=true;}
        }
        if(!e.refactor()){r.status=e.expired()?"time_limit":"numerical_error";return out;}
        if(need_phase) {
            const auto before=e.iterations;
            r.status=e.optimize(phase,phase.size(),false,true);
            if(e.reopt)out.reopt.phase_one_iterations+=e.iterations-before;
            if(r.status!="optimal"){r.iterations=e.iterations;return out;}
            long double value=0;for(std::size_t i=0;i<m;++i)if(e.artificial(e.basis[i]))value+=e.x[i];
            if(value>10*opt.tolerance) {
                long double contradiction=0,magnitude=1;bool verified=true;
                for(std::size_t i=0;i<m;++i){if(!s.equality[i])e.pi[i]=std::min(0.0,e.pi[i]);contradiction+=s.rhs[i]*e.pi[i];magnitude+=std::abs(s.rhs[i]*e.pi[i]);}
                for(std::size_t j=0;j<n;++j)if(dot(s.columns[j],e.pi)>10*opt.tolerance)verified=false;
                r.infeasibility_verified=verified&&contradiction>10*opt.tolerance*magnitude;
                r.status=r.infeasibility_verified?"infeasible":"numerical_error";r.iterations=e.iterations;return out;
            }
            for(std::size_t i=0;i<m;++i)if(e.artificial(e.basis[i])) {
                std::vector<bool> basic(s.columns.size(),false);for(auto j:e.basis)basic[j]=true;
                std::vector<double> unit(m,0);unit[i]=1;auto row=e.btran(unit);std::size_t entering=original;
                for(std::size_t j=0;j<original;++j)if(!basic[j]&&!e.artificial(j)&&std::abs(dot(s.columns[j],row))>opt.tolerance){entering=j;break;}
                if(entering==original||!e.pivot(i,entering,e.direction(entering))){r.status="numerical_error";r.iterations=e.iterations;return out;}
            }
        }
        cost.resize(s.columns.size(),0);r.status=e.optimize(cost,original);
    }
    r.iterations=e.iterations;out.factorizations=e.factorizations;
    if(r.status=="unbounded") {
        bool valid=e.ray.size()==n;long double improvement=0;
        for(std::size_t j=0;j<n&&valid;++j){if(!std::isfinite(e.ray[j])||e.ray[j]<-opt.tolerance)valid=false;improvement+=s.cost[j]*e.ray[j];}
        for(std::size_t i=0;i<m&&valid;++i){double v=dot(s.rows[i],e.ray);if((s.equality[i]?std::abs(v):v)>10*opt.tolerance)valid=false;}
        r.unboundedness_verified=valid&&improvement<-opt.tolerance;
        if(r.unboundedness_verified){r.unbounded_ray.assign(p.cost.size(),0);for(std::size_t j=0;j<p.cost.size();++j)for(auto a:s.mapping[j])r.unbounded_ray[j]+=a.second*e.ray[a.first];}
        else r.status="numerical_error";
        return out;
    }
    if(r.status!="optimal")return out;
    out.basis.columns=e.basis;out.basis.structural_columns=n;
    out.basis.compact_equalities=opt.compact_equalities;
    if(opt.primal_warm_start){
        auto structure=std::make_shared<LpBasisStructure>();structure->rows=s.rows;structure->mapping=s.mapping;structure->equality=s.equality;
        out.basis.structure=structure;
    }
    out.canonical_primal.assign(n,0);for(std::size_t i=0;i<m;++i)if(e.basis[i]<n)out.canonical_primal[e.basis[i]]=e.x[i];
    out.canonical_dual.resize(m);out.row_dual.assign(p.rows.size(),0);
    long double primal_objective=0,dual_objective=0;
    for(std::size_t j=0;j<n;++j)primal_objective+=s.cost[j]*out.canonical_primal[j];
    for(std::size_t i=0;i<m;++i) {
        if(!s.equality[i])e.pi[i]=std::min(0.0,e.pi[i]);dual_objective+=static_cast<long double>(s.rhs[i])*e.pi[i];
        out.canonical_dual[i]=e.pi[i]*s.cost_scale/s.scale[i];
        if(s.origin[i].first<p.rows.size())out.row_dual[s.origin[i].first]+=s.origin[i].second*out.canonical_dual[i];
    }
    for(std::size_t j=0;j<n;++j) {
        long double aty=0,scale=1+std::abs(s.cost[j]);
        for(auto a:s.columns[j]){long double v=a.second*e.pi[a.first];aty+=v;scale+=std::abs(v);}
        r.scaled_dual_violation=std::max(r.scaled_dual_violation,static_cast<double>(std::max(0.0L,aty-s.cost[j])/scale));
    }
    r.primal=s.shift;
    for(std::size_t j=0;j<p.cost.size();++j)for(auto a:s.mapping[j])r.primal[j]+=a.second*out.canonical_primal[a.first];
    r.objective=p.offset;for(std::size_t j=0;j<p.cost.size();++j)r.objective+=p.cost[j]*r.primal[j];
    r.max_violation=original_violation(p,r.primal,false);r.scaled_primal_violation=original_violation(p,r.primal,true);
    r.relative_gap=static_cast<double>(std::abs(primal_objective-dual_objective)/(1+std::max(std::abs(primal_objective),std::abs(dual_objective))));
    r.optimality_verified=std::isfinite(r.objective)&&r.scaled_primal_violation<=10*opt.tolerance&&r.scaled_dual_violation<=10*opt.tolerance&&r.relative_gap<=10*opt.tolerance;
    r.dual=out.canonical_dual;
    if(!r.optimality_verified)r.status="numerical_error";
    if(opt.primal_warm_start&&r.optimality_verified&&out.warm_started&&out.reopt.compatible)out.reopt.verified=1;
    out.best_bound=static_cast<double>(dual_objective)*s.cost_scale+s.offset;
    return out;
}
SparseLpResult solve_sparse_lp(const LinearProblem& p,const Options& opt,const LpBasis* warm) {
    auto start=std::chrono::steady_clock::now();auto result=solve_sparse_lp_impl(p,opt,warm);
    if(opt.compact_equalities&&(result.solution.status=="numerical_error"||result.solution.status=="numerical_stall")) {
        double left=opt.time_limit_seconds-std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        if(left>0){
            Options fallback=opt;fallback.compact_equalities=false;fallback.time_limit_seconds=left;
            auto ordinary=solve_sparse_lp_impl(p,fallback,nullptr);ordinary.solution.iterations+=result.solution.iterations;
            ordinary.refinement.add(result.refinement);
            ordinary.reopt.add(result.reopt);
            ordinary.compact_fallback=true;return ordinary;
        }
    }
    return result;
}
}
