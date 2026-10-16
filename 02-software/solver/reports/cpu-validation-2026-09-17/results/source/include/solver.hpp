#pragma once
#include <cstddef>
#include <string>
#include <vector>

namespace sovereign {
// Initial subset: minimize c*x, A*x <= b, x >= 0.
struct Model {
    std::vector<double> cost;
    std::vector<std::vector<double> > rows;
    std::vector<double> rhs;
};
struct Options {
    double tolerance = 1e-9;
    std::size_t iteration_limit = 10000;
    double time_limit_seconds = 30;
    std::size_t max_tableau_cells = 16000000;
    bool scaling = true;
    bool compact_equalities = false;
    bool refine_basis = false; // Experimental sparse-LP RHS correction.
    bool capture_refinement = false;
    bool refine_at_checks = false; // Require refine_basis; verify before terminal decisions.
    bool primal_warm_start = false; // Opt-in, exact canonical-structure guard; private pump only in MILP.
    bool warm_infeasibility_certificate = false; // Guarded exact-integer dual row; requires primal_warm_start.
};
struct Result {
    std::string status;
    std::vector<double> primal;
    double objective = 0;
    double max_violation = 0;
    std::size_t iterations = 0;
    std::vector<double> dual;
    double scaled_primal_violation = 0;
    double scaled_dual_violation = 0;
    double relative_gap = 0;
    bool optimality_verified = false;
    bool infeasibility_verified = false;
    std::vector<double> unbounded_ray;
    bool unboundedness_verified = false;
};
double check_solution(const Model&, const std::vector<double>&);
Result solve(const Model&, const Options& = Options());
}
