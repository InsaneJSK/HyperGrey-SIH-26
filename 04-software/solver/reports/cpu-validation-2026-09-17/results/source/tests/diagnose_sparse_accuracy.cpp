// Diagnostic only: includes the implementation to inspect its private basis.
// Build separately, never part of the solver library or CLI.
#include "../src/sparse_lp.cpp"
#include <iostream>
#include <iomanip>
#include <fstream>

using namespace sovereign;
static std::vector<double> residual(const Engine& e, const std::vector<double>& rhs,
                                    const std::vector<double>& x, bool transpose) {
    std::vector<long double> r(rhs.begin(),rhs.end());
    for(std::size_t j=0;j<e.m;++j)for(auto a:e.s.columns[e.basis[j]])
        if(transpose)r[j]-=static_cast<long double>(a.second)*x[a.first];
        else r[a.first]-=static_cast<long double>(a.second)*x[j];
    return std::vector<double>(r.begin(),r.end());
}
static double norm(const std::vector<double>& x) {
    double v=0;for(double a:x)v=std::max(v,std::abs(a));return v;
}
static void report(Engine& e,const LinearProblem& p,const std::vector<double>& cb,const char* label) {
    std::vector<double> canonical(e.n,0),point=e.s.shift;
    for(std::size_t i=0;i<e.m;++i)if(e.basis[i]<e.n)canonical[e.basis[i]]=e.x[i];
    for(std::size_t j=0;j<point.size();++j)for(auto a:e.s.mapping[j])point[j]+=a.second*canonical[a.first];
    long double obj=0,dual=0;
    for(std::size_t j=0;j<e.n;++j)obj+=static_cast<long double>(e.s.cost[j])*canonical[j];
    for(std::size_t i=0;i<e.m;++i)dual+=static_cast<long double>(e.s.rhs[i])*std::min(0.,e.pi[i]);
    auto r=residual(e,e.s.rhs,e.x,false);
    std::size_t worst=std::max_element(r.begin(),r.end(),[](double a,double b){return std::abs(a)<std::abs(b);})-r.begin();
    std::cout<<label<<" rhs_residual="<<norm(r)<<" worst_row="<<worst<<" rhs="<<e.s.rhs[worst]
        <<" transpose_residual="<<norm(residual(e,cb,e.pi,true))<<" violation="<<original_violation(p,point,false)
        <<" objective="<<static_cast<double>(obj)<<" dual="<<static_cast<double>(dual)
        <<" gap="<<static_cast<double>(std::abs(obj-dual)/(1+std::max(std::abs(obj),std::abs(dual))))
        <<" eta_updates="<<e.updates.size()<<" pivots="<<e.iterations<<" factors="<<e.factorizations<<"\n";
}
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::cout<<std::setprecision(17);
    std::ifstream input(argv[1]);LinearProblem p=read_mps(input); Options opt;
    Canonical s=canonicalize(p,opt.scaling,false);Engine e(opt,s);
    std::vector<double> phase(e.original,0),cost(e.original,0);e.basis.resize(e.m);
    for(std::size_t j=0;j<e.n;++j)cost[j]=s.cost[j];
    for(std::size_t i=0;i<e.m;++i) {
        e.basis[i]=e.n+i;
        if(s.rhs[i]<0){e.basis[i]=s.columns.size();s.columns.push_back({{i,-1}});phase.push_back(1);}
    }
    if(!e.refactor())return 3;
    std::cout<<"phase1="<<e.optimize(phase,phase.size(),false,true)<<"\n";
    for(std::size_t i=0;i<e.m;++i)if(e.artificial(e.basis[i]))return 4;
    cost.resize(s.columns.size(),0);std::cout<<"phase2="<<e.optimize(cost,e.original)<<"\n";
    std::vector<double> cb(e.m);for(std::size_t i=0;i<e.m;++i)cb[i]=cost[e.basis[i]];
    report(e,p,cb,"original");
    const auto saved_x=e.x,saved_pi=e.pi;
    for(int k=0;k<3;++k) {
        auto dx=e.ftran(residual(e,s.rhs,e.x,false));auto dy=e.btran(residual(e,cb,e.pi,true));
        for(std::size_t i=0;i<e.m;++i){e.x[i]+=dx[i];e.pi[i]+=dy[i];}
        report(e,p,cb,("refinement"+std::to_string(k+1)).c_str());
    }
    e.x=saved_x;e.pi=saved_pi;if(!e.refactor())return 5;e.values(cost);report(e,p,cb,"fresh_factor");
    return 0;
}
