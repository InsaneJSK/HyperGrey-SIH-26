#include "qp.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace sovereign {
namespace {
struct Reader {
    std::istream& in;
    explicit Reader(std::istream& stream) : in(stream) {}
    std::vector<std::string> pending;
    std::size_t at = 0;
    std::string token() {
        while (at == pending.size()) {
            std::string line;
            if (!std::getline(in, line)) throw std::runtime_error("Truncated QPLIB input");
            auto comment = line.find('#'); if (comment != std::string::npos) line.resize(comment);
            std::istringstream s(line); pending.clear(); at = 0;
            std::string v; while (s >> v) pending.push_back(v);
        }
        return pending[at++];
    }
    long double number() {
        std::string v = token(); std::size_t used;
        long double x = std::stold(v, &used);
        if (used != v.size() || !std::isfinite(x)) throw std::runtime_error("Invalid QPLIB number");
        return x;
    }
    std::size_t count(std::size_t maximum = 5000000) {
        long double v = number();
        if (v < 0 || v > maximum || std::floor(v) != v) throw std::runtime_error("Invalid or oversized QPLIB count");
        return static_cast<std::size_t>(v);
    }
    std::size_t index(std::size_t n) {
        auto i = count(n); if (i == 0) throw std::runtime_error("QPLIB indices are one-based"); return i-1;
    }
    std::vector<double> vector(std::size_t n, long double infinity = std::numeric_limits<long double>::infinity()) {
        auto convert = [&](long double v) {
            if (std::abs(v) >= infinity) return v < 0 ? -std::numeric_limits<double>::infinity() : std::numeric_limits<double>::infinity();
            if (std::abs(v) > std::numeric_limits<double>::max()) throw std::runtime_error("QPLIB value overflow");
            return static_cast<double>(v);
        };
        double def = convert(number()); std::vector<double> result(n, def);
        auto entries = count(n); std::set<std::size_t> seen;
        for (std::size_t k = 0; k < entries; ++k) {
            auto j = index(n); if (!seen.insert(j).second) throw std::runtime_error("Duplicate QPLIB vector entry");
            result[j] = convert(number());
        }
        return result;
    }
};
double clip(double x, double lo, double up) { return std::max(lo, std::min(up, x)); }
std::vector<double> multiply(const QuadraticProblem& q, const std::vector<double>& x) {
    std::vector<double> result(x.size(), 0);
    for (auto h : q.hessian) {
        result[h.row] += h.value*x[h.col];
        if (h.row != h.col) result[h.col] += h.value*x[h.row];
    }
    return result;
}
}

QuadraticProblem read_qplib(std::istream& input) {
    Reader r(input); QuadraticProblem q; auto& p = q.linear;
    p.name = r.token(); std::string type = r.token(), sense = r.token();
    if (type.size()!=3 || type[1]!='C' || std::string("CDQ").find(type[0])==std::string::npos ||
        std::string("NBL").find(type[2])==std::string::npos)
        throw std::runtime_error("unsupported_qplib_type: continuous quadratic objective with linear/box constraints required");
    if (sense != "minimize" && sense != "maximize") throw std::runtime_error("Invalid QPLIB objective sense");
    p.maximize = sense == "maximize";
    auto n = r.count(100000); if (!n) throw std::runtime_error("Empty QPLIB model");
    auto m = type[2]=='L' ? r.count(100000) : 0;
    auto nz = r.count();
    std::set<std::pair<std::size_t,std::size_t> > seen;
    for (std::size_t k=0;k<nz;++k) {
        auto i=r.index(n), j=r.index(n); double v=static_cast<double>(r.number());
        if (i<j || !seen.insert({i,j}).second || !std::isfinite(v)) throw std::runtime_error("Invalid QPLIB Hessian entry");
        // QPLIB stores half*x^T Q_lower*x, so off-diagonal entries contribute
        // half their listed value to each side of the symmetric Hessian.
        q.hessian.push_back({i,j,i==j?v:0.5*v});
    }
    p.cost=r.vector(n); p.offset=static_cast<double>(r.number());
    p.rows.resize(m);
    if (m) {
        auto count=r.count(); std::set<std::pair<std::size_t,std::size_t> > entries;
        for (std::size_t k=0;k<count;++k) {
            auto i=r.index(m),j=r.index(n);double v=static_cast<double>(r.number());
            if (!entries.insert({i,j}).second || !std::isfinite(v)) throw std::runtime_error("Invalid QPLIB matrix entry");
            p.rows[i].push_back({j,v});
        }
    }
    long double infinity=r.number(); if (infinity<=0) throw std::runtime_error("Invalid infinity marker");
    if (m) { p.row_lower=r.vector(m,infinity); p.row_upper=r.vector(m,infinity); }
    if (type[2]!='N') { p.lower=r.vector(n,infinity); p.upper=r.vector(n,infinity); }
    else { p.lower.assign(n,-std::numeric_limits<double>::infinity()); p.upper.assign(n,std::numeric_limits<double>::infinity()); }
    // Parse but deliberately do not use published starting points in benchmarks.
    r.vector(n); if (m) r.vector(m); r.vector(n);
    p.names.resize(n); p.integer.assign(n,false);
    for (std::size_t j=0;j<n;++j) p.names[j]="x"+std::to_string(j+1);
    auto names=r.count(n); std::set<std::size_t> named;
    for (std::size_t k=0;k<names;++k) {
        auto j=r.index(n);if (!named.insert(j).second) throw std::runtime_error("Duplicate variable name entry");p.names[j]=r.token();
    }
    names=r.count(m); named.clear();
    for (std::size_t k=0;k<names;++k) { auto i=r.index(m); if (!named.insert(i).second) throw std::runtime_error("Duplicate row name entry");r.token(); }
    if (r.at<r.pending.size()) throw std::runtime_error("Unexpected trailing QPLIB tokens");
    std::string line;
    while(std::getline(input,line)) {
        line=line.substr(0,line.find('#'));
        if(line.find_first_not_of(" \t\r\n")!=std::string::npos) throw std::runtime_error("Unexpected trailing QPLIB content");
    }
    return q;
}

QpResult solve_qp_legacy(const QuadraticProblem& original, double limit, std::size_t max_iterations, double tol) {
    if (!std::isfinite(limit)||limit<0||!std::isfinite(tol)||tol<=0) throw std::invalid_argument("Invalid QP options");
    auto start=std::chrono::steady_clock::now();
    QuadraticProblem q=original; auto& p=q.linear;
    validate_linear_problem(p);
    for(bool integer:p.integer) if(integer) throw std::invalid_argument("QP requires continuous variables");
    const std::size_t n=p.cost.size(),m=p.rows.size();
    QpResult result;
    if (!n||p.lower.size()!=n||p.upper.size()!=n||p.row_lower.size()!=m||p.row_upper.size()!=m)
        throw std::invalid_argument("Invalid QP dimensions");
    double sign=p.maximize?-1:1;
    for(double& c:p.cost) { c*=sign; if(!std::isfinite(c)) throw std::invalid_argument("Non-finite QP cost"); }
    p.offset*=sign;
    std::vector<double> diagonal(n,0), radius(n,0), hsums(n,0);
    for(auto& h:q.hessian) {
        if(h.row>=n||h.col>=n||!std::isfinite(h.value)) throw std::invalid_argument("Invalid QP Hessian");
        h.value*=sign;hsums[h.row]+=std::abs(h.value);
        if(h.row==h.col) diagonal[h.row]+=h.value;
        else {radius[h.row]+=std::abs(h.value);radius[h.col]+=std::abs(h.value);hsums[h.col]+=std::abs(h.value);}
    }
    bool diagonal_dominant=true;
    for(std::size_t j=0;j<n;++j) {
        if(std::isnan(p.lower[j])||std::isnan(p.upper[j])) throw std::invalid_argument("NaN QP bound");
        if(p.lower[j]>p.upper[j]) {result.status="infeasible_bounds";return result;}
        if(diagonal[j]<radius[j]) diagonal_dominant=false;
    }
    if(!diagonal_dominant) {
        // Conservative PSD test: small matrices use unpivoted LDL; large
        // non-diagonally-dominant matrices are outside this initial implementation.
        if(n>200) {result.status="unsupported_curvature";return result;}
        std::vector<std::vector<double> > matrix(n,std::vector<double>(n,0));
        for(auto h:q.hessian) {matrix[h.row][h.col]+=h.value;if(h.row!=h.col)matrix[h.col][h.row]+=h.value;}
        for(std::size_t k=0;k<n;++k) {
            if(matrix[k][k]<0) {result.status="unsupported_curvature";return result;}
            if(matrix[k][k]==0) {
                for(std::size_t i=k+1;i<n;++i) if(matrix[i][k]!=0) {result.status="unsupported_curvature";return result;}
            } else for(std::size_t i=k+1;i<n;++i) for(std::size_t j=i;j<n;++j) {
                matrix[j][i]-=matrix[i][k]*matrix[j][k]/matrix[k][k];matrix[i][j]=matrix[j][i];
            }
        }
    }
    double hnorm=*std::max_element(hsums.begin(),hsums.end());
    std::vector<double> colsum(n,0);double maxrow=0;
    for(std::size_t i=0;i<m;++i) {
        if(p.row_lower[i]>p.row_upper[i]) {result.status="infeasible_bounds";return result;}
        double sum=0;
        for(auto a:p.rows[i]) {if(a.first>=n||!std::isfinite(a.second))throw std::invalid_argument("Invalid QP row");sum+=std::abs(a.second);colsum[a.first]+=std::abs(a.second);}
        maxrow=std::max(maxrow,sum);
    }
    double anorm=std::sqrt(maxrow*(*std::max_element(colsum.begin(),colsum.end())));
    if(!std::isfinite(anorm)||!std::isfinite(hnorm)) {result.status="numerical_error";return result;}
    double tau=.9/std::max(1e-12,hnorm+anorm),sigma=anorm>0?.9/anorm:1;
    std::vector<double> x(n),extrapolated(n),y(m,0);double momentum=1;
    for(std::size_t j=0;j<n;++j) x[j]=clip(0,p.lower[j],p.upper[j]);
    extrapolated=x;result.status="iteration_limit";
    for(std::size_t iteration=0;iteration<=max_iterations;++iteration) {
        result.iterations=iteration;
        if(iteration%25==0 || iteration==max_iterations) {
            auto gradient=multiply(q,x);double objective=p.offset;
            for(std::size_t j=0;j<n;++j) {objective+=.5*x[j]*gradient[j]+p.cost[j]*x[j];gradient[j]+=p.cost[j];}
            double complementarity=0;
            for(std::size_t i=0;i<m;++i) {
                double ax=0;for(auto a:p.rows[i]) {ax+=a.second*x[a.first];gradient[a.first]+=a.second*y[i];}
                double target=y[i]>=0?p.row_upper[i]:p.row_lower[i];
                if(y[i]!=0) {
                    double violation=std::abs(y[i]*(target-ax))/(1+std::abs(objective));
                    if(!std::isfinite(violation)) violation=std::numeric_limits<double>::infinity();
                    complementarity=std::max(complementarity,violation);
                }
            }
            result.primal_residual=original_violation(p,x,true);result.stationarity_residual=0;
            for(std::size_t j=0;j<n;++j) {
                double residual=std::abs(x[j]-clip(x[j]-gradient[j],p.lower[j],p.upper[j]))/(1+std::abs(x[j]));
                if(!std::isfinite(gradient[j])||!std::isfinite(residual)) residual=std::numeric_limits<double>::infinity();
                result.stationarity_residual=std::max(result.stationarity_residual,residual);
            }
            result.complementarity_residual=complementarity;result.objective=sign*objective;
            if(!std::isfinite(objective)||!std::isfinite(result.stationarity_residual)) {result.status="numerical_error";break;}
            if(std::max(result.primal_residual,std::max(result.stationarity_residual,complementarity))<=tol) {result.status="optimal";break;}
            if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=limit) {result.status="time_limit";break;}
        }
        if(iteration==max_iterations) break;
        std::vector<double> next(n);
        if(m==0) {
            auto g=multiply(q,extrapolated);
            for(std::size_t j=0;j<n;++j) next[j]=clip(extrapolated[j]-(g[j]+p.cost[j])/std::max(hnorm,1e-12),p.lower[j],p.upper[j]);
            double next_momentum=(1+std::sqrt(1+4*momentum*momentum))/2;
            for(std::size_t j=0;j<n;++j) extrapolated[j]=next[j]+((momentum-1)/next_momentum)*(next[j]-x[j]);
            momentum=next_momentum;
        } else {
            for(std::size_t i=0;i<m;++i) {
                double ax=0;for(auto a:p.rows[i]) ax+=a.second*extrapolated[a.first];
                double v=y[i]+sigma*ax;y[i]=v-sigma*clip(v/sigma,p.row_lower[i],p.row_upper[i]);
            }
            auto g=multiply(q,x);
            for(std::size_t i=0;i<m;++i)for(auto a:p.rows[i])g[a.first]+=a.second*y[i];
            for(std::size_t j=0;j<n;++j) {next[j]=clip(x[j]-tau*(g[j]+p.cost[j]),p.lower[j],p.upper[j]);extrapolated[j]=2*next[j]-x[j];}
        }
        x.swap(next);
    }
    result.primal=x;result.row_dual=y;return result;
}
}
