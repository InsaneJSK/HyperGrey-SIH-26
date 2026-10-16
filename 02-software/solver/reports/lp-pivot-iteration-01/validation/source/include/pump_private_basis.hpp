#pragma once
#include "sparse_lp.hpp"

namespace sovereign { namespace detail {
// Separate from the public point-only PumpDiveSeed. This state is never a
// tree bound/certificate. Update at the SAME selection event as the seed.
struct PumpPrivateBasis {
    LpBasis basis;
    std::shared_ptr<const LinearProblem> parent;
    bool select(bool point_selected,const LpBasis& candidate,const LinearProblem* model=nullptr) {
        if(!point_selected)return false;
        // Build the replacement before clearing, including the self-alias case.
        LpBasis replacement;
        if(candidate.structure&&!candidate.columns.empty()&&!candidate.reduced_upper_bounds)replacement=candidate;
        auto retained=model&&!replacement.columns.empty()?std::make_shared<const LinearProblem>(*model):nullptr;
        basis=std::move(replacement);parent=std::move(retained);
        return !basis.columns.empty();
    }
    bool same_parent_domain(const LinearProblem& target) const {
        // Conservative prefilter for an OBJECTIVE-ONLY bridge. The sparse LP
        // engine still checks exact canonical identity and basis feasibility.
        return parent&&basis.structure&&!basis.columns.empty()&&!basis.reduced_upper_bounds
            &&parent->cost.size()==target.cost.size()&&parent->rows==target.rows
            &&parent->lower==target.lower&&parent->upper==target.upper
            &&parent->row_lower==target.row_lower&&parent->row_upper==target.row_upper
            &&parent->integer==target.integer;
    }
};
}}
