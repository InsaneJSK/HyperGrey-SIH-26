# Third-party notices

The default `reference` engine is **HiGHS 1.12.0**, distributed through
`highspy`. It is separate from this repository's Sovereign C++ solver.
Its MIT license is reproduced in `licences/HiGHS.txt`, copied from the
installed highspy 1.12.0 distribution. Source: https://github.com/ERGO-Code/HiGHS.

Python package license metadata remains installed in each package's
`*.dist-info` directory in the container. This includes FastAPI, Starlette,
Uvicorn, Pydantic, NumPy and their dependencies. Caddy is distributed in its
separate official container, including its own notices.

`marco_refinery.mps` and `marco_low_sulfur.mps` are teaching-model conversions
from the published GAMS MARCO refinery case:
https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_marco.html.
The latter tightens the fuel-oil sulfur specification. They are not plant data.
Model provenance is retained in
`SIH-backup-solver/examples/industrial/manifest.json` in the source repository.
`production_lotsizing.mps` is the project's synthetic six-period production case.
