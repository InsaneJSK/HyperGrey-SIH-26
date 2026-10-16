# Iteration 32 model ledger

Every observation, both profiles. `Published` is literature context only, and is
deliberately absent for the fresh holdout.

## Development, 27 reused models, two repeats per profile

| Run | Category | Objective | Bound | Gap | Root after cuts | Cuts | Gomory applied | Purged | First point s | Nodes | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p0033.control.0 | exact_proof_checked | 3089 | 3089 | 0 | - | 0 | 0 | 0 | 0.6137 | 1 | 26.8 | 3089 |
| p0033.candidate.0 | exact_proof_checked | 3089 | 3089 | 0 | - | 0 | 0 | 0 | 0.4716 | 1 | 26.8 | 3089 |
| p0033.candidate.1 | exact_proof_checked | 3089 | 3089 | 0 | - | 0 | 0 | 0 | 0.509 | 1 | 26.8 | 3089 |
| p0033.control.1 | exact_proof_checked | 3089 | 3089 | 0 | - | 0 | 0 | 0 | 0.4775 | 1 | 26.8 | 3089 |
| enigma.candidate.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | -4.9406565e-324 | 24 | 14 | 10 | 1.313 | 7724 | 9.9 | 0 |
| enigma.control.0 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | -4.9406565e-324 | 5 | 0 | 0 | 1.708 | 21760 | 17.7 | 0 |
| enigma.control.1 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | -4.9406565e-324 | 5 | 0 | 0 | 1.857 | 21760 | 17.7 | 0 |
| enigma.candidate.1 | numerical_completion_checked | 0 | -4.940656458e-324 | 4.941e-324 | -4.9406565e-324 | 24 | 14 | 10 | 1.565 | 7724 | 9.8 | 0 |
| flugpl.control.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 1167185.6 | 0 | 0 | 0 | 0.02882 | 641 | 1.4 | 1201500 |
| flugpl.candidate.0 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 1171918.6 | 8 | 20 | 12 | 0.02637 | 545 | 1.5 | 1201500 |
| flugpl.candidate.1 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 1171918.6 | 8 | 20 | 12 | 0.03297 | 545 | 1.5 | 1201500 |
| flugpl.control.1 | numerical_completion_checked | 1201500 | 1201499.88 | 1e-07 | 1167185.6 | 0 | 0 | 0 | 0.02816 | 641 | 1.5 | 1201500 |
| stein27.candidate.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 13 | 9 | 67 | 58 | 0.007933 | 4707 | 6.7 | 18 |
| stein27.control.0 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 13 | 0 | 0 | 0 | 0.001773 | 4993 | 6.8 | 18 |
| stein27.control.1 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 13 | 0 | 0 | 0 | 0.002657 | 4993 | 6.7 | 18 |
| stein27.candidate.1 | numerical_completion_checked | 18 | 18 | 1.87e-16 | 13 | 9 | 67 | 58 | 0.007962 | 4707 | 6.7 | 18 |
| markshare_4_0.control.0 | exact_proof_checked | 1 | 1 | 0 | - | 0 | 0 | 0 | 0.8013 | 1 | 13.9 | 1 |
| markshare_4_0.candidate.0 | exact_proof_checked | 1 | 1 | 0 | - | 0 | 0 | 0 | 0.8626 | 1 | 13.9 | 1 |
| markshare_4_0.candidate.1 | exact_proof_checked | 1 | 1 | 0 | - | 0 | 0 | 0 | 0.8599 | 1 | 13.9 | 1 |
| markshare_4_0.control.1 | exact_proof_checked | 1 | 1 | 0 | - | 0 | 0 | 0 | 0.8551 | 1 | 13.9 | 1 |
| blend2.candidate.0 | completion_reference_pending | 7.598985 | 7.59898414 | 1e-07 | 7.0249011 | 3 | 6 | 3 | 5.473 | 10834 | 53.0 | 7.598985 |
| blend2.control.0 | completion_reference_pending | 7.598985 | 7.59898414 | 1e-07 | 6.9156743 | 0 | 0 | 0 | 0.02965 | 10683 | 59.7 | 7.598985 |
| blend2.control.1 | completion_reference_pending | 7.598985 | 7.59898414 | 1e-07 | 6.9156743 | 0 | 0 | 0 | 0.02887 | 10683 | 60.2 | 7.598985 |
| blend2.candidate.1 | completion_reference_pending | 7.598985 | 7.59898414 | 1e-07 | 7.0249011 | 3 | 6 | 3 | 5.07 | 10834 | 53.3 | 7.598985 |
| binkar10_1.control.0 | feasible_limit | 6762.080017 | 6686.352207 | 0.0112 | 6662.931 | 29 | 0 | 0 | 0.3474 | 11657 | 443.6 | 6742.200024 |
| binkar10_1.candidate.0 | feasible_limit | 6762.940024 | 6694.347056 | 0.01014 | 6672.2557 | 49 | 80 | 69 | 0.4226 | 7851 | 300.0 | 6742.200024 |
| binkar10_1.candidate.1 | feasible_limit | 6762.940024 | 6692.413792 | 0.01043 | 6672.2557 | 49 | 80 | 69 | 0.6703 | 4077 | 158.5 | 6742.200024 |
| binkar10_1.control.1 | feasible_limit | 6762.080017 | 6685.831112 | 0.01127 | 6662.931 | 29 | 0 | 0 | 0.6202 | 9889 | 375.4 | 6742.200024 |
| egout.candidate.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 528.54782 | 21 | 52 | 31 | 0.006176 | 233 | 1.9 | 568.1007 |
| egout.control.0 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 367.08485 | 0 | 0 | 0 | 0.00248 | 3827 | 7.6 | 568.1007 |
| egout.control.1 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 367.08485 | 0 | 0 | 0 | 0.004137 | 3827 | 7.6 | 568.1007 |
| egout.candidate.1 | numerical_completion_checked | 568.1007 | 568.1007 | 0 | 528.54782 | 21 | 52 | 31 | 0.008334 | 233 | 1.8 | 568.1007 |
| gt2.control.0 | feasible_limit | 35409 | 13970 | 0.6055 | 13461 | 0 | 0 | 0 | 0.3491 | 301589 | 1138.7 | 21166 |
| gt2.candidate.0 | feasible_limit | 32143 | 18489 | 0.4248 | 18344 | 8 | 20 | 12 | 0.2704 | 200468 | 762.8 | 21166 |
| gt2.candidate.1 | feasible_limit | 32143 | 18489 | 0.4248 | 18344 | 8 | 20 | 12 | 0.5324 | 141668 | 550.8 | 21166 |
| gt2.control.1 | feasible_limit | 35409 | 13970 | 0.6055 | 13461 | 0 | 0 | 0 | 0.3641 | 269426 | 972.8 | 21166 |
| lseu.candidate.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 1028 | 17 | 20 | 18 | 0.03046 | 8299 | 7.3 | 1120 |
| lseu.control.0 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 1000 | 12 | 0 | 0 | 0.01396 | 7167 | 7.7 | 1120 |
| lseu.control.1 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 1000 | 12 | 0 | 0 | 0.01274 | 7167 | 7.7 | 1120 |
| lseu.candidate.1 | numerical_completion_checked | 1120 | 1120 | 2.028e-16 | 1028 | 17 | 20 | 18 | 0.03621 | 8299 | 7.3 | 1120 |
| mod008.control.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 292 | 9 | 0 | 0 | 0.03307 | 8793 | 13.6 | 307 |
| mod008.candidate.0 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 292 | 9 | 0 | 0 | 0.03313 | 8793 | 13.5 | 307 |
| mod008.candidate.1 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 292 | 9 | 0 | 0 | 0.02947 | 8793 | 13.4 | 307 |
| mod008.control.1 | numerical_completion_checked | 307 | 307 | 1.846e-16 | 292 | 9 | 0 | 0 | 0.03316 | 8793 | 13.6 | 307 |
| p0201.candidate.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 7265 | 15 | 30 | 25 | 1.563 | 1937 | 13.6 | 7615 |
| p0201.control.0 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 7125 | 5 | 0 | 0 | 1.53 | 3219 | 13.6 | 7615 |
| p0201.control.1 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 7125 | 5 | 0 | 0 | 1.531 | 3219 | 13.6 | 7615 |
| p0201.candidate.1 | numerical_completion_checked | 7615 | 7615 | 1.194e-16 | 7265 | 15 | 30 | 25 | 1.567 | 1931 | 13.6 | 7615 |
| p0282.control.0 | feasible_limit | 258411 | 246129 | 0.04753 | 226637 | 35 | 0 | 0 | 0.2955 | 90193 | 277.2 | 258411 |
| p0282.candidate.0 | feasible_limit | 266359 | 232696 | 0.1264 | 213581 | 38 | 80 | 69 | 0.2631 | 66321 | 354.2 | 258411 |
| p0282.candidate.1 | feasible_limit | 282043 | 232833 | 0.1745 | 213581 | 38 | 80 | 69 | 0.2773 | 69105 | 372.3 | 258411 |
| p0282.control.1 | feasible_limit | 258411 | 246160 | 0.04741 | 226637 | 35 | 0 | 0 | 0.2548 | 93310 | 284.2 | 258411 |
| misc03.candidate.0 | numerical_completion_checked | 3360 | 3360 | 1.353e-16 | 1995 | 3 | 7 | 4 | 0.4778 | 1187 | 7.7 | 3360 |
| misc03.control.0 | numerical_completion_checked | 3360 | 3360 | 0 | 1910 | 0 | 0 | 0 | 0.1797 | 711 | 7.5 | 3360 |
| misc03.control.1 | numerical_completion_checked | 3360 | 3360 | 0 | 1910 | 0 | 0 | 0 | 0.1911 | 711 | 7.5 | 3360 |
| misc03.candidate.1 | numerical_completion_checked | 3360 | 3360 | 1.353e-16 | 1995 | 3 | 7 | 4 | 0.5036 | 1187 | 7.6 | 3360 |
| misc07.control.0 | feasible_limit | 2810 | 2625 | 0.06581 | 1415 | 0 | 0 | 0 | 1.54 | 27571 | 73.9 | 2810 |
| misc07.candidate.0 | feasible_limit | 2810 | 2615 | 0.06937 | 1415 | 0 | 0 | 0 | 1.529 | 26328 | 73.3 | 2810 |
| misc07.candidate.1 | feasible_limit | 2810 | 2635 | 0.06226 | 1415 | 0 | 0 | 0 | 1.379 | 28656 | 74.0 | 2810 |
| misc07.control.1 | feasible_limit | 2810 | 2605 | 0.07293 | 1415 | 0 | 0 | 0 | 1.443 | 25120 | 72.0 | 2810 |
| pk1.candidate.0 | feasible_limit | 12 | 7.428927004 | 0.3516 | -1e-07 | 4 | 18 | 14 | 0.006134 | 140802 | 297.5 | 11 |
| pk1.control.0 | feasible_limit | 16 | 7.738805793 | 0.486 | -1e-07 | 0 | 0 | 0 | 0.003146 | 139841 | 297.0 | 11 |
| pk1.control.1 | feasible_limit | 16 | 7.731425614 | 0.4864 | -1e-07 | 0 | 0 | 0 | 0.00314 | 139250 | 298.0 | 11 |
| pk1.candidate.1 | feasible_limit | 12 | 7.161503163 | 0.3722 | -1e-07 | 4 | 18 | 14 | 0.007182 | 121196 | 229.5 | 11 |
| rgn.control.0 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 48.799994 | 0 | 0 | 0 | 0.002086 | 5591 | 6.2 | 82.19999924 |
| rgn.candidate.0 | numerical_completion_checked | 82.19999921 | 82.19999091 | 9.978e-08 | 52.76446 | 8 | 20 | 12 | 0.007412 | 4603 | 4.9 | 82.19999924 |
| rgn.candidate.1 | numerical_completion_checked | 82.19999921 | 82.19999091 | 9.978e-08 | 52.76446 | 8 | 20 | 12 | 0.00614 | 4603 | 4.9 | 82.19999924 |
| rgn.control.1 | numerical_completion_checked | 82.19999923 | 82.19999072 | 1.023e-07 | 48.799994 | 0 | 0 | 0 | 0.003615 | 5591 | 6.3 | 82.19999924 |
| gen-ip002.candidate.0 | feasible_limit | -4723.655868 | -4811.11032 | 0.01851 | -4839.2991 | 5 | 9 | 4 | 0.007072 | 140370 | 174.6 | -4783.733392 |
| gen-ip002.control.0 | feasible_limit | -4731.716605 | -4810.894197 | 0.01673 | -4840.5424 | 0 | 0 | 0 | 0.004382 | 136488 | 174.6 | -4783.733392 |
| gen-ip002.control.1 | feasible_limit | -4747.4863 | -4810.703152 | 0.01331 | -4840.5424 | 0 | 0 | 0 | 0.004487 | 142467 | 174.5 | -4783.733392 |
| gen-ip002.candidate.1 | feasible_limit | -4722.379406 | -4811.836973 | 0.01894 | -4839.2991 | 5 | 9 | 4 | 0.008917 | 118974 | 119.0 | -4783.733392 |
| assign1-5-8.control.0 | feasible_limit | 213 | 190.8340076 | 0.1036 | 183.36254 | 0 | 0 | 0 | 0.04793 | 10578 | 36.2 | 212 |
| assign1-5-8.candidate.0 | feasible_limit | 212 | 191.0582712 | 0.09832 | 183.36254 | 0 | 0 | 0 | 0.04503 | 12974 | 42.9 | 212 |
| assign1-5-8.candidate.1 | feasible_limit | 213 | 191.1683681 | 0.102 | 183.36254 | 0 | 0 | 0 | 0.0439 | 14586 | 47.0 | 212 |
| assign1-5-8.control.1 | feasible_limit | 214 | 191.1465895 | 0.1063 | 183.36254 | 0 | 0 | 0 | 0.0412 | 14188 | 45.7 | 212 |
| lotsize.candidate.0 | no_incumbent_limit | - | 417641.7825 | - | 407728.14 | 42 | 80 | 38 | - | 3961 | 205.5 | 1480195 |
| lotsize.control.0 | no_incumbent_limit | - | 391814.2573 | - | 348385.31 | 0 | 0 | 0 | - | 3838 | 197.8 | 1480195 |
| lotsize.control.1 | no_incumbent_limit | - | 392274.5333 | - | 348385.31 | 0 | 0 | 0 | - | 4107 | 214.2 | 1480195 |
| lotsize.candidate.1 | no_incumbent_limit | - | 417343.0019 | - | 407728.14 | 42 | 80 | 38 | - | 3403 | 178.7 | 1480195 |
| eil33-2.control.0 | feasible_limit | 987.674133 | 885.8747967 | 0.103 | 811.27891 | 0 | 0 | 0 | 2.167 | 2762 | 51.6 | 934.007916 |
| eil33-2.candidate.0 | feasible_limit | 987.674133 | 885.5697734 | 0.1033 | 811.27891 | 0 | 0 | 0 | 2.221 | 2732 | 51.1 | 934.007916 |
| eil33-2.candidate.1 | feasible_limit | 987.674133 | 885.2195778 | 0.1036 | 811.27891 | 0 | 0 | 0 | 2.216 | 2702 | 50.9 | 934.007916 |
| eil33-2.control.1 | feasible_limit | 987.674133 | 882.7172936 | 0.1062 | 811.27891 | 0 | 0 | 0 | 2.224 | 2499 | 49.2 | 934.007916 |
| mas74.candidate.0 | feasible_limit | 13169.76915 | 11041.95011 | 0.1616 | 10482.794 | 0 | 0 | 0 | 0.009285 | 98302 | 313.0 | 11801.18573 |
| mas74.control.0 | feasible_limit | 12586.09998 | 11043.78495 | 0.1225 | 10482.794 | 0 | 0 | 0 | 0.01162 | 100744 | 320.3 | 11801.18573 |
| mas74.control.1 | feasible_limit | 13046.50896 | 11042.983 | 0.1536 | 10482.794 | 0 | 0 | 0 | 0.01155 | 99662 | 316.4 | 11801.18573 |
| mas74.candidate.1 | feasible_limit | 13087.46319 | 11042.02594 | 0.1563 | 10482.794 | 0 | 0 | 0 | 0.009091 | 98409 | 313.0 | 11801.18573 |
| gen-ip054.control.0 | feasible_limit | 6912.402426 | 6792.24431 | 0.01738 | 6765.2084 | 0 | 0 | 0 | 0.001596 | 186074 | 165.5 | 6840.966 |
| gen-ip054.candidate.0 | feasible_limit | 6886.311777 | 6792.258202 | 0.01366 | 6767.456 | 4 | 14 | 10 | 0.003522 | 177522 | 160.1 | 6840.966 |
| gen-ip054.candidate.1 | feasible_limit | 6886.311777 | 6792.049097 | 0.01369 | 6767.456 | 4 | 14 | 10 | 0.003384 | 169365 | 155.0 | 6840.966 |
| gen-ip054.control.1 | feasible_limit | 6912.402426 | 6792.081485 | 0.0174 | 6765.2084 | 0 | 0 | 0 | 0.001537 | 179363 | 161.5 | 6840.966 |
| neos859080.candidate.0 | terminal_status_crosschecked | - | - | - | 1 | 1 | 4 | 3 | - | 89 | 7.3 | infeasible |
| neos859080.control.0 | terminal_reference_pending | - | - | - | 1 | 0 | 0 | 0 | - | 93 | 7.8 | infeasible |
| neos859080.control.1 | terminal_reference_pending | - | - | - | 1 | 0 | 0 | 0 | - | 93 | 8.0 | infeasible |
| neos859080.candidate.1 | terminal_reference_pending | - | - | - | 1 | 1 | 4 | 3 | - | 89 | 7.2 | infeasible |
| danoint.control.0 | feasible_limit | 85.99999998 | 62.86235536 | 0.2659 | 62.637274 | 0 | 0 | 0 | 16.57 | 804 | 36.7 | 65.66666667 |
| danoint.candidate.0 | feasible_limit | 85.99999998 | 62.85854038 | 0.266 | 62.637274 | 0 | 0 | 0 | 17.88 | 760 | 36.8 | 65.66666667 |
| danoint.candidate.1 | feasible_limit | 85.99999998 | 62.86546777 | 0.2659 | 62.637274 | 0 | 0 | 0 | 16.08 | 845 | 37.0 | 65.66666667 |
| danoint.control.1 | feasible_limit | 85.99999998 | 62.87299383 | 0.2658 | 62.637274 | 0 | 0 | 0 | 15.31 | 952 | 36.9 | 65.66666667 |
| rout.candidate.0 | feasible_limit | 1154.68 | 998.9515237 | 0.1348 | 982.17276 | 4 | 10 | 6 | 2.159 | 15154 | 142.6 | 1077.56 |
| rout.control.0 | feasible_limit | 1131.72 | 998.7585034 | 0.1174 | 981.86419 | 0 | 0 | 0 | 0.3131 | 17653 | 169.6 | 1077.56 |
| rout.control.1 | feasible_limit | 1131.72 | 998.6998723 | 0.1174 | 981.86419 | 0 | 0 | 0 | 0.3287 | 16519 | 159.8 | 1077.56 |
| rout.candidate.1 | feasible_limit | 1154.68 | 998.8964146 | 0.1348 | 982.17276 | 4 | 10 | 6 | 1.88 | 14391 | 136.8 | 1077.56 |
| mas76.control.0 | feasible_limit | 40898.1417 | 39530.87734 | 0.03343 | 38893.9 | 0 | 0 | 0 | 0.007722 | 100721 | 319.3 | 40005.05414 |
| mas76.candidate.0 | feasible_limit | 40990.36687 | 39544.88067 | 0.03526 | 38893.9 | 0 | 0 | 0 | 0.007312 | 113226 | 356.6 | 40005.05414 |
| mas76.candidate.1 | feasible_limit | 40005.05414 | 39539.035 | 0.01165 | 38893.9 | 0 | 0 | 0 | 0.007804 | 107811 | 325.0 | 40005.05414 |
| mas76.control.1 | feasible_limit | 40966.14711 | 39541.94996 | 0.03476 | 38893.9 | 0 | 0 | 0 | 0.007387 | 110510 | 348.8 | 40005.05414 |

## Third fresh untouched holdout, 10 MIPLIB 3 models

| Run | Category | Objective | Bound | Gap | Root after cuts | Cuts | Gomory applied | Purged | First point s | Nodes | Peak commit MiB | Published |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| air04.control.0 | feasible_limit | 57528 | 55678 | 0.03216 | 55536 | 0 | 0 | 0 | 6.355 | 67 | 33.9 | - |
| air04.candidate.0 | feasible_limit | 57528 | 55666 | 0.03237 | 55536 | 0 | 0 | 0 | 6.202 | 61 | 33.7 | - |
| arki001.candidate.0 | no_incumbent_limit | - | 7579731.751 | - | 7579599 | 0 | 0 | 0 | - | 1630 | 140.8 | - |
| arki001.control.0 | no_incumbent_limit | - | 7579731.751 | - | 7579599 | 0 | 0 | 0 | - | 1608 | 140.2 | - |
| dano3mip.control.0 | no_incumbent_limit | - | - | - | - | 0 | 0 | 0 | - | 1 | 86.4 | - |
| dano3mip.candidate.0 | no_incumbent_limit | - | - | - | - | 0 | 0 | 0 | - | 1 | 65.1 | - |
| gen.candidate.0 | numerical_completion_checked | 112313.3627 | 112313.3515 | 9.999e-08 | 112313.35 | 20 | 34 | 31 | 0.1067 | 1 | 2.8 | - |
| gen.control.0 | numerical_completion_checked | 112313.3627 | 112313.3515 | 1e-07 | 112312.58 | 18 | 0 | 0 | 0.06885 | 19 | 2.8 | - |
| markshare1.control.0 | feasible_limit | 43.99999997 | -1.000000009e-07 | 0.9778 | -1e-07 | 0 | 0 | 0 | 0.001408 | 340272 | 441.9 | - |
| markshare1.candidate.0 | feasible_limit | 32 | -1.000000009e-07 | 0.9697 | -1e-07 | 5 | 14 | 9 | 0.004956 | 277534 | 310.0 | - |
| markshare2.candidate.0 | feasible_limit | 84.99999996 | -1.000000009e-07 | 0.9884 | -1e-07 | 5 | 15 | 10 | 0.01469 | 210518 | 326.0 | - |
| markshare2.control.0 | feasible_limit | 60.99999997 | -1.000000009e-07 | 0.9839 | -1e-07 | 0 | 0 | 0 | 0.001862 | 266624 | 390.3 | - |
| mkc.control.0 | feasible_limit | -478.83 | -611.3593253 | 0.2762 | -611.35933 | 27 | 0 | 0 | 3.175 | 2996 | 272.8 | - |
| mkc.candidate.0 | feasible_limit | -431.268 | -603.8562326 | 0.3993 | -603.85623 | 64 | 79 | 51 | 4.001 | 2684 | 245.4 | - |
| rentacar.candidate.0 | no_incumbent_limit | - | 28928376.73 | - | 28928377 | 6 | 8 | 2 | - | 2 | 304.3 | - |
| rentacar.control.0 | no_incumbent_limit | - | 28928376.73 | - | 28928377 | 0 | 0 | 0 | - | 147 | 151.0 | - |
| seymour.control.0 | no_incumbent_limit | - | 406 | - | 404 | 0 | 0 | 0 | - | 144 | 95.0 | - |
| seymour.candidate.0 | no_incumbent_limit | - | 407 | - | 406 | 7 | 36 | 29 | - | 76 | 110.2 | - |
| swath.candidate.0 | feasible_limit | 633.899081 | 378.475399 | 0.4023 | 373.36764 | 46 | 28 | 10 | 2.769 | 1687 | 187.7 | - |
| swath.control.0 | feasible_limit | 685.595576 | 350.0438683 | 0.4887 | 334.49682 | 0 | 0 | 0 | 2.223 | 3884 | 379.3 | - |

