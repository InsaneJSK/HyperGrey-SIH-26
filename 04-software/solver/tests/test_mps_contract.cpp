#include "milp.hpp"
#include <iostream>
#include <sstream>
using namespace sovereign;
void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
std::string text(const std::string& bounds,bool maximize=false){
    return std::string("NAME CONTRACT\nOBJSENSE\n ")+(maximize?"MAX":"MIN")+
        "\nROWS\n N OBJ\n L CAP\n G FLOOR\nCOLUMNS\n M0 'MARKER' 'INTORG'\n X OBJ "+
        (maximize?"1":"-1")+" CAP 1\n X FLOOR 1\n M1 'MARKER' 'INTEND'\n Y OBJ 0\nRHS\n B CAP 7 FLOOR -4\n"+
        (bounds.empty()?"":"BOUNDS\n"+bounds)+"ENDATA\n";
}
LinearProblem read(const std::string& s){std::istringstream stream(s);return read_mps(stream);}
int main(){try{
    struct Case{std::string bounds;double lo,up,solution;};
    std::vector<Case> cases={{"",0,1,1},{" UP B Y 2\n",0,1,1},
        {" LO B X 0\n",0,INFINITY,7},{" LO B X 2\n",2,INFINITY,7},
        {" UP B X 4\n",0,4,4},{" UP B X 0\n",0,0,0},{" FX B X 2\n",2,2,2},
        {" FR B X\n",-INFINITY,INFINITY,7},{" MI B X\n",-INFINITY,INFINITY,7},
        {" PL B X\n",0,INFINITY,7},{" BV B X\n",0,1,1},{" UI B X 4\n",0,4,4},
        {" LI B X 2\n",2,INFINITY,7},{" LO B X 2\n UP B X 4\n",2,4,4},
        {" BV B X 1.0\n",0,1,1},{" FR B X 0\n",-INFINITY,INFINITY,7}};
    for(const auto& c:cases)for(bool maximize:{false,true}){
        auto p=read(text(c.bounds,maximize));
        require(p.integer[0]&&!p.integer[1]&&p.lower[0]==c.lo&&p.upper[0]==c.up,"Wrong per-column marker domain");
        if(c.bounds!=" UP B Y 2\n")require(p.upper[1]==INFINITY,"Continuous default was changed");
        MilpOptions options;options.lp.time_limit_seconds=3;
        auto r=solve_milp(p,options);
        require((r.status=="optimal"||r.status=="gap_limit")&&std::abs(r.objective-(maximize?c.solution:-c.solution))<1e-7,"Wrong parsed-model numerical optimum");
        require(original_violation(p,r.primal,false)<=1e-7,"Parsed-model point infeasible");
        options.binary_proof=true;r=solve_milp(p,options);
        require((r.status=="optimal"||r.status=="gap_limit")&&std::abs(r.objective-(maximize?c.solution:-c.solution))<1e-7,"Proof-enabled mode changed marker semantics");
    }
    auto p=read(text(""));p.rows.push_back({{0,1}});p.row_lower.push_back(2);p.row_upper.push_back(INFINITY);
    require(solve_milp(p).status=="infeasible","Marker binary domain did not imply infeasibility");
    auto raw=text("");auto at=raw.find(" L CAP\n G FLOOR\n");raw.erase(at,std::string(" L CAP\n G FLOOR\n").size());
    at=raw.find(" CAP 1\n X FLOOR 1");raw.erase(at,std::string(" CAP 1\n X FLOOR 1").size());
    at=raw.find("RHS\n B CAP 7 FLOOR -4\n");raw.erase(at,std::string("RHS\n B CAP 7 FLOOR -4\n").size());
    auto bounded=solve_milp(read(raw));require(bounded.status=="optimal"&&bounded.objective==-1,"No-row marker model misclassified unbounded");
    for(const auto& malformed:std::vector<std::string>{" SC B X 4\n"," SI B X 4\n"," UP B MISSING 2\n"," UP B X nan\n"," BV B X one\n"," MI B X 1 2\n"}){
        bool rejected=false;try{read(text(malformed));}catch(const std::runtime_error&){rejected=true;}
        require(rejected,"Unsupported or invalid MPS silently accepted");
    }
    // Standard conventions: later N rows are free rows and are dropped with their
    // entries; text after ENDATA is ignored. Duplicate names are still errors.
    {
        auto swap_text=[](std::string& s,const std::string& from,const std::string& to){
            const auto at=s.find(from);require(at!=std::string::npos,"Fixture text missing");s.replace(at,from.size(),to);
        };
        std::string extra=text("");
        swap_text(extra," N OBJ\n"," N OBJ\n N SPARE\n");
        swap_text(extra," X FLOOR 1\n"," X FLOOR 1 SPARE 5\n");
        swap_text(extra," B CAP 7 FLOOR -4\n"," B CAP 7 FLOOR -4\n B SPARE 9\n");
        extra+="G53 2\n  trailing notes\n";
        auto q=read(extra),base=read(text(""));
        require(q.rows==base.rows&&q.row_lower==base.row_lower&&q.row_upper==base.row_upper&&q.cost==base.cost&&
                q.lower==base.lower&&q.upper==base.upper&&q.integer==base.integer&&q.offset==base.offset,"Free N row or trailing text changed the model");
        for(const auto& dup:{std::string(" N OBJ\n N OBJ\n"),std::string(" N OBJ\n N CAP\n")}){
            auto bad=text("");swap_text(bad," N OBJ\n",dup);
            bool rejected=false;try{read(bad);}catch(const std::runtime_error&){rejected=true;}
            require(rejected,"Duplicate row name accepted");
        }
    }
    std::cout<<"32 marker-domain models pass numerical/proof-enabled paths; infeasible, no-row, invalid-input, free-row and trailing-text guards pass\n";
    return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
