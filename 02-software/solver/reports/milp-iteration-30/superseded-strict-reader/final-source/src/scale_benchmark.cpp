#include "accelerated_qp.hpp"
#include <chrono>
#include <iostream>
#include <iomanip>
#include <cstdlib>

int main(int argc,char** argv) {
    try {
        std::size_t n=argc>1?std::stoull(argv[1]):10000;
        std::string backend=argc>2?argv[2]:"cpu";int threads=argc>3?std::stoi(argv[3]):1;
        double limit=argc>4?std::stod(argv[4]):120;
        if(n<2||n>2000000||(backend!="cpu"&&backend!="cuda"))throw std::invalid_argument("Usage: solver_scale [n:2..2000000] [cpu|cuda] [threads] [seconds]");
        sovereign::QuadraticProblem q;auto& p=q.linear;p.name="seeded_tridiagonal_convex_box";
        p.names.resize(n);p.cost.resize(n);p.lower.assign(n,0);p.upper.assign(n,3);p.integer.assign(n,false);
        std::vector<double> optimum(n);unsigned state=26119;
        for(std::size_t j=0;j<n;++j){state=1664525u*state+1013904223u;optimum[j]=.5+double(state%10001)/10000;p.names[j]="x"+std::to_string(j);}
        long double expected=0;
        for(std::size_t j=0;j<n;++j){q.hessian.push_back({j,j,2.02});if(j)q.hessian.push_back({j,j-1,-1});double hx=2.02*optimum[j]-(j?optimum[j-1]:0)-(j+1<n?optimum[j+1]:0);p.cost[j]=-hx;expected-=.5L*optimum[j]*hx;}
        sovereign::QpOptions o;o.time_limit=limit;o.iteration_limit=20000;o.tolerance=1e-7;o.threads=threads;
        auto start=std::chrono::steady_clock::now();auto r=sovereign::solve_accelerated_box(q,o,backend=="cuda");
        double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count(),error=0;
        for(std::size_t j=0;j<r.primal.size();++j)error=std::max(error,std::abs(r.primal[j]-optimum[j]));
        double objective_error=std::abs(r.objective-static_cast<double>(expected))/(1+std::abs(static_cast<double>(expected)));
        bool passed=r.status=="optimal"&&r.optimality_verified&&objective_error<=1e-8&&error<1e-4;
        std::cout<<std::setprecision(17)<<"{\"status\":\""<<r.status<<"\",\"passed\":"<<(passed?"true":"false")<<",\"backend\":\""<<backend<<"\",\"columns\":"<<n<<",\"rows\":0,\"hessian_nonzeros_lower\":"<<q.hessian.size()<<",\"threads\":"<<threads<<",\"solve_seconds\":"<<seconds<<",\"iterations\":"<<r.iterations<<",\"objective\":"<<r.objective<<",\"known_objective\":"<<static_cast<double>(expected)<<",\"relative_objective_error\":"<<objective_error<<",\"max_solution_error\":"<<error<<",\"stationarity_residual\":"<<r.stationarity_residual<<",\"synthetic\":true}\n";
        return passed?0:1;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
}
