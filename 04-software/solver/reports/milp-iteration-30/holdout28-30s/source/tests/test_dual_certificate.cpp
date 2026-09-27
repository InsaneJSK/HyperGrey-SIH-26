#include "dual_certificate.hpp"
#include "milp.hpp"
#include <iostream>
#include <iomanip>
#include <stdexcept>
using namespace sovereign;
void check(bool b,const char* why){if(!b)throw std::runtime_error(why);}
int main(int argc,char** argv){try{
    if(argc==2&&std::string(argv[1])=="--arithmetic"){
        std::uint64_t state=739112;
        auto sample=[&](){state^=state<<13;state^=state>>7;state^=state<<17;
            const double mantissa=1.+static_cast<double>((state>>1)%1024)/1024.;
            return std::ldexp((state&1)?mantissa:-mantissa,static_cast<int>((state>>12)%2098)-1074);};
        for(int i=0;i<1600;++i){double a=sample(),b=sample();if(i%10==0)a=i%20?1:0;
            const auto p=detail::dual_certificate::product(a,b),s=detail::dual_certificate::add(detail::dual_certificate::Interval(a),detail::dual_certificate::Interval(b));
            std::cout<<std::setprecision(17)<<a<<' '<<b<<' '<<p.lo<<' '<<p.hi<<' '<<s.lo<<' '<<s.hi<<'\n';}
        return 0;
    }
    check(argc==1,"Unexpected arguments");
    auto p=linear_from_dense({{1},{{1}},{-1}});
    std::vector<SparseVector> columns={{{0,1}},{{0,1}}};
    std::vector<double> rhs={-1},scale={1},row={1};std::vector<bool> equality={false};
    std::vector<std::pair<std::size_t,double> > origin={{0,1}};
    auto verify=[&](){return detail::verify_dual_row(p,columns,rhs,equality,1,origin,scale,row,1e-9,[](){return false;});};
    check(verify(),"Exact contradiction missed");
    columns[0][0].second=-1e-12;p.rows[0][0].second=-1e-12;
    check(!verify(),"Feasible tiny negative coefficient declared infeasible");
    columns[0][0].second=1;p.rows[0][0].second=-1;
    check(!verify(),"Original coefficients not checked");
    p.rows[0][0].second=1;rhs[0]=-1e-15;p.row_upper[0]=-1e-15;
    check(!verify(),"Insufficient contradiction accepted");
    rhs[0]=-1;p.row_upper[0]=-1;row[0]=.5;
    check(!verify(),"Noninteger multiplier accepted");
    row[0]=NAN;check(!verify(),"Nonfinite multiplier accepted");
    row[0]=1;columns[0][0].second=INFINITY;check(!verify(),"Nonfinite column accepted");
    columns[0][0].second=1;
    check(!detail::verify_dual_row(p,columns,rhs,equality,1,origin,scale,row,1e-9,[](){return true;}),"Exhausted deadline ignored");
    // Equality multipliers may be negative; there is no equality slack.
    equality[0]=true;row[0]=-1;columns[0][0].second=-1;rhs[0]=1;
    p.rows[0][0].second=-1;p.row_lower[0]=p.row_upper[0]=1;
    check(verify(),"Equality sign mishandled");
    p.lower[0]=-INFINITY;check(!verify(),"Free original variable falsely certified");
    // Coefficient and sum overflow must reject, not wrap.
    std::int64_t value=detail::dual_certificate::sum_limit;
    check(!detail::dual_certificate::accumulate(value,1,1),"Integer sum overflow accepted");
    check(!detail::dual_certificate::integer(1e30,value),"Out-of-range coefficient accepted");
    std::size_t accepted=0,cases=0;
    for(bool scaling:{false,true})for(bool compact:{false,true})for(bool maximum:{false,true})for(double shift:{-3.,0.,2.}){
        Options o;o.primal_warm_start=true;o.refine_basis=true;o.refine_at_checks=true;
        o.scaling=scaling;o.compact_equalities=compact;
        auto model=linear_from_dense({{maximum?-1.:1.},{{-1}},{-1-shift}});
        model.maximize=maximum;model.lower={shift};model.upper={shift+2};
        auto parent=solve_sparse_lp(model,o);check(parent.solution.optimality_verified,"Parent unverified");
        const auto saved=parent.basis.columns;
        auto child=model;child.upper[0]=shift+.5;
        auto cold=solve_sparse_lp(child,o);check(cold.solution.infeasibility_verified,"Cold local infeasibility missing");
        o.warm_infeasibility_certificate=true;
        auto local=solve_sparse_lp(child,o,&parent.basis);
        check(local.solution.status=="infeasible"&&local.solution.infeasibility_verified,"Warm certificate unverified");
        check(local.reopt.certificate_accepted==1&&local.reopt.phase_one_iterations==0,"Shortcut did not avoid phase one");
        check(local.basis.columns.empty()&&!local.warm_started&&parent.basis.columns==saved,"Failed branch changed parent ownership");
        accepted+=local.reopt.certificate_accepted;
        child.upper[0]=shift+1.5;auto alternate=solve_sparse_lp(child,o,&parent.basis);
        check(alternate.solution.optimality_verified&&original_violation(child,alternate.solution.primal,false)<1e-7,"Alternate parent reuse failed");
        check(!alternate.reopt.certificate_accepted,"Feasible branch shortcut used");
        auto bad=parent.basis;bad.columns[0]=std::numeric_limits<std::size_t>::max();
        auto fallback=solve_sparse_lp(child,o,&bad);check(fallback.solution.optimality_verified&&!fallback.reopt.certificate_attempts,"Invalid basis shortcut used");
        o.time_limit_seconds=0;auto stopped=solve_sparse_lp(child,o,&parent.basis);
        check(stopped.solution.status=="time_limit"&&!stopped.reopt.certificate_accepted,"Zero time shortcut used");
        o.time_limit_seconds=30;o.iteration_limit=0;child=model;child.lower[0]=shift+1.25;
        auto capped=solve_sparse_lp(child,o,&parent.basis);check(!capped.reopt.certificate_accepted,"Feasible pivot cap certified infeasible");
        o.iteration_limit=10000;o.warm_infeasibility_certificate=false;child=model;child.upper[0]=shift+.5;
        auto off=solve_sparse_lp(child,o,&parent.basis);check(off.solution.infeasibility_verified&&!off.reopt.certificate_attempts,"Disabled path changed");
        ++cases;
    }
    // A valid local contradiction with fractional coefficients must keep the
    // ordinary cold fallback; this shortcut intentionally cannot certify it.
    Options fractional;fractional.scaling=false;fractional.primal_warm_start=true;
    auto f=linear_from_dense({{1},{{-.5}},{-.5}});f.upper={2};
    auto fp=solve_sparse_lp(f,fractional);check(fp.solution.optimality_verified,"Fractional parent failed");
    f.upper={.5};fractional.warm_infeasibility_certificate=true;
    auto fr=solve_sparse_lp(f,fractional,&fp.basis);
    check(fr.solution.infeasibility_verified&&fr.reopt.certificate_attempts==1&&!fr.reopt.certificate_accepted&&fr.reopt.phase_one_iterations>0,"Uncertain certificate did not fall back");
    bool rejected=false;Options invalid;invalid.warm_infeasibility_certificate=true;
    try{solve_sparse_lp(p,invalid);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"Unguarded LP certificate option allowed");
    rejected=false;MilpOptions mo;mo.private_dual_certificate=true;
    try{solve_milp(p,mo);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"Private option dependency ignored");
    rejected=false;mo.private_dual_certificate=false;mo.lp.warm_infeasibility_certificate=true;
    try{solve_milp(p,mo);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"Global MILP shortcut allowed");
    std::cout<<cases<<" transformed local/alternate/budget cases, "<<accepted<<" certificates; exact signs, original bounds and rejection guards PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
