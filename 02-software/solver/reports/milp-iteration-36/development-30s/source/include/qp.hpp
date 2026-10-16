#pragma once
#include "mps.hpp"

namespace sovereign {
struct QuadraticTerm { std::size_t row, col; double value; };
struct QuadraticProblem {
    LinearProblem linear;
    // Symmetric Hessian: one lower-triangle entry; off-diagonal mirrored.
    std::vector<QuadraticTerm> hessian;
};
struct QpResult {
    std::string status;
    std::vector<double> primal, row_dual;
    double objective = std::numeric_limits<double>::quiet_NaN();
    double primal_residual = std::numeric_limits<double>::infinity();
    double stationarity_residual = std::numeric_limits<double>::infinity();
    double complementarity_residual = std::numeric_limits<double>::infinity();
    std::size_t iterations = 0;
    double dual_bound=-std::numeric_limits<double>::infinity();
    double relative_gap=std::numeric_limits<double>::infinity();
    bool optimality_verified=false;
    std::string algorithm;
};
struct QpOptions {
    double time_limit=30,tolerance=1e-7;
    std::size_t iteration_limit=200000;
    int threads=1;
    bool scaling=true;
};
QuadraticProblem read_qplib(std::istream&);
QpResult solve_qp(const QuadraticProblem&, double time_limit = 30, std::size_t iterations = 200000, double tolerance = 1e-7);
QpResult solve_qp_admm(const QuadraticProblem&,const QpOptions& = QpOptions());
bool check_convex_hessian(const QuadraticProblem&);
void check_qp_solution(const QuadraticProblem&,QpResult&,double tolerance);
}
