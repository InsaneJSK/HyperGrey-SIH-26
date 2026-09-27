#include "sparse_lp.hpp"
#include "accelerated_qp.hpp"
#include "milp.hpp"
#include "milp_neighborhood.hpp"
#include <iostream>

void require(bool condition,const char* text){if(!condition)throw std::runtime_error(text);}
int main(){try{
    sovereign::SparseLU lu;
    std::vector<sovereign::SparseVector> columns={{{0,0},{1,2},{2,1}},{{0,1},{1,3}},{{0,2},{2,4}}};
    require(lu.factor(columns),"Sparse LU pivoting failed");
    auto x=lu.solve({8,8,13});
    require(std::abs(x[0]-1)<1e-10&&std::abs(x[1]-2)<1e-10&&std::abs(x[2]-3)<1e-10,"LU forward solve wrong");
    auto y=lu.solve({7,7,14},true);
    require(std::abs(y[0]-1)<1e-10&&std::abs(y[1]-2)<1e-10&&std::abs(y[2]-3)<1e-10,"LU transpose solve wrong");
    auto unbounded=sovereign::solve_sparse_lp(sovereign::linear_from_dense({{-1},{{-1}},{-2}}));
    require(unbounded.solution.status=="unbounded"&&unbounded.solution.unboundedness_verified&&unbounded.solution.unbounded_ray[0]>0,"Missing validated unbounded ray");
    sovereign::QuadraticProblem q;auto& p=q.linear;
    const std::size_t n=300;p.names.resize(n);p.cost.assign(n,-1);p.lower.assign(n,0);p.upper.assign(n,10);p.integer.assign(n,false);
    for(std::size_t j=0;j<n;++j){p.names[j]="x"+std::to_string(j);q.hessian.push_back({j,j,j%2?5.0:1.0});if(j%2)q.hessian.push_back({j,j-1,2.0});}
    require(sovereign::check_convex_hessian(q),"Large PSD non-diagonally-dominant Hessian rejected");
    sovereign::QpOptions options;options.time_limit=10;
    auto r=sovereign::solve_accelerated_box(q,options,false);
    require(r.status=="optimal"&&r.optimality_verified,"Large PSD box QP failed");
    q.hessian[0].value=-1;require(!sovereign::check_convex_hessian(q),"Indefinite Hessian accepted");
    sovereign::QuadraticProblem diagonal;auto& dp=diagonal.linear;
    dp.names={"a","b","c"};dp.cost={-4,-10,-20};dp.lower={0,0,0};dp.upper={10,10,10};dp.integer={false,false,false};
    dp.rows={{{0,1},{1,1},{2,1}}};dp.row_lower={6};dp.row_upper={6};diagonal.hessian={{0,0,2},{1,1,4},{2,2,6}};
    auto equality=sovereign::solve_qp_admm(diagonal);
    require(equality.status=="optimal"&&std::abs(equality.objective+48)<1e-6,"Diagonal equality QP failed");
    dp.lower[0]=dp.upper[0]=1;equality=sovereign::solve_qp_admm(diagonal);
    require(equality.status=="optimal"&&std::abs(equality.objective+48)<1e-6,"Fixed-variable diagonal QP failed");
    dp.maximize=true;for(double& v:dp.cost)v=-v;for(auto& h:diagonal.hessian)h.value=-h.value;
    equality=sovereign::solve_qp_admm(diagonal);require(equality.status=="optimal"&&std::abs(equality.objective-48)<1e-6,"Concave maximization QP normalization failed");
    require(std::isfinite(equality.dual_bound)&&equality.relative_gap<1e-7,"Diagonal maximization dual bound missing");
    require(std::abs(equality.dual_bound+48)<1e-6,"QP dual bound must use minimization sense");
    auto invalid=equality;invalid.primal[0]=NAN;sovereign::check_qp_solution(diagonal,invalid,1e-7);
    require(!invalid.optimality_verified,"Nonfinite candidate retained an optimality claim");
    invalid=equality;invalid.row_dual.clear();sovereign::check_qp_solution(diagonal,invalid,1e-7);
    require(!invalid.optimality_verified,"Malformed dual retained an optimality claim");
    // Structure-based routing above the former 512-variable limit; duplicated
    // rows deliberately make the dual Newton Schur system rank deficient.
    sovereign::QuadraticProblem big;auto& bp=big.linear;
    const std::size_t count=600;bp.names.resize(count);bp.cost.assign(count,0);bp.lower.assign(count,-INFINITY);bp.upper.assign(count,INFINITY);bp.integer.assign(count,false);
    for(std::size_t j=0;j<count;++j){bp.names[j]="z"+std::to_string(j);big.hessian.push_back({j,j,j%2?1e-12:1});}
    for(std::size_t j=0;j<count;j+=2){bp.rows.push_back({{j,1},{j+1,1e-6}});bp.row_lower.push_back(1e4);bp.row_upper.push_back(1e4);}
    bp.rows.push_back(bp.rows[0]);bp.row_lower.push_back(1e4);bp.row_upper.push_back(1e4);
    auto large=sovereign::solve_qp_admm(big);
    require(large.status=="optimal"&&large.algorithm=="diagonal_qp_dual_newton","Large structured QP dispatch failed");
    require(std::abs(large.objective-7.5e9)<750&&large.relative_gap<1e-7,"Large scaled QP objective/bound failed");
    bp.lower[0]=2;bp.upper[0]=1;large=sovereign::solve_qp_admm(big);
    require(large.status=="infeasible_bounds"&&!large.optimality_verified,"Invalid bounds reached the specialist");
    sovereign::QuadraticProblem flat;flat.linear.names={"flat","row"};flat.linear.cost={0,0};flat.linear.lower={-1e12,-1};flat.linear.upper={1e12,1};flat.linear.integer={false,false};
    flat.hessian={{0,0,1e-16},{1,1,1}};flat.linear.rows={{{1,1}}};flat.linear.row_lower={0};flat.linear.row_upper={0};
    sovereign::QpResult misleading;misleading.primal={1e8,0};misleading.row_dual={0};sovereign::check_qp_solution(flat,misleading,1e-7);
    require(misleading.stationarity_residual<1e-7&&misleading.relative_gap>.1&&!misleading.optimality_verified,"Tiny gradient bypassed the available diagonal dual-gap gate");
    sovereign::QuadraticProblem linear;linear.linear=sovereign::linear_from_dense({{-1e-12},{},{}});
    auto linear_qp=sovereign::solve_accelerated_box(linear,options,false);require(linear_qp.status=="unbounded","Zero-Hessian unbounded QP misclassified");
    bool rejected=false;try{options.threads=0;sovereign::solve_accelerated_box(q,options,false);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Invalid thread setting accepted");
    // General-integer interior targets require explicit absolute-distance columns.
    // With presolve disabled the root is fractional and rounding is infeasible;
    // the pump must project, detect a repeated target, perturb, and verify a repair.
    sovereign::LinearProblem pump_model;
    pump_model.names={"integer"};pump_model.cost={1};pump_model.lower={-3};pump_model.upper={3};pump_model.integer={true};
    pump_model.rows={{{0,1}}};pump_model.row_lower={1.25};pump_model.row_upper={INFINITY};
    sovereign::MilpOptions mo;mo.presolve=false;mo.cover_cuts=false;mo.node_limit=1;mo.lp.time_limit_seconds=10;
    auto pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.pump_projections>0&&pumped.pump_restarts>0&&pumped.pump_incumbents==1,"General-integer pump was not exercised");
    require(pumped.primal.size()==1&&pumped.primal[0]==2&&pumped.objective==2,"Pump produced an invalid integer repair");
    require(pumped.status=="node_limit"&&pumped.best_bound<=1.25&&pumped.gap>0,"Heuristic objective leaked into the proof bound");
    auto repeated=sovereign::solve_milp(pump_model,mo);
    require(repeated.primal==pumped.primal&&repeated.pump_projections==pumped.pump_projections,"Fixed-seed pump is not reproducible");
    pump_model.lower={.1};pump_model.upper={3.8};pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.primal.size()==1&&pumped.primal[0]==2,"Fractional bounds caused a nonintegral pump target");
    pump_model.lower={-3};pump_model.upper={3};
    pump_model.row_lower={-INFINITY};pump_model.row_upper={-1.25};pump_model.cost={1};pump_model.maximize=true;
    pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.primal.size()==1&&pumped.primal[0]==-2&&pumped.objective==-2&&pumped.best_bound>=-1.25,"Negative integer/maximization pump failed");
    pump_model.row_lower={.5};pump_model.row_upper={.5};pump_model.maximize=false;
    pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.primal.empty()&&pumped.pump_incumbents==0,"Infeasible rounded candidate was accepted");
    mo.feasibility_pump=false;pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.pump_projections==0&&pumped.pump_restarts==0,"Pump ablation flag ignored");
    mo.feasibility_pump=true;mo.heuristics=false;pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.pump_projections==0,"No-heuristics flag must disable the pump too");
    mo.lp.time_limit_seconds=0;pumped=sovereign::solve_milp(pump_model,mo);
    require(pumped.status=="time_limit"&&pumped.nodes==0&&pumped.primal.empty(),"Zero time budget was ignored");
    // Trial branch bounds and pseudocosts are selection information only.
    // The genuine root lower bound must survive a one-node search limit.
    pump_model.row_lower={1.25};pump_model.row_upper={INFINITY};pump_model.maximize=false;
    mo.lp.time_limit_seconds=5;mo.node_limit=1;mo.branching="reliability";
    auto branched=sovereign::solve_milp(pump_model,mo);
    require(branched.strong_branch_probes>0&&branched.pseudocost_updates>0,"Reliability branching was not exercised");
    require(branched.primal.size()==1&&branched.primal[0]==2&&branched.best_bound<=1.25&&branched.gap>0,"Trial branch estimate leaked into proof bound");
    require(branched.incumbent_trace.size()==1&&branched.incumbent_trace[0].second==2,"Incumbent trace did not record checked solution");
    mo.node_limit=100;branched=sovereign::solve_milp(pump_model,mo);
    require((branched.status=="optimal"||branched.status=="gap_limit")&&branched.objective==2,"Reliability general-integer solve failed");
    pump_model.row_lower={-INFINITY};pump_model.row_upper={-1.25};pump_model.maximize=true;
    branched=sovereign::solve_milp(pump_model,mo);
    require((branched.status=="optimal"||branched.status=="gap_limit")&&branched.objective==-2,"Reliability maximization sign failed");
    mo.branching="fractionality";branched=sovereign::solve_milp(pump_model,mo);
    require(branched.strong_branch_probes==0&&branched.pseudocost_updates==0,"Control branching mode changed");
    mo.branching="reliability";mo.lp.time_limit_seconds=0;branched=sovereign::solve_milp(pump_model,mo);
    require(branched.status=="time_limit"&&branched.strong_branch_probes==0,"Probe ignored zero solve budget");
    mo.branching="unknown";rejected=false;try{sovereign::solve_milp(pump_model,mo);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"Invalid branching mode accepted");
    // A zero-pivot root cannot be discarded as infeasible or called optimal.
    sovereign::MilpOptions recovery;recovery.presolve=false;recovery.heuristics=false;recovery.cover_cuts=false;
    recovery.lp.time_limit_seconds=5;recovery.lp.iteration_limit=0;recovery.capture_lp_failure=true;
    auto hard=sovereign::linear_from_dense({{-1,-8,4,-7,-8,7,8},{{2,4,2,6,3,4,-1},{5,3,-2,1,4,5,-1},{3,0,-1,4,0,4,2}},{2,7,1}});
    hard.upper.assign(7,1);hard.integer.assign(7,true);
    auto stopped=sovereign::solve_milp(hard,recovery);
    require(stopped.status=="iteration_limit"&&stopped.lp_recovery_attempts==0,"Control LP failure semantics changed");
    recovery.lp_recovery=true;stopped=sovereign::solve_milp(hard,recovery);
    require(stopped.status=="unresolved_relaxations"&&stopped.unresolved_nodes==1&&stopped.primal.empty()&&!std::isfinite(stopped.best_bound),"Unresolved root acquired a false proof");
    require(stopped.first_lp_failure.captured&&stopped.first_lp_failure.model.cost==hard.cost&&stopped.first_lp_failure.iterations==0,"First LP failure snapshot missing");
    require(!stopped.first_lp_failure.model.integer[0],"Captured node must be a continuous relaxation");
    recovery.lp.iteration_limit=2;stopped=sovereign::solve_milp(hard,recovery);
    require(stopped.status=="optimal"&&stopped.objective==0&&stopped.lp_recovery_successes>0&&stopped.unresolved_nodes==0,"Bounded cold/dense LP recovery failed");
    require(!stopped.first_lp_failure.input_basis.columns.empty(),"Failed warm basis was not captured");
    // Two deliberately unresolved child LPs survive while the remaining tree
    // finds a checked incumbent. Their parent bound must stay in the global gap.
    sovereign::LinearProblem mixed;
    mixed.names={"a","b","c","d","e"};mixed.cost={7,2,7,2,3};mixed.lower={-2,-1,0,-3,0};mixed.upper={3,3,4,2,4};mixed.integer={true,true,true,false,false};
    mixed.rows={{{0,2},{2,2},{3,2},{4,-2}},{{0,-1},{1,2},{2,4},{3,-1},{4,-2}},{{0,2},{2,2},{3,1},{4,-2}},{{0,3},{1,-1},{2,1},{3,-2}},{{0,1},{1,2},{2,-1},{3,-3},{4,1}}};
    mixed.row_lower={-INFINITY,6.0230996577106071,-INFINITY,10.331336987816075,-INFINITY};mixed.row_upper={9.4991327593059758,INFINITY,10.496200915067943,INFINITY,10.454121384716};
    auto deferred=sovereign::solve_milp(mixed,recovery);
    require(deferred.status=="unresolved_relaxations"&&deferred.unresolved_nodes==2&&deferred.nodes==9,"Unresolved child did not preserve the rest of the search");
    require(deferred.objective==13&&deferred.best_bound<9.121&&deferred.best_bound>9.119&&deferred.gap>.2,"Deferred child bound lost from proof accounting");
    for(auto& c:mixed.cost)c=-c;mixed.maximize=true;deferred=sovereign::solve_milp(mixed,recovery);
    require(deferred.status=="unresolved_relaxations"&&deferred.objective==-13&&deferred.best_bound>-9.121&&deferred.gap>.2,"Deferred maximization bound sign failed");
    recovery.lp.time_limit_seconds=0;stopped=sovereign::solve_milp(hard,recovery);
    require(stopped.status=="time_limit"&&stopped.lp_recovery_attempts==0,"Recovery ignored zero time budget");
    auto almost=sovereign::linear_from_dense({{1},{{100},{-100}},{100.000008,-100.000008}});
    almost.integer={true};almost.upper={2};recovery.lp.time_limit_seconds=5;recovery.lp.iteration_limit=10000;
    recovery.lp_recovery=false;auto rejected_round=sovereign::solve_milp(almost,recovery);
    require(rejected_round.status=="numerical_error"&&rejected_round.primal.empty(),"Near-integer test did not exercise strict rejection");
    recovery.lp_recovery=true;rejected_round=sovereign::solve_milp(almost,recovery);
    require(rejected_round.status=="unresolved_relaxations"&&rejected_round.unresolved_nodes==1&&rejected_round.primal.empty(),"Rejected integer repair incorrectly became a proof or incumbent");
    require(rejected_round.best_bound<1.00000008&&rejected_round.best_bound>.999,"Rejected repair lost the checked LP bound");
    recovery.capture_rejected_candidates=true;recovery.repair_candidates=true;
    rejected_round=sovereign::solve_milp(almost,recovery);
    require(rejected_round.primal.empty()&&rejected_round.status=="infeasible"&&rejected_round.repair_branch_nodes==1,"Infeasible near-integer assignment was not branched safely");
    require(rejected_round.rejected_candidates.size()==1&&rejected_round.rejected_candidates[0].fixing.captured,"Rejected candidate diagnostic missing");
    require(rejected_round.rejected_candidates[0].rounded_violation>1e-7&&!rejected_round.rejected_candidates[0].fallback_accepted,"Invalid dense repair accepted");
    // An asymmetric convex V: the LP minimizer is 1+8e-8, rounding to integer1
    // can be repaired to cost80, but integer2 costs only~1. A successful fixing
    // LP must not close the whole node; branch on the tiny integer fraction.
    auto steep=sovereign::linear_from_dense({{0,1},{{-1e9,-1},{1,-1}},{-1000000080,1.00000008}});
    steep.upper={2,INFINITY};steep.integer={true,false};
    sovereign::MilpOptions robust;robust.presolve=false;robust.heuristics=false;robust.cover_cuts=false;robust.lp.time_limit_seconds=5;
    robust.capture_rejected_candidates=true;
    auto corrected=sovereign::solve_milp(steep,robust);
    require(corrected.repair_branch_nodes>0&&corrected.objective<1.000001&&corrected.primal[0]==2,"Fixed-assignment repair was mistaken for a whole-node proof");
    robust.repair_candidates=true;robust.node_limit=1;corrected=sovereign::solve_milp(steep,robust);
    require(corrected.status=="node_limit"&&corrected.objective>79&&corrected.best_bound<=0&&corrected.gap>.9,"Repaired incumbent overwrote the genuine node bound");
    robust.node_limit=100;for(auto& c:steep.cost)c=-c;steep.maximize=true;corrected=sovereign::solve_milp(steep,robust);
    require(corrected.primal[0]==2&&corrected.objective> -1.000001&&corrected.objective<0,"Repair maximization sign failed");
    robust.lp.time_limit_seconds=0;corrected=sovereign::solve_milp(steep,robust);
    require(corrected.status=="time_limit"&&corrected.candidate_repair_attempts==0&&corrected.rejected_candidates.empty(),"Repair ignored zero time budget");
    // Enumeration case 33: root heuristics find -8, local search improves to -9,
    // but the root's -10.5 relaxation remains the proof bound at node_limit=1.
    auto neighborhood=sovereign::linear_from_dense({{5,2,1,5,-3,-6,-2},{{-3,3,-2,-2,5,0,-3},{3,4,2,-1,-3,2,6},{1,2,1,4,6,0,4}},{5,11,9}});
    neighborhood.upper.assign(7,1);neighborhood.integer.assign(7,true);
    sovereign::MilpOptions local;local.cover_cuts=false;local.node_limit=1;local.lp.time_limit_seconds=5;
    auto control=sovereign::solve_milp(neighborhood,local);local.improve_incumbent=true;
    auto improved=sovereign::solve_milp(neighborhood,local);
    require(control.objective==-8&&improved.objective==-9&&improved.neighborhood_improvements==1,"Neighborhood did not improve the existing incumbent");
    require(improved.status=="node_limit"&&improved.best_bound==control.best_bound&&improved.gap>.1,"Local search leaked a bound into the global tree");
    require(sovereign::original_violation(neighborhood,improved.primal,false)<=1e-7,"Neighborhood candidate failed original feasibility");
    local.neighborhood="diversified";local.capture_neighborhood=true;
    auto diverse=sovereign::solve_milp(neighborhood,local);
    require(diverse.objective==-9&&diverse.best_bound==control.best_bound&&diverse.status=="node_limit","Diversified neighborhood corrupted global bound");
    require(diverse.neighborhood_trace.size()==1&&diverse.neighborhood_trace[0].improved&&diverse.neighborhood_trace[0].improved_primal==diverse.primal,"Neighborhood accepted vector capture missing");
    require(diverse.neighborhood_trace[0].free_variables.size()==7&&diverse.neighborhood_trace[0].nodes<=64,"Neighborhood restriction/node budget failed");
    local.pace_neighborhood=true;local.neighborhood="guided";
    auto paced=sovereign::solve_milp(neighborhood,local);
    require(paced.objective==-9&&paced.best_bound==control.best_bound&&paced.status=="node_limit","Paced search corrupted incumbent or global bound");
    require(paced.neighborhood_trace.size()==1&&paced.neighborhood_calls==1,"Pacing delayed the first available call");
    for(auto& c:neighborhood.cost)c=-c;neighborhood.maximize=true;improved=sovereign::solve_milp(neighborhood,local);
    require(improved.objective==9&&improved.neighborhood_improvements==1&&improved.best_bound>10.49,"Neighborhood maximization failed");
    local.heuristics=false;improved=sovereign::solve_milp(neighborhood,local);
    require(improved.neighborhood_calls==0,"No-heuristics did not disable neighborhood");
    local.heuristics=true;local.lp.time_limit_seconds=0;improved=sovereign::solve_milp(neighborhood,local);
    require(improved.status=="time_limit"&&improved.neighborhood_calls==0,"Neighborhood ignored zero time budget");
    local.neighborhood="invalid";bool invalid_neighborhood=false;
    try{sovereign::solve_milp(neighborhood,local);}catch(const std::invalid_argument&){invalid_neighborhood=true;}
    require(invalid_neighborhood,"Invalid neighborhood strategy accepted");
    // Symmetric binary cover with a half-integral relaxation: enough tree work
    // to exercise stalled neighbourhood selection, with an analytic optimum16.
    sovereign::LinearProblem symmetric;symmetric.cost.assign(30,1);symmetric.lower.assign(30,0);
    symmetric.upper.assign(30,1);symmetric.integer.assign(30,true);symmetric.names.resize(30);
    symmetric.rows.resize(1);for(std::size_t j=0;j<30;++j)symmetric.rows[0].push_back({j,1});
    symmetric.row_lower={15.5};symmetric.row_upper={INFINITY};
    sovereign::MilpOptions varied;varied.cover_cuts=false;varied.node_limit=1000;varied.lp.time_limit_seconds=5;
    varied.improve_incumbent=true;varied.neighborhood="diversified";varied.capture_neighborhood=true;
    auto symmetry=sovereign::solve_milp(symmetric,varied);bool used_diversity=false;
    require(symmetry.objective==16&&symmetry.best_bound<=16,"Diversification lost the analytic incumbent or bound");
    for(const auto& sample:symmetry.neighborhood_trace){
        if(sample.selection!="guided")used_diversity=true;
        auto released=sample.free_variables;std::sort(released.begin(),released.end());
        require(released.size()<=16&&std::adjacent_find(released.begin(),released.end())==released.end(),"Duplicate or oversized free set");
        require(!released.empty()&&released.back()<30&&sample.nodes<=(sample.stalls_before>=4?128u:64u),"Invalid neighbourhood domain or node budget");
    }
    require(used_diversity,"Stalled diversified selector was not exercised");
    // Clock-independent scheduling regressions. Numerical crumbs must not
    // restart a guided sequence, and a fresh center cannot spend future quotas.
    using sovereign::detail::reserved_neighborhood_plan;
    require(!sovereign::detail::material_gain(73.,73.-1e-8)&&sovereign::detail::material_gain(73.,72.),"Material-gain threshold failed");
    require(sovereign::detail::material_gain(-10.,-11.),"Normalized maximization gain failed");
    auto schedule=reserved_neighborhood_plan(180,1,0,0,4,0,4,0,false);
    require(schedule.strong&&schedule.budget==4,"Stalled early search did not get one strong attempt");
    schedule=reserved_neighborhood_plan(180,60,4,0,4,1,0,1,true);
    require(schedule.strong&&schedule.budget==0,"Fresh center consumed a reserved late call too early");
    schedule=reserved_neighborhood_plan(180,72,4,0,4,1,0,1,false);
    require(schedule.budget==4,"Late search quota was not released");
    schedule=reserved_neighborhood_plan(180,75,8,0,4,2,0,72,false);
    require(schedule.budget==0,"Repeated strong search ignored spacing");
    schedule=reserved_neighborhood_plan(180,75,8,0,4,2,0,72,true);
    require(schedule.budget==4,"Fresh late incumbent did not trigger reserved search");
    schedule=reserved_neighborhood_plan(180,100,12,0,4,3,0,75,true);
    require(schedule.budget==0,"Last call was not reserved until 65 percent");
    schedule=reserved_neighborhood_plan(180,117,12,0,4,3,0,75,false);
    require(schedule.budget==4,"Final call not released");
    require(reserved_neighborhood_plan(180,150,27,21,12,3,4,117,true).budget==0,"Cumulative time cap exceeded");
    require(reserved_neighborhood_plan(0,0,0,0,0,0,0,0,true).budget==0,"Zero scheduler budget failed");
    // Independently enumerate a binary Hamming ball, including a general integer
    // and a continuous variable. The general integer is fixed; the latter is free.
    auto ball=symmetric;ball.cost.resize(5,1);ball.lower={0,0,0,-2,-3};ball.upper={1,1,1,4,7};
    ball.integer={true,true,true,true,false};ball.names.resize(5);ball.rows.clear();ball.row_lower.clear();ball.row_upper.clear();
    std::vector<double> center={1,0,1,2,.5};auto free=sovereign::detail::binary_neighborhood(ball,center,1);
    require(free==std::vector<std::size_t>({0,1,2})&&ball.lower[3]==2&&ball.upper[3]==2&&ball.lower[4]==-3&&ball.upper[4]==7,"Binary neighborhood domain corrupted");
    for(int mask=0;mask<8;++mask){auto point=center;int distance=0;for(int j=0;j<3;++j){point[j]=(mask>>j)&1;distance+=point[j]!=center[j];}
        require((sovereign::original_violation(ball,point,false)<=1e-7)==(distance<=1),"Hamming restriction differs from enumeration");}
    varied.neighborhood="reserved";auto coupled=sovereign::solve_milp(symmetric,varied);bool used_ball=false;
    require(coupled.objective==16&&coupled.best_bound<=15.50001&&symmetric.rows.size()==1,"Private neighborhood leaked into global model/proof");
    for(const auto& sample:coupled.neighborhood_trace)if(sample.selection=="local_branching"){
        used_ball=true;require(sample.strong&&sample.radius==4&&sample.free_variables.size()==30&&sample.nodes<=512,"Coupled search was not exercised correctly");
        require(sample.center_primal.size()==30,"Coupled center capture missing");
    }
    require(used_ball,"Reserved strong neighborhood never ran");
    varied.heuristics=false;require(sovereign::solve_milp(symmetric,varied).neighborhood_calls==0,"Reserved search ignored no-heuristics");
    varied.heuristics=true;varied.lp.time_limit_seconds=0;
    require(sovereign::solve_milp(symmetric,varied).neighborhood_calls==0,"Reserved search ignored zero time");
    std::cout<<"V2 sparse LU, transpose, ray, extended PSD and option regressions passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
