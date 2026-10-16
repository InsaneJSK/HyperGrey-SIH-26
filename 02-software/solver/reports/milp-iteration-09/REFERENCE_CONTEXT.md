# Public comparison context — 15 September 2026

The [official MIPLIB Binkar page](https://miplib.zib.de/instance_details_binkar10_1.html)
currently lists objective 6741.38002393972. Older MIPLIB2010 listings and some
solution rows show 6742.2; neither should be confused with our iteration08
incumbent 6747.310014559364 or the earlier 30-second HiGHS incumbent 6746.760023.

This is external benchmark context only. No published solution, incumbent or
target value is passed to the core. A table entry does not prove that our
solver found or certified that answer. Our claim must come from each saved
run's own checked incumbent and valid bound, under the documented numerical
or restricted exact-proof scope.

Binkar has 2298 variables, including 170 binary and 2128 continuous variables,
and 1026 constraints. The existing at-most-36-binary exact proof engine cannot
certify it. The compact-equality change aims to reduce LP work while retaining
the same model; it does not create a new exact proof system.
