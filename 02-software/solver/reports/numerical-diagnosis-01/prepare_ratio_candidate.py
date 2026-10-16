"""Build the separate two-pass ratio candidate; retain the failed refresh variant."""
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_binary_proof import sha, save


def main():
    dst = BASE / 'ratio-candidate-source'
    shutil.copytree(BASE / 'diagnostic-source', dst)
    path = dst / 'src/sparse_lp.cpp'
    text = path.read_text()
    old = '''                double ratio=inf;
                for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance) {
                    double r=std::max(0.0,x[i])/d[i];
                    if(r<ratio||(r==ratio&&leaving<m&&basis[i]<basis[leaving])){ratio=r;leaving=i;}
                }'''
    assert text.count(old) == 1
    new = '''                double ratio=inf;
                if(!bland)for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance)
                    ratio=std::min(ratio,(std::max(0.0,x[i])+opt.tolerance)/d[i]);
                for(std::size_t i=0;i<m;++i)if(d[i]>opt.tolerance) {
                    double r=std::max(0.0,x[i])/d[i];
                    if(bland) {
                        if(r<ratio||(r==ratio&&leaving<m&&basis[i]<basis[leaving])){ratio=r;leaving=i;}
                    } else if(r<=ratio&&(leaving==m||d[i]>d[leaving]||(d[i]==d[leaving]&&basis[i]<basis[leaving])))leaving=i;
                }'''
    path.write_text(text.replace(old, new))
    save(BASE / 'RATIO_CANDIDATE_IDENTITY.json', {p.relative_to(dst).as_posix(): sha(p) for p in sorted(dst.rglob('*')) if p.is_file()})
    runner = (BASE / 'run_lp_candidate.py').read_text()
    runner = runner.replace("'lp-candidate-results'", "'ratio-candidate-results'").replace('build-lp-refresh-01', 'build-lp-ratio-01')
    runner = runner.replace('LP_CANDIDATE_IDENTITY.json', 'RATIO_CANDIDATE_IDENTITY.json').replace('lp_candidate_cli.exe', 'ratio_candidate_cli.exe')
    (BASE / 'run_ratio_candidate.py').write_text(runner)
    print('Separate ratio candidate prepared.')


if __name__ == '__main__':
    main()
