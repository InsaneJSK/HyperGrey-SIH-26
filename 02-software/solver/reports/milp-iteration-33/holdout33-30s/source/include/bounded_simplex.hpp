#pragma once
#include "sparse_lp.hpp"
#include <cstdint>
#include <memory>

namespace sovereign {
// Bounded revised simplex, implemented independently for MILP relaxations.
// Variables keep their own bounds and every row is a ranged logical r = A x,
// so branching changes bounds without adding rows. The result reports the
// same original-model checks as solve_sparse_lp; any unverified outcome is
// returned honestly so a caller can use the existing engine instead.
struct BoundedBasis {
    std::size_t structural=0;
    // Structural columns first, then one logical per row:
    // 0 basic, 1 at lower, 2 at upper, 3 free/superbasic.
    std::vector<std::uint8_t> status;
};
struct BoundedLpStats {
    std::size_t calls=0,warm=0,cold=0,optimal=0,infeasible=0,cutoffs=0,failures=0,
        iterations=0,dual_iterations=0,primal_iterations=0,flips=0,refactors=0,
        cleanups=0,artificial=0,singular_repairs=0,farkas_rejected=0,verification_rejected=0,prepared=0;
    double seconds=0;
    void add(const BoundedLpStats& s) {
        calls+=s.calls;warm+=s.warm;cold+=s.cold;optimal+=s.optimal;infeasible+=s.infeasible;
        cutoffs+=s.cutoffs;failures+=s.failures;iterations+=s.iterations;dual_iterations+=s.dual_iterations;
        primal_iterations+=s.primal_iterations;flips+=s.flips;refactors+=s.refactors;cleanups+=s.cleanups;
        artificial+=s.artificial;singular_repairs+=s.singular_repairs;farkas_rejected+=s.farkas_rejected;
        verification_rejected+=s.verification_rejected;prepared+=s.prepared;seconds+=s.seconds;
    }
};
// Immutable scaled copy of a model's rows and objective; bounds are per solve.
// Scale factors are powers of two, so unscaling is exact.
struct BoundedLpModel {
    std::size_t n=0,m=0;
    std::vector<int> col_start,col_index,row_start,row_index;
    std::vector<double> col_value,row_value; // scaled coefficients
    std::vector<double> cost;                // scaled minimization-sense cost
    std::vector<double> col_scale,row_scale; // x = col_scale*xs, rs = row_scale*r
    double cost_scale=1,sense=1,offset=0;    // offset is in minimization sense
};
std::shared_ptr<const BoundedLpModel> prepare_bounded_lp(const LinearProblem&,bool scaling=true);
// problem supplies the original rows/objective used for verification and must
// match model. lower/upper replace problem.lower/upper for this solve. cutoff is
// in minimization sense including the offset: when a verified dual bound reaches
// it, the solve stops with status "cutoff" and best_bound set to that bound.
SparseLpResult solve_bounded_lp(const LinearProblem& problem,const BoundedLpModel& model,
    const std::vector<double>& lower,const std::vector<double>& upper,const Options& options,
    const BoundedBasis* warm=nullptr,double cutoff=std::numeric_limits<double>::infinity(),
    BoundedLpStats* stats=nullptr);
SparseLpResult solve_bounded_lp(const LinearProblem& problem,const Options& options,
    const BoundedBasis* warm=nullptr,BoundedLpStats* stats=nullptr);

// Gomory mixed-integer cut, in ORIGINAL structural variables: row x <= rhs.
struct GomoryCut {
    std::vector<std::pair<std::size_t,double> > row;
    double rhs=0,efficacy=0;   // efficacy is the distance from the cut point
    std::size_t source=0;      // basic integer variable the row came from
};
struct GomoryStats {
    std::size_t calls=0,candidates=0,attempts=0,generated=0,basis_rejected=0,skipped_free=0,
        skipped_drop=0,skipped_consistency=0,skipped_dynamism=0,skipped_support=0,
        skipped_efficacy=0,skipped_parallel=0,rejected_incumbent=0;
    double seconds=0;
    void add(const GomoryStats& s) {
        calls+=s.calls;candidates+=s.candidates;attempts+=s.attempts;generated+=s.generated;
        basis_rejected+=s.basis_rejected;skipped_free+=s.skipped_free;skipped_drop+=s.skipped_drop;
        skipped_consistency+=s.skipped_consistency;skipped_dynamism+=s.skipped_dynamism;
        skipped_support+=s.skipped_support;skipped_efficacy+=s.skipped_efficacy;skipped_parallel+=s.skipped_parallel;
        rejected_incumbent+=s.rejected_incumbent;seconds+=s.seconds;
    }
};
// Separates cuts from the tableau of basis, which must belong to model with
// these bounds. lower/upper and the returned rows are in original space.
// incumbent, when given, is a known feasible point: any cut that would remove
// it is rejected instead of returned.
std::vector<GomoryCut> separate_gomory(const LinearProblem& problem,const BoundedLpModel& model,
    const std::vector<double>& lower,const std::vector<double>& upper,const Options& options,
    const BoundedBasis& basis,std::size_t max_cuts,double budget_seconds,
    const std::vector<double>* incumbent=nullptr,GomoryStats* stats=nullptr);
}
