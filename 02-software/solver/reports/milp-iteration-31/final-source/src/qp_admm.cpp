#include "qp.hpp"
#include "sparse_matrix.hpp"
#include <chrono>
#include <numeric>

namespace sovereign {
QpResult solve_qp_legacy(const QuadraticProblem&,double,std::size_t,double);
QpResult solve_diagonal_equalities(const QuadraticProblem&,const QpOptions&);
QpResult solve_qp(const QuadraticProblem& q,double limit,std::size_t iterations,double tolerance) {
    if(q.linear.rows.empty()) {
        auto r=solve_qp_legacy(q,limit,iterations,tolerance);r.algorithm="accelerated_projected_gradient";
        if(!r.primal.empty())check_qp_solution(q,r,tolerance);
        if(r.status=="unsupported_curvature"&&check_convex_hessian(q)) {
            QpOptions o;o.time_limit=limit;o.iteration_limit=iterations;o.tolerance=tolerance;return solve_qp_admm(q,o);
        }
        return r;
    }
    QpOptions o;o.time_limit=limit;o.iteration_limit=iterations;o.tolerance=tolerance;return solve_qp_admm(q,o);
}
namespace {
double clip(double x,double lo,double up){return std::max(lo,std::min(up,x));}
double norm(const std::vector<double>& x){double v=0;for(double a:x)v=std::max(v,std::abs(a));return v;}
double dot(const std::vector<double>& a,const std::vector<double>& b){long double s=0;for(std::size_t j=0;j<a.size();++j)s+=static_cast<long double>(a[j])*b[j];return static_cast<double>(s);}
CsrMatrix hessian(const QuadraticProblem& q) {
    std::vector<SparseVector> rows(q.linear.cost.size());double sign=q.linear.maximize?-1:1;
    for(auto a:q.hessian){rows[a.row].push_back({a.col,sign*a.value});if(a.row!=a.col)rows[a.col].push_back({a.row,sign*a.value});}
    return CsrMatrix(rows.size(),rows);
}
}
bool check_convex_hessian(const QuadraticProblem& q) {
    std::size_t n=q.linear.cost.size();double sign=q.linear.maximize?-1:1;
    std::vector<double> diagonal(n,0),radius(n,0);
    for(auto a:q.hessian) {
        if(a.row>=n||a.col>=n||!std::isfinite(a.value))throw std::invalid_argument("Invalid Hessian");
        if(a.row==a.col)diagonal[a.row]+=sign*a.value;
        else {radius[a.row]+=std::abs(a.value);radius[a.col]+=std::abs(a.value);}
    }
    bool dd=true;for(std::size_t j=0;j<n;++j){if(diagonal[j]<0||(diagonal[j]==0&&radius[j]>0))return false;if(diagonal[j]<radius[j])dd=false;}
    if(dd)return true;
    // Congruence scaling followed by sparse LDL^T with complete fill retention.
    // This accepts sparse PSD matrices beyond the old 200-variable cutoff.
    std::vector<std::map<std::size_t,double> > lower(n);
    for(auto a:q.hessian) {
        auto i=std::max(a.row,a.col),j=std::min(a.row,a.col);
        if(diagonal[i]>0&&diagonal[j]>0)lower[j][i]+=sign*a.value/std::sqrt(diagonal[i]*diagonal[j]);
    }
    std::size_t fill=q.hessian.size();
    for(std::size_t k=0;k<n;++k) {
        double d=lower[k].count(k)?lower[k][k]:0;
        if(d<-1e-12)return false;
        std::vector<std::pair<std::size_t,double> > off;
        for(auto a:lower[k])if(a.first>k)off.push_back(a);
        if(d<=1e-12){for(auto a:off)if(std::abs(a.second)>1e-10)return false;continue;}
        for(std::size_t u=0;u<off.size();++u)for(std::size_t v=u;v<off.size();++v) {
            auto i=off[u].first,j=off[v].first;
            if(!lower[i].count(j)&&++fill>4000000)return false;
            lower[i][j]-=off[u].second*off[v].second/d;
        }
        lower[k].clear();
    }
    return true;
}
void check_qp_solution(const QuadraticProblem& q,QpResult& r,double tol) {
    const auto& p=q.linear;const auto& x=r.primal;double sign=p.maximize?-1:1;
    r.optimality_verified=false;
    r.objective=std::numeric_limits<double>::quiet_NaN();r.dual_bound=-std::numeric_limits<double>::infinity();
    r.primal_residual=r.stationarity_residual=r.complementarity_residual=r.relative_gap=std::numeric_limits<double>::infinity();
    if(x.size()!=p.cost.size()||r.row_dual.size()!=p.rows.size())return;
    for(double v:x)if(!std::isfinite(v))return;
    for(double v:r.row_dual)if(!std::isfinite(v))return;
    std::vector<double> gradient(x.size(),0);long double value=sign*p.offset;
    std::vector<long double> diagonal,linear;bool positive_diagonal=true;
    for(auto h:q.hessian){gradient[h.row]+=sign*h.value*x[h.col];if(h.row!=h.col){gradient[h.col]+=sign*h.value*x[h.row];if(h.value!=0)positive_diagonal=false;}}
    if(positive_diagonal){
        diagonal.assign(x.size(),0);for(auto h:q.hessian)if(h.row==h.col)diagonal[h.row]+=sign*h.value;
        for(long double d:diagonal)if(!(d>0))positive_diagonal=false;
        if(positive_diagonal){linear.resize(x.size());for(std::size_t j=0;j<x.size();++j)linear[j]=sign*p.cost[j];}
    }
    for(std::size_t j=0;j<x.size();++j){value+=.5L*x[j]*gradient[j]+sign*p.cost[j]*x[j];gradient[j]+=sign*p.cost[j];}
    r.objective=sign*static_cast<double>(value);r.primal_residual=original_violation(p,x,true);r.complementarity_residual=0;
    long double bound=value,dual_constant=sign*p.offset;
    for(std::size_t i=0;i<p.rows.size();++i) {
        long double activity=0;for(auto a:p.rows[i]){activity+=static_cast<long double>(a.second)*x[a.first];gradient[a.first]+=a.second*r.row_dual[i];if(positive_diagonal)linear[a.first]+=static_cast<long double>(a.second)*r.row_dual[i];}
        const double y=r.row_dual[i],target=y>=0?p.row_upper[i]:p.row_lower[i];
        if(y!=0) {
            dual_constant-=static_cast<long double>(y)*target;
            long double correction=y*(activity-target);bound+=correction;
            double residual=static_cast<double>(std::abs(correction)/(1+std::abs(value)));
            if(!std::isfinite(residual))residual=std::numeric_limits<double>::infinity();
            r.complementarity_residual=std::max(r.complementarity_residual,residual);
        }
    }
    r.stationarity_residual=0;
    for(std::size_t j=0;j<x.size();++j) {
        const double g=gradient[j];double residual=std::abs(x[j]-clip(x[j]-g,p.lower[j],p.upper[j]))/(1+std::abs(x[j]));
        if(!std::isfinite(g)||!std::isfinite(residual))residual=std::numeric_limits<double>::infinity();
        r.stationarity_residual=std::max(r.stationarity_residual,residual);
        // Tangent affine underestimator of a convex quadratic, minimized over
        // the original box. A finite value is a valid numerical dual bound.
        if(g!=0) {double target=g>0?p.lower[j]:p.upper[j];if(std::isfinite(target))bound+=g*(target-x[j]);else bound=-std::numeric_limits<long double>::infinity();}
    }
    // Strictly positive diagonal curvature permits exact separable minimization
    // of the Lagrangian over the original box. Unlike the affine tangent bound,
    // it stays finite at unbounded variable endpoints. This is a numerical bound,
    // not an interval-arithmetic proof, and never substitutes for feasibility.
    if(positive_diagonal){
        bound=dual_constant;
        for(std::size_t j=0;j<x.size();++j){
            long double minimizer=std::max(static_cast<long double>(p.lower[j]),std::min(static_cast<long double>(p.upper[j]),-linear[j]/diagonal[j]));
            bound+=.5L*diagonal[j]*minimizer*minimizer+linear[j]*minimizer;
        }
    }
    r.dual_bound=static_cast<double>(bound);
    r.relative_gap=std::isfinite(bound)?static_cast<double>(std::abs(value-bound)/(1+std::abs(value))):std::numeric_limits<double>::infinity();
    r.optimality_verified=std::isfinite(r.objective)&&std::max(r.primal_residual,std::max(r.stationarity_residual,r.complementarity_residual))<=tol;
    if(positive_diagonal)r.optimality_verified=r.optimality_verified&&r.relative_gap<=tol;
}
QpResult solve_qp_admm(const QuadraticProblem& original,const QpOptions& opt) {
    if(!std::isfinite(opt.time_limit)||opt.time_limit<0||!std::isfinite(opt.tolerance)||opt.tolerance<=0||opt.threads<1)throw std::invalid_argument("Invalid QP options");
    auto start=std::chrono::steady_clock::now();validate_linear_problem(original.linear);
    for(bool integer:original.linear.integer)if(integer)throw std::invalid_argument("Continuous QP required");
    QpResult result;result.algorithm="scaled_admm_pcg";
    if(!check_convex_hessian(original)){result.status="unsupported_curvature";return result;}
    const std::size_t n=original.linear.cost.size(),m=original.linear.rows.size();
    const auto& p=original.linear;
    for(std::size_t j=0;j<n;++j)if(p.lower[j]>p.upper[j]){result.status="infeasible_bounds";return result;}
    for(std::size_t i=0;i<m;++i)if(p.row_lower[i]>p.row_upper[i]){result.status="infeasible_bounds";return result;}
    // Dispatch by mathematical structure, not instance name or a 512-column
    // eligibility cutoff. Keep at least half the solve budget for ADMM fallback.
    {
        QpOptions specialized_options=opt;
        specialized_options.time_limit=std::min(n<=512?2.0:10.0,(n<=512?.2:.5)*opt.time_limit);
        auto specialized=solve_diagonal_equalities(original,specialized_options);
        if(specialized.status=="optimal")return specialized;
    }
    auto h=hessian(original);
    std::vector<double> variable(n,1),row_scale(m+n,1),diagonal(n,0),c=p.cost;
    double sign=p.maximize?-1:1;
    for(std::size_t i=0;i<n;++i)for(int k=h.start[i];k<h.start[i+1];++k)if(h.index[k]==static_cast<int>(i))diagonal[i]=h.value[k];
    // Curvature-based variable units are especially useful for tiny, nonzero
    // Hessian entries. No coefficient is dropped.
    if(opt.scaling)for(std::size_t j=0;j<n;++j)if(diagonal[j]>0)variable[j]=1/std::sqrt(std::max(1e-16,diagonal[j]));
    for(std::size_t i=0;i<n;++i)for(int k=h.start[i];k<h.start[i+1];++k)h.value[k]*=variable[i]*variable[h.index[k]];
    std::vector<SparseVector> rows=p.rows;
    std::vector<double> lower=p.row_lower,upper=p.row_upper;
    for(std::size_t i=0;i<m;++i) {
        double maximum=0;for(auto& a:rows[i]){a.second*=variable[a.first];maximum=std::max(maximum,std::abs(a.second));}
        if(opt.scaling&&maximum>0)row_scale[i]=1/maximum;
        for(auto& a:rows[i])a.second*=row_scale[i];
        lower[i]*=row_scale[i];upper[i]*=row_scale[i];
    }
    for(std::size_t j=0;j<n;++j){rows.push_back({{j,1}});lower.push_back(p.lower[j]/variable[j]);upper.push_back(p.upper[j]/variable[j]);}
    for(std::size_t j=0;j<n;++j)c[j]*=sign*variable[j];
    double cost_scale=opt.scaling?1/std::max(1.0,norm(c)):1;
    for(double& a:h.value)a*=cost_scale;for(double& v:c)v*=cost_scale;
    CsrMatrix a(n,rows),at=a.transpose();const std::size_t constraints=rows.size();
    std::fill(diagonal.begin(),diagonal.end(),0);
    for(std::size_t i=0;i<n;++i)for(int k=h.start[i];k<h.start[i+1];++k)if(h.index[k]==static_cast<int>(i))diagonal[i]=h.value[k];
    std::vector<double> x(n),z(constraints),y(constraints,0),ax,hx,aty,rho(constraints),preconditioner(n),temporary,product;
    for(std::size_t j=0;j<n;++j)x[j]=clip(0,lower[m+j],upper[m+j]);
    a.multiply(x,ax,opt.threads);for(std::size_t i=0;i<constraints;++i)z[i]=clip(ax[i],lower[i],upper[i]);
    double rho_base=.1,sigma=1e-8;
    auto setup=[&]() {
        for(std::size_t i=0;i<constraints;++i)rho[i]=rho_base*(lower[i]==upper[i]?100:1);
        preconditioner=diagonal;for(double& d:preconditioner)d+=sigma;
        for(std::size_t i=0;i<constraints;++i)for(int k=a.start[i];k<a.start[i+1];++k)preconditioner[a.index[k]]+=rho[i]*a.value[k]*a.value[k];
    };setup();
    auto system=[&](const std::vector<double>& v,std::vector<double>& output) {
        h.multiply(v,output,opt.threads);a.multiply(v,temporary,opt.threads);
        for(std::size_t i=0;i<constraints;++i)temporary[i]*=rho[i];at.multiply(temporary,product,opt.threads);
        for(std::size_t j=0;j<n;++j)output[j]+=sigma*v[j]+product[j];
    };
    auto polish=[&]() {
        // Guess active rows from ADMM multipliers, then solve the KKT equations.
        // Accept only after checking the ORIGINAL model; a bad active set is discarded.
        std::vector<std::size_t> active;
        for(std::size_t i=0;i<constraints;++i)if(lower[i]==upper[i]||std::abs(y[i])>1e-5)active.push_back(i);
        if(n+active.size()>10000)return false;
        const std::size_t size=n+active.size();const double regularization=1e-9;
        auto check_polished=[&](const std::vector<double>& px,const std::vector<double>& py) {
            QpResult candidate;candidate.algorithm="scaled_admm_pcg_kkt_polish";
            candidate.primal=px;candidate.row_dual.assign(m,0);
            for(std::size_t j=0;j<n;++j)candidate.primal[j]*=variable[j];
            for(std::size_t k=0;k<active.size();++k)if(active[k]<m)candidate.row_dual[active[k]]=py[k]*row_scale[active[k]]/cost_scale;
            check_qp_solution(original,candidate,opt.tolerance);
            if(candidate.optimality_verified){candidate.iterations=result.iterations;candidate.status="optimal";result=candidate;return true;}
            return false;
        };
        bool diagonal_hessian=true;for(std::size_t j=0;j<n;++j){if(diagonal[j]<=0)diagonal_hessian=false;for(int k=h.start[j];k<h.start[j+1];++k)if(h.index[k]!=static_cast<int>(j))diagonal_hessian=false;}
        if(diagonal_hessian&&!active.empty()) {
            std::vector<SparseVector> active_rows;std::vector<double> target;
            for(auto i:active){active_rows.push_back(rows[i]);target.push_back(lower[i]==upper[i]?lower[i]:(y[i]>0?upper[i]:lower[i]));if(!std::isfinite(target.back()))return false;}
            CsrMatrix k(n,active_rows),kt=k.transpose();
            std::vector<double> inverse_c(n),rhs,diagonal_s(active.size(),1e-18),lambda(active.size(),0),residual,zp,direction_s,mv,work,extra;
            for(std::size_t j=0;j<n;++j)inverse_c[j]=c[j]/diagonal[j];k.multiply(inverse_c,rhs);
            for(std::size_t i=0;i<active.size();++i){rhs[i]=-rhs[i]-target[i];for(auto e:active_rows[i])diagonal_s[i]+=e.second*e.second/diagonal[e.first];}
            residual=rhs;zp.resize(rhs.size());for(std::size_t i=0;i<rhs.size();++i)zp[i]=residual[i]/diagonal_s[i];direction_s=zp;double rz=dot(residual,zp);
            auto polish_start=std::chrono::steady_clock::now();
            for(int inner=0;inner<20000&&norm(residual)>1e-13*(1+norm(rhs));++inner) {
                kt.multiply(direction_s,work);for(std::size_t j=0;j<n;++j)work[j]/=diagonal[j];k.multiply(work,mv);
                double den=dot(direction_s,mv);if(!(den>0)||!std::isfinite(den))break;
                double alpha=rz/den;for(std::size_t i=0;i<rhs.size();++i){lambda[i]+=alpha*direction_s[i];residual[i]-=alpha*mv[i];zp[i]=residual[i]/diagonal_s[i];}
                double next=dot(residual,zp),beta=next/rz;rz=next;
                for(std::size_t i=0;i<rhs.size();++i)direction_s[i]=zp[i]+beta*direction_s[i];
                if(inner%100==0&&(std::chrono::duration<double>(std::chrono::steady_clock::now()-polish_start).count()>2||std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit))break;
            }
            kt.multiply(lambda,work);for(std::size_t j=0;j<n;++j)work[j]=-(work[j]+c[j])/diagonal[j];
            if(check_polished(work,lambda))return true;
            return false;
        }
        std::vector<SparseVector> columns(size);std::vector<double> rhs(size),solution(size,0);
        for(std::size_t j=0;j<n;++j){rhs[j]=-c[j];columns[j].push_back({j,regularization});}
        for(std::size_t i=0;i<n;++i)for(int k=h.start[i];k<h.start[i+1];++k)columns[h.index[k]].push_back({i,h.value[k]});
        for(std::size_t k=0;k<active.size();++k) {
            auto i=active[k];double target=y[i]>=0?upper[i]:lower[i];if(lower[i]==upper[i])target=lower[i];
            if(!std::isfinite(target))return false;rhs[n+k]=target;
            columns[n+k].push_back({n+k,-regularization});
            for(int pos=a.start[i];pos<a.start[i+1];++pos){auto j=a.index[pos];columns[j].push_back({n+k,a.value[pos]});columns[n+k].push_back({static_cast<std::size_t>(j),a.value[pos]});}
        }
        SparseLU factor;
        auto polish_start=std::chrono::steady_clock::now();
        auto cancelled=[&](){auto now=std::chrono::steady_clock::now();return std::chrono::duration<double>(now-start).count()>=opt.time_limit||std::chrono::duration<double>(now-polish_start).count()>2;};
        try{if(!factor.factor(columns,8000000,cancelled))return false;}catch(const std::runtime_error&){return false;}
        std::vector<double> residual=rhs;
        for(int refinement=0;refinement<8;++refinement) {
            auto correction=factor.solve(residual);for(std::size_t j=0;j<size;++j)solution[j]+=correction[j];
            residual=rhs;
            for(std::size_t j=0;j<size;++j)for(auto v:columns[j])residual[v.first]-=v.second*solution[j];
            for(std::size_t j=0;j<size;++j)residual[j]+=(j<n?regularization:-regularization)*solution[j];
        }
        QpResult candidate;candidate.algorithm="scaled_admm_pcg_kkt_polish";
        candidate.primal.assign(solution.begin(),solution.begin()+n);candidate.row_dual.assign(m,0);
        for(std::size_t j=0;j<n;++j)candidate.primal[j]*=variable[j];
        for(std::size_t k=0;k<active.size();++k)if(active[k]<m)candidate.row_dual[active[k]]=solution[n+k]*row_scale[active[k]]/cost_scale;
        check_qp_solution(original,candidate,opt.tolerance);
        if(candidate.optimality_verified){candidate.iterations=result.iterations;candidate.status="optimal";result=candidate;return true;}
        return false;
    };
    result.status="iteration_limit";
    for(std::size_t iteration=0;iteration<=opt.iteration_limit;++iteration) {
        result.iterations=iteration;
        if(iteration%25==0||iteration==opt.iteration_limit) {
            result.primal=x;for(std::size_t j=0;j<n;++j)result.primal[j]*=variable[j];
            result.row_dual.assign(y.begin(),y.begin()+m);for(std::size_t i=0;i<m;++i)result.row_dual[i]*=row_scale[i]/cost_scale;
            check_qp_solution(original,result,opt.tolerance);
            if(result.optimality_verified){result.status="optimal";break;}
            if(!std::isfinite(result.objective)||!std::isfinite(result.stationarity_residual)){result.status="numerical_error";break;}
            if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit){result.status="time_limit";break;}
            if(iteration==250||iteration==1000||iteration==5000){if(polish())break;}
            if(iteration&&iteration%100==0) {
                a.multiply(x,ax,opt.threads);h.multiply(x,hx,opt.threads);at.multiply(y,aty,opt.threads);
                double primal=0,dual=0;for(std::size_t i=0;i<constraints;++i)primal=std::max(primal,std::abs(ax[i]-z[i]));
                for(std::size_t j=0;j<n;++j)dual=std::max(dual,std::abs(hx[j]+c[j]+aty[j]));
                primal/=1+std::max(norm(ax),norm(z));dual/=1+std::max(norm(c),std::max(norm(hx),norm(aty)));
                double next=std::max(1e-6,std::min(1e6,rho_base*std::sqrt(std::max(1e-16,primal)/std::max(1e-16,dual))));
                if(next>5*rho_base||next<rho_base/5){rho_base=next;setup();}
            }
        }
        if(iteration==opt.iteration_limit)break;
        std::vector<double> yz(constraints),rhs,sys,r(n),direction(n),pre(n),kd;
        for(std::size_t i=0;i<constraints;++i)yz[i]=rho[i]*z[i]-y[i];at.multiply(yz,rhs,opt.threads);
        for(std::size_t j=0;j<n;++j)rhs[j]+=sigma*x[j]-c[j];
        std::vector<double> next=x;system(next,sys);
        for(std::size_t j=0;j<n;++j){r[j]=rhs[j]-sys[j];pre[j]=r[j]/preconditioner[j];}
        direction=pre;double rz=dot(r,pre);
        // Tighten the inexact linear solve as ADMM progresses. Original-model
        // KKT checks, not this inner tolerance, determine optimal termination.
        const double accuracy=std::min(1e-7,.05/std::pow(static_cast<double>(iteration+1),1.6))*(1+norm(rhs));
        for(std::size_t inner=0;inner<std::min<std::size_t>(4000,2*n+20)&&norm(r)>accuracy;++inner) {
            system(direction,kd);double denominator=dot(direction,kd);if(!(denominator>0)||!std::isfinite(denominator))break;
            double alpha=rz/denominator;for(std::size_t j=0;j<n;++j){next[j]+=alpha*direction[j];r[j]-=alpha*kd[j];pre[j]=r[j]/preconditioner[j];}
            double next_rz=dot(r,pre),beta=next_rz/rz;rz=next_rz;
            for(std::size_t j=0;j<n;++j)direction[j]=pre[j]+beta*direction[j];
            if(inner%100==0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit)break;
        }
        a.multiply(next,ax,opt.threads);
        for(std::size_t i=0;i<constraints;++i){double relaxed=1.6*ax[i]-.6*z[i];double nz=clip(relaxed+y[i]/rho[i],lower[i],upper[i]);y[i]+=rho[i]*(relaxed-nz);z[i]=nz;}
        for(std::size_t j=0;j<n;++j)x[j]=1.6*next[j]-.6*x[j];
    }
    return result;
}
}
