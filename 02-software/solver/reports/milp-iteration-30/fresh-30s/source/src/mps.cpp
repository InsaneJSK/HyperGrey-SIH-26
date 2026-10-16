#include "mps.hpp"
#include <algorithm>
#include <cmath>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace sovereign {
namespace {
const double inf = std::numeric_limits<double>::infinity();
bool integral_literal(const std::string& s) {
    std::size_t k=0;if(k<s.size()&&(s[k]=='+'||s[k]=='-'))++k;
    std::string digits;std::size_t fractional=0;bool dot=false;
    while(k<s.size()&&s[k]!='E'&&s[k]!='e'){
        char c=s[k++];if(c=='.'&&!dot){dot=true;continue;}
        if(c<'0'||c>'9')return false;digits.push_back(c);if(dot)++fractional;
    }
    if(digits.empty())return false;int exponent=0,sign=1;
    if(k<s.size()){
        ++k;if(k<s.size()&&(s[k]=='+'||s[k]=='-')){if(s[k]=='-')sign=-1;++k;}
        if(k==s.size())return false;
        for(;k<s.size();++k){if(s[k]<'0'||s[k]>'9'||exponent>1000000)return false;exponent=exponent*10+s[k]-'0';}
    }
    if(digits.find_first_not_of('0')==std::string::npos)return true;
    long long scale=static_cast<long long>(sign)*exponent-static_cast<long long>(fractional);
    if(scale>=0)return true;auto zeros=static_cast<std::size_t>(-scale);
    if(zeros>digits.size())return false;
    return digits.find_first_not_of('0',digits.size()-zeros)==std::string::npos;
}
double number(std::string s,bool* exact_integer=nullptr) {
    std::replace(s.begin(), s.end(), 'D', 'E');
    std::replace(s.begin(), s.end(), 'd', 'e');
    std::size_t used = 0;
    double v = std::stod(s, &used);
    if (used != s.size() || !std::isfinite(v)) throw std::runtime_error("Invalid MPS number: " + s);
    if(exact_integer&&(!integral_literal(s)||std::abs(v)>std::ldexp(1.,50)))*exact_integer=false;
    return v;
}
std::vector<std::string> tokens(const std::string& line) {
    std::istringstream in(line); std::vector<std::string> out; std::string s;
    while (in >> s) { if (s[0] == '$') break; out.push_back(s); }
    return out;
}
}

void validate_linear_problem(const LinearProblem& p) {
    const std::size_t n=p.names.size(),m=p.rows.size();
    if(!n||p.cost.size()!=n||p.lower.size()!=n||p.upper.size()!=n||p.integer.size()!=n||
       p.row_lower.size()!=m||p.row_upper.size()!=m||!std::isfinite(p.offset))
        throw std::invalid_argument("Invalid linear problem dimensions or offset");
    for(std::size_t j=0;j<n;++j)
        if(!std::isfinite(p.cost[j])||std::isnan(p.lower[j])||std::isnan(p.upper[j])||p.lower[j]==inf||p.upper[j]==-inf)
            throw std::invalid_argument("Invalid variable coefficient or bound");
    for(std::size_t i=0;i<m;++i) {
        if(std::isnan(p.row_lower[i])||std::isnan(p.row_upper[i])||p.row_lower[i]==inf||p.row_upper[i]==-inf)
            throw std::invalid_argument("Invalid row bound");
        for(auto a:p.rows[i])if(a.first>=n||!std::isfinite(a.second))throw std::invalid_argument("Invalid sparse row entry");
    }
}

LinearProblem read_mps(std::istream& input) {
    LinearProblem p;
    std::map<std::string, std::size_t> row_index, col_index;
    std::vector<char> senses;
    std::vector<double> rhs, ranges;
    std::vector<bool> has_range;
    std::set<std::size_t> explicit_lower, negative_upper, explicit_bounds;
    std::set<std::string> free_rows;
    std::vector<std::map<std::size_t, double> > coefficients;
    std::string section, objective, line, previous_column, rhs_set, range_set, bound_set;
    std::set<std::string> rhs_seen, range_seen;
    bool integer_mode = false, ended = false, seen_rows = false, seen_columns = false;
    std::size_t line_number = 0;
    try {
        while (std::getline(input, line)) {
            ++line_number;
            if (line.empty() || line[0] == '*') continue;
            auto t = tokens(line); if (t.empty()) continue;
            if (t[0] == "NAME" && section.empty()) {
                p.name = t.size() > 1 ? t[1] : "unnamed"; section = "NAME"; continue;
            }
            if (t[0] == "ENDATA" && t.size() == 1) { ended = true; break; }
            if ((t[0] == "ROWS" || t[0] == "COLUMNS" || t[0] == "RHS" ||
                 t[0] == "RANGES" || t[0] == "BOUNDS" || t[0] == "OBJSENSE") && t.size() == 1) {
                section = t[0];
                if (section == "ROWS") { if (seen_rows) throw std::runtime_error("Repeated ROWS"); seen_rows = true; }
                if (section == "COLUMNS") { if (!seen_rows || seen_columns) throw std::runtime_error("Invalid COLUMNS order"); seen_columns = true; }
                continue;
            }
            if (t[0] == "OBJSENSE" && t.size() == 2) {
                section = "OBJSENSE"; t.erase(t.begin());
            }
            if (section == "OBJSENSE") {
                if (t.size() != 1 || (t[0] != "MIN" && t[0] != "MAX"))
                    throw std::runtime_error("Expected MIN or MAX");
                p.maximize = t[0] == "MAX"; continue;
            }
            if (section == "ROWS") {
                if (t.size() != 2 || t[0].size() != 1 || std::string("NLEG").find(t[0]) == std::string::npos)
                    throw std::runtime_error("Unsupported row definition");
                if (t[1] == objective || free_rows.count(t[1]) || row_index.count(t[1])) throw std::runtime_error("Duplicate row");
                if (t[0] == "N") {
                    // Standard MPS: the first N row is the objective; later N
                    // rows are free rows and are dropped with their entries.
                    if (objective.empty()) objective = t[1]; else free_rows.insert(t[1]);
                    continue;
                }
                row_index[t[1]] = senses.size(); senses.push_back(t[0][0]);
                rhs.push_back(0); ranges.push_back(0); has_range.push_back(false); coefficients.emplace_back();
            } else if (section == "COLUMNS") {
                if (t.size() == 3 && t[1] == "'MARKER'") {
                    if (t[2] == "'INTORG'" && !integer_mode) integer_mode = true;
                    else if (t[2] == "'INTEND'" && integer_mode) integer_mode = false;
                    else throw std::runtime_error("Invalid integer marker");
                    continue;
                }
                // Fixed MPS permits a blank repeated column name.
                if (t.size() == 2 || t.size() == 4) {
                    if (previous_column.empty()) throw std::runtime_error("Missing column name");
                    t.insert(t.begin(), previous_column);
                }
                if (t.size() != 3 && t.size() != 5) throw std::runtime_error("Invalid column record");
                previous_column = t[0];
                if (!col_index.count(t[0])) {
                    col_index[t[0]] = p.names.size(); p.names.push_back(t[0]);
                    p.cost.push_back(0); p.lower.push_back(0); p.upper.push_back(inf); p.integer.push_back(integer_mode);
                }
                std::size_t j = col_index.at(t[0]);
                if (integer_mode != p.integer[j]) throw std::runtime_error("Inconsistent integer marker scope");
                for (std::size_t k = 1; k < t.size(); k += 2) {
                    double v = number(t[k + 1],&p.integer_input_literals);
                    if (t[k] == objective) {
                        if(std::abs(p.cost[j])>std::ldexp(1.,50)-std::abs(v))p.integer_input_literals=false;
                        p.cost[j] += v;
                    }
                    else if (free_rows.count(t[k])) continue;
                    else {
                        if (!row_index.count(t[k])) throw std::runtime_error("Unknown row: " + t[k]);
                        auto& value=coefficients[row_index.at(t[k])][j];
                        if(std::abs(value)>std::ldexp(1.,50)-std::abs(v))p.integer_input_literals=false;
                        value += v;
                    }
                }
            } else if (section == "RHS" || section == "RANGES") {
                if (t.size() == 2 || t.size() == 4) t.insert(t.begin(), "__blank__");
                if (t.size() != 3 && t.size() != 5) throw std::runtime_error("Invalid RHS/range record");
                std::string& selected = section == "RHS" ? rhs_set : range_set;
                if (selected.empty()) selected = t[0];
                if (selected != t[0]) throw std::runtime_error("Multiple RHS/range sets unsupported");
                auto& seen = section == "RHS" ? rhs_seen : range_seen;
                for (std::size_t k = 1; k < t.size(); k += 2) {
                    if (!seen.insert(t[k]).second) throw std::runtime_error("Duplicate RHS/range entry");
                    double v = number(t[k + 1],&p.integer_input_literals);
                    if (free_rows.count(t[k])) continue;
                    if (t[k] == objective && section == "RHS") { p.offset = -v; continue; }
                    if (!row_index.count(t[k])) throw std::runtime_error("Unknown RHS/range row");
                    std::size_t i = row_index.at(t[k]);
                    if (section == "RHS") rhs[i] = v;
                    else { ranges[i] = v; has_range[i] = true; }
                }
            } else if (section == "BOUNDS") {
                if (t.size() < 3 || t.size() > 4) throw std::runtime_error("Invalid bound record");
                if (bound_set.empty()) bound_set = t[1];
                if (bound_set != t[1]) throw std::runtime_error("Multiple bound sets unsupported");
                if (!col_index.count(t[2])) throw std::runtime_error("Unknown bound variable");
                std::size_t j = col_index.at(t[2]);
                explicit_bounds.insert(j);
                const std::string type = t[0];
                bool valued = type == "LO" || type == "UP" || type == "FX" || type == "LI" || type == "UI";
                // Common writers add an unused value to BV/MI/PL/FR records; it
                // must still be a number, and it is ignored as other readers do.
                bool optional = type == "BV" || type == "MI" || type == "PL" || type == "FR";
                if ((valued && t.size() != 4) || (!valued && t.size() != 3 && !(optional && t.size() == 4)))
                    throw std::runtime_error("Invalid bound value count");
                if (!valued && t.size() == 4) number(t[3]);
                double v = valued ? number(t[3],&p.integer_input_literals) : 0;
                if (type == "LO" || type == "LI") p.lower[j] = v;
                else if (type == "UP" || type == "UI") p.upper[j] = v;
                else if (type == "FX") p.lower[j] = p.upper[j] = v;
                else if (type == "FR") { p.lower[j] = -inf; p.upper[j] = inf; }
                else if (type == "MI") p.lower[j] = -inf;
                else if (type == "PL") p.upper[j] = inf;
                else if (type == "BV") { p.lower[j] = 0; p.upper[j] = 1; p.integer[j] = true; }
                else throw std::runtime_error("Unsupported bound type: " + type);
                if (type == "LI" || type == "UI") p.integer[j] = true;
                if(type=="LO"||type=="LI"||type=="FX"||type=="FR"||type=="MI"||type=="BV") explicit_lower.insert(j);
                if((type=="UP"||type=="UI")&&v<0) negative_upper.insert(j);
            } else throw std::runtime_error("Unsupported MPS section or record: " + t[0]);
        }
        if (!ended || !seen_columns || objective.empty() || integer_mode || p.names.empty())
            throw std::runtime_error("Incomplete MPS model");
        // Integer-marker variables with NO bound record default to [0,1].
        // Any explicit record for that column instead uses the ordinary
        // [0,+inf] defaults for unspecified sides (including LO-only).
        // A BOUNDS entry for another column must not suppress this default.
        for(std::size_t j=0;j<p.names.size();++j)
            if(p.integer[j]&&!explicit_bounds.count(j))p.upper[j]=1;
        for(auto j:negative_upper) if(!explicit_lower.count(j))
            throw std::runtime_error("Negative upper bound requires explicit lower bound in this MPS subset");
        // Standard MPS readers ignore anything after ENDATA (e.g. MIPLIB 3
        // branching-priority notes); it is not model data.
        for (std::size_t i = 0; i < senses.size(); ++i) {
            double lo = -inf, up = inf;
            if (senses[i] == 'L' || senses[i] == 'E') up = rhs[i];
            if (senses[i] == 'G' || senses[i] == 'E') lo = rhs[i];
            if (has_range[i]) {
                if (senses[i] == 'L') lo = rhs[i] - std::abs(ranges[i]);
                else if (senses[i] == 'G') up = rhs[i] + std::abs(ranges[i]);
                else if (ranges[i] >= 0) up = rhs[i] + ranges[i];
                else lo = rhs[i] + ranges[i];
            }
            p.row_lower.push_back(lo); p.row_upper.push_back(up); p.rows.emplace_back();
            for (auto entry : coefficients[i]) if (entry.second != 0) p.rows.back().push_back(entry);
        }
    } catch (const std::exception& e) {
        throw std::runtime_error("MPS line " + std::to_string(line_number) + ": " + e.what());
    }
    validate_linear_problem(p);
    return p;
}

StandardForm standardize(const LinearProblem& p, std::size_t max_cells) {
    validate_linear_problem(p);
    StandardForm s;
    s.objective_sign = p.maximize ? -1 : 1;
    s.objective_offset = p.offset;
    s.shift.assign(p.names.size(), 0); s.mapping.resize(p.names.size());
    for (std::size_t j = 0; j < p.names.size(); ++j) {
        if (p.integer[j]) throw std::runtime_error("Integer model requires MILP solver; LP relaxation is not implicit");
        if (std::isfinite(p.lower[j])) s.shift[j] = p.lower[j];
        else if (std::isfinite(p.upper[j])) s.shift[j] = p.upper[j];
        double sign = std::isfinite(p.lower[j]) ? 1 : -1;
        s.mapping[j].push_back({s.model.cost.size(), sign});
        s.model.cost.push_back(s.objective_sign * p.cost[j] * sign);
        if (!std::isfinite(p.lower[j]) && !std::isfinite(p.upper[j])) {
            s.mapping[j].push_back({s.model.cost.size(), 1});
            s.model.cost.push_back(s.objective_sign * p.cost[j]);
        }
        s.objective_offset += p.cost[j] * s.shift[j];
    }
    const std::size_t n = s.model.cost.size();
    auto add = [&](std::vector<double> row, double bound) {
        if (s.model.rows.size() + 1 > max_cells / std::max(std::size_t(1), n))
            throw std::runtime_error("resource_limit: dense standard-form allocation");
        s.model.rows.push_back(std::move(row)); s.model.rhs.push_back(bound);
    };
    for (std::size_t i = 0; i < p.rows.size(); ++i) {
        std::vector<double> row(n, 0); double shift = 0;
        for (auto a : p.rows[i]) {
            shift += a.second * s.shift[a.first];
            for (auto term : s.mapping[a.first]) row[term.first] += a.second * term.second;
        }
        if (std::isfinite(p.row_upper[i])) add(row, p.row_upper[i] - shift);
        if (std::isfinite(p.row_lower[i])) {
            for (double& v : row) v = -v;
            add(row, shift - p.row_lower[i]);
        }
    }
    for (std::size_t j = 0; j < p.names.size(); ++j)
        if (std::isfinite(p.lower[j]) && std::isfinite(p.upper[j])) {
            std::vector<double> row(n, 0); row[s.mapping[j][0].first] = 1;
            add(row, p.upper[j] - p.lower[j]);
        }
    return s;
}

std::vector<double> StandardForm::recover(const std::vector<double>& x) const {
    std::vector<double> out = shift;
    for (std::size_t j = 0; j < mapping.size(); ++j)
        for (auto term : mapping[j]) out[j] += term.second * x.at(term.first);
    return out;
}

double original_violation(const LinearProblem& p, const std::vector<double>& x, bool scaled) {
    validate_linear_problem(p);
    if (x.size() != p.names.size()) throw std::invalid_argument("Wrong original solution size");
    double result = 0;
    auto check = [&](long double activity, double bound, bool lower, long double scale) {
        if (!std::isfinite(bound)) return;
        long double v = lower ? bound - activity : activity - bound;
        if (scaled) v /= 1 + std::abs(bound) + scale;
        result = std::max(result, static_cast<double>(v));
    };
    for (std::size_t j = 0; j < x.size(); ++j) {
        if (!std::isfinite(x[j])) return inf;
        check(x[j], p.lower[j], true, std::abs(x[j]));
        check(x[j], p.upper[j], false, std::abs(x[j]));
    }
    for (std::size_t i = 0; i < p.rows.size(); ++i) {
        long double activity = 0, scale = 0;
        for (auto a : p.rows[i]) {
            long double term = static_cast<long double>(a.second) * x[a.first];
            activity += term; scale += std::abs(term);
        }
        if (!std::isfinite(activity)) return inf;
        check(activity, p.row_lower[i], true, scale); check(activity, p.row_upper[i], false, scale);
    }
    return result;
}
}
