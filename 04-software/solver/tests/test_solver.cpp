#include "solver.hpp"
#include "mps.hpp"
#include "milp.hpp"
#include "qp.hpp"
#include "sparse_lp.hpp"
#include <sstream>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

void require(bool ok, const char* label) {
    if (!ok) throw std::runtime_error(label);
}
void optimal(const sovereign::Model& m, double expected) {
    auto r = sovereign::solve(m);
    require(r.status == "optimal", "Expected optimal status");
    require(r.optimality_verified, "Optimality validation failed");
    require(std::abs(r.objective - expected) < 1e-7, "Wrong objective");
    require(sovereign::check_solution(m, r.primal) < 1e-7, "Infeasible solution");
    auto sparse = sovereign::solve_sparse_lp(sovereign::linear_from_dense(m));
    if(sparse.solution.status!="optimal") std::cerr << "Sparse status: " << sparse.solution.status << '\n';
    require(sparse.solution.status=="optimal" && sparse.solution.optimality_verified,"Sparse LP optimality failed");
    require(std::abs(sparse.solution.objective-expected)<1e-7,"Sparse LP wrong objective");
}
int main() {
    try {
        optimal({{-3, -2}, {{1, 1}, {1, 0}, {0, 1}}, {4, 2, 3}}, -10);
        optimal({{40, 60}, {{-1, -1}, {1, 0}, {0, 1}, {.01, -.01}}, {-100, 80, 80, 0}}, 5000);
        optimal({{1}, {{-1}, {-2}, {1}}, {-2, -4, 2}}, 2);
        optimal({{-1, -1}, {{1, 0}, {0, 1}, {1, 1}}, {0, 1, 1}}, -1);
        optimal({{2}, {}, {}}, 0);
        optimal({{0}, {{0}}, {0}}, 0);
        optimal({{-1}, {{1e-12}}, {1e-12}}, -1);
        optimal({{-1e-12}, {{1}}, {2}}, -2e-12);
        // Beale cycling example: Bland's rule must terminate at objective -1.
        optimal({{-10, 57, 9, 24}, {{.5, -5.5, -2.5, 9}, {.5, -1.5, -.5, 1}, {1, 0, 0, 0}}, {0, 0, 1}}, -1);
        require(sovereign::solve({{1}, {{1}, {-1}}, {1, -2}}).status == "infeasible", "Missed infeasibility");
        require(sovereign::solve({{1}, {{0}}, {-1}}).status == "infeasible", "Missed inconsistent zero row");
        require(sovereign::solve({{-1}, {}, {}}).status == "unbounded", "Missed unboundedness");
        require(sovereign::solve({{-1}, {{-1}}, {-2}}).status == "unbounded", "Missed phase-II unboundedness");
        sovereign::Options options; options.iteration_limit = 0;
        require(sovereign::solve({{-1}, {{1}}, {1}}, options).status == "iteration_limit", "Iteration limit ignored");
        require(sovereign::check_solution({{1}, {{1}}, {2}}, {3}) == 1, "Checker missed row violation");
        require(sovereign::check_solution({{1}, {}, {}}, {-2}) == 2, "Checker missed bound violation");
        bool rejected = false;
        try { sovereign::solve({{1}, {{1, 2}}, {1}}); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "Malformed model accepted");
        rejected = false;
        try { sovereign::solve({{std::numeric_limits<double>::infinity()}, {}, {}}); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "Non-finite model accepted");
        std::istringstream mps("NAME CHECK\nOBJSENSE\n MAX\nROWS\n N COST\n L R\nCOLUMNS\n X COST 2 R 1\n Y COST 1 R 1\nRHS\n B R 4 COST -3\nRANGES\n RNG R 2\nBOUNDS\n LO B X -1\n UP B X 2\n FR B Y\nENDATA\n");
        auto p = sovereign::read_mps(mps);
        auto s = sovereign::standardize(p);
        auto solution = sovereign::solve(s.model);
        require(solution.status == "optimal", "MPS solve failed");
        auto x = s.recover(solution.primal);
        require(std::abs(2*x[0] + x[1] + p.offset - 9) < 1e-8, "MPS bounds, sense or offset incorrect");
        require(sovereign::original_violation(p, x, false) < 1e-8, "MPS reconstruction infeasible");
        require(p.row_lower[0] == 2 && p.row_upper[0] == 4, "Range parsing failed");
        auto sparse_mps=sovereign::solve_sparse_lp(p);
        require(sparse_mps.solution.status=="optimal"&&std::abs(sparse_mps.solution.objective-9)<1e-8,"Sparse MPS reconstruction failed");
        p.upper[0]=1;
        auto warm=sovereign::solve_sparse_lp(p,sovereign::Options(),&sparse_mps.basis);
        require(warm.warm_started&&std::abs(warm.solution.objective-8)<1e-8,"Dual-simplex warm start failed");
        auto sparse_bad=sovereign::solve_sparse_lp(sovereign::linear_from_dense({{1},{{1},{-1}},{1,-2}}));
        require(sparse_bad.solution.status=="infeasible"&&sparse_bad.solution.infeasibility_verified,"Sparse Farkas test failed");
        rejected = false;
        std::istringstream invalid("NAME BAD\nROWS\n N O\n L R\nCOLUMNS\n X O 1\nRHS\n A R 1\n B R 2\nENDATA\n");
        try { sovereign::read_mps(invalid); } catch (const std::runtime_error&) { rejected = true; }
        require(rejected, "Multiple RHS sets silently accepted");
        std::istringstream mip("NAME MIP\nOBJSENSE\n MAX\nROWS\n N COST\n L CAP\nCOLUMNS\n X COST 3 CAP 2\n Y COST 2 CAP 2\nRHS\n B CAP 3\nBOUNDS\n BV B X\n BV B Y\nENDATA\n");
        auto integer_problem = sovereign::read_mps(mip);
        auto mr = sovereign::solve_milp(integer_problem);
        require(mr.status == "optimal" || mr.status == "gap_limit", "MILP did not finish");
        require(std::abs(mr.objective - 3) < 1e-8, "Wrong integer optimum");
        require(mr.lp_iterations > 0, "MILP did not solve its relaxation");
        integer_problem.row_lower[0] = 1; integer_problem.row_upper[0] = 1;
        auto infeasible_mip = sovereign::solve_milp(integer_problem);
        require(infeasible_mip.status == "infeasible", "Missed integer infeasibility");
        sovereign::MilpOptions mo; mo.node_limit = 0;
        require(sovereign::solve_milp(integer_problem, mo).status == "node_limit", "MILP node limit ignored");
        sovereign::QuadraticProblem qp;
        qp.linear.names={"x","y"};qp.linear.cost={-2,-4};
        qp.linear.lower={-10,-10};qp.linear.upper={10,10};qp.linear.integer={false,false};
        qp.hessian={{0,0,2},{1,1,2}};
        auto qr=sovereign::solve_qp(qp);
        require(qr.status=="optimal" && std::abs(qr.objective+5)<1e-7,"Unconstrained QP failed");
        qp.linear.rows={{{0,1},{1,1}}};qp.linear.row_lower={4};qp.linear.row_upper={10};
        qr=sovereign::solve_qp(qp);
        require(qr.status=="optimal" && std::abs(qr.objective+4.5)<1e-6,"Linearly constrained QP failed");
        qp.hessian[0].value=-2;
        require(sovereign::solve_qp(qp).status=="unsupported_curvature","Nonconvex QP accepted");
        options.max_tableau_cells = 1;
        require(sovereign::solve({{1}, {{1}}, {2}}, options).status == "resource_limit", "Resource guard failed");
        std::cout << "All LP, MPS, MILP and QP correctness checks passed\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
