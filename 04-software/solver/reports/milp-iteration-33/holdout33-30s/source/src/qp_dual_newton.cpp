#include "qp.hpp"
#include "sparse_matrix.hpp"
#include <chrono>

namespace sovereign {
// For positive diagonal Hessians and equality rows, minimizing the Lagrangian
// over the box is separable. Newton iterations solve the concave dual using a
// matrix-free active-set Schur system; every accepted optimum is checked on q.
QpResult solve_diagonal_equalities(const QuadraticProblem& q,const QpOptions& opt) {
    QpResult result;result.status="unsupported_structure";result.algorithm="diagonal_qp_dual_newton";
    auto start=std::chrono::steady_clock::now();
    const auto& p=q.linear;std::size_t n=p.cost.size(),m=p.rows.size();double sign=p.maximize?-1:1;
    if(!m)return result;
    for(std::size_t i=0;i<m;++i)if(p.row_lower[i]!=p.row_upper[i]||!std::isfinite(p.row_lower[i]))return result;
    std::vector<double> h(n,0),units(n),lo(n),up(n),c(n),row_units(m),b(m);
    for(auto a:q.hessian){if(a.row!=a.col&&a.value!=0)return result;h[a.row]+=sign*a.value;}
    for(std::size_t j=0;j<n;++j){if(h[j]<=0||!std::isfinite(h[j]))return result;units[j]=1/std::sqrt(h[j]);lo[j]=p.lower[j]/units[j];up[j]=p.upper[j]/units[j];c[j]=sign*p.cost[j]*units[j];}
    std::vector<SparseVector> rows=p.rows;
    for(std::size_t i=0;i<m;++i){double maximum=0;for(auto& a:rows[i]){a.second*=units[a.first];maximum=std::max(maximum,std::abs(a.second));}row_units[i]=maximum?1/maximum:1;for(auto& a:rows[i])a.second*=row_units[i];b[i]=p.row_lower[i]*row_units[i];}
    // Whiten curvature first, then normalize the magnitude of the problem.
    // If w = scale*z, divide the objective by scale^2 and equalities by
    // scale. The Schur matrix stays unchanged; original row multipliers
    // are scale*row_units*y, not row_units*y.
    double magnitude=1;
    if(opt.scaling){
        for(std::size_t j=0;j<n;++j){magnitude=std::max(magnitude,std::abs(c[j]));magnitude=std::max(magnitude,std::abs(std::max(lo[j],std::min(up[j],0.0))));}
        for(double rhs:b)magnitude=std::max(magnitude,std::abs(rhs));
    }
    for(std::size_t j=0;j<n;++j){units[j]*=magnitude;lo[j]/=magnitude;up[j]/=magnitude;c[j]/=magnitude;}
    for(std::size_t i=0;i<m;++i){b[i]/=magnitude;row_units[i]*=magnitude;}
    for(std::size_t j=0;j<n;++j)if(!std::isfinite(units[j])||!std::isfinite(c[j])||std::isnan(lo[j])||std::isnan(up[j])){result.status="numerical_scaling_failure";return result;}
    for(std::size_t i=0;i<m;++i)if(!std::isfinite(b[i])||!std::isfinite(row_units[i])){result.status="numerical_scaling_failure";return result;}
    CsrMatrix a(n,rows),at=a.transpose();std::vector<double> y(m,0),x,gradient,mask;
    auto norm=[](const std::vector<double>& v){double value=0;for(double x:v)value=std::max(value,std::abs(x));return value;};
    auto dot=[](const std::vector<double>& a,const std::vector<double>& b){long double sum=0;for(std::size_t j=0;j<a.size();++j)sum+=static_cast<long double>(a[j])*b[j];return static_cast<double>(sum);};
    auto evaluate=[&](const std::vector<double>& dual,std::vector<double>& primal,std::vector<double>& g,std::vector<double>& free) {
        at.multiply(dual,primal,opt.threads);free.resize(n);long double value=0;
        for(std::size_t j=0;j<n;++j){double raw=-(primal[j]+c[j]);free[j]=(raw>=lo[j]&&raw<=up[j])?1:0;primal[j]=std::max(lo[j],std::min(up[j],raw));value+=.5L*primal[j]*primal[j]+c[j]*primal[j];}
        a.multiply(primal,g,opt.threads);for(std::size_t i=0;i<m;++i){g[i]-=b[i];value+=static_cast<long double>(dual[i])*g[i];}return value;
    };
    result.status="iteration_limit";
    for(std::size_t iteration=0;iteration<std::min<std::size_t>(opt.iteration_limit,500);++iteration) {
        long double value=evaluate(y,x,gradient,mask);result.iterations=iteration;result.primal=x;result.row_dual=y;
        for(std::size_t j=0;j<n;++j)result.primal[j]*=units[j];for(std::size_t i=0;i<m;++i)result.row_dual[i]*=row_units[i];
        check_qp_solution(q,result,opt.tolerance);if(result.optimality_verified){result.status="optimal";return result;}
        if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit){result.status="time_limit";return result;}
        std::vector<double> diagonal(m,0),r=gradient,z(m),direction(m),step(m,0),mv,work;
        for(std::size_t i=0;i<m;++i)for(auto v:rows[i])diagonal[i]+=v.second*v.second*mask[v.first];
        double regularization=1e-12*(1+norm(diagonal));for(std::size_t i=0;i<m;++i){diagonal[i]+=regularization;z[i]=r[i]/diagonal[i];}
        direction=z;double rz=dot(r,z),accuracy=std::max(1e-12,std::min(.01,std::sqrt(norm(gradient)))*norm(gradient));
        for(std::size_t inner=0;inner<std::min<std::size_t>(10000,4*m+50)&&norm(r)>accuracy;++inner) {
            at.multiply(direction,work,opt.threads);for(std::size_t j=0;j<n;++j)work[j]*=mask[j];a.multiply(work,mv,opt.threads);
            for(std::size_t i=0;i<m;++i)mv[i]+=regularization*direction[i];double denominator=dot(direction,mv);
            if(!(denominator>0)||!std::isfinite(denominator))break;
            double alpha=rz/denominator;for(std::size_t i=0;i<m;++i){step[i]+=alpha*direction[i];r[i]-=alpha*mv[i];z[i]=r[i]/diagonal[i];}
            double next=dot(r,z),beta=next/rz;rz=next;for(std::size_t i=0;i<m;++i)direction[i]=z[i]+beta*direction[i];
            if(inner%100==0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit)break;
        }
        double slope=dot(gradient,step);if(!(slope>0)||!std::isfinite(slope)){step=gradient;slope=dot(gradient,gradient);}
        bool accepted=false;double length=1;std::vector<double> next_y(m),next_x,next_gradient,next_mask;
        for(int backtrack=0;backtrack<60;++backtrack){for(std::size_t i=0;i<m;++i)next_y[i]=y[i]+length*step[i];long double next=evaluate(next_y,next_x,next_gradient,next_mask);
            if(std::isfinite(next)&&next>=value+1e-4*length*slope-1e-13*(1+std::abs(value))){y.swap(next_y);accepted=true;break;}length*=.5;}
        if(!accepted){result.status="numerical_stall";return result;}
    }
    return result;
}
}
