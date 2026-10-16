#include "milp.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <queue>
#include <stdexcept>

namespace sovereign {
namespace {
struct Node {
    std::vector<double> lower, upper;
    double bound;
    std::size_t id;
};
struct Order {
    bool operator()(const Node& a, const Node& b) const {
        return a.bound == b.bound ? a.id > b.id : a.bound > b.bound;
    }
};
}
MilpResult solve_milp(const LinearProblem& p, const MilpOptions& opt) {
    validate_linear_problem(p);
    if (opt.integer_tolerance <= 0 || !std::isfinite(opt.integer_tolerance) ||
        opt.relative_gap < 0 || !std::isfinite(opt.relative_gap)) throw std::invalid_argument("Invalid MILP tolerances");
    MilpResult out;
    auto start = std::chrono::steady_clock::now();
    const double sign = p.maximize ? -1 : 1;
    double incumbent = std::numeric_limits<double>::infinity();
    std::priority_queue<Node, std::vector<Node>, Order> queue;
    Node root = {p.lower, p.upper, -std::numeric_limits<double>::infinity(), 0};
    for (std::size_t j = 0; j < p.names.size(); ++j) if (p.integer[j]) {
        root.lower[j] = std::ceil(root.lower[j]); root.upper[j] = std::floor(root.upper[j]);
    }
    queue.push(root);
    std::size_t serial = 1;
    out.status = "optimal";
    while (!queue.empty()) {
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        if (elapsed >= opt.lp.time_limit_seconds) { out.status = "time_limit"; break; }
        if (out.nodes >= opt.node_limit) { out.status = "node_limit"; break; }
        const double allowance = opt.relative_gap * (1 + std::abs(incumbent));
        if (std::isfinite(incumbent) && queue.top().bound >= incumbent - allowance) {
            out.status = "gap_limit"; break;
        }
        Node node = queue.top(); queue.pop(); ++out.nodes;
        bool contradiction = false;
        for (std::size_t j = 0; j < p.names.size(); ++j)
            if (node.lower[j] > node.upper[j]) contradiction = true;
        if (contradiction) continue;
        LinearProblem relaxed = p;
        relaxed.lower = node.lower; relaxed.upper = node.upper;
        std::fill(relaxed.integer.begin(), relaxed.integer.end(), false);
        StandardForm s = standardize(relaxed, opt.lp.max_tableau_cells);
        Options lp_options = opt.lp;
        lp_options.time_limit_seconds = std::max(0.0, opt.lp.time_limit_seconds - elapsed);
        auto lp = solve(s.model, lp_options);
        out.lp_iterations += lp.iterations;
        if (lp.status == "infeasible" && lp.infeasibility_verified) continue;
        if (lp.status != "optimal" || !lp.optimality_verified) {
            // Keep the unsolved node in the bound calculation; never silently prune it.
            queue.push(node);
            out.status = lp.status == "unbounded" ? "unbounded_relaxation" : lp.status;
            break;
        }
        auto x = s.recover(lp.primal);
        long double canonical_dual = 0;
        for (std::size_t i = 0; i < s.model.rhs.size(); ++i)
            canonical_dual += static_cast<long double>(s.model.rhs[i])*lp.dual[i];
        double bound = static_cast<double>(canonical_dual) + sign*s.objective_offset;
        // Numerical safety margin, not an interval-arithmetic proof.
        bound -= 100 * opt.lp.tolerance * (1 + std::abs(bound));
        node.bound = std::max(node.bound, bound);
        if (std::isfinite(incumbent) && node.bound >= incumbent) continue;
        std::size_t branch = p.names.size();
        double most_fractional = opt.integer_tolerance;
        for (std::size_t j = 0; j < x.size(); ++j) if (p.integer[j]) {
            double fractional = std::abs(x[j]-std::round(x[j]));
            if (fractional > most_fractional) { most_fractional = fractional; branch = j; }
        }
        if (branch == p.names.size()) {
            for (std::size_t j = 0; j < x.size(); ++j) if (p.integer[j]) x[j] = std::round(x[j]);
            if (original_violation(relaxed, x, false) > 1e-7) {
                queue.push(node); out.status = "numerical_error"; break;
            }
            double value = sign*p.offset;
            for (std::size_t j = 0; j < x.size(); ++j) value += sign*p.cost[j]*x[j];
            if (!std::isfinite(value)) { queue.push(node); out.status = "numerical_error"; break; }
            if (value < incumbent) { incumbent = value; out.primal = x; out.objective = sign*value; }
            continue;
        }
        Node down = node, up = node;
        down.upper[branch] = std::min(down.upper[branch], std::floor(x[branch]));
        up.lower[branch] = std::max(up.lower[branch], std::ceil(x[branch]));
        down.id = serial++; up.id = serial++;
        if (down.lower[branch] <= down.upper[branch]) queue.push(std::move(down));
        if (up.lower[branch] <= up.upper[branch]) queue.push(std::move(up));
    }
    if (queue.empty()) {
        if (out.primal.empty()) out.status = "infeasible";
        out.best_bound = out.primal.empty() ? sign*std::numeric_limits<double>::infinity() : out.objective;
        out.gap = out.primal.empty() ? std::numeric_limits<double>::infinity() : 0;
    } else {
        double bound = std::min(queue.top().bound, incumbent);
        out.best_bound = sign*bound;
        if (std::isfinite(incumbent) && std::isfinite(bound)) out.gap = std::max(0.0, incumbent-bound)/(1+std::abs(incumbent));
    }
    return out;
}
}
