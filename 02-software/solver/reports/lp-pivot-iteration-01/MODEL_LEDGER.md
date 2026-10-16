# Complete final-executable validation ledger

Both opt-in LP profiles, retained default failures, compact control and unchanged-QP checks.

| Model/profile | Status | Objective | Pivots/iterations | Abs. violation | Scaled violation | Checked completion | RSS MiB |
|---|---|---:|---:|---:|---:|---|---:|
| adlittle.stable | optimal | 225494.9632 | 191 | 4.547473509e-13 | 6.676898767e-15 | True | 1.89453125 |
| adlittle.stable_refined | optimal | 225494.9632 | 191 | 1.136868377e-13 | 9.504197764e-17 | True | 5.453125 |
| afiro.stable | optimal | -464.7531429 | 17 | 5.684341886e-14 | 1.798065157e-16 | True | 1.890625 |
| afiro.stable_refined | optimal | -464.7531429 | 17 | 4.263256415e-14 | 8.990325784e-17 | True | 1.8984375 |
| blend.stable | optimal | -30.81214985 | 162 | 1.023181539e-12 | 1.058844471e-14 | True | 5.4765625 |
| blend.stable_refined | optimal | -30.81214985 | 162 | 2.842170943e-14 | 1.622336767e-16 | True | 1.88671875 |
| boeing2.stable | optimal | -315.018728 | 261 | 3.836930773e-13 | 2.385241948e-13 | True | 5.59765625 |
| boeing2.stable_refined | optimal | -315.018728 | 261 | 1.136868377e-13 | 9.276098882e-17 | True | 5.43359375 |
| degen2.stable | optimal | -1435.178 | 2949 | 4.440892099e-16 | 7.401486831e-17 | True | 15.76953125 |
| degen2.stable_refined | optimal | -1435.178 | 2949 | 4.440892099e-16 | 7.401486831e-17 | True | 15.71484375 |
| kb2.stable | optimal | -1749.90013 | 96 | 3.183231456e-12 | 4.990716835e-15 | True | 1.88671875 |
| kb2.stable_refined | optimal | -1749.90013 | 96 | 9.094947018e-13 | 1.331084212e-16 | True | 1.890625 |
| sc105.stable | optimal | -52.20206121 | 115 | 2.273736754e-13 | 6.488206027e-15 | True | 1.88671875 |
| sc105.stable_refined | optimal | -52.20206121 | 115 | 2.842170943e-14 | 1.012997519e-16 | True | 1.88671875 |
| sc205.stable | optimal | -52.20206121 | 263 | 2.273736754e-12 | 1.433332212e-12 | True | 6.0078125 |
| sc205.stable_refined | optimal | -52.20206121 | 263 | 2.273736754e-13 | 1.413866782e-16 | True | 5.71875 |
| sc50a.stable | optimal | -64.57507706 | 49 | 1.136868377e-13 | 1.893562862e-16 | True | 1.90625 |
| sc50a.stable_refined | optimal | -64.57507706 | 49 | 5.684341886e-14 | 1.044089254e-16 | True | 1.88671875 |
| sc50b.stable | optimal | -70 | 54 | 1.136868377e-13 | 3.853791109e-16 | True | 1.9140625 |
| sc50b.stable_refined | optimal | -70 | 54 | 2.842170943e-14 | 1.08938847e-16 | True | 1.8828125 |
| share2b.stable | optimal | -415.7322407 | 212 | 4.547473509e-13 | 4.889368324e-14 | True | 5.0390625 |
| share2b.stable_refined | optimal | -415.7322407 | 212 | 4.547473509e-13 | 4.889368324e-14 | True | 5.16015625 |
| stocfor1.stable | optimal | -41131.97622 | 143 | 2.273736754e-12 | 1.511041747e-14 | True | 5.234375 |
| stocfor1.stable_refined | optimal | -41131.97622 | 143 | 9.094947018e-13 | 9.945099502e-17 | True | 5.23828125 |
| agg.stable | optimal | -35991767.29 | 152 | 5.413312465e-09 | 5.279927376e-15 | True | 6.60546875 |
| agg.stable_refined | optimal | -35991767.29 | 152 | 1.164153218e-10 | 1.093562315e-16 | True | 6.1328125 |
| bandm.stable | optimal | -158.6280185 | 3254 | 7.995826223e-13 | 2.108774995e-15 | True | 19.4140625 |
| bandm.stable_refined | optimal | -158.6280185 | 3254 | 1.421085472e-13 | 2.571607831e-16 | True | 19.36328125 |
| israel.stable | optimal | -896644.8219 | 393 | 1.164153218e-10 | 5.470247026e-13 | True | 5.8359375 |
| israel.stable_refined | optimal | -896644.8219 | 393 | 1.022271157e-11 | 1.807553807e-16 | True | 5.67578125 |
| scagr7.stable | optimal | -2331389.824 | 384 | 7.275957614e-12 | 7.270705024e-16 | True | 5.8359375 |
| scagr7.stable_refined | optimal | -2331389.824 | 384 | 9.094947018e-13 | 1.036808857e-16 | True | 5.8359375 |
| bandm.control | numerical_error | — | 200 | — | — | False | 6.59375 |
| bandm.control_refined | numerical_error | — | 200 | — | — | False | 6.8203125 |
| bandm.compact | optimal | -158.6280185 | 1279 | 1.421085472e-13 | 2.571607831e-16 | True | 8.6015625 |
| 8792.default | optimal | 3593.516294 | 50 | 1.110223025e-16 | 4.706585819e-17 | True | 11.16015625 |
| 8991.default | optimal | -0.001667867362 | 25 | 0 | 0 | True | 11.0546875 |
| 9002.default | optimal | 5698097499 | 180 | 2.381022491 | 8.5718305e-08 | True | 6.41796875 |
