#pragma once
#include "solver.hpp"
#include <istream>
#include <limits>
#include <utility>

namespace sovereign {
struct LinearProblem {
    std::string name;
    std::vector<std::string> names;
    std::vector<double> cost, lower, upper;
    std::vector<bool> integer;
    std::vector<std::vector<std::pair<std::size_t, double> > > rows;
    std::vector<double> row_lower, row_upper;
    double offset = 0;
    bool maximize = false;
    // Parsed decimal literals were integral BEFORE conversion to double, and
    // their magnitudes/accumulations stay within the exact 2^50 guard.
    // Programmatic models have no source literals; exact paths still guard all values.
    bool integer_input_literals = true;
};
struct StandardForm {
    Model model;
    std::vector<double> shift;
    std::vector<std::vector<std::pair<std::size_t, double> > > mapping;
    double objective_offset = 0;
    double objective_sign = 1;
    std::vector<double> recover(const std::vector<double>&) const;
};
LinearProblem read_mps(std::istream&);
void validate_linear_problem(const LinearProblem&);
StandardForm standardize(const LinearProblem&, std::size_t max_cells = 16000000);
double original_violation(const LinearProblem&, const std::vector<double>&, bool scaled);
}
