#include "solver.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <chrono>
#include <set>

namespace sovereign {
namespace {
void validate(const Model& m) {
    if (m.cost.empty() || m.rows.size() != m.rhs.size())
        throw std::invalid_argument("Invalid model dimensions");
    for (double c : m.cost) if (!std::isfinite(c))
        throw std::invalid_argument("Non-finite objective coefficient");
    for (std::size_t i = 0; i < m.rows.size(); ++i) {
        if (m.rows[i].size() != m.cost.size() || !std::isfinite(m.rhs[i]))
            throw std::invalid_argument("Invalid constraint");
        for (double a : m.rows[i]) if (!std::isfinite(a))
            throw std::invalid_argument("Non-finite constraint coefficient");
    }
}
struct Tableau {
    std::vector<std::vector<double> > rows;
    std::vector<std::size_t> basis;
    std::size_t width;
    std::size_t iterations = 0;
    Options opt;
    std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now();
    void pivot(std::size_t r, std::size_t col) {
        const double p = rows[r][col];
        for (double& v : rows[r]) v /= p;
        for (std::size_t i = 0; i < rows.size(); ++i) if (i != r) {
            const double factor = rows[i][col];
            for (std::size_t j = 0; j <= width; ++j)
                rows[i][j] -= factor * rows[r][j];
            rows[i][col] = 0;
        }
        basis[r] = col;
        ++iterations;
    }
    std::string optimize(std::size_t entering_columns) {
        std::set<std::vector<std::size_t> > visited;
        bool bland = false;
        while (true) {
            if (std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count()
                >= opt.time_limit_seconds) return "time_limit";
            for (const auto& row : rows) for (double v : row)
                if (!std::isfinite(v)) return "numerical_error";
            std::size_t col = entering_columns;
            std::vector<bool> basic(width, false);
            for (auto j : basis) basic[j] = true;
            // Most-negative reduced cost normally; deterministic Bland fallback
            // if a basis repeats under floating-point arithmetic.
            for (std::size_t j = 0; j < entering_columns; ++j)
                if (!basic[j] && rows.back()[j] < -opt.tolerance) {
                    if (col == entering_columns || rows.back()[j] < rows.back()[col]) col = j;
                    if (bland) break;
                }
            if (col == entering_columns) return "optimal";
            // Exact Bland pivots cannot revisit a basis. In floating point,
            // repeated bases indicate numerical stalling, not useful progress.
            auto key = basis; std::sort(key.begin(), key.end());
            if (!visited.insert(key).second) {
                if (bland) return "numerical_stall";
                bland = true; visited.clear(); continue;
            }
            if (iterations >= opt.iteration_limit) return "iteration_limit";
            std::size_t leaving = basis.size();
            double ratio = std::numeric_limits<double>::infinity();
            for (std::size_t i = 0; i < basis.size(); ++i) {
                if (rows[i][col] <= opt.tolerance) continue;
                double candidate = rows[i][width] / rows[i][col];
                if (candidate < ratio ||
                    (candidate == ratio && leaving < basis.size() && basis[i] < basis[leaving])) {
                    ratio = candidate; leaving = i;
                }
            }
            if (leaving == basis.size()) return "unbounded";
            pivot(leaving, col);
        }
    }
};
}

double check_solution(const Model& m, const std::vector<double>& x) {
    validate(m);
    if (x.size() != m.cost.size()) throw std::invalid_argument("Wrong solution size");
    double violation = 0;
    for (double v : x) {
        if (!std::isfinite(v)) return std::numeric_limits<double>::infinity();
        violation = std::max(violation, -v);
    }
    for (std::size_t i = 0; i < m.rows.size(); ++i) {
        long double activity = 0;
        for (std::size_t j = 0; j < x.size(); ++j)
            activity += static_cast<long double>(m.rows[i][j]) * x[j];
        if (!std::isfinite(activity)) return std::numeric_limits<double>::infinity();
        violation = std::max(violation, static_cast<double>(activity - m.rhs[i]));
    }
    return violation;
}

Result solve_tableau(const Model& m, const Options& opt) {
    validate(m);
    if (!std::isfinite(opt.tolerance) || opt.tolerance <= 0)
        throw std::invalid_argument("Tolerance must be finite and positive");
    const std::size_t n = m.cost.size(), count = m.rows.size();
    const std::size_t original_cols = n + count;
    std::size_t artificials = 0;
    for (double b : m.rhs) if (b < 0) ++artificials;
    Tableau t;
    t.width = original_cols + artificials;
    t.opt = opt;
    if (t.width + 1 > opt.max_tableau_cells / (count + 1)) {
        Result limited; limited.status = "resource_limit"; return limited;
    }
    t.rows.assign(count + 1, std::vector<double>(t.width + 1, 0));
    t.basis.resize(count);
    std::size_t next_art = original_cols;
    for (std::size_t i = 0; i < count; ++i) {
        const double sign = m.rhs[i] < 0 ? -1 : 1;
        for (std::size_t j = 0; j < n; ++j) t.rows[i][j] = sign * m.rows[i][j];
        t.rows[i][n + i] = sign;
        t.rows[i][t.width] = sign * m.rhs[i];
        t.basis[i] = n + i;
        if (sign < 0) {
            t.basis[i] = next_art;
            t.rows[i][next_art++] = 1;
        }
    }
    Result out;
    if (artificials) {
        // Phase I maximizes minus the sum of artificial variables.
        for (std::size_t j = original_cols; j < t.width; ++j) t.rows.back()[j] = 1;
        for (std::size_t i = 0; i < count; ++i) if (t.basis[i] >= original_cols)
            for (std::size_t j = 0; j <= t.width; ++j) t.rows.back()[j] -= t.rows[i][j];
        out.status = t.optimize(t.width);
        out.iterations = t.iterations;
        if (out.status != "optimal") {
            if (out.status == "unbounded") out.status = "numerical_error";
            return out;
        }
        if (t.rows.back()[t.width] < -opt.tolerance) {
            out.dual.resize(count);
            long double contradiction = 0, magnitude = 1;
            bool certificate = true;
            for (std::size_t i = 0; i < count; ++i) {
                out.dual[i] = std::min(0.0, -t.rows.back()[n + i]);
                long double term = static_cast<long double>(m.rhs[i]) * out.dual[i];
                contradiction += term; magnitude += std::abs(term);
            }
            for (std::size_t j = 0; j < n; ++j) {
                long double aty = 0, scale = 1;
                for (std::size_t i = 0; i < count; ++i) {
                    long double term = static_cast<long double>(m.rows[i][j]) * out.dual[i];
                    aty += term; scale += std::abs(term);
                }
                if (!std::isfinite(aty) || aty > opt.tolerance * scale) certificate = false;
            }
            out.infeasibility_verified = certificate && std::isfinite(contradiction)
                && contradiction > 10 * opt.tolerance * magnitude;
            out.status = out.infeasibility_verified ? "infeasible" : "numerical_error";
            return out;
        }
        for (std::size_t i = 0; i < t.basis.size();) {
            if (t.basis[i] < original_cols) { ++i; continue; }
            std::size_t col = 0;
            while (col < original_cols && std::abs(t.rows[i][col]) <= opt.tolerance) ++col;
            if (col < original_cols) {
                if (t.iterations >= opt.iteration_limit) {
                    out.status = "iteration_limit"; out.iterations = t.iterations; return out;
                }
                t.pivot(i, col); ++i;
            } else {
                t.rows.erase(t.rows.begin() + i);
                t.basis.erase(t.basis.begin() + i);
            }
        }
    }
    // Phase II maximizes -c*x. Eliminate basic costs from the objective row.
    std::fill(t.rows.back().begin(), t.rows.back().end(), 0);
    for (std::size_t j = 0; j < n; ++j) t.rows.back()[j] = m.cost[j];
    for (std::size_t i = 0; i < t.basis.size(); ++i) {
        const double factor = t.rows.back()[t.basis[i]];
        for (std::size_t j = 0; j <= t.width; ++j) t.rows.back()[j] -= factor * t.rows[i][j];
    }
    out.status = t.optimize(original_cols);
    out.iterations = t.iterations;
    if (out.status != "optimal") return out;
    out.primal.assign(n, 0);
    for (std::size_t i = 0; i < t.basis.size(); ++i)
        if (t.basis[i] < n) out.primal[t.basis[i]] = t.rows[i][t.width];
    for (std::size_t j = 0; j < n; ++j) out.objective += m.cost[j] * out.primal[j];
    out.max_violation = check_solution(m, out.primal);
    out.dual.resize(count);
    for (std::size_t i = 0; i < count; ++i)
        // Project roundoff onto the known <=-row dual sign constraint. The
        // resulting vector must still pass the independent gap/stationarity checks.
        out.dual[i] = std::min(0.0, -t.rows.back()[n + i]);
    if (!std::isfinite(out.objective) || out.max_violation > 10 * opt.tolerance)
        out.status = "numerical_error";
    return out;
}

Result solve(const Model& m, const Options& opt) {
    validate(m);
    if (!std::isfinite(opt.time_limit_seconds) || opt.time_limit_seconds < 0)
        throw std::invalid_argument("Invalid time limit");
    Model scaled = m;
    std::vector<double> row_scale(m.rows.size(), 1);
    double cost_scale = 1;
    if (opt.scaling) {
        cost_scale = 0;
        for (double c : m.cost) cost_scale = std::max(cost_scale, std::abs(c));
        if (cost_scale == 0) cost_scale = 1;
        for (double& c : scaled.cost) c /= cost_scale;
        for (std::size_t i = 0; i < m.rows.size(); ++i) {
            double factor = 0;
            for (double a : m.rows[i]) factor = std::max(factor, std::abs(a));
            if (factor == 0) factor = 1;
            row_scale[i] = factor;
            for (double& a : scaled.rows[i]) a /= factor;
            scaled.rhs[i] /= factor;
            if (!std::isfinite(scaled.rhs[i])) {
                Result bad; bad.status = "numerical_error"; return bad;
            }
        }
    }
    Result r = solve_tableau(scaled, opt);
    if (r.infeasibility_verified) {
        // Farkas multipliers transform by the row scaling only (no objective).
        for (std::size_t i = 0; i < r.dual.size(); ++i) r.dual[i] /= row_scale[i];
        long double contradiction=0,scale=1;
        for(std::size_t i=0;i<r.dual.size();++i) {
            if(!std::isfinite(r.dual[i])) r.infeasibility_verified=false;
            long double term=static_cast<long double>(m.rhs[i])*r.dual[i];
            contradiction+=term;scale+=std::abs(term);
        }
        if(!std::isfinite(contradiction)||contradiction<=10*opt.tolerance*scale) r.infeasibility_verified=false;
        for(std::size_t j=0;j<m.cost.size();++j) {
            long double activity=0,magnitude=1;
            for(std::size_t i=0;i<r.dual.size();++i) {
                long double term=static_cast<long double>(m.rows[i][j])*r.dual[i];activity+=term;magnitude+=std::abs(term);
            }
            if(!std::isfinite(activity)||activity>opt.tolerance*magnitude)r.infeasibility_verified=false;
        }
        if(!r.infeasibility_verified)r.status="numerical_error";
    }
    if (r.primal.empty()) return r;
    r.objective = 0;
    for (std::size_t j = 0; j < m.cost.size(); ++j) r.objective += m.cost[j] * r.primal[j];
    r.max_violation = check_solution(m, r.primal);
    long double dual_objective = 0;
    for (std::size_t i = 0; i < m.rows.size(); ++i) {
        r.dual[i] = r.dual[i] * cost_scale / row_scale[i];
        if (!std::isfinite(r.dual[i])) { r.status = "numerical_error"; return r; }
        dual_objective += static_cast<long double>(m.rhs[i]) * r.dual[i];
        r.scaled_dual_violation = std::max(r.scaled_dual_violation,
            std::max(0.0, r.dual[i]) / (1 + std::abs(r.dual[i])));
        long double activity = 0, scale = 1 + std::abs(m.rhs[i]);
        for (std::size_t j = 0; j < m.cost.size(); ++j) {
            long double term = static_cast<long double>(m.rows[i][j]) * r.primal[j];
            activity += term; scale += std::abs(term);
        }
        r.scaled_primal_violation = std::max(r.scaled_primal_violation,
            static_cast<double>(std::max(0.0L, activity - m.rhs[i]) / scale));
    }
    for (std::size_t j = 0; j < m.cost.size(); ++j) {
        r.scaled_primal_violation = std::max(r.scaled_primal_violation,
            std::max(0.0, -r.primal[j]) / (1 + std::abs(r.primal[j])));
        long double aty = 0, scale = 1 + std::abs(m.cost[j]);
        for (std::size_t i = 0; i < m.rows.size(); ++i) {
            long double term = static_cast<long double>(m.rows[i][j]) * r.dual[i];
            aty += term; scale += std::abs(term);
        }
        r.scaled_dual_violation = std::max(r.scaled_dual_violation,
            static_cast<double>(std::max(0.0L, aty - m.cost[j]) / scale));
    }
    r.relative_gap = static_cast<double>(std::abs(r.objective - dual_objective) /
        (1 + std::max(std::abs(static_cast<long double>(r.objective)), std::abs(dual_objective))));
    r.optimality_verified = std::isfinite(r.objective) && std::isfinite(r.relative_gap)
        && r.scaled_primal_violation <= 10 * opt.tolerance
        && r.scaled_dual_violation <= 10 * opt.tolerance && r.relative_gap <= 10 * opt.tolerance;
    // A failed internal check remains a failure even when the external residuals pass.
    if (!r.optimality_verified) r.status = "numerical_error";
    return r;
}
}
