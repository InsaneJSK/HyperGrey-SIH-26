"""Create a separate numerical candidate from the retained diagnostic source."""
import json
from pathlib import Path
import shutil
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_binary_proof import sha, save


def main():
    src = BASE / 'diagnostic-source'
    dst = BASE / 'lp-candidate-source'
    shutil.copytree(src, dst)
    path = dst / 'src/sparse_lp.cpp'
    text = path.read_text()
    old = '            if(!pivot(leaving,entering,std::move(d)))return expired()?"time_limit":"numerical_error";'
    assert text.count(old) == 1
    new = '''            double direction_norm=0;for(double value:d)direction_norm=std::max(direction_norm,std::abs(value));
            if(!updates.empty()&&std::abs(d[leaving])<=1e-7*(1+direction_norm)) {
                trace("refresh_small_pivot");
                if(!refactor())return expired()?"time_limit":"numerical_error";
                values(cost);checked=false;goto recheck_values;
            }
''' + old
    path.write_text(text.replace(old, new))
    save(BASE / 'LP_CANDIDATE_IDENTITY.json', {p.relative_to(dst).as_posix(): sha(p) for p in sorted(dst.rglob('*')) if p.is_file()})
    print('Isolated LP candidate prepared.')


if __name__ == '__main__':
    main()
