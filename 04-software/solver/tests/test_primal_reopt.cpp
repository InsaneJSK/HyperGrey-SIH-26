#include "milp.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace sovereign;
void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
void optimal(const LinearProblem& p,const SparseLpResult& r,double expected){
    if(r.solution.status!="optimal"||!r.solution.optimality_verified)throw std::runtime_error("Unverified optimum: "+r.solution.status+" expected "+std::to_string(expected));
    require(original_violation(p,r.solution.primal,false)<=1e-7,"Original feasibility failed");
    require(std::abs(r.solution.objective-expected)<1e-7,"Wrong objective");
}
double number(std::istream& in){std::string s;in>>s;return std::stod(s);}
std::vector<SparseVector> sparse(std::istream& in){
    std::size_t m;in>>m;require(m<=100000,"Too many replay rows");std::vector<SparseVector> rows(m);
    for(auto& row:rows){std::size_t size;in>>size;require(size<=200000,"Too many replay entries");for(std::size_t k=0;k<size;++k){std::size_t j;in>>j;row.push_back({j,number(in)});}}
    return rows;
}
void replay(const char* path){
    std::ifstream in(path);require(bool(in),"Replay missing");LinearProblem p;LpBasis basis;Options o;
    std::size_t n,m;in>>n>>m>>p.maximize;require(n<=10000&&m<=20000,"Replay too large");p.offset=number(in);
    in>>o.scaling>>o.compact_equalities>>o.refine_basis>>o.refine_at_checks;o.time_limit_seconds=10;
    p.cost.resize(n);p.lower.resize(n);p.upper.resize(n);p.integer.assign(n,false);p.names.resize(n);
    for(std::size_t j=0;j<n;++j){p.cost[j]=number(in);p.lower[j]=number(in);p.upper[j]=number(in);p.names[j]="x"+std::to_string(j);}
    p.row_lower.resize(m);p.row_upper.resize(m);for(std::size_t i=0;i<m;++i){p.row_lower[i]=number(in);p.row_upper[i]=number(in);}p.rows=sparse(in);require(p.rows.size()==m,"Replay row mismatch");
    std::size_t size;in>>basis.structural_columns>>basis.compact_equalities>>basis.reduced_upper_bounds>>size;
    basis.columns.resize(size);for(auto& j:basis.columns)in>>j;
    auto structure=std::make_shared<LpBasisStructure>();structure->rows=sparse(in);structure->mapping=sparse(in);
    in>>size;structure->equality.resize(size);for(std::size_t i=0;i<size;++i){int b;in>>b;structure->equality[i]=b;}basis.structure=structure;require(bool(in),"Malformed replay");
    for(int mode=0;mode<4;++mode){
        o.primal_warm_start=mode>=2;o.warm_infeasibility_certificate=mode==3;
        auto r=solve_sparse_lp(p,o,mode?&basis:nullptr);const auto& s=r.solution;
        std::cout<<std::setprecision(17)<<"{\"mode\":\""<<(mode==0?"cold":mode==1?"dual_only":mode==2?"adaptive":"certified")<<"\",\"status\":\""<<s.status<<"\",\"verified\":"<<(s.optimality_verified?"true":"false")
            <<",\"infeasibility_verified\":"<<(s.infeasibility_verified?"true":"false")<<",\"certificate_attempts\":"<<r.reopt.certificate_attempts<<",\"certificate_accepted\":"<<r.reopt.certificate_accepted
            <<",\"objective\":"<<s.objective<<",\"iterations\":"<<s.iterations<<",\"warm_started\":"<<(r.warm_started?"true":"false")
            <<",\"compatible\":"<<r.reopt.compatible<<",\"primal_restarts\":"<<r.reopt.primal<<",\"dual_restarts\":"<<r.reopt.dual
            <<",\"factorizations\":"<<r.factorizations<<",\"phase_one_iterations\":"<<r.reopt.phase_one_iterations<<",\"primal\":[";
        for(std::size_t j=0;j<s.primal.size();++j){if(j)std::cout<<',';std::cout<<s.primal[j];}std::cout<<"]}\n";
    }
}
int main(int argc,char** argv){try{
    if(argc==3&&std::string(argv[1])=="--replay"){replay(argv[2]);return 0;}
    require(argc==1,"Unexpected arguments");Options o;o.primal_warm_start=true;o.refine_basis=true;o.refine_at_checks=true;
    std::size_t cases=0;
    for(bool scaling:{false,true})for(bool compact:{false,true})for(bool maximum:{false,true})for(double shift:{-3.,0.,2.}){
        std::cout<<"case "<<scaling<<' '<<compact<<' '<<maximum<<' '<<shift<<'\n';
        auto p=linear_from_dense({{1,2},{{-1,-1}},{-1}});p.lower={shift,shift};p.upper={shift+1,shift+1};p.row_upper={-1-2*shift};
        p.maximize=maximum;if(maximum)for(auto& c:p.cost)c=-c;
        o.scaling=scaling;o.compact_equalities=compact;auto old=solve_sparse_lp(p,o);optimal(p,old,(maximum?-1:1)*(1+3*shift));
        require(bool(old.basis.structure),"Missing immutable structure");
        auto q=p;std::swap(q.cost[0],q.cost[1]);auto r=solve_sparse_lp(q,o,&old.basis);optimal(q,r,(maximum?-1:1)*(1+3*shift));
        require(r.reopt.primal==1&&r.reopt.verified==1&&r.warm_started&&r.reopt.phase_one_iterations==0,"Objective change did not reoptimize primal basis");
        q=p;q.upper[0]=shift+.25;r=solve_sparse_lp(q,o,&old.basis);optimal(q,r,(maximum?-1:1)*(1.75+3*shift));
        require(r.reopt.dual==1&&r.warm_started,"Bound change did not use dual basis");
        q.upper[1]=shift+.25;std::swap(q.cost[0],q.cost[1]);r=solve_sparse_lp(q,o,&old.basis);
        require(r.solution.status=="infeasible"&&r.solution.infeasibility_verified,"Cold fallback did not verify infeasibility");
        require(r.reopt.rejected==1&&!r.warm_started,"Neither-feasible basis accepted");
        q=p;q.rows[0][0].second=-2;q.row_upper[0]=-1-3*shift;r=solve_sparse_lp(q,o,&old.basis);auto cold=solve_sparse_lp(q,o);optimal(q,r,cold.solution.objective);
        require(r.reopt.compatible==0&&!r.warm_started,"Same-shape different matrix reused");
        q=p;q.lower[0]=-INFINITY;r=solve_sparse_lp(q,o,&old.basis);cold=solve_sparse_lp(q,o);optimal(q,r,cold.solution.objective);require(r.reopt.compatible==0,"Different variable mapping accepted");
        for(int bad=0;bad<3;++bad){auto b=old.basis;if(bad==0)b.columns[0]=std::numeric_limits<std::size_t>::max();else if(bad==1)b.columns[0]=b.columns[1];else b.reduced_upper_bounds=true;
            r=solve_sparse_lp(p,o,&b);optimal(p,r,old.solution.objective);require(!r.warm_started&&r.reopt.compatible==0,"Invalid basis accepted");}
        o.time_limit_seconds=0;r=solve_sparse_lp(p,o,&old.basis);require(r.solution.status=="time_limit"&&!r.solution.optimality_verified,"Zero time ignored");o.time_limit_seconds=30;
        o.iteration_limit=0;q=p;std::swap(q.cost[0],q.cost[1]);r=solve_sparse_lp(q,o,&old.basis);require(r.solution.status=="iteration_limit"&&!r.solution.optimality_verified,"Zero pivots ignored");o.iteration_limit=10000;
        Options off=o;off.primal_warm_start=false;r=solve_sparse_lp(q,off,&old.basis);optimal(q,r,(maximum?-1:1)*(1+3*shift));require(r.reopt.calls==0&&!r.basis.structure,"Disabled path changed metadata");
        ++cases;
    }
    // Free and upper-only variables, equalities, and alternate-branch parent reuse.
    for(bool compact:{false,true}){
        std::cout<<"free/equality "<<compact<<'\n';
        auto p=linear_from_dense({{1,2},{{1,1}},{1}});p.lower={-INFINITY,-2};p.upper={2,2};p.row_lower={1};o.compact_equalities=compact;
        auto a=solve_sparse_lp(p,o);optimal(p,a,0);auto q=p;q.cost={2,1};auto b=solve_sparse_lp(q,o,&a.basis);optimal(q,b,0);
        require(b.reopt.primal==1&&b.warm_started,"Upper-only objective restart missed");
        p.lower[0]=-INFINITY;p.upper[0]=INFINITY;a=solve_sparse_lp(p,o);optimal(p,a,-1);q=p;q.cost={2,1};b=solve_sparse_lp(q,o,&a.basis);optimal(q,b,0);
        q=p;q.upper[1]=1;b=solve_sparse_lp(q,o,&a.basis);optimal(q,b,-1);
        q=p;q.lower[1]=0;b=solve_sparse_lp(q,o,&a.basis);optimal(q,b,1);
    }
    o.compact_equalities=false;auto p=linear_from_dense({{1},{},{}});auto a=solve_sparse_lp(p,o);p.cost={-1};auto u=solve_sparse_lp(p,o,&a.basis);
    require(u.solution.status=="unbounded"&&u.solution.unboundedness_verified,"Unbounded restart uncertified");
    MilpOptions m;m.lp.primal_warm_start=true;bool rejected=false;try{solve_milp(p,m);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"General MILP reoptimizer allowed");
    std::cout<<cases<<" transformed objective/bound/structure/budget cases; free/upper-only/equality/alternate/unbounded and private-only guards PASS\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
