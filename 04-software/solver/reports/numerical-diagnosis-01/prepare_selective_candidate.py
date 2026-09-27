"""Test a weak-pivot-only ratio safeguard without modifying the working engine."""
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_binary_proof import sha, save


def main():
    dst = BASE / 'selective-candidate-source'
    shutil.copytree(BASE / 'diagnostic-source', dst)
    path = dst / 'src/sparse_lp.cpp'
    text = path.read_text()
    anchor = '                if(leaving==m) {'
    assert text.count(anchor) == 1
    policy = '''                double direction_norm=0;for(double value:d)direction_norm=std::max(direction_norm,std::abs(value));
                if(!bland&&leaving<m&&d[leaving]<=1e-7*(1+direction_norm)) {
                    trace("stable_ratio");
                    double expanded=inf;
                    for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance)
                        expanded=std::min(expanded,(std::max(0.0,x[i])+opt.tolerance)/d[i]);
                    for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance&&std::max(0.0,x[i])/d[i]<=expanded)
                        if(d[i]>d[leaving]||(d[i]==d[leaving]&&basis[i]<basis[leaving]))leaving=i;
                }
'''
    path.write_text(text.replace(anchor, policy + anchor))
    save(BASE / 'SELECTIVE_CANDIDATE_IDENTITY.json', {p.relative_to(dst).as_posix(): sha(p) for p in sorted(dst.rglob('*')) if p.is_file()})
    runner = (BASE / 'run_lp_candidate.py').read_text()
    runner = runner.replace("'lp-candidate-results'", "'selective-candidate-results'").replace('build-lp-refresh-01', 'build-lp-selective-01')
    runner = runner.replace('LP_CANDIDATE_IDENTITY.json', 'SELECTIVE_CANDIDATE_IDENTITY.json').replace('lp_candidate_cli.exe', 'selective_candidate_cli.exe')
    runner = runner.replace("e['event'] == 'refresh_small_pivot'", "e['event'] == 'stable_ratio'").replace('refreshes', 'stable_ratio_calls')
    (BASE / 'run_selective_candidate.py').write_text(runner)
    print('Selective ratio candidate prepared.')


if __name__ == '__main__':
    main()
