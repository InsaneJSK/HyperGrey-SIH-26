# Netlib expansion utility

`emps.c` is downloaded unchanged from https://netlib.org/lp/data/emps.c .
It is David M. Gay's Netlib compressed-MPS **data decompressor**, not an
optimization algorithm or a linked dependency of the solver. Preserve its
attribution. It is compiled into a separate executable used only to prepare
benchmark inputs. The download script records its SHA-256 hash.

No existing solver implementation is incorporated into our optimization core.
