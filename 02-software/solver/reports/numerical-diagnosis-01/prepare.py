"""Copy the frozen current engine and add diagnostic output only."""
import hashlib
import json
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    dst = BASE / 'diagnostic-source'
    dst.mkdir(exist_ok=False)
    identities = {}
    for folder in ('src', 'include', 'tests'):
        for p in sorted((ROOT / folder).iterdir()):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT)
            frozen = ROOT / 'reports/milp-iteration-29/final-source' / rel
            assert sha(p) == sha(frozen), rel
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            identities[rel.as_posix()] = sha(p)
    shutil.copy2(ROOT / 'CMakeLists.txt', dst / 'CMakeLists.txt')
    identities['CMakeLists.txt'] = sha(ROOT / 'CMakeLists.txt')

    p = dst / 'src/sparse_lp.cpp'
    s = p.read_text().replace('#include <numeric>', '#include <numeric>\n#include <iostream>\n#include <iomanip>')
    method = r'''
    void trace(const char* event,bool full=false) const {
        std::cerr<<std::setprecision(17)<<"{\"event\":\""<<event<<"\",\"iterations\":"<<iterations<<",\"updates\":"<<updates.size()<<",\"rows\":"<<m;
        if(full){
            std::cerr<<",\"basis\":[";for(std::size_t i=0;i<m;++i){if(i)std::cerr<<',';std::cerr<<basis[i];}
            std::cerr<<"],\"rhs\":[";for(std::size_t i=0;i<m;++i){if(i)std::cerr<<',';std::cerr<<s.rhs[i];}
            std::cerr<<"],\"x\":[";for(std::size_t i=0;i<x.size();++i){if(i)std::cerr<<',';if(std::isfinite(x[i]))std::cerr<<x[i];else std::cerr<<"null";}
            std::cerr<<"],\"basis_columns\":[";
            for(std::size_t j=0;j<m;++j){if(j)std::cerr<<',';std::cerr<<'[';bool first=true;for(auto a:s.columns[basis[j]]){if(!first)std::cerr<<',';first=false;std::cerr<<'['<<a.first<<','<<a.second<<']';}std::cerr<<']';}std::cerr<<']';
        }
        std::cerr<<"}\n";
    }
'''
    s = s.replace('    bool refactor() {', method + '    bool refactor() {')
    old = '++factorizations;updates.clear();return lu.factor(b,opt.max_tableau_cells,[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit_seconds;});'
    assert old in s
    s = s.replace(old, '++factorizations;updates.clear();bool ok=lu.factor(b,opt.max_tableau_cells,[&](){return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=opt.time_limit_seconds;});if(!ok)trace("refactor_failed",true);return ok;')
    s = s.replace('if(std::abs(d[row])<1e-12)return false;', 'if(std::abs(d[row])<1e-7)std::cerr<<std::setprecision(17)<<"{\\"event\\":\\"small_pivot\\",\\"iteration\\":"<<iterations<<",\\"row\\":"<<row<<",\\"entering\\":"<<col<<",\\"leaving\\":"<<basis[row]<<",\\"value\\":"<<d[row]<<",\\"x\\":"<<x[row]<<"}\\n";if(std::abs(d[row])<1e-12)return false;')
    old = 'for(double v:x)if(v<-100*opt.tolerance){if(repair())goto recheck_values;return "numerical_error";}'
    assert old in s
    s = s.replace(old, 'for(double v:x)if(v<-100*opt.tolerance){if(repair())goto recheck_values;trace("primal_infeasible",true);return "numerical_error";}')
    p.write_text(s)
    p = dst / 'include/sparse_lu.hpp'
    s = p.read_text().replace('#include <functional>', '#include <functional>\n#include <iostream>\n#include <iomanip>')
    old = 'if(pivot==n||largest<1e-14||!std::isfinite(largest)) return false;'
    assert old in s
    s = s.replace(old, 'if(pivot==n||largest<1e-14||!std::isfinite(largest)){std::cerr<<std::setprecision(17)<<"{\\"event\\":\\"lu_reject\\",\\"column\\":"<<k<<",\\"size\\":"<<n<<",\\"largest\\":"<<largest<<"}\\n";return false;}')
    p.write_text(s)

    p = dst / 'src/qp_dual_newton.cpp'
    s = p.read_text().replace('#include <chrono>', '#include <chrono>\n#include <iostream>\n#include <iomanip>')
    old = 'check_qp_solution(q,result,opt.tolerance);if(result.optimality_verified)'
    s = s.replace(old, 'check_qp_solution(q,result,opt.tolerance);std::cerr<<std::setprecision(17)<<"{\\"event\\":\\"qp_iteration\\",\\"iteration\\":"<<iteration<<",\\"gradient\\":"<<norm(gradient)<<",\\"primal_residual\\":"<<result.primal_residual<<",\\"stationarity\\":"<<result.stationarity_residual<<",\\"gap\\":"<<result.relative_gap<<"}\\n";if(result.optimality_verified)')
    s = s.replace('for(std::size_t inner=0;inner<std::min<std::size_t>(10000,4*m+50)', 'std::size_t inner_count=0;for(std::size_t inner=0;inner<std::min<std::size_t>(10000,4*m+50)')
    s = s.replace('at.multiply(direction,work,opt.threads);', '++inner_count;at.multiply(direction,work,opt.threads);')
    s = s.replace('if(!accepted){result.status=', 'std::cerr<<std::setprecision(17)<<"{\\"event\\":\\"qp_step\\",\\"iteration\\":"<<iteration<<",\\"inner\\":"<<inner_count<<",\\"accuracy\\":"<<accuracy<<",\\"residual\\":"<<norm(r)<<",\\"step_norm\\":"<<norm(step)<<",\\"slope\\":"<<slope<<",\\"length\\":"<<length<<",\\"accepted\\":"<<(accepted?"true":"false")<<"}\\n";if(!accepted){result.status=')
    p.write_text(s)
    p = dst / 'src/qp_admm.cpp'
    s = p.read_text().replace('#include <numeric>', '#include <numeric>\n#include <iostream>\n#include <iomanip>')
    anchor = '        if(specialized.status=="optimal")return specialized;'
    assert anchor in s
    output = r'''
        std::cerr<<std::setprecision(17)<<"{\"event\":\"specialist_exit\",\"status\":\""<<specialized.status<<"\",\"iterations\":"<<specialized.iterations<<",\"tolerance\":"<<opt.tolerance<<",\"primal\":[";
        for(std::size_t j=0;j<specialized.primal.size();++j){if(j)std::cerr<<',';std::cerr<<specialized.primal[j];}std::cerr<<"],\"row_dual\":[";
        for(std::size_t i=0;i<specialized.row_dual.size();++i){if(i)std::cerr<<',';std::cerr<<specialized.row_dual[i];}std::cerr<<"]}\n";
'''
    s = s.replace(anchor, output + anchor)
    p.write_text(s)
    (BASE / 'SOURCE_IDENTITY.json').write_text(json.dumps({
        'production': identities,
        'diagnostic': {p.relative_to(dst).as_posix(): sha(p) for p in sorted(dst.rglob('*')) if p.is_file()},
        'note': 'Logging only in sparse LP/LU and QP specialist/dispatch.'}, indent=2) + '\n')
    print('Diagnostic source prepared.')


if __name__ == '__main__':
    main()
