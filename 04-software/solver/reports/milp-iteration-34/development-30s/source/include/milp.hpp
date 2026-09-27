#pragma once
#include "mps.hpp"
#include "sparse_lp.hpp"
#include "binary_proof.hpp"
#include "lifted_cover.hpp"
#include "objective_lattice.hpp"
#include "milp_work.hpp"
#include "cut_policy.hpp"
#include "feasibility_trace.hpp"
#include "pump_guidance.hpp"
#include "pump_distance.hpp"
#include "distance_stage.hpp"
#include "bounded_simplex.hpp"

namespace sovereign {
struct MilpOptions {
    Options lp;
    std::size_t node_limit = 10000;
    double integer_tolerance = 1e-7;
    double relative_gap = 1e-6;
    bool presolve = true;
    bool heuristics = true;
    bool bounded_lp = false; // Bounded dual simplex for non-private relaxations; verified fallback to the existing engine.
    double open_node_memory_mib = 960; // Frontier guard, active with bounded_lp only.
    bool tree_dives = false; // Periodic incumbent-phase dives with an incumbent-guided mode.
    bool fix_propagate = false; // Fix-and-propagate first-point search (root and no-incumbent tree nodes).
    bool gomory_cuts = false; // Root tableau Gomory mixed-integer cuts; requires bounded_lp.
    std::size_t root_iteration_limit = 0; // Root relaxation cap: max(lp.iteration_limit, this). 0 keeps lp.iteration_limit.
    bool feasibility_pump = true;
    bool pump_guided_diving = false; // Heuristic guidance only; no projection proof/basis reuse.
    bool pump_distance_diving = false; // Private distance LP; requires pump-guided-diving.
    bool pump_primal_reopt = false; // Objective-changing pump projections only; not tree/dive LPs.
    bool pump_distance_reopt = false; // Guarded private pump-basis handoff; requires both modes above.
    bool pump_distance_stage = false; // Objective-only parent solve before any private branch bound.
    bool private_dual_certificate = false; // Verified local infeasibility only; requires distance reopt.
    bool pump_distance_alternate_reserve = false; // Half remaining private slice for primary.
    bool pump_distance_stable_ranking = false; // Near ties in private distance dives only.
    bool cover_cuts = true;
    bool lifted_covers = false;
    bool late_lifted_covers = false;
    bool late_compact_equalities = false;
    bool reduced_bound_lp = false,late_reduced_bound_lp = false;
    bool objective_lattice = false; // Experimental numerical bound strengthening.
    bool raw_lp_priority = false; // Search ranking independent of proof bounds.
    bool capture_frontier = false;
    bool capture_work = false;
    bool capture_feasibility = false;
    bool capture_private_dive = false; // Bounded exact expensive/failed LP fixtures.
    bool adaptive_cut_rounds = false, capture_cut_rounds = false;
    bool cut_after_incumbent = false; // Requires adaptive mode; allocation only.
    std::size_t root_cut_rounds = 5; // Per root, including a full-domain restart.
    bool restart_by_nodes = false; // Counter-only trigger; disables half-time trigger.
    // Legacy test hook; --restart-nodes enables the counter-only CLI trigger.
    std::size_t late_cover_restart_nodes = std::numeric_limits<std::size_t>::max();
    // Experimental choice remains opt-in until paired hard-instance evidence.
    std::string branching = "fractionality";
    bool lp_recovery = false;
    bool improve_incumbent = false;
    std::string neighborhood = "guided";
    bool capture_neighborhood = false;
    bool pace_neighborhood = false;
    bool capture_lp_failure = false;
    bool capture_rejected_candidates = false;
    bool repair_candidates = false;
    bool repair_heuristic_candidates = false; // Uses the existing shared repair allowance.
    bool binary_meet = false;
    bool binary_proof = false;
    std::size_t binary_proof_work = 50000000;
};
struct MilpLpFailure {
    LinearProblem model;
    LpBasis input_basis;
    std::string status;
    std::size_t node=0,depth=0,iterations=0;
    double parent_bound=-std::numeric_limits<double>::infinity();
    bool captured=false;
};
struct PrivateDiveReplay {
    MilpLpFailure lp;
    std::size_t step=0,branch=0,total_iterations=0;
    bool alternate=false;
    double available_seconds=0,seconds=0;
    LpReoptStats reopt;
};
struct MilpResult {
    PrivateDiveReplay private_dive_expensive,private_dive_failed;
    std::size_t private_reserve_primary=0,private_reserve_alternate=0;
    LpReoptStats pump_reopt;
    BoundedLpStats bounded_lp;
    std::size_t bounded_lp_fallbacks=0,bounded_lp_cutoff_nodes=0;
    std::size_t tree_dive_calls=0,tree_dive_improvements=0;
    double tree_dive_seconds=0;
    std::size_t fix_propagate_calls=0,fix_propagate_fixings=0,fix_propagate_lps=0,fix_propagate_successes=0;
    double fix_propagate_seconds=0;
    GomoryStats gomory;
    std::size_t gomory_applied=0,gomory_rounds=0,gomory_purged=0; // Applied rows, rounds that produced one, rows later dropped as slack.
    double gomory_best_efficacy=0;
    MilpLpFailure pump_reopt_replay; // First bounded actual primal restart, capture-feasibility only.
    LpReoptStats distance_reopt;
    std::size_t private_certificate_attempts=0,private_certificate_accepted=0;
    std::size_t distance_seed_updates=0,distance_seed_offers=0,distance_seed_compatible=0,distance_seed_verified=0;
    MilpLpFailure distance_reopt_replay; // First offered seed basis, bounded diagnostic only.
    detail::DistanceStageStats distance_stage;
    std::size_t private_ranking_calls=0,private_ranking_ties=0,private_ranking_changes=0;
    MilpLpFailure distance_stage_replay,distance_stage_child_replay;
    detail::PumpGuidanceStats pump_guidance;
    detail::PumpDistanceStats pump_distance;
    detail::FeasibilityTrace feasibility;
    detail::MilpWork work;
    std::vector<detail::CutRound> cut_round_trace;
    std::size_t adaptive_cut_stops=0;
    std::string status;
    std::vector<double> primal;
    double objective = std::numeric_limits<double>::quiet_NaN();
    double best_bound = -std::numeric_limits<double>::infinity();
    double gap = std::numeric_limits<double>::infinity();
    std::size_t nodes = 0;
    struct FrontierEvent {
        std::string operation;
        std::size_t id,depth,queued,deferred;
        double proof,rank; // Checkpoints use global bound and incumbent instead.
    };
    std::vector<FrontierEvent> frontier_trace;
    std::size_t frontier_events=0,frontier_priority_mismatches=0,frontier_max_queued=0;
    detail::ObjectiveLattice objective_lattice;
    std::size_t lattice_bound_calls=0,lattice_bound_improvements=0;
    struct LatticeBound {std::size_t node;double before,after;};
    std::vector<LatticeBound> lattice_bound_trace; // First 4096 improvements.
    std::size_t lp_iterations = 0;
    std::size_t compact_lp_calls=0,compact_lp_fallbacks=0,root_lp_rows=0,root_compact_equalities=0;
    std::size_t reduced_bound_lp_calls=0,reduced_bound_lp_fallbacks=0,reduced_bound_lp_accepted=0;
    std::size_t reduced_upper_candidates=0,root_reduced_upper_bounds=0;
    std::size_t warm_starts = 0, heuristic_solves = 0, cuts = 0, bound_tightenings = 0;
    std::size_t pump_projections = 0, pump_restarts = 0, pump_incumbents = 0;
    std::size_t cut_rollbacks = 0;
    std::size_t lifted_cover_states=0,lifted_cover_checked=0;
    double lifted_cover_seconds=0;
    double root_bound_before_cuts=-std::numeric_limits<double>::infinity(),root_bound_after_cuts=-std::numeric_limits<double>::infinity();
    std::vector<detail::VerifiedCover> lifted_cover_trace;
    std::size_t cut_restarts=0,cut_restart_nodes=0;
    double cut_restart_seconds=0,cut_restart_bound=-std::numeric_limits<double>::infinity();
    double cut_restart_objective=std::numeric_limits<double>::quiet_NaN();
    std::vector<double> cut_restart_primal;
    std::size_t pseudocost_updates = 0, strong_branch_probes = 0;
    double strong_branch_seconds = 0;
    std::size_t lp_recovery_attempts=0,lp_recovery_successes=0,deferred_nodes=0,unresolved_nodes=0;
    double lp_recovery_seconds=0;
    std::size_t neighborhood_calls=0,neighborhood_nodes=0,neighborhood_improvements=0;
    double neighborhood_seconds=0;
    struct NeighborhoodSample {
        std::size_t node=0,nodes=0,lp_failures=0,stalls_before=0;
        double start_seconds=0,seconds=0,budget=0,objective_before=0,objective_after=0;
        std::string selection;
        std::vector<std::size_t> free_variables;
        std::vector<double> improved_primal,center_primal;
        std::size_t radius=0;
        bool improved=false,material_improved=false,strong=false,frontier_exhausted=false;
    };
    std::vector<NeighborhoodSample> neighborhood_trace;
    MilpLpFailure first_lp_failure;
    struct RejectedCandidate {
        MilpLpFailure fixing;
        std::vector<double> relaxation,rounded,repair_primal,node_lower,node_upper,fallback_primal;
        std::string fallback_status;
        double relaxation_violation=0,rounded_violation=0,repair_violation=0;
        bool repair_infeasibility_verified=false,repair_optimality_verified=false,repair_accepted=false;
        bool fallback_accepted=false;
    };
    std::size_t rejected_integer_candidates=0;
    std::vector<RejectedCandidate> rejected_candidates;
    std::size_t candidate_repair_attempts=0,candidate_repair_successes=0,repair_branch_nodes=0;
    double candidate_repair_seconds=0;
    std::size_t heuristic_repair_attempts=0,heuristic_repair_successes=0,heuristic_repair_duplicates=0;
    std::size_t heuristic_repair_sparse_calls=0,heuristic_repair_dense_calls=0;
    double heuristic_repair_seconds=0;
    std::size_t binary_meet_attempts=0,binary_meet_left_states=0,binary_meet_right_states=0,binary_meet_query_nodes=0;
    double binary_meet_seconds=0,binary_meet_budget=0;
    bool binary_meet_eligible=false,binary_meet_completed=false,binary_meet_improved=false;
    std::vector<double> binary_meet_primal;
    BinaryProofResult binary_proof;
    std::size_t binary_proof_attempts=0;
    double binary_proof_budget=0;
    std::vector<std::pair<double,double> > incumbent_trace; // seconds, original-sense objective
    double first_incumbent_seconds = std::numeric_limits<double>::quiet_NaN();
    std::string message;
};
MilpResult solve_milp(const LinearProblem&, const MilpOptions& = MilpOptions());
}
