#pragma once
#include "mps.hpp"
#include "sparse_lu.hpp"
#include "basis_refinement.hpp"
#include <memory>

namespace sovereign {
// Immutable structural identity, retained ONLY by the opt-in reoptimizer.
// RHS, shifts and costs may change; canonical coefficients/mapping may not.
struct LpBasisStructure {
    std::vector<SparseVector> rows,mapping;
    std::vector<bool> equality;
};
struct BoundedBasis;
struct LpBasis {
    std::vector<std::size_t> columns; std::size_t structural_columns=0;
    bool compact_equalities=false,reduced_upper_bounds=false;
    std::shared_ptr<const LpBasisStructure> structure;
    std::shared_ptr<const BoundedBasis> bounded; // Only read by solve_bounded_lp.
};
struct LpReoptStats {
    std::size_t calls=0,compatible=0,primal=0,dual=0,rejected=0,verified=0;
    std::size_t phase_one_iterations=0,factorizations=0;
    std::size_t certificate_attempts=0,certificate_accepted=0;
    double canonical_seconds=0,factor_seconds=0,pricing_seconds=0;
    void add(const LpReoptStats& s) {
        calls+=s.calls;compatible+=s.compatible;primal+=s.primal;dual+=s.dual;
        rejected+=s.rejected;verified+=s.verified;phase_one_iterations+=s.phase_one_iterations;factorizations+=s.factorizations;
        certificate_attempts+=s.certificate_attempts;certificate_accepted+=s.certificate_accepted;
        canonical_seconds+=s.canonical_seconds;factor_seconds+=s.factor_seconds;pricing_seconds+=s.pricing_seconds;
    }
};
struct SparseLpResult {
    Result solution;
    LpBasis basis;
    std::vector<double> canonical_primal, canonical_dual, row_dual;
    double best_bound=-std::numeric_limits<double>::infinity();
    bool warm_started=false;
    LpReoptStats reopt;
    std::size_t factorizations=0;
    BasisRefinementStats refinement;
    std::size_t canonical_rows=0,compact_equality_rows=0;
    bool compact_fallback=false;
    std::size_t reduced_upper_candidates=0;
    bool reduced_upper_accepted=false,reduced_upper_fallback=false;
};
SparseLpResult solve_sparse_lp(const LinearProblem&, const Options& = Options(), const LpBasis* = nullptr);
LinearProblem linear_from_dense(const Model&);
}
