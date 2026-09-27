# Control versus candidate by model

Each cell: status / objective / gap, one line per repeat.

## Development, 27 reused models, two repeats per profile

| Model | Control | Candidate | Root bound C -> K | Published |
|---|---|---|---|---:|
| p0033 | done / 3089 / 0<br>done / 3089 / 0 | done / 3089 / 0<br>done / 3089 / 0 | - | 3089 |
| enigma | done / 0 / 4.94e-324<br>done / 0 / 4.94e-324 | done / 0 / 4.94e-324<br>done / 0 / 4.94e-324 | -4.9406565e-324 -> -4.9406565e-324 (same)<br>-4.9406565e-324 -> -4.9406565e-324 (same) | 0 |
| flugpl | done / 1201500 / 1e-07<br>done / 1201500 / 1e-07 | done / 1201500 / 1e-07<br>done / 1201500 / 1e-07 | 1167185.6 -> 1171918.6 (better)<br>1167185.6 -> 1171918.6 (better) | 1201500 |
| stein27 | done / 18 / 1.87e-16<br>done / 18 / 1.87e-16 | done / 18 / 1.87e-16<br>done / 18 / 1.87e-16 | 13 -> 13 (same)<br>13 -> 13 (same) | 18 |
| markshare_4_0 | done / 1 / 0<br>done / 1 / 0 | done / 1 / 0<br>done / 1 / 0 | - | 1 |
| blend2 | gap_limit / 7.598985 / 1e-07<br>gap_limit / 7.598985 / 1e-07 | gap_limit / 7.598985 / 1e-07<br>gap_limit / 7.598985 / 1e-07 | 6.9156743 -> 7.0249011 (better)<br>6.9156743 -> 7.0249011 (better) | 7.598985 |
| binkar10_1 | time_limit / 6762.08 / 0.0112<br>time_limit / 6762.08 / 0.0113 | time_limit / 6762.94 / 0.0101<br>time_limit / 6762.94 / 0.0104 | 6662.931 -> 6672.2557 (better)<br>6662.931 -> 6672.2557 (better) | 6742.200024 |
| egout | done / 568.1007 / 0<br>done / 568.1007 / 0 | done / 568.1007 / 0<br>done / 568.1007 / 0 | 367.08485 -> 528.54782 (better)<br>367.08485 -> 528.54782 (better) | 568.1007 |
| gt2 | node_limit / 35409 / 0.605<br>time_limit / 35409 / 0.605 | time_limit / 32143 / 0.425<br>time_limit / 32143 / 0.425 | 13461 -> 18344 (better)<br>13461 -> 18344 (better) | 21166 |
| lseu | done / 1120 / 2.03e-16<br>done / 1120 / 2.03e-16 | done / 1120 / 2.03e-16<br>done / 1120 / 2.03e-16 | 1000 -> 1028 (better)<br>1000 -> 1028 (better) | 1120 |
| mod008 | done / 307 / 1.85e-16<br>done / 307 / 1.85e-16 | done / 307 / 1.85e-16<br>done / 307 / 1.85e-16 | 292 -> 292 (same)<br>292 -> 292 (same) | 307 |
| p0201 | done / 7615 / 1.19e-16<br>done / 7615 / 1.19e-16 | done / 7615 / 1.19e-16<br>done / 7615 / 1.19e-16 | 7125 -> 7265 (better)<br>7125 -> 7265 (better) | 7615 |
| p0282 | time_limit / 258411 / 0.0475<br>time_limit / 258411 / 0.0474 | time_limit / 266359 / 0.126<br>time_limit / 282043 / 0.174 | 226637 -> 213581 (worse)<br>226637 -> 213581 (worse) | 258411 |
| misc03 | done / 3360 / 0<br>done / 3360 / 0 | done / 3360 / 1.35e-16<br>done / 3360 / 1.35e-16 | 1910 -> 1995 (better)<br>1910 -> 1995 (better) | 3360 |
| misc07 | time_limit / 2810 / 0.0658<br>time_limit / 2810 / 0.0729 | time_limit / 2810 / 0.0694<br>time_limit / 2810 / 0.0623 | 1415 -> 1415 (same)<br>1415 -> 1415 (same) | 2810 |
| pk1 | time_limit / 16 / 0.486<br>time_limit / 16 / 0.486 | time_limit / 12 / 0.352<br>time_limit / 12 / 0.372 | -1e-07 -> -1e-07 (same)<br>-1e-07 -> -1e-07 (same) | 11 |
| rgn | done / 82.199999 / 1.02e-07<br>done / 82.199999 / 1.02e-07 | done / 82.199999 / 9.98e-08<br>done / 82.199999 / 9.98e-08 | 48.799994 -> 52.76446 (better)<br>48.799994 -> 52.76446 (better) | 82.19999924 |
| gen-ip002 | time_limit / -4731.7166 / 0.0167<br>time_limit / -4747.4863 / 0.0133 | time_limit / -4723.6559 / 0.0185<br>time_limit / -4722.3794 / 0.0189 | -4840.5424 -> -4839.2991 (better)<br>-4840.5424 -> -4839.2991 (better) | -4783.733392 |
| assign1-5-8 | time_limit / 213 / 0.104<br>time_limit / 214 / 0.106 | time_limit / 212 / 0.0983<br>time_limit / 213 / 0.102 | 183.36254 -> 183.36254 (same)<br>183.36254 -> 183.36254 (same) | 212 |
| lotsize | time_limit / - / -<br>time_limit / - / - | time_limit / - / -<br>time_limit / - / - | 348385.31 -> 407728.14 (better)<br>348385.31 -> 407728.14 (better) | 1480195 |
| eil33-2 | time_limit / 987.67413 / 0.103<br>time_limit / 987.67413 / 0.106 | time_limit / 987.67413 / 0.103<br>time_limit / 987.67413 / 0.104 | 811.27891 -> 811.27891 (same)<br>811.27891 -> 811.27891 (same) | 934.007916 |
| mas74 | time_limit / 12586.1 / 0.123<br>time_limit / 13046.509 / 0.154 | time_limit / 13169.769 / 0.162<br>time_limit / 13087.463 / 0.156 | 10482.794 -> 10482.794 (same)<br>10482.794 -> 10482.794 (same) | 11801.18573 |
| gen-ip054 | time_limit / 6912.4024 / 0.0174<br>time_limit / 6912.4024 / 0.0174 | time_limit / 6886.3118 / 0.0137<br>time_limit / 6886.3118 / 0.0137 | 6765.2084 -> 6767.456 (better)<br>6765.2084 -> 6767.456 (better) | 6840.966 |
| neos859080 | infeasible / - / -<br>infeasible / - / - | done / - / -<br>infeasible / - / - | 1 -> 1 (same)<br>1 -> 1 (same) | infeasible |
| danoint | time_limit / 86 / 0.266<br>time_limit / 86 / 0.266 | time_limit / 86 / 0.266<br>time_limit / 86 / 0.266 | 62.637274 -> 62.637274 (same)<br>62.637274 -> 62.637274 (same) | 65.66666667 |
| rout | time_limit / 1131.72 / 0.117<br>time_limit / 1131.72 / 0.117 | time_limit / 1154.68 / 0.135<br>time_limit / 1154.68 / 0.135 | 981.86419 -> 982.17276 (better)<br>981.86419 -> 982.17276 (better) | 1077.56 |
| mas76 | time_limit / 40898.142 / 0.0334<br>time_limit / 40966.147 / 0.0348 | time_limit / 40990.367 / 0.0353<br>time_limit / 40005.054 / 0.0116 | 38893.9 -> 38893.9 (same)<br>38893.9 -> 38893.9 (same) | 40005.05414 |

control: 22 completions, 50 checked points, 0 validation failures. candidate: 23 completions, 50 checked points, 0 validation failures.
Root bound: candidate better on 26, worse on 2, unchanged on 22 paired observations.

## Third fresh untouched holdout, 10 MIPLIB 3 models

| Model | Control | Candidate | Root bound C -> K | Published |
|---|---|---|---|---:|
| air04 | time_limit / 57528 / 0.0322 | time_limit / 57528 / 0.0324 | 55536 -> 55536 (same) | - |
| arki001 | time_limit / - / - | time_limit / - / - | 7579599 -> 7579599 (same) | - |
| dano3mip | time_limit / - / - | time_limit / - / - | - | - |
| gen | done / 112313.36 / 1e-07 | done / 112313.36 / 1e-07 | 112312.58 -> 112313.35 (better) | - |
| markshare1 | time_limit / 44 / 0.978 | time_limit / 32 / 0.97 | -1e-07 -> -1e-07 (same) | - |
| markshare2 | time_limit / 61 / 0.984 | time_limit / 85 / 0.988 | -1e-07 -> -1e-07 (same) | - |
| mkc | time_limit / -478.83 / 0.276 | time_limit / -431.268 / 0.399 | -611.35933 -> -603.85623 (better) | - |
| rentacar | time_limit / - / - | time_limit / - / - | 28928377 -> 28928377 (same) | - |
| seymour | time_limit / - / - | time_limit / - / - | 404 -> 406 (better) | - |
| swath | time_limit / 685.59558 / 0.489 | time_limit / 633.89908 / 0.402 | 334.49682 -> 373.36764 (better) | - |

control: 1 completions, 6 checked points, 0 validation failures. candidate: 1 completions, 6 checked points, 0 validation failures.
Root bound: candidate better on 4, worse on 0, unchanged on 5 paired observations.

