# Iteration 30 model ledger

Every observation, all profiles. `Published` is literature context only.

## Development, 27 reused models, repeat 1

| Run | Category | Objective | Bound | Gap | First point s | Nodes | LP iterations | Bounded calls | Fallbacks | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p0033.control.0 | exact_proof_checked | 3089 | 3089 | 0 | 1.521 | 1 | 0 | 0 | 0 | 26.8 | 3089 |
| p0033.candidate.0 | exact_proof_checked | 3089 | 3089 | 0 | 1.763 | 1 | 0 | 0 | 0 | 26.7 | 3089 |
| p0033.norestart.0 | exact_proof_checked | 3089 | 3089 | 0 | 2.097 | 1 | 0 | 0 | 0 | 26.7 | 3089 |
| enigma.candidate.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 6.381 | 21760 | 74012 | 16957 | 0 | 17.7 | 0 |
| enigma.norestart.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 5.165 | 21760 | 74012 | 16957 | 0 | 17.8 | 0 |
| enigma.control.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 4.922 | 21760 | 74012 | 16957 | 0 | 17.7 | 0 |
| flugpl.norestart.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.05755 | 641 | 1178 | 442 | 0 | 1.5 | 1201500 |
| flugpl.control.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.1178 | 641 | 1140 | 425 | 0 | 1.4 | 1201500 |
| flugpl.candidate.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.04437 | 641 | 1178 | 442 | 0 | 1.5 | 1201500 |
| stein27.control.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.0402 | 4993 | 18813 | 5043 | 0 | 6.7 | 18 |
| stein27.candidate.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.003224 | 4993 | 19002 | 5220 | 0 | 6.5 | 18 |
| stein27.norestart.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.002392 | 4993 | 19002 | 5220 | 0 | 6.8 | 18 |
| markshare_4_0.candidate.0 | exact_proof_checked | 1 | 1 | 0 | 1.707 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| markshare_4_0.norestart.0 | exact_proof_checked | 1 | 1 | 0 | 2.177 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| markshare_4_0.control.0 | exact_proof_checked | 1 | 1 | 0 | 2.004 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| blend2.norestart.0 | feasible_limit | 8.082396 | 7.59898414 | 0.05323 | 0.05904 | 26293 | 212834 | 29430 | 0 | 92.4 | 7.598985 |
| blend2.control.0 | feasible_limit | 7.971263 | 7.59898414 | 0.0415 | 9.525 | 29229 | 228309 | 33276 | 0 | 60.7 | 7.598985 |
| blend2.candidate.0 | feasible_limit | 7.971263 | 7.59898414 | 0.0415 | 0.05492 | 31122 | 239037 | 34858 | 0 | 57.4 | 7.598985 |
| binkar10_1.control.0 | feasible_limit | 6797.600025 | 6677.78913 | 0.01762 | 21.79 | 1314 | 47494 | 2657 | 0 | 37.4 | 6742.200024 |
| binkar10_1.candidate.0 | feasible_limit | 6769.740025 | 6681.730532 | 0.013 | 0.3211 | 3552 | 93980 | 5500 | 0 | 89.0 | 6742.200024 |
| binkar10_1.norestart.0 | feasible_limit | 6762.080017 | 6683.018522 | 0.01169 | 0.7678 | 3859 | 94218 | 5519 | 0 | 149.1 | 6742.200024 |
| egout.candidate.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.002789 | 3827 | 7239 | 4376 | 0 | 7.6 | 568.1007 |
| egout.norestart.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.006785 | 3827 | 7239 | 4376 | 0 | 7.6 | 568.1007 |
| egout.control.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.07691 | 3827 | 7292 | 4173 | 0 | 7.5 | 568.1007 |
| gt2.norestart.0 | feasible_limit | 35409 | 13958 | 0.6058 | 0.6282 | 139183 | 241149 | 153979 | 0 | 547.8 | 21166 |
| gt2.control.0 | feasible_limit | 50894 | 13940 | 0.7261 | 0.5156 | 119312 | 175747 | 120378 | 0 | 225.9 | 21166 |
| gt2.candidate.0 | feasible_limit | 35409 | 13945 | 0.6062 | 0.7457 | 137257 | 225283 | 152377 | 0 | 302.2 | 21166 |
| lseu.control.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.02509 | 26991 | 72565 | 27314 | 0 | 22.0 | 1120 |
| lseu.candidate.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.04062 | 26991 | 73979 | 28181 | 0 | 22.3 | 1120 |
| lseu.norestart.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.0242 | 7167 | 23345 | 8067 | 0 | 7.7 | 1120 |
| mod008.candidate.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 0.05054 | 8793 | 32824 | 11039 | 0 | 13.5 | 307 |
| mod008.norestart.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 0.1375 | 8793 | 32736 | 10953 | 0 | 13.4 | 307 |
| mod008.control.0 | completion_reference_pending | 307 | 307 | 1.846e-16 | 0.04195 | 8793 | 31185 | 9772 | 0 | 13.4 | 307 |
| p0201.norestart.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 1.551 | 3219 | 38906 | 3968 | 0 | 13.5 | 7615 |
| p0201.control.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 0.4115 | 4568 | 62617 | 4785 | 0 | 20.2 | 7615 |
| p0201.candidate.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 0.03968 | 4568 | 61578 | 5456 | 0 | 15.7 | 7615 |
| p0282.control.0 | feasible_limit | 266462 | 257458 | 0.03379 | 0.2998 | 26305 | 114409 | 27216 | 0 | 59.1 | 258411 |
| p0282.candidate.0 | feasible_limit | 262642 | 257420 | 0.01988 | 0.08696 | 25631 | 110568 | 27834 | 0 | 57.6 | 258411 |
| p0282.norestart.0 | feasible_limit | 258411 | 245002 | 0.05189 | 0.619 | 25845 | 108237 | 27949 | 0 | 88.8 | 258411 |
| misc03.candidate.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.125 | 711 | 8606 | 905 | 0 | 3.5 | 3360 |
| misc03.norestart.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.4558 | 711 | 9127 | 968 | 0 | 7.5 | 3360 |
| misc03.control.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.7365 | 711 | 10619 | 776 | 0 | 4.4 | 3360 |
| misc07.norestart.0 | feasible_limit | 2810 | 2250 | 0.1992 | 1.996 | 5553 | 125018 | 6118 | 0 | 27.6 | 2810 |
| misc07.control.0 | feasible_limit | 3130 | 2185 | 0.3018 | 4.14 | 6818 | 166497 | 6953 | 0 | 25.4 | 2810 |
| misc07.candidate.0 | feasible_limit | 2810 | 2225 | 0.2081 | 0.3784 | 9248 | 211011 | 9961 | 0 | 25.8 | 2810 |
| pk1.control.0 | feasible_limit | 16.99999996 | 5.171419876 | 0.6571 | 0.00722 | 58657 | 640732 | 59396 | 0 | 56.7 | 11 |
| pk1.candidate.0 | feasible_limit | 16.99999996 | 5.485615229 | 0.6397 | 0.006386 | 68975 | 774097 | 73501 | 0 | 72.3 | 11 |
| pk1.norestart.0 | feasible_limit | 16.99999996 | 5.894124863 | 0.617 | 0.0044 | 47984 | 538968 | 51397 | 0 | 87.8 | 11 |
| rgn.candidate.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.006501 | 5591 | 27140 | 6771 | 0 | 6.2 | 82.19999924 |
| rgn.norestart.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.007469 | 5591 | 27140 | 6771 | 0 | 6.4 | 82.19999924 |
| rgn.control.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.02835 | 5591 | 26691 | 6569 | 0 | 5.6 | 82.19999924 |
| gen-ip002.norestart.0 | feasible_limit | -4710.174791 | -4813.153763 | 0.02186 | 0.009436 | 81617 | 531307 | 88340 | 0 | 89.5 | -4783.733392 |
| gen-ip002.control.0 | feasible_limit | -4681.758266 | -4816.114834 | 0.02869 | 0.002217 | 73775 | 457368 | 74302 | 0 | 45.5 | -4783.733392 |
| gen-ip002.candidate.0 | feasible_limit | -4737.336979 | -4818.182534 | 0.01706 | 0.008623 | 46370 | 301971 | 50348 | 0 | 27.1 | -4783.733392 |
| assign1-5-8.control.0 | feasible_limit | 212 | 189.3320971 | 0.1064 | 0.2268 | 4401 | 63117 | 4549 | 0 | 10.4 | 212 |
| assign1-5-8.candidate.0 | feasible_limit | 212 | 189.3847066 | 0.1062 | 0.1466 | 4235 | 67204 | 5156 | 0 | 10.6 | 212 |
| assign1-5-8.norestart.0 | feasible_limit | 213 | 190.1459993 | 0.1068 | 0.2267 | 5260 | 80761 | 6501 | 0 | 19.5 | 212 |
| lotsize.candidate.0 | no_incumbent_limit | - | 379461.6694 | - | - | 1219 | 22715 | 2635 | 0 | 62.1 | 1480195 |
| lotsize.norestart.0 | no_incumbent_limit | - | 384187.4255 | - | - | 1322 | 20391 | 2853 | 0 | 70.3 | 1480195 |
| lotsize.control.0 | no_incumbent_limit | - | 383032.1653 | - | - | 2084 | 34445 | 4600 | 0 | 63.9 | 1480195 |
| eil33-2.norestart.0 | feasible_limit | 987.674133 | 879.9883952 | 0.1089 | 2.233 | 2277 | 37666 | 2710 | 0 | 47.1 | 934.007916 |
| eil33-2.control.0 | feasible_limit | 987.674133 | 876.786399 | 0.1122 | 6.436 | 3026 | 50162 | 3119 | 0 | 54.3 | 934.007916 |
| eil33-2.candidate.0 | feasible_limit | 989.386363 | 871.7002497 | 0.1188 | 2.195 | 2943 | 49419 | 3568 | 0 | 38.1 | 934.007916 |
| mas74.control.0 | feasible_limit | 12590.37126 | 11005.7938 | 0.1258 | 0.01732 | 113311 | 683707 | 114437 | 0 | 195.5 | 11801.18573 |
| mas74.candidate.0 | feasible_limit | 12421.38658 | 10999.74906 | 0.1144 | 0.008606 | 109087 | 693429 | 121865 | 0 | 179.7 | 11801.18573 |
| mas74.norestart.0 | feasible_limit | 12492.16312 | 11042.63427 | 0.116 | 0.01823 | 99211 | 632706 | 111248 | 0 | 315.8 | 11801.18573 |
| gen-ip054.candidate.0 | feasible_limit | 6907.862512 | 6790.425909 | 0.017 | 0.001374 | 234166 | 1188738 | 248302 | 0 | 102.4 | 6840.966 |
| gen-ip054.norestart.0 | feasible_limit | 6873.960506 | 6791.650463 | 0.01197 | 0.001706 | 162813 | 820493 | 171824 | 0 | 153.8 | 6840.966 |
| gen-ip054.control.0 | feasible_limit | 6911.531524 | 6788.97289 | 0.01773 | 0.01244 | 169054 | 834448 | 169988 | 0 | 79.1 | 6840.966 |
| neos859080.norestart.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 8.0 | infeasible |
| neos859080.control.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 8.0 | infeasible |
| neos859080.candidate.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 7.9 | infeasible |
| danoint.control.0 | feasible_limit | 85.99999997 | 62.86412178 | 0.2659 | 13.27 | 1231 | 202710 | 1354 | 0 | 36.8 | 65.66666667 |
| danoint.candidate.0 | no_incumbent_limit | - | 62.80040484 | - | - | 496 | 125208 | 670 | 0 | 37.2 | 65.66666667 |
| danoint.norestart.0 | feasible_limit | 85.99999998 | 62.88143212 | 0.2657 | 15.24 | 1079 | 187544 | 1405 | 0 | 36.7 | 65.66666667 |
| rout.candidate.0 | feasible_limit | 1131.72 | 998.3416094 | 0.1178 | 0.1404 | 20104 | 415314 | 22948 | 0 | 106.1 | 1077.56 |
| rout.norestart.0 | feasible_limit | 1131.72 | 998.6450108 | 0.1175 | 0.3767 | 15639 | 315111 | 17568 | 0 | 151.7 | 1077.56 |
| rout.control.0 | feasible_limit | 1305.77 | 998.2212075 | 0.2354 | 1.065 | 16445 | 329406 | 16518 | 0 | 89.4 | 1077.56 |
| mas76.norestart.0 | feasible_limit | 40735.65352 | 39487.60848 | 0.03064 | 0.01277 | 68981 | 406454 | 75772 | 0 | 230.0 | 40005.05414 |
| mas76.control.0 | feasible_limit | 41519.99574 | 39486.15652 | 0.04898 | 0.01412 | 134014 | 759834 | 135133 | 0 | 231.9 | 40005.05414 |
| mas76.candidate.0 | feasible_limit | 40962.96914 | 39444.87328 | 0.03706 | 0.009838 | 79719 | 467362 | 87140 | 0 | 151.1 | 40005.05414 |

## Development, 27 reused models, repeat 2

| Run | Category | Objective | Bound | Gap | First point s | Nodes | LP iterations | Bounded calls | Fallbacks | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p0033.control.0 | exact_proof_checked | 3089 | 3089 | 0 | 0.8647 | 1 | 0 | 0 | 0 | 26.8 | 3089 |
| p0033.candidate.0 | exact_proof_checked | 3089 | 3089 | 0 | 0.8566 | 1 | 0 | 0 | 0 | 26.7 | 3089 |
| p0033.norestart.0 | exact_proof_checked | 3089 | 3089 | 0 | 0.894 | 1 | 0 | 0 | 0 | 26.7 | 3089 |
| enigma.candidate.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 2.708 | 21760 | 74012 | 16957 | 0 | 17.7 | 0 |
| enigma.norestart.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 2.763 | 21760 | 74012 | 16957 | 0 | 17.7 | 0 |
| enigma.control.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | 2.689 | 21760 | 74012 | 16957 | 0 | 17.7 | 0 |
| flugpl.norestart.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.03382 | 641 | 1178 | 442 | 0 | 1.4 | 1201500 |
| flugpl.control.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.03723 | 641 | 1140 | 425 | 0 | 1.4 | 1201500 |
| flugpl.candidate.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 0.03715 | 641 | 1178 | 442 | 0 | 1.5 | 1201500 |
| stein27.control.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.02195 | 4993 | 18813 | 5043 | 0 | 6.6 | 18 |
| stein27.candidate.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.002545 | 4993 | 19002 | 5220 | 0 | 6.6 | 18 |
| stein27.norestart.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 0.002945 | 4993 | 19002 | 5220 | 0 | 6.6 | 18 |
| markshare_4_0.candidate.0 | exact_proof_checked | 1 | 1 | 0 | 1.214 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| markshare_4_0.norestart.0 | exact_proof_checked | 1 | 1 | 0 | 1.288 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| markshare_4_0.control.0 | exact_proof_checked | 1 | 1 | 0 | 1.206 | 1 | 0 | 0 | 0 | 13.9 | 1 |
| blend2.norestart.0 | feasible_limit | 7.971263 | 7.59898414 | 0.0415 | 0.0454 | 47572 | 295094 | 52023 | 0 | 98.8 | 7.598985 |
| blend2.control.0 | feasible_limit | 7.971263 | 7.59898414 | 0.0415 | 6.738 | 39845 | 294806 | 43888 | 0 | 69.9 | 7.598985 |
| blend2.candidate.0 | feasible_limit | 7.971263 | 7.59898414 | 0.0415 | 0.04347 | 44499 | 316228 | 49765 | 0 | 68.0 | 7.598985 |
| binkar10_1.control.0 | feasible_limit | 6759.380024 | 6683.380466 | 0.01124 | 2.879 | 6943 | 154311 | 8046 | 0 | 153.7 | 6742.200024 |
| binkar10_1.candidate.0 | feasible_limit | 6775.250025 | 6683.358051 | 0.01356 | 0.1607 | 7629 | 176611 | 9918 | 0 | 152.4 | 6742.200024 |
| binkar10_1.norestart.0 | feasible_limit | 6762.080017 | 6685.224734 | 0.01136 | 0.4105 | 8109 | 178205 | 10173 | 0 | 309.1 | 6742.200024 |
| egout.candidate.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.004496 | 3827 | 7239 | 4376 | 0 | 7.6 | 568.1007 |
| egout.norestart.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.004016 | 3827 | 7239 | 4376 | 0 | 7.6 | 568.1007 |
| egout.control.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 0.03927 | 3827 | 7292 | 4173 | 0 | 7.6 | 568.1007 |
| gt2.norestart.0 | feasible_limit | 35409 | 13970 | 0.6055 | 0.3713 | 279814 | 491376 | 307892 | 0 | 1088.2 | 21166 |
| gt2.control.0 | feasible_limit | 50894 | 13957 | 0.7257 | 0.2595 | 260837 | 398945 | 261903 | 0 | 500.9 | 21166 |
| gt2.candidate.0 | feasible_limit | 35409 | 13947 | 0.6061 | 0.3689 | 184789 | 303436 | 204163 | 0 | 349.6 | 21166 |
| lseu.control.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.0179 | 26991 | 72565 | 27314 | 0 | 21.8 | 1120 |
| lseu.candidate.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.04426 | 26991 | 73979 | 28181 | 0 | 22.2 | 1120 |
| lseu.norestart.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 0.02422 | 7167 | 23345 | 8067 | 0 | 7.8 | 1120 |
| mod008.candidate.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 0.06525 | 8793 | 32344 | 10627 | 0 | 13.5 | 307 |
| mod008.norestart.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 0.07131 | 8793 | 32346 | 10616 | 0 | 13.4 | 307 |
| mod008.control.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 0.02517 | 8793 | 31185 | 9772 | 0 | 13.1 | 307 |
| p0201.norestart.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 1.537 | 3219 | 38906 | 3968 | 0 | 13.6 | 7615 |
| p0201.control.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 0.1706 | 4568 | 62617 | 4785 | 0 | 19.8 | 7615 |
| p0201.candidate.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 0.04139 | 4568 | 65191 | 5317 | 0 | 19.8 | 7615 |
| p0282.control.0 | feasible_limit | 266462 | 257873 | 0.03223 | 0.1838 | 45443 | 186023 | 46347 | 0 | 103.7 | 258411 |
| p0282.candidate.0 | feasible_limit | 258682 | 258153 | 0.002045 | 0.07301 | 51935 | 182231 | 54787 | 0 | 103.0 | 258411 |
| p0282.norestart.0 | feasible_limit | 258411 | 245711 | 0.04915 | 0.4255 | 55120 | 230959 | 57617 | 0 | 181.8 | 258411 |
| misc03.candidate.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.06652 | 711 | 9306 | 990 | 0 | 3.9 | 3360 |
| misc03.norestart.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.2603 | 711 | 8628 | 905 | 0 | 7.5 | 3360 |
| misc03.control.0 | numerical_completion_checked | 3360 | 3360 | 0 | 0.357 | 711 | 10619 | 776 | 0 | 4.4 | 3360 |
| misc07.norestart.0 | feasible_limit | 2810 | 2415 | 0.1405 | 1.911 | 11464 | 219116 | 12196 | 0 | 49.1 | 2810 |
| misc07.control.0 | feasible_limit | 3130 | 2220 | 0.2906 | 3.196 | 9687 | 223839 | 9783 | 0 | 29.4 | 2810 |
| misc07.candidate.0 | feasible_limit | 2810 | 2275 | 0.1903 | 0.2693 | 12330 | 267253 | 13161 | 0 | 29.5 | 2810 |
| pk1.control.0 | feasible_limit | 16.99999996 | 5.649432849 | 0.6306 | 0.005401 | 80422 | 875802 | 81161 | 0 | 77.1 | 11 |
| pk1.candidate.0 | feasible_limit | 16 | 5.570975103 | 0.6135 | 0.003167 | 78020 | 873430 | 83011 | 0 | 76.2 | 11 |
| pk1.norestart.0 | feasible_limit | 16 | 6.781642895 | 0.5423 | 0.004012 | 81242 | 907486 | 86061 | 0 | 163.0 | 11 |
| rgn.candidate.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.002935 | 5591 | 27140 | 6771 | 0 | 6.2 | 82.19999924 |
| rgn.norestart.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.00439 | 5591 | 27140 | 6771 | 0 | 6.2 | 82.19999924 |
| rgn.control.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 0.02008 | 5591 | 26691 | 6569 | 0 | 5.7 | 82.19999924 |
| gen-ip002.norestart.0 | feasible_limit | -4711.521919 | -4812.214854 | 0.02137 | 0.007142 | 101172 | 657471 | 109343 | 0 | 105.0 | -4783.733392 |
| gen-ip002.control.0 | feasible_limit | -4681.758266 | -4814.76997 | 0.0284 | 0.003845 | 109142 | 677068 | 109669 | 0 | 57.9 | -4783.733392 |
| gen-ip002.candidate.0 | feasible_limit | -4715.114695 | -4815.008101 | 0.02118 | 0.007767 | 101708 | 662429 | 110373 | 0 | 55.6 | -4783.733392 |
| assign1-5-8.control.0 | feasible_limit | 212 | 189.9677482 | 0.1034 | 0.1213 | 8470 | 115274 | 8618 | 0 | 17.3 | 212 |
| assign1-5-8.candidate.0 | feasible_limit | 213 | 189.9999809 | 0.1075 | 0.05874 | 8309 | 126869 | 10149 | 0 | 17.3 | 212 |
| assign1-5-8.norestart.0 | feasible_limit | 213 | 190.1550442 | 0.1068 | 0.08529 | 5376 | 82330 | 6590 | 0 | 19.9 | 212 |
| lotsize.candidate.0 | no_incumbent_limit | - | 382778.3333 | - | - | 1639 | 28986 | 3533 | 0 | 62.6 | 1480195 |
| lotsize.norestart.0 | no_incumbent_limit | - | 387737.2512 | - | - | 2194 | 34149 | 4725 | 0 | 120.6 | 1480195 |
| lotsize.control.0 | no_incumbent_limit | - | 382658.7135 | - | - | 1858 | 32345 | 3985 | 0 | 64.2 | 1480195 |
| eil33-2.norestart.0 | feasible_limit | 989.386363 | 875.2133577 | 0.1153 | 2.214 | 1895 | 32374 | 2279 | 0 | 43.7 | 934.007916 |
| eil33-2.control.0 | feasible_limit | 989.386363 | 866.8678978 | 0.1237 | 6.294 | 1898 | 33217 | 1957 | 0 | 47.6 | 934.007916 |
| eil33-2.candidate.0 | feasible_limit | 989.386363 | 862.4442329 | 0.1282 | 2.357 | 1670 | 30943 | 2016 | 0 | 33.4 | 934.007916 |
| mas74.control.0 | feasible_limit | 12590.37126 | 10967.35451 | 0.1289 | 0.02118 | 67626 | 409587 | 68752 | 0 | 121.0 | 11801.18573 |
| mas74.candidate.0 | feasible_limit | 12341.94716 | 10978.05208 | 0.1105 | 0.02749 | 78829 | 503261 | 88743 | 0 | 140.6 | 11801.18573 |
| mas74.norestart.0 | feasible_limit | 12929.58969 | 11024.49821 | 0.1473 | 0.01032 | 78478 | 500368 | 87771 | 0 | 256.0 | 11801.18573 |
| gen-ip054.candidate.0 | feasible_limit | 6898.674835 | 6788.924297 | 0.01591 | 0.002281 | 167456 | 855258 | 178064 | 0 | 78.8 | 6840.966 |
| gen-ip054.norestart.0 | feasible_limit | 6911.255518 | 6791.186017 | 0.01737 | 0.001624 | 146196 | 739443 | 154879 | 0 | 153.9 | 6840.966 |
| gen-ip054.control.0 | feasible_limit | 6911.531524 | 6788.744284 | 0.01776 | 0.01237 | 157054 | 776477 | 157988 | 0 | 78.5 | 6840.966 |
| neos859080.norestart.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 7.8 | infeasible |
| neos859080.control.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 8.0 | infeasible |
| neos859080.candidate.0 | terminal_reference_pending | - | - | - | - | 93 | 9389 | 132 | 0 | 7.9 | infeasible |
| danoint.control.0 | feasible_limit | 71.24999999 | 62.80834796 | 0.1168 | 28.94 | 549 | 131073 | 730 | 0 | 40.9 | 65.66666667 |
| danoint.candidate.0 | feasible_limit | 71.99999997 | 62.80377306 | 0.126 | 25.68 | 557 | 134702 | 750 | 0 | 41.3 | 65.66666667 |
| danoint.norestart.0 | feasible_limit | 85.99999998 | 62.86709903 | 0.2659 | 16.76 | 866 | 158217 | 1116 | 0 | 36.9 | 65.66666667 |
| rout.candidate.0 | feasible_limit | 1131.72 | 998.0782228 | 0.118 | 0.2665 | 13406 | 302781 | 15844 | 0 | 73.9 | 1077.56 |
| rout.norestart.0 | feasible_limit | 1131.72 | 998.6014952 | 0.1175 | 0.38 | 14861 | 301804 | 16878 | 0 | 145.9 | 1077.56 |
| rout.control.0 | feasible_limit | 1305.77 | 998.1651872 | 0.2354 | 1.466 | 15114 | 308604 | 15278 | 0 | 84.4 | 1077.56 |
| mas76.norestart.0 | feasible_limit | 40990.36687 | 39525.53385 | 0.03574 | 0.01361 | 95935 | 565048 | 104513 | 0 | 305.8 | 40005.05414 |
| mas76.control.0 | feasible_limit | 41519.99574 | 39465.0216 | 0.04949 | 0.01345 | 112543 | 637269 | 113662 | 0 | 179.7 | 40005.05414 |
| mas76.candidate.0 | feasible_limit | 41278.02501 | 39464.72227 | 0.04393 | 0.01449 | 107173 | 630199 | 117276 | 0 | 178.5 | 40005.05414 |

## Second fresh untouched holdout, 12 models: control and candidate

| Run | Category | Objective | Bound | Gap | First point s | Nodes | LP iterations | Bounded calls | Fallbacks | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10teams.control.0 | feasible_limit | 934 | 916.9999082 | 0.01818 | 6.083 | 844 | 81922 | 924 | 0 | 50.8 | 924 |
| 10teams.candidate.0 | feasible_limit | 934 | 916.9999082 | 0.01818 | 6.437 | 683 | 79254 | 940 | 0 | 94.1 | 924 |
| air03.candidate.0 | numerical_completion_checked | 340160 | 340160 | 0 | 2.571 | 3 | 633 | 17 | 0 | 15.3 | 340160 |
| air03.control.0 | numerical_completion_checked | 340160 | 340160 | 0 | 5.446 | 3 | 1485 | 16 | 0 | 106.1 | 340160 |
| cap6000.control.0 | feasible_limit | -2451336 | -2451411 | 3.06e-05 | 2.791 | 2416 | 20455 | 3283 | 0 | 90.1 | -2451377 |
| cap6000.candidate.0 | feasible_limit | -2450867 | -2451414 | 0.0002232 | 7.448 | 1048 | 14798 | 1951 | 0 | 81.2 | -2451377 |
| gesa2_o.candidate.0 | feasible_limit | 25972277.63 | 25536591.96 | 0.01678 | 0.8376 | 5142 | 39278 | 6655 | 0 | 79.5 | 25779856.37 |
| gesa2_o.control.0 | no_incumbent_limit | - | 25523409.98 | - | - | 1028 | 14430 | 2216 | 0 | 35.7 | 25779856.37 |
| gesa3_o.control.0 | feasible_limit | 28061180.3 | 27920510.6 | 0.005013 | 2.215 | 3062 | 30911 | 3549 | 0 | 36.1 | 27991042.65 |
| gesa3_o.candidate.0 | feasible_limit | 27991430.12 | 27925759.6 | 0.002346 | 0.4078 | 4433 | 40391 | 4976 | 0 | 55.1 | 27991042.65 |
| harp2.candidate.0 | feasible_limit | -71531923 | -74226327 | 0.03767 | 1.676 | 4338 | 52366 | 4887 | 4 | 157.5 | -73899798 |
| harp2.control.0 | feasible_limit | -70381679 | -74226327 | 0.05463 | 3.519 | 7194 | 74642 | 7472 | 2 | 214.4 | -73899798 |
| mitre.control.0 | no_incumbent_limit | - | 114765 | - | - | 542 | 17954 | 781 | 0 | 89.8 | 115155 |
| mitre.candidate.0 | no_incumbent_limit | - | 114750 | - | - | 273 | 16077 | 355 | 0 | 61.1 | 115155 |
| mod011.candidate.0 | no_incumbent_limit | - | -60286535.85 | - | - | 30 | 19005 | 58 | 0 | 67.1 | -54558535 |
| mod011.control.0 | no_incumbent_limit | - | -59459009.58 | - | - | 110 | 30534 | 139 | 0 | 74.5 | -54558535 |
| p2756.control.0 | no_incumbent_limit | - | 2701 | - | - | 2678 | 26317 | 5868 | 0 | 71.8 | 3124 |
| p2756.candidate.0 | no_incumbent_limit | - | 2700 | - | - | 1892 | 19059 | 4031 | 0 | 62.9 | 3124 |
| pp08aCUTS.candidate.0 | feasible_limit | 8090 | 6291.79238 | 0.2222 | 0.03686 | 22943 | 212043 | 26015 | 0 | 61.2 | 7350 |
| pp08aCUTS.control.0 | feasible_limit | 7890 | 6275.336321 | 0.2046 | 1.049 | 20094 | 175845 | 20804 | 0 | 52.9 | 7350 |
| qnet1.control.0 | feasible_limit | 29189.42013 | 14600.17375 | 0.4998 | 8.287 | 3112 | 91511 | 3359 | 1 | 62.2 | 16029.6927 |
| qnet1.candidate.0 | feasible_limit | 18591.4066 | 14591.15052 | 0.2152 | 0.8861 | 3426 | 104393 | 4001 | 1 | 128.6 | 16029.6927 |
| nw04.candidate.0 | feasible_limit | 17514 | 16436 | 0.06155 | 14.38 | 38 | 938 | 47 | 0 | 267.4 | 16862 |
| nw04.control.0 | feasible_limit | 17514 | 16400 | 0.0636 | 8.604 | 39 | 972 | 46 | 0 | 262.9 | 16862 |

## Second fresh untouched holdout, 12 models: norestart

| Run | Category | Objective | Bound | Gap | First point s | Nodes | LP iterations | Bounded calls | Fallbacks | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10teams.norestart.0 | feasible_limit | 934 | 916.9999082 | 0.01818 | 7.102 | 744 | 85131 | 1019 | 0 | 76.1 | 924 |
| air03.norestart.0 | numerical_completion_checked | 340160 | 340160 | 0 | 2.381 | 3 | 633 | 17 | 0 | 15.3 | 340160 |
| cap6000.norestart.0 | feasible_limit | -2451336 | -2451409 | 2.978e-05 | 6.061 | 2005 | 17597 | 3343 | 0 | 128.7 | -2451377 |
| gesa2_o.norestart.0 | feasible_limit | 25973473.61 | 25548288.23 | 0.01637 | 0.515 | 10284 | 75646 | 12383 | 0 | 236.1 | 25779856.37 |
| gesa3_o.norestart.0 | feasible_limit | 27991430.12 | 27940588.74 | 0.001816 | 0.4514 | 11369 | 93870 | 12148 | 0 | 196.3 | 27991042.65 |
| harp2.norestart.0 | feasible_limit | -70566414 | -74235860 | 0.052 | 1.057 | 6211 | 68422 | 6806 | 13 | 335.4 | -73899798 |
| mitre.norestart.0 | no_incumbent_limit | - | 114765 | - | - | 1615 | 16382 | 2564 | 0 | 147.6 | 115155 |
| mod011.norestart.0 | feasible_limit | -51986929.02 | -57924286.13 | 0.1142 | 1.631 | 436 | 101675 | 653 | 0 | 146.5 | -54558535 |
| p2756.norestart.0 | no_incumbent_limit | - | 2702 | - | - | 4404 | 36791 | 9656 | 0 | 213.3 | 3124 |
| pp08aCUTS.norestart.0 | feasible_limit | 7770 | 6434.273728 | 0.1719 | 0.03107 | 42482 | 385894 | 46222 | 0 | 212.6 | 7350 |
| qnet1.norestart.0 | feasible_limit | 17290.9285 | 14639.55503 | 0.1533 | 2.314 | 3839 | 126558 | 4643 | 5 | 132.0 | 16029.6927 |
| nw04.norestart.0 | feasible_limit | 17004 | 16486 | 0.03046 | 10.58 | 108 | 1647 | 130 | 0 | 319.8 | 16862 |

