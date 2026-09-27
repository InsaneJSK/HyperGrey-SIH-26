#include "accelerated_qp.hpp"
#include "sparse_lp.hpp"
#include <chrono>

namespace sovereign {
#ifndef SOVEREIGN_CUDA
std::unique_ptr<BoxIteration> make_cuda_box(const CsrMatrix&,const std::vector<double>&,
    const std::vector<double>&,const std::vector<double>&,double) {
    throw std::runtime_error("CUDA backend not built; configure with -DSOVEREIGN_ENABLE_CUDA=ON on a CUDA machine");
}
std::string cuda_device_name(){return "CUDA backend not built";}
#endif
QpResult solve_accelerated_box(const QuadraticProblem& q,const QpOptions& opt,bool cuda) {
    auto start=std::chrono::steady_clock::now();validate_linear_problem(q.linear);
    if(!q.linear.rows.empty())throw std::invalid_argument("Accelerated box QP requires box constraints only");
    for(bool v:q.linear.integer)if(v)throw std::invalid_argument("Accelerated box QP requires continuous variables");
    if(opt.tolerance<=0||!std::isfinite(opt.tolerance)||opt.time_limit<0||!std::isfinite(opt.time_limit)||opt.threads<1)throw std::invalid_argument("Invalid box QP options");
    QpResult r;r.algorithm=cuda?"cuda_fista_box":"cpu_fista_box";
    if(!check_convex_hessian(q)){r.status="unsupported_curvature";return r;}
    const auto& p=q.linear;std::size_t n=p.cost.size();double sign=p.maximize?-1:1;
    std::vector<SparseVector> rows(n);std::vector<double> c=p.cost;
    for(double& v:c)v*=sign;
    for(auto h:q.hessian){rows[h.row].push_back({h.col,sign*h.value});if(h.row!=h.col)rows[h.col].push_back({h.row,sign*h.value});}
    CsrMatrix h(n,rows);rows.clear();rows.shrink_to_fit();
    double lipschitz=0;
    for(std::size_t i=0;i<n;++i){double sum=0;for(int k=h.start[i];k<h.start[i+1];++k)sum+=std::abs(h.value[k]);lipschitz=std::max(lipschitz,sum);}
    if(lipschitz==0) {
        if(cuda)throw std::invalid_argument("Zero-Hessian models use the CPU LP path");
        Options lp_options;lp_options.time_limit_seconds=opt.time_limit;lp_options.tolerance=std::min(1e-9,opt.tolerance);lp_options.iteration_limit=opt.iteration_limit;
        auto lp=solve_sparse_lp(p,lp_options);r.status=lp.solution.status;r.algorithm="zero_hessian_sparse_lp";r.iterations=lp.solution.iterations;
        r.primal=lp.solution.primal;r.row_dual.clear();if(!r.primal.empty())check_qp_solution(q,r,opt.tolerance);return r;
    }
    std::vector<double> x(n),extrapolated(n),gradient;
    for(std::size_t j=0;j<n;++j){if(p.lower[j]>p.upper[j]){r.status="infeasible_bounds";return r;}x[j]=std::max(p.lower[j],std::min(p.upper[j],0.0));}
    extrapolated=x;std::unique_ptr<BoxIteration> device;
    if(cuda)device=make_cuda_box(h,c,p.lower,p.upper,lipschitz);
    double t=1;r.status="iteration_limit";
    for(std::size_t iteration=0;iteration<=opt.iteration_limit;++iteration) {
        r.iterations=iteration;
        if(iteration%25==0||iteration==opt.iteration_limit) {
            r.primal=cuda?device->primal():x;r.row_dual.clear();check_qp_solution(q,r,opt.tolerance);
            if(r.optimality_verified){r.status="optimal";break;}
            if(!std::isfinite(r.objective)||!std::isfinite(r.stationarity_residual)){r.status="numerical_error";break;}
            if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit){r.status="time_limit";break;}
        }
        if(iteration==opt.iteration_limit)break;
        double next_t=(1+std::sqrt(1+4*t*t))/2,beta=(t-1)/next_t;t=next_t;
        if(cuda)device->step(beta);
        else {
            h.multiply(extrapolated,gradient,opt.threads);
            #ifdef _OPENMP
            #pragma omp parallel for num_threads(opt.threads) if(opt.threads>1 && n>2000) schedule(static)
            #endif
            for(long long j=0;j<static_cast<long long>(n);++j) {
                double next=std::max(p.lower[j],std::min(p.upper[j],extrapolated[j]-(gradient[j]+c[j])/lipschitz));
                extrapolated[j]=next+beta*(next-x[j]);x[j]=next;
            }
        }
    }
    return r;
}
}
