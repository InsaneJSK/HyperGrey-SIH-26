#include "solver.hpp"
#include "mps.hpp"
#include "milp.hpp"
#include "qp.hpp"
#include "sparse_lp.hpp"
#include "accelerated_qp.hpp"
#include "bounded_simplex.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <cmath>

namespace {
double number_option(const char* text){std::size_t used=0;double value=std::stod(text,&used);if(used!=std::string(text).size()||!std::isfinite(value))throw std::invalid_argument("Expected a finite numeric option");return value;}
std::size_t count_option(const char* text){double value=number_option(text);if(value<0||value>100000000||std::floor(value)!=value)throw std::invalid_argument("Expected an integer option in [0,100000000]");return static_cast<std::size_t>(value);}
void numeric(double v) { if (std::isfinite(v)) std::cout << v; else std::cout << "null"; }
void array(const std::vector<double>& v) {
    std::cout << '[';
    for (std::size_t i = 0; i < v.size(); ++i) { if (i) std::cout << ','; numeric(v[i]); }
    std::cout << ']';
}
void lp_failure(const sovereign::MilpLpFailure& f) {
    if(f.status.empty()){std::cout<<"null";return;}
    std::cout<<"{\"status\":\""<<f.status<<"\",\"captured\":"<<(f.captured?"true":"false")<<",\"node\":"<<f.node<<",\"depth\":"<<f.depth<<",\"iterations\":"<<f.iterations<<",\"parent_bound_minimization_sense\":";numeric(f.parent_bound);
    if(f.captured){
        const auto& p=f.model;
        std::cout<<",\"maximize\":"<<(p.maximize?"true":"false")<<",\"offset\":";numeric(p.offset);
        std::cout<<",\"cost\":";array(p.cost);std::cout<<",\"lower\":";array(p.lower);std::cout<<",\"upper\":";array(p.upper);
        std::cout<<",\"row_lower\":";array(p.row_lower);std::cout<<",\"row_upper\":";array(p.row_upper);
        std::cout<<",\"rows\":[";
        for(std::size_t i=0;i<p.rows.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t k=0;k<p.rows[i].size();++k){if(k)std::cout<<',';std::cout<<'['<<p.rows[i][k].first<<',';numeric(p.rows[i][k].second);std::cout<<']';}std::cout<<']';}
        std::cout<<"],\"basis_structural_columns\":"<<f.input_basis.structural_columns<<",\"basis_compact_equalities\":"<<(f.input_basis.compact_equalities?"true":"false")<<",\"basis_reduced_upper_bounds\":"<<(f.input_basis.reduced_upper_bounds?"true":"false")<<",\"input_basis_columns\":[";
        for(std::size_t k=0;k<f.input_basis.columns.size();++k){if(k)std::cout<<',';std::cout<<f.input_basis.columns[k];}std::cout<<']';
        if(f.input_basis.structure){
            const auto& s=*f.input_basis.structure;
            auto sparse=[](const std::vector<sovereign::SparseVector>& rows){std::cout<<'[';for(std::size_t i=0;i<rows.size();++i){if(i)std::cout<<',';std::cout<<'[';for(std::size_t k=0;k<rows[i].size();++k){if(k)std::cout<<',';std::cout<<'['<<rows[i][k].first<<',';numeric(rows[i][k].second);std::cout<<']';}std::cout<<']';}std::cout<<']';};
            std::cout<<",\"basis_rows\":";sparse(s.rows);std::cout<<",\"basis_mapping\":";sparse(s.mapping);
            std::cout<<",\"basis_equality\":[";for(std::size_t i=0;i<s.equality.size();++i){if(i)std::cout<<',';std::cout<<(s.equality[i]?1:0);}std::cout<<']';
        }
    }
    std::cout<<'}';
}
void refinement_work(const sovereign::BasisRefinementStats& s) {
    std::cout<<"{\"rhs_calls\":"<<s.rhs_calls<<",\"primal_rhs\":"<<s.primal_rhs<<",\"dual_rhs\":"<<s.dual_rhs
             <<",\"scans\":"<<s.scans<<",\"entries\":"<<s.entries<<",\"attempts\":"<<s.attempts<<",\"accepted\":"<<s.accepted<<",\"seconds\":";
    numeric(s.seconds);std::cout<<'}';
}
}

int main(int argc, char** argv) {
    if(argc==2&&std::string(argv[1])=="--version"){std::cout<<"Sovereign SIH26119 V2 candidate; C++ core, sparse simplex, branch-and-cut, convex QP\n";return 0;}
    if (argc < 2) { std::cerr << "Usage: solver_cli MODEL.{lpmini,mps} [--json] [--no-scaling] [--time-limit seconds]\n"; return 2; }
    try {
        bool json = false;
        bool milp = false;
        std::string lp_method="sparse";
        int threads=1;
        std::string backend="cpu";
        bool custom_iterations=false,custom_tolerance=false;
        sovereign::MilpOptions mip_options;
        sovereign::Options options;
        for (int i = 2; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "--json") json = true;
            else if (arg == "--milp") milp = true;
            else if (arg == "--no-scaling") options.scaling = false;
            else if (arg == "--compact-equalities") options.compact_equalities=true;
            else if (arg == "--refine-basis") options.refine_basis=true;
            else if (arg == "--refine-at-checks") options.refine_at_checks=true;
            else if (arg == "--capture-refinement") {options.capture_refinement=true;mip_options.capture_work=true;}
            else if (arg == "--reduced-bound-lp") mip_options.reduced_bound_lp=true;
            else if (arg == "--objective-lattice") mip_options.objective_lattice=true;
            else if (arg == "--raw-lp-priority") mip_options.raw_lp_priority=true;
            else if (arg == "--capture-frontier") mip_options.capture_frontier=true;
            else if (arg == "--capture-work") mip_options.capture_work=true;
            else if (arg == "--capture-feasibility") mip_options.capture_feasibility=true;
            else if (arg == "--capture-private-dive") mip_options.capture_private_dive=true;
            else if (arg == "--repair-heuristic-candidates") mip_options.repair_heuristic_candidates=true;
            else if (arg == "--pump-guided-diving") mip_options.pump_guided_diving=true;
            else if (arg == "--pump-distance-diving") mip_options.pump_distance_diving=true;
            else if (arg == "--pump-primal-reopt") mip_options.pump_primal_reopt=true;
            else if (arg == "--pump-distance-reopt") mip_options.pump_distance_reopt=true;
            else if (arg == "--pump-distance-stage") mip_options.pump_distance_stage=true;
            else if (arg == "--private-dual-certificate") mip_options.private_dual_certificate=true;
            else if (arg == "--bounded-lp") mip_options.bounded_lp=true;
            else if (arg == "--tree-dives") mip_options.tree_dives=true;
            else if (arg == "--fix-propagate") mip_options.fix_propagate=true;
            else if (arg == "--gomory-cuts") mip_options.gomory_cuts=true;
            else if (arg == "--root-iteration-limit" && i+1<argc) mip_options.root_iteration_limit=count_option(argv[++i]);
            else if (arg == "--open-node-memory-mib" && i+1<argc) mip_options.open_node_memory_mib=number_option(argv[++i]);
            else if (arg == "--pump-distance-alternate-reserve") mip_options.pump_distance_alternate_reserve=true;
            else if (arg == "--pump-distance-stable-ranking") mip_options.pump_distance_stable_ranking=true;
            else if (arg == "--adaptive-cut-rounds") mip_options.adaptive_cut_rounds=true;
            else if (arg == "--cut-after-incumbent") mip_options.cut_after_incumbent=true;
            else if (arg == "--capture-cut-rounds") mip_options.capture_cut_rounds=true;
            else if (arg == "--root-cut-rounds" && i+1<argc) mip_options.root_cut_rounds=count_option(argv[++i]);
            else if (arg == "--restart-nodes" && i+1<argc) {mip_options.late_cover_restart_nodes=count_option(argv[++i]);mip_options.restart_by_nodes=true;}
            else if (arg == "--late-reduced-bound-lp") {mip_options.late_reduced_bound_lp=true;mip_options.late_compact_equalities=true;mip_options.lifted_covers=true;mip_options.late_lifted_covers=true;}
            else if (arg == "--late-compact-equalities") {mip_options.late_compact_equalities=true;mip_options.lifted_covers=true;mip_options.late_lifted_covers=true;}
            else if (arg == "--lp-method" && i+1<argc) lp_method=argv[++i];
            else if (arg == "--stable-primal-ratio") options.stable_primal_ratio=true;
            else if (arg == "--iteration-limit" && i+1<argc) {options.iteration_limit=count_option(argv[++i]);custom_iterations=true;}
            else if (arg == "--tolerance" && i+1<argc) {options.tolerance=number_option(argv[++i]);custom_tolerance=true;}
            else if (arg == "--threads" && i+1<argc) threads=static_cast<int>(count_option(argv[++i]));
            else if (arg == "--backend" && i+1<argc) backend=argv[++i];
            else if (arg == "--node-limit" && i+1<argc) mip_options.node_limit=count_option(argv[++i]);
            else if (arg == "--no-presolve") mip_options.presolve=false;
            else if (arg == "--no-heuristics") mip_options.heuristics=false;
            else if (arg == "--no-pump") mip_options.feasibility_pump=false;
            else if (arg == "--no-cuts") mip_options.cover_cuts=false;
            else if (arg == "--lifted-covers") mip_options.lifted_covers=true;
            else if (arg == "--late-lifted-covers") {mip_options.lifted_covers=true;mip_options.late_lifted_covers=true;}
            else if (arg == "--branching" && i+1<argc) mip_options.branching=argv[++i];
            else if (arg == "--lp-recovery") mip_options.lp_recovery=true;
            else if (arg == "--improve-incumbent") mip_options.improve_incumbent=true;
            else if (arg == "--neighborhood" && i+1<argc) mip_options.neighborhood=argv[++i];
            else if (arg == "--capture-neighborhood") mip_options.capture_neighborhood=true;
            else if (arg == "--pace-neighborhood") mip_options.pace_neighborhood=true;
            else if (arg == "--capture-lp-failure") mip_options.capture_lp_failure=true;
            else if (arg == "--capture-rejected-candidates") mip_options.capture_rejected_candidates=true;
            else if (arg == "--repair-candidates") mip_options.repair_candidates=true;
            else if (arg == "--binary-meet") mip_options.binary_meet=true;
            else if (arg == "--binary-proof") mip_options.binary_proof=true;
            else if (arg == "--binary-proof-work" && i+1<argc) mip_options.binary_proof_work=count_option(argv[++i]);
            else if (arg == "--gap" && i+1<argc) mip_options.relative_gap=number_option(argv[++i]);
            else if (arg == "--time-limit" && i + 1 < argc) options.time_limit_seconds = number_option(argv[++i]);
            else throw std::runtime_error("Unknown or incomplete option: " + arg);
        }
        if(lp_method!="sparse"&&lp_method!="dense"&&lp_method!="bounded")throw std::runtime_error("LP method must be sparse, dense or bounded");
        if(options.refine_at_checks&&!options.refine_basis)throw std::runtime_error("refine-at-checks requires refine-basis");
        if(backend!="cpu"&&backend!="cuda")throw std::runtime_error("Backend must be cpu or cuda");
        if(threads<1||threads>256)throw std::runtime_error("Threads must be between 1 and 256");
        if(options.tolerance<=0||options.time_limit_seconds<0||mip_options.relative_gap<0)throw std::runtime_error("Tolerance must be positive; limits and gap must be nonnegative");
        auto total_start = std::chrono::steady_clock::now();
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("Cannot open model");
        std::string path = argv[1];
        if(path.size()>=6 && path.substr(path.size()-6)==".qplib") {
            if(milp) throw std::runtime_error("MIQP is not supported");
            auto problem=sovereign::read_qplib(input);
            sovereign::QpOptions qo;qo.time_limit=options.time_limit_seconds;qo.threads=threads;
            qo.scaling=options.scaling;if(custom_iterations)qo.iteration_limit=options.iteration_limit;if(custom_tolerance)qo.tolerance=options.tolerance;
            if(backend=="cuda"&&!problem.linear.rows.empty())throw std::runtime_error("CUDA currently supports convex box QPs; use CPU for linearly constrained QP");
            auto result=problem.linear.rows.empty()?sovereign::solve_accelerated_box(problem,qo,backend=="cuda"):sovereign::solve_qp_admm(problem,qo);
            double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-total_start).count();
            std::cout<<std::setprecision(17);
            if(json) {
                std::cout<<"{\"status\":\""<<result.status<<"\",\"algorithm\":\""<<result.algorithm<<"\",\"threads\":"<<threads<<",\"optimality_verified\":"<<(result.optimality_verified?"true":"false")<<",\"iterations\":"<<result.iterations
                         <<",\"total_seconds\":"<<seconds<<",\"rows\":"<<problem.linear.rows.size()
                         <<",\"columns\":"<<problem.linear.cost.size()<<",\"objective\":";numeric(result.objective);
                std::cout<<",\"primal_residual\":";numeric(result.primal_residual);
                std::cout<<",\"stationarity_residual\":";numeric(result.stationarity_residual);
                std::cout<<",\"complementarity_residual\":";numeric(result.complementarity_residual);
                std::cout<<",\"dual_bound_minimization_sense\":";numeric(result.dual_bound);
                std::cout<<",\"relative_gap\":";numeric(result.relative_gap);
                std::cout<<",\"primal\":";array(result.primal);
                std::cout<<",\"row_dual\":";array(result.row_dual);std::cout<<"}\n";
            } else std::cout<<"status: "<<result.status<<"\nobjective: "<<result.objective
                           <<"\niterations: "<<result.iterations<<"\nstationarity_residual: "<<result.stationarity_residual<<'\n';
            return result.status=="optimal"?0:1;
        }
        bool mps = path.size() >= 4 && (path.substr(path.size() - 4) == ".mps" || path.substr(path.size() - 4) == ".MPS");
        if(backend!="cpu")throw std::runtime_error("CUDA currently supports QPLIB box QPs only");
        sovereign::Model m;
        sovereign::LinearProblem problem;
        sovereign::StandardForm standard;
        std::size_t row_count = 0, col_count = 0, nonzeros = 0;
        if (mps) {
            problem = sovereign::read_mps(input);
            if (milp) {
                mip_options.lp = options;
                auto result = sovereign::solve_milp(problem, mip_options);
                double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now()-total_start).count();
                std::cout << std::setprecision(17);
                if (!json) {
                    std::cout << "status: " << result.status << "\nnodes: " << result.nodes
                              << "\nobjective: " << result.objective << "\nbest_bound: " << result.best_bound
                              << "\ngap: " << result.gap << "\nseconds: " << seconds << '\n';
                } else {
                    std::cout << "{\"status\":\"" << result.status << "\",\"message\":\""<<result.message<<"\",\"nodes\":" << result.nodes
                              << ",\"lp_iterations\":" << result.lp_iterations << ",\"total_seconds\":" << seconds
                              << ",\"warm_starts\":"<<result.warm_starts<<",\"heuristic_solves\":"<<result.heuristic_solves<<",\"cuts\":"<<result.cuts<<",\"bound_tightenings\":"<<result.bound_tightenings
                              << ",\"rows\":" << problem.rows.size() << ",\"columns\":" << problem.names.size()
                              << ",\"objective\":"; numeric(result.objective);
                    std::cout << ",\"pump_projections\":" << result.pump_projections << ",\"pump_restarts\":" << result.pump_restarts
                              << ",\"pump_incumbents\":" << result.pump_incumbents << ",\"cut_rollbacks\":" << result.cut_rollbacks
                              << ",\"first_incumbent_seconds\":"; numeric(result.first_incumbent_seconds);
                    std::cout << ",\"best_bound\":"; numeric(result.best_bound);
                    const auto& guidance=result.pump_guidance;
                    const auto& reopt=result.pump_reopt;
                    std::cout<<",\"pump_reopt\":{\"enabled\":"<<(mip_options.pump_primal_reopt?"true":"false")
                        <<",\"calls\":"<<reopt.calls<<",\"compatible\":"<<reopt.compatible<<",\"primal\":"<<reopt.primal
                        <<",\"dual\":"<<reopt.dual<<",\"rejected\":"<<reopt.rejected<<",\"verified\":"<<reopt.verified
                        <<",\"phase_one_iterations\":"<<reopt.phase_one_iterations<<",\"factorizations\":"<<reopt.factorizations
                        <<",\"canonical_seconds\":";numeric(reopt.canonical_seconds);std::cout<<",\"factor_seconds\":";numeric(reopt.factor_seconds);
                    std::cout<<",\"pricing_seconds\":";numeric(reopt.pricing_seconds);std::cout<<",\"replay\":";lp_failure(result.pump_reopt_replay);std::cout<<'}';
                    const auto& dr=result.distance_reopt;
                    std::cout<<",\"distance_reopt\":{\"enabled\":"<<(mip_options.pump_distance_reopt?"true":"false")
                        <<",\"seed_updates\":"<<result.distance_seed_updates<<",\"seed_offers\":"<<result.distance_seed_offers
                        <<",\"seed_compatible\":"<<result.distance_seed_compatible<<",\"seed_verified\":"<<result.distance_seed_verified
                        <<",\"calls\":"<<dr.calls<<",\"compatible\":"<<dr.compatible<<",\"primal\":"<<dr.primal
                        <<",\"dual\":"<<dr.dual<<",\"rejected\":"<<dr.rejected<<",\"verified\":"<<dr.verified
                        <<",\"phase_one_iterations\":"<<dr.phase_one_iterations<<",\"factorizations\":"<<dr.factorizations
                        <<",\"canonical_seconds\":";numeric(dr.canonical_seconds);std::cout<<",\"factor_seconds\":";numeric(dr.factor_seconds);
                    std::cout<<",\"pricing_seconds\":";numeric(dr.pricing_seconds);std::cout<<",\"replay\":";lp_failure(result.distance_reopt_replay);std::cout<<'}';
                    std::cout<<",\"private_ranking\":{\"enabled\":"<<(mip_options.pump_distance_stable_ranking?"true":"false")
                        <<",\"calls\":"<<result.private_ranking_calls<<",\"ties\":"<<result.private_ranking_ties
                        <<",\"changes\":"<<result.private_ranking_changes<<'}';
                    std::cout<<",\"private_dual_certificate\":{\"enabled\":"<<(mip_options.private_dual_certificate?"true":"false")
                        <<",\"attempts\":"<<result.private_certificate_attempts<<",\"accepted\":"<<result.private_certificate_accepted<<'}';
                    const auto& bl=result.bounded_lp;
                    std::cout<<",\"bounded_lp\":{\"enabled\":"<<(mip_options.bounded_lp?"true":"false")
                        <<",\"calls\":"<<bl.calls<<",\"warm\":"<<bl.warm<<",\"cold\":"<<bl.cold<<",\"optimal\":"<<bl.optimal
                        <<",\"infeasible\":"<<bl.infeasible<<",\"cutoffs\":"<<bl.cutoffs<<",\"cutoff_nodes\":"<<result.bounded_lp_cutoff_nodes
                        <<",\"failures\":"<<bl.failures<<",\"fallbacks\":"<<result.bounded_lp_fallbacks
                        <<",\"iterations\":"<<bl.iterations<<",\"dual_iterations\":"<<bl.dual_iterations<<",\"primal_iterations\":"<<bl.primal_iterations
                        <<",\"flips\":"<<bl.flips<<",\"refactors\":"<<bl.refactors<<",\"cleanups\":"<<bl.cleanups<<",\"artificial\":"<<bl.artificial
                        <<",\"singular_repairs\":"<<bl.singular_repairs<<",\"farkas_rejected\":"<<bl.farkas_rejected
                        <<",\"verification_rejected\":"<<bl.verification_rejected<<",\"prepared\":"<<bl.prepared<<",\"seconds\":";numeric(bl.seconds);std::cout<<'}';
                    std::cout<<",\"tree_dives\":{\"enabled\":"<<(mip_options.tree_dives?"true":"false")
                        <<",\"calls\":"<<result.tree_dive_calls<<",\"improvements\":"<<result.tree_dive_improvements<<",\"seconds\":";
                    numeric(result.tree_dive_seconds);std::cout<<'}';
                    std::cout<<",\"fix_propagate\":{\"enabled\":"<<(mip_options.fix_propagate?"true":"false")
                        <<",\"calls\":"<<result.fix_propagate_calls<<",\"fixings\":"<<result.fix_propagate_fixings
                        <<",\"lps\":"<<result.fix_propagate_lps<<",\"successes\":"<<result.fix_propagate_successes<<",\"seconds\":";
                    numeric(result.fix_propagate_seconds);std::cout<<'}';
                    const auto& gc=result.gomory;
                    std::cout<<",\"gomory_cuts\":{\"enabled\":"<<(mip_options.gomory_cuts?"true":"false")
                        <<",\"calls\":"<<gc.calls<<",\"candidates\":"<<gc.candidates<<",\"attempts\":"<<gc.attempts
                        <<",\"generated\":"<<gc.generated<<",\"applied\":"<<result.gomory_applied<<",\"purged\":"<<result.gomory_purged<<",\"basis_kept\":"<<result.gomory_basis_kept<<",\"rounds\":"<<result.gomory_rounds
                        <<",\"basis_rejected\":"<<gc.basis_rejected<<",\"skipped_free\":"<<gc.skipped_free
                        <<",\"skipped_drop\":"<<gc.skipped_drop<<",\"skipped_consistency\":"<<gc.skipped_consistency
                        <<",\"skipped_dynamism\":"<<gc.skipped_dynamism<<",\"skipped_support\":"<<gc.skipped_support
                        <<",\"skipped_efficacy\":"<<gc.skipped_efficacy<<",\"skipped_parallel\":"<<gc.skipped_parallel<<",\"rejected_incumbent\":"<<gc.rejected_incumbent
                        <<",\"best_efficacy\":";numeric(result.gomory_best_efficacy);
                    std::cout<<",\"seconds\":";numeric(gc.seconds);std::cout<<'}';
                    std::cout<<",\"private_alternate_reserve\":{\"enabled\":"<<(mip_options.pump_distance_alternate_reserve?"true":"false")
                        <<",\"primary_capped\":"<<result.private_reserve_primary<<",\"alternate_calls\":"<<result.private_reserve_alternate<<'}';
                    auto private_replay=[&](const sovereign::PrivateDiveReplay& f){
                        std::cout<<"{\"step\":"<<f.step<<",\"branch\":"<<f.branch<<",\"alternate\":"<<(f.alternate?"true":"false")<<",\"available_seconds\":";numeric(f.available_seconds);
                        std::cout<<",\"seconds\":";numeric(f.seconds);std::cout<<",\"total_iterations\":"<<f.total_iterations<<",\"compatible\":"<<f.reopt.compatible<<",\"rejected\":"<<f.reopt.rejected
                            <<",\"verified\":"<<f.reopt.verified<<",\"phase_one_iterations\":"<<f.reopt.phase_one_iterations<<",\"lp\":";lp_failure(f.lp);std::cout<<'}';
                    };
                    std::cout<<",\"private_dive_capture\":{\"enabled\":"<<(mip_options.capture_private_dive?"true":"false")<<",\"expensive\":";private_replay(result.private_dive_expensive);
                    std::cout<<",\"failed\":";private_replay(result.private_dive_failed);std::cout<<'}';
                    const auto& ds=result.distance_stage;const auto& sr=ds.reopt;
                    std::cout<<",\"distance_stage\":{\"enabled\":"<<(mip_options.pump_distance_stage?"true":"false")
                        <<",\"considered\":"<<ds.considered<<",\"eligible\":"<<ds.eligible<<",\"attempts\":"<<ds.attempts<<",\"verified\":"<<ds.verified<<",\"incumbents\":"<<ds.incumbents
                        <<",\"child_offers\":"<<ds.child_offers<<",\"child_compatible\":"<<ds.child_compatible<<",\"child_verified\":"<<ds.child_verified
                        <<",\"reopt\":{\"calls\":"<<sr.calls<<",\"compatible\":"<<sr.compatible<<",\"primal\":"<<sr.primal<<",\"dual\":"<<sr.dual<<",\"rejected\":"<<sr.rejected
                        <<",\"verified\":"<<sr.verified<<",\"phase_one_iterations\":"<<sr.phase_one_iterations<<",\"factorizations\":"<<sr.factorizations
                        <<",\"canonical_seconds\":";numeric(sr.canonical_seconds);std::cout<<",\"factor_seconds\":";numeric(sr.factor_seconds);std::cout<<",\"pricing_seconds\":";numeric(sr.pricing_seconds);
                    std::cout<<"},\"replay\":";lp_failure(result.distance_stage_replay);std::cout<<",\"child_replay\":";lp_failure(result.distance_stage_child_replay);
                    std::cout<<",\"samples\":[";
                    for(std::size_t i=0;i<ds.samples.size();++i){if(i)std::cout<<',';const auto& s=ds.samples[i];
                        std::cout<<"{\"node\":"<<s.node<<",\"iterations\":"<<s.iterations<<",\"eligible\":"<<(s.eligible?"true":"false")<<",\"attempted\":"<<(s.attempted?"true":"false")
                            <<",\"verified\":"<<(s.verified?"true":"false")<<",\"accepted\":"<<(s.accepted?"true":"false")<<",\"status\":\""<<s.status<<"\",\"available_seconds\":";numeric(s.available_seconds);
                        std::cout<<",\"seconds\":";numeric(s.seconds);std::cout<<'}';}
                    std::cout<<"]}";
                    std::cout<<",\"pump_guidance\":{\"enabled\":"<<(mip_options.pump_guided_diving?"true":"false")
                        <<",\"calls\":"<<guidance.calls<<",\"candidates\":"<<guidance.candidates<<",\"rejected\":"<<guidance.rejected
                        <<",\"improvements\":"<<guidance.improvements<<",\"dives\":"<<guidance.dives<<",\"steps\":"<<guidance.steps
                        <<",\"stored_values\":"<<guidance.stored_values<<",\"samples\":[";
                    for(std::size_t i=0;i<guidance.samples.size();++i){if(i)std::cout<<',';const auto& s=guidance.samples[i];
                        std::cout<<"{\"node\":"<<s.node<<",\"candidates\":"<<s.candidates<<",\"rejected\":"<<s.rejected
                            <<",\"improvements\":"<<s.improvements<<",\"steps\":"<<s.steps<<",\"selected\":"<<(s.selected?"true":"false")
                            <<",\"used\":"<<(s.used?"true":"false")<<",\"initial_distance\":";numeric(s.initial_distance);
                        std::cout<<",\"best_distance\":";numeric(s.best_distance);std::cout<<",\"initial\":";array(s.initial);
                        std::cout<<",\"point\":";array(s.point);std::cout<<'}';}
                    std::cout<<"]}";
                    const auto& distance=result.pump_distance;
                    std::cout<<",\"pump_distance\":{\"enabled\":"<<(mip_options.pump_distance_diving?"true":"false")
                        <<",\"dives\":"<<distance.dives<<",\"lp_calls\":"<<distance.lp_calls
                        <<",\"verified_points\":"<<distance.verified_points<<",\"warm_starts\":"<<distance.warm_starts<<",\"samples\":[";
                    for(std::size_t i=0;i<distance.samples.size();++i){if(i)std::cout<<',';const auto& s=distance.samples[i];
                        std::cout<<"{\"node\":"<<s.node<<",\"auxiliaries\":"<<s.auxiliaries<<",\"lp_calls\":"<<s.lp_calls
                            <<",\"verified_points\":"<<s.verified_points<<",\"warm_starts\":"<<s.warm_starts<<",\"initial_distance\":";numeric(s.initial_distance);
                        std::cout<<",\"first_distance\":";numeric(s.first_distance);std::cout<<",\"last_distance\":";numeric(s.last_distance);
                        std::cout<<",\"first_target_distance\":";numeric(s.first_target_distance);std::cout<<",\"last_target_distance\":";numeric(s.last_target_distance);std::cout<<'}';}
                    std::cout<<"]}";
                    std::cout<<",\"heuristic_repair\":{\"enabled\":"<<(mip_options.repair_heuristic_candidates?"true":"false")
                        <<",\"attempts\":"<<result.heuristic_repair_attempts<<",\"successes\":"<<result.heuristic_repair_successes
                        <<",\"duplicate_skips\":"<<result.heuristic_repair_duplicates<<",\"sparse_calls\":"<<result.heuristic_repair_sparse_calls
                        <<",\"dense_calls\":"<<result.heuristic_repair_dense_calls<<",\"seconds\":";numeric(result.heuristic_repair_seconds);
                    std::cout<<",\"shared_seconds\":";numeric(result.candidate_repair_seconds);std::cout<<",\"allowance\":";numeric(std::min(15.0,.1*options.time_limit_seconds));std::cout<<'}';
                    std::cout<<",\"feasibility\":{\"enabled\":"<<(mip_options.capture_feasibility?"true":"false")
                        <<",\"events\":"<<result.feasibility.events<<",\"stored_values\":"<<result.feasibility.stored_values
                        <<",\"calls\":"<<result.feasibility.calls<<",\"rejected_point\":";array(result.feasibility.rejected_point);
                    std::cout<<",\"rejected_rounded_violation\":";numeric(result.feasibility.rejected_rounded_violation);
                    std::cout<<",\"rejected_node\":"<<result.feasibility.rejected_node<<",\"rejected_call\":"<<result.feasibility.rejected_call
                        <<",\"rejected_step\":"<<result.feasibility.rejected_step<<",\"samples\":[";
                    for(std::size_t i=0;i<result.feasibility.samples.size();++i){if(i)std::cout<<',';const auto& e=result.feasibility.samples[i];
                        std::cout<<"{\"kind\":\""<<e.kind<<"\",\"status\":\""<<e.status<<"\",\"node\":"<<e.node<<",\"call\":"<<e.call
                            <<",\"step\":"<<e.step<<",\"mode\":"<<e.mode<<",\"variable\":"<<e.variable<<",\"iterations\":"<<e.iterations
                            <<",\"fractional\":"<<e.fractional<<",\"alternate\":"<<(e.alternate?"true":"false")<<",\"accepted\":"<<(e.accepted?"true":"false")
                            <<",\"distance\":";numeric(e.distance);std::cout<<",\"violation\":";numeric(e.violation);
                        std::cout<<",\"point\":";array(e.point);std::cout<<",\"target\":";array(e.target);std::cout<<'}';}
                    std::cout<<"]}";
                    std::cout<<",\"work\":{\"enabled\":"<<(mip_options.capture_work?"true":"false")<<",\"seconds\":";
                    numeric(result.work.seconds);std::cout<<",\"root_cut_rounds\":"<<mip_options.root_cut_rounds
                        <<",\"restart_by_nodes\":"<<(mip_options.restart_by_nodes?"true":"false")<<",\"restart_nodes\":";
                    if(mip_options.restart_by_nodes)std::cout<<mip_options.late_cover_restart_nodes;else std::cout<<"null";
                    std::cout<<",\"refinement_enabled\":"<<(options.capture_refinement?"true":"false")<<",\"refinement\":";refinement_work(result.work.refinement);
                    std::cout<<",\"phases\":[";
                    for(std::size_t i=0;i<result.work.phases.size();++i){if(i)std::cout<<',';const auto& w=result.work.phases[i];
                        std::cout<<"{\"name\":\""<<sovereign::detail::phase_name(i)<<"\",\"seconds\":";numeric(w.seconds);
                        std::cout<<",\"lp_calls\":"<<w.lp_calls<<",\"iterations\":"<<w.iterations<<",\"refinement\":";refinement_work(w.refinement);std::cout<<'}';}
                    std::cout<<"]}";
                    auto extended=[](double x){if(std::isfinite(x))numeric(x);else std::cout<<(x<0?"\"-inf\"":"\"inf\"");};
                    std::cout<<",\"cut_policy\":{\"version\":2,\"enabled\":"<<(mip_options.adaptive_cut_rounds?"true":"false")
                             <<",\"require_incumbent\":"<<(mip_options.cut_after_incumbent?"true":"false")
                             <<",\"capture_enabled\":"<<((mip_options.capture_cut_rounds||mip_options.adaptive_cut_rounds)?"true":"false")
                             <<",\"stops\":"<<result.adaptive_cut_stops<<",\"rounds\":[";
                    for(std::size_t i=0;i<result.cut_round_trace.size();++i){if(i)std::cout<<',';const auto& c=result.cut_round_trace[i];
                        std::cout<<"{\"node\":"<<c.node<<",\"restart\":"<<c.restart<<",\"round\":"<<c.round
                                 <<",\"root_iterations\":"<<c.root_iterations<<",\"iterations\":"<<c.iterations<<",\"before\":";numeric(c.before);
                        std::cout<<",\"after\":";numeric(c.after);std::cout<<",\"offset\":";numeric(c.offset);
                        std::cout<<",\"incumbent_objective\":";numeric(c.incumbent_objective);
                        std::cout<<",\"decision\":\""<<c.decision<<"\"}";}
                    std::cout<<"]}";
                    std::cout<<",\"frontier\":{\"raw_lp_priority\":"<<(mip_options.raw_lp_priority?"true":"false")
                             <<",\"capture_enabled\":"<<(mip_options.capture_frontier?"true":"false")<<",\"event_count\":"<<result.frontier_events
                             <<",\"priority_minimum_mismatches\":"<<result.frontier_priority_mismatches<<",\"max_queued\":"<<result.frontier_max_queued
                             <<",\"trace_truncated\":"<<(result.frontier_events>result.frontier_trace.size()?"true":"false")<<",\"trace\":[";
                    for(std::size_t k=0;k<result.frontier_trace.size();++k){if(k)std::cout<<',';const auto& e=result.frontier_trace[k];
                        std::cout<<"{\"op\":\""<<e.operation<<"\",\"id\":"<<e.id<<",\"depth\":"<<e.depth<<",\"queued\":"<<e.queued<<",\"deferred\":"<<e.deferred<<",\"proof\":";extended(e.proof);
                        std::cout<<",\"rank\":";extended(e.rank);std::cout<<'}';}
                    std::cout<<"]}";
                    const auto& lattice=result.objective_lattice;
                    std::cout<<",\"objective_lattice\":{\"enabled\":"<<(mip_options.objective_lattice?"true":"false")
                             <<",\"eligible\":"<<(lattice.eligible?"true":"false")<<",\"reason\":\""<<lattice.reason<<"\",\"offset_minimization\":";numeric(lattice.offset);
                    std::cout<<",\"step\":";numeric(lattice.step);std::cout<<",\"coefficients_minimization\":[";
                    for(std::size_t k=0;k<lattice.coefficients.size();++k){if(k)std::cout<<',';std::cout<<lattice.coefficients[k];}
                    std::cout<<"],\"substitutions\":[";
                    for(std::size_t k=0;k<lattice.substitutions.size();++k){if(k)std::cout<<',';std::cout<<"{\"column\":"<<lattice.substitutions[k].first<<",\"row\":"<<lattice.substitutions[k].second<<'}';}
                    std::cout<<"],\"bound_calls\":"<<result.lattice_bound_calls<<",\"bound_improvements\":"<<result.lattice_bound_improvements
                             <<",\"trace_truncated\":"<<(result.lattice_bound_improvements>result.lattice_bound_trace.size()?"true":"false")<<",\"trace\":[";
                    for(std::size_t k=0;k<result.lattice_bound_trace.size();++k){if(k)std::cout<<',';const auto& t=result.lattice_bound_trace[k];
                        std::cout<<"{\"node\":"<<t.node<<",\"before_minimization\":";numeric(t.before);std::cout<<",\"after_minimization\":";numeric(t.after);std::cout<<'}';}
                    std::cout<<"]}";
                    std::cout<<",\"compact_equalities_enabled\":"<<((options.compact_equalities||mip_options.late_compact_equalities)?"true":"false")<<",\"late_compact_equalities_enabled\":"<<(mip_options.late_compact_equalities?"true":"false")<<",\"compact_lp_calls\":"<<result.compact_lp_calls<<",\"compact_lp_fallbacks\":"<<result.compact_lp_fallbacks<<",\"root_lp_rows\":"<<result.root_lp_rows<<",\"root_compact_equalities\":"<<result.root_compact_equalities;
                    std::cout<<",\"stable_primal_ratio_enabled\":"<<(options.stable_primal_ratio?"true":"false");
                    std::cout<<",\"basis_refinement_enabled\":"<<(options.refine_basis?"true":"false");
                    std::cout<<",\"basis_refinement_at_checks\":"<<(options.refine_at_checks?"true":"false");
                    std::cout << ",\"branching\":\"" << mip_options.branching << "\",\"pseudocost_updates\":" << result.pseudocost_updates
                              << ",\"reduced_bound_lp_enabled\":"<<((mip_options.reduced_bound_lp||mip_options.late_reduced_bound_lp)?"true":"false")<<",\"late_reduced_bound_lp_enabled\":"<<(mip_options.late_reduced_bound_lp?"true":"false")
                              << ",\"reduced_bound_lp_calls\":"<<result.reduced_bound_lp_calls<<",\"reduced_bound_lp_fallbacks\":"<<result.reduced_bound_lp_fallbacks<<",\"reduced_bound_lp_accepted\":"<<result.reduced_bound_lp_accepted
                              << ",\"reduced_upper_candidates\":"<<result.reduced_upper_candidates<<",\"root_reduced_upper_bounds\":"<<result.root_reduced_upper_bounds
                              << ",\"strong_branch_probes\":" << result.strong_branch_probes << ",\"strong_branch_seconds\":";numeric(result.strong_branch_seconds);
                    std::cout << ",\"gap\":"; numeric(result.gap);
                    std::cout << ",\"lp_recovery_attempts\":"<<result.lp_recovery_attempts<<",\"lp_recovery_successes\":"<<result.lp_recovery_successes<<",\"lp_recovery_seconds\":";numeric(result.lp_recovery_seconds);
                    std::cout << ",\"lp_resource_limits\":"<<result.lp_resource_limits<<",\"separator_rows_discarded\":"<<result.separator_rows_discarded<<",\"deferred_nodes\":"<<result.deferred_nodes<<",\"unresolved_nodes\":"<<result.unresolved_nodes
                              << ",\"neighborhood_calls\":"<<result.neighborhood_calls<<",\"neighborhood_nodes\":"<<result.neighborhood_nodes
                              << ",\"neighborhood_improvements\":"<<result.neighborhood_improvements<<",\"neighborhood_seconds\":";numeric(result.neighborhood_seconds);
                    std::cout<<",\"neighborhood_paced\":"<<(mip_options.pace_neighborhood?"true":"false")<<",\"neighborhood_min_spacing_seconds\":";
                    numeric(mip_options.pace_neighborhood?std::min(5.0,.02*options.time_limit_seconds):0);
                    std::cout<<",\"neighborhood\":\""<<mip_options.neighborhood<<"\",\"neighborhood_trace\":[";
                    for(std::size_t k=0;k<result.neighborhood_trace.size();++k){
                        if(k)std::cout<<',';const auto& sample=result.neighborhood_trace[k];
                        std::cout<<"{\"node\":"<<sample.node<<",\"nodes\":"<<sample.nodes<<",\"lp_failures\":"<<sample.lp_failures<<",\"stalls_before\":"<<sample.stalls_before;
                        std::cout<<",\"selection\":\""<<sample.selection<<"\",\"start_seconds\":";numeric(sample.start_seconds);
                        std::cout<<",\"seconds\":";numeric(sample.seconds);std::cout<<",\"budget\":";numeric(sample.budget);
                        std::cout<<",\"objective_before\":";numeric(sample.objective_before);std::cout<<",\"objective_after\":";numeric(sample.objective_after);
                        std::cout<<",\"improved\":"<<(sample.improved?"true":"false")<<",\"frontier_exhausted\":"<<(sample.frontier_exhausted?"true":"false")<<",\"free_variables\":[";
                        for(std::size_t j=0;j<sample.free_variables.size();++j){if(j)std::cout<<',';std::cout<<sample.free_variables[j];}
                        std::cout<<"],\"material_improved\":"<<(sample.material_improved?"true":"false")<<",\"radius\":"<<sample.radius;
                        std::cout<<",\"strong\":"<<(sample.strong?"true":"false");
                        std::cout<<",\"center_primal\":";array(sample.center_primal);
                        std::cout<<",\"improved_primal\":";array(sample.improved_primal);std::cout<<'}';
                    }
                    std::cout<<']';
                    std::cout << ",\"first_lp_failure\":";lp_failure(result.first_lp_failure);
                    std::cout << ",\"rejected_integer_candidates\":"<<result.rejected_integer_candidates<<",\"rejected_candidates\":[";
                    for(std::size_t k=0;k<result.rejected_candidates.size();++k){
                        if(k)std::cout<<',';const auto& sample=result.rejected_candidates[k];
                        std::cout<<"{\"fixing\":";lp_failure(sample.fixing);
                        std::cout<<",\"relaxation\":";array(sample.relaxation);std::cout<<",\"rounded\":";array(sample.rounded);std::cout<<",\"repair_primal\":";array(sample.repair_primal);
                        std::cout<<",\"node_lower\":";array(sample.node_lower);std::cout<<",\"node_upper\":";array(sample.node_upper);
                        std::cout<<",\"relaxation_violation\":";numeric(sample.relaxation_violation);std::cout<<",\"rounded_violation\":";numeric(sample.rounded_violation);std::cout<<",\"repair_violation\":";numeric(sample.repair_violation);
                        std::cout<<",\"repair_infeasibility_verified\":"<<(sample.repair_infeasibility_verified?"true":"false")<<",\"repair_optimality_verified\":"<<(sample.repair_optimality_verified?"true":"false")<<",\"repair_accepted\":"<<(sample.repair_accepted?"true":"false");
                        std::cout<<",\"fallback_status\":\""<<sample.fallback_status<<"\",\"fallback_accepted\":"<<(sample.fallback_accepted?"true":"false")<<",\"fallback_primal\":";array(sample.fallback_primal);std::cout<<'}';
                    }
                    std::cout<<']';
                    std::cout<<",\"candidate_repair_attempts\":"<<result.candidate_repair_attempts<<",\"candidate_repair_successes\":"<<result.candidate_repair_successes<<",\"repair_branch_nodes\":"<<result.repair_branch_nodes<<",\"candidate_repair_seconds\":";numeric(result.candidate_repair_seconds);
                    std::cout<<",\"binary_meet_enabled\":"<<(mip_options.binary_meet?"true":"false")<<",\"binary_meet_attempts\":"<<result.binary_meet_attempts;
                    std::cout<<",\"binary_meet_eligible\":"<<(result.binary_meet_eligible?"true":"false")<<",\"binary_meet_completed\":"<<(result.binary_meet_completed?"true":"false");
                    std::cout<<",\"binary_meet_improved\":"<<(result.binary_meet_improved?"true":"false")<<",\"binary_meet_left_states\":"<<result.binary_meet_left_states;
                    std::cout<<",\"binary_meet_right_states\":"<<result.binary_meet_right_states<<",\"binary_meet_query_nodes\":"<<result.binary_meet_query_nodes;
                    std::cout<<",\"binary_meet_seconds\":";numeric(result.binary_meet_seconds);std::cout<<",\"binary_meet_budget\":";numeric(result.binary_meet_budget);
                    std::cout<<",\"binary_meet_primal\":";array(result.binary_meet_primal);
                    std::cout<<",\"lifted_covers_enabled\":"<<(mip_options.lifted_covers?"true":"false")<<",\"lifted_cover_states\":"<<result.lifted_cover_states<<",\"lifted_cover_checked\":"<<result.lifted_cover_checked;
                    std::cout<<",\"lifted_cover_seconds\":";numeric(result.lifted_cover_seconds);
                    std::cout<<",\"late_lifted_covers_enabled\":"<<(mip_options.late_lifted_covers?"true":"false")<<",\"cut_restarts\":"<<result.cut_restarts<<",\"cut_restart_nodes\":"<<result.cut_restart_nodes;
                    std::cout<<",\"cut_restart_seconds\":";numeric(result.cut_restart_seconds);std::cout<<",\"cut_restart_bound\":";numeric(result.cut_restart_bound);
                    std::cout<<",\"cut_restart_objective\":";numeric(result.cut_restart_objective);std::cout<<",\"cut_restart_primal\":";array(result.cut_restart_primal);
                    std::cout<<",\"root_bound_before_cuts\":";numeric(result.root_bound_before_cuts);std::cout<<",\"root_bound_after_cuts\":";numeric(result.root_bound_after_cuts);
                    std::cout<<",\"lifted_cover_trace\":[";
                    for(std::size_t k=0;k<result.lifted_cover_trace.size();++k){const auto& c=result.lifted_cover_trace[k];if(k)std::cout<<",";
                        std::cout<<"{\"source_row\":"<<c.source_row<<",\"side\":"<<c.side<<",\"rhs\":";numeric(c.rhs);std::cout<<",\"assignments\":"<<c.assignments<<",\"row\":[";
                        for(std::size_t j=0;j<c.row.size();++j){if(j)std::cout<<",";std::cout<<"["<<c.row[j].first<<",";numeric(c.row[j].second);std::cout<<"]";}std::cout<<"]}";
                    }std::cout<<"]";
                    const auto& proof=result.binary_proof;
                    std::cout<<",\"binary_proof_enabled\":"<<(mip_options.binary_proof?"true":"false")<<",\"binary_proof_attempts\":"<<result.binary_proof_attempts<<",\"binary_proof_budget\":";numeric(result.binary_proof_budget);
                    std::cout<<",\"binary_proof\":{\"version\":1,\"arithmetic\":\"checked_int64\",\"status\":\""<<proof.status<<"\",\"reason\":\""<<proof.reason<<"\"";
                    std::cout<<",\"eligible\":"<<(proof.eligible?"true":"false")<<",\"completed\":"<<(proof.completed?"true":"false")<<",\"verified\":"<<(proof.verified?"true":"false")<<",\"feasible\":"<<(proof.feasible?"true":"false");
                    std::cout<<",\"seconds\":";numeric(proof.seconds);std::cout<<",\"work\":"<<proof.work<<",\"work_limit\":"<<mip_options.binary_proof_work;
                    std::cout<<",\"left_states\":"<<proof.left_states<<",\"right_states\":"<<proof.right_states<<",\"query_nodes\":"<<proof.query_nodes<<",\"objective_minimization\":";
                    if(proof.feasible)std::cout<<proof.objective_minimization;else std::cout<<"null";
                    std::cout<<",\"binary_indices\":[";for(std::size_t j=0;j<proof.binary_indices.size();++j){if(j)std::cout<<',';std::cout<<proof.binary_indices[j];}
                    std::cout<<"],\"primal\":[";for(std::size_t j=0;j<proof.primal.size();++j){if(j)std::cout<<',';std::cout<<proof.primal[j];}std::cout<<"]}";
                    std::cout << ",\"incumbent_trace\":[";
                    for(std::size_t k=0;k<result.incumbent_trace.size();++k){if(k)std::cout<<',';std::cout<<'[';numeric(result.incumbent_trace[k].first);std::cout<<',';numeric(result.incumbent_trace[k].second);std::cout<<']';}
                    std::cout << ']';
                    std::cout << ",\"primal\":"; array(result.primal); std::cout << "}\n";
                }
                return result.status == "optimal" || result.status == "gap_limit" ? 0 : 1;
            }
            if(lp_method=="dense") {standard = sovereign::standardize(problem, options.max_tableau_cells);m = standard.model;}
            row_count = problem.rows.size(); col_count = problem.cost.size();
            for (const auto& row : problem.rows) nonzeros += row.size();
        } else {
        if (milp) throw std::runtime_error("MILP input requires MPS with integer declarations");
        long long n, rows;
        if (!(input >> n >> rows) || n <= 0 || rows < 0 || n > 1000 || rows > 1000)
            throw std::runtime_error("Invalid dimensions (prototype limit: 1000 each)");
        m.cost.resize(static_cast<std::size_t>(n));
        m.rows.assign(static_cast<std::size_t>(rows), std::vector<double>(n));
        m.rhs.resize(static_cast<std::size_t>(rows));
        for (double& c : m.cost) if (!(input >> c)) throw std::runtime_error("Invalid objective");
        for (std::size_t i = 0; i < m.rows.size(); ++i) {
            for (double& a : m.rows[i]) if (!(input >> a)) throw std::runtime_error("Invalid row");
            if (!(input >> m.rhs[i])) throw std::runtime_error("Missing RHS");
        }
        std::string extra;
        if (input >> extra) throw std::runtime_error("Unexpected trailing input");
        row_count = m.rows.size(); col_count = m.cost.size();
        for (const auto& row : m.rows) for (double a : row) nonzeros += a != 0;
        }
        auto start = std::chrono::steady_clock::now();
        sovereign::SparseLpResult sparse_result;
        sovereign::Result r;
        if(lp_method=="sparse") {
            sparse_result=sovereign::solve_sparse_lp(mps?problem:sovereign::linear_from_dense(m),options);
            r=sparse_result.solution;
        } else if(lp_method=="bounded") {
            sparse_result=sovereign::solve_bounded_lp(mps?problem:sovereign::linear_from_dense(m),options);
            r=sparse_result.solution;
        } else r=sovereign::solve(m, options);
        double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        double original_scaled = r.scaled_primal_violation;
        auto canonical_primal = lp_method=="dense"?r.primal:sparse_result.canonical_primal;
        if (mps && lp_method=="dense" && !r.primal.empty()) {
            r.primal = standard.recover(r.primal);
            r.objective = problem.offset;
            for (std::size_t j = 0; j < r.primal.size(); ++j) r.objective += problem.cost[j] * r.primal[j];
            r.max_violation = sovereign::original_violation(problem, r.primal, false);
            original_scaled = sovereign::original_violation(problem, r.primal, true);
            if (!std::isfinite(r.objective) || original_scaled > 10 * options.tolerance) {
                r.status = "numerical_error"; r.optimality_verified = false;
            }
        }
        double total = std::chrono::duration<double>(std::chrono::steady_clock::now() - total_start).count();
        std::cout << std::setprecision(17);
        if (json) {
            std::cout << "{\"status\":\"" << r.status << "\",\"algorithm\":\""<<(lp_method=="bounded"?"bounded_dual":lp_method)<<"_simplex\",\"rows\":" << row_count << ",\"columns\":" << col_count
                      << ",\"nonzeros\":" << nonzeros << ",\"iterations\":" << r.iterations
                      << ",\"solve_seconds\":" << elapsed << ",\"total_seconds\":" << total << ",\"objective\":";
            if (r.primal.empty()) std::cout << "null"; else numeric(r.objective);
            std::cout << ",\"max_primal_violation\":"; numeric(r.max_violation);
            std::cout<<",\"compact_equalities_enabled\":"<<(options.compact_equalities?"true":"false")<<",\"compact_fallback\":"<<(sparse_result.compact_fallback?"true":"false")<<",\"canonical_rows\":"<<sparse_result.canonical_rows<<",\"compact_equality_rows\":"<<sparse_result.compact_equality_rows;
            std::cout << ",\"scaled_primal_violation\":"; numeric(original_scaled);
            std::cout << ",\"stable_primal_ratio_enabled\":" << (options.stable_primal_ratio?"true":"false");
            std::cout << ",\"basis_refinement_enabled\":" << (options.refine_basis?"true":"false")
                      << ",\"basis_refinement_attempts\":" << sparse_result.refinement.attempts
                      << ",\"basis_refinement_accepted\":" << sparse_result.refinement.accepted;
            std::cout<<",\"capture_refinement\":"<<(options.capture_refinement?"true":"false")<<",\"basis_refinement_work\":";refinement_work(sparse_result.refinement);
            std::cout<<",\"basis_refinement_at_checks\":"<<(options.refine_at_checks?"true":"false");
            std::cout << ",\"scaled_dual_violation\":"; numeric(r.scaled_dual_violation);
            std::cout << ",\"relative_gap\":"; numeric(r.relative_gap);
            std::cout << ",\"optimality_verified\":" << (r.optimality_verified ? "true" : "false");
            std::cout << ",\"infeasibility_verified\":" << (r.infeasibility_verified ? "true" : "false");
            std::cout << ",\"unboundedness_verified\":" << (r.unboundedness_verified ? "true" : "false");
            std::cout << ",\"unbounded_ray\":";array(r.unbounded_ray);
            std::cout << ",\"primal\":"; array(r.primal);
            std::cout << ",\"canonical_primal\":"; array(canonical_primal);
            std::cout << ",\"canonical_dual\":"; array(r.dual);
            std::cout << "}\n";
        } else {
        std::cout << "status: " << r.status << "\niterations: " << r.iterations
                  << "\nseconds: " << elapsed << '\n';
        if (!r.primal.empty()) {
            std::cout << "objective: " << r.objective << "\nmax_primal_violation: " << r.max_violation
                      << "\nrelative_gap: " << r.relative_gap << "\noptimality_verified: " << r.optimality_verified << '\n';
            for (std::size_t j = 0; j < r.primal.size(); ++j)
                std::cout << "x[" << j << "]: " << r.primal[j] << '\n';
        }
        }
        return r.status == "optimal" ? 0 : 1;
    } catch (const std::exception& e) { std::cerr << "error: " << e.what() << '\n'; return 2; }
}
