# Preserved direct-cut experiment — not promoted

15 September2026, local CPU. The root-only prototype build-milp-iter8 improved
Binkar's numerical root lower bound from6645.940875 to6662.930958. Initial
uncut bound6637.187363; root-only total times11.02/11.28s. The29 retained cuts
all passed independent exhaustive row checks. This did not establish a full
solver improvement. Prototype source/binary and root-screen-02 remain saved.

The resource-guarded direct build-milp-iter8b then ran one sequential180s pair
per model, references afterward:

| Model | Mode | Objective | Final bound | Gap | Solve seconds |
|---|---|---:|---:|---:|---:|
| Binkar | Guided | 6747.310015 | 6665.032821 | 1.21923% | 181.04 |
| Binkar | Direct lifted cuts | 6775.200015 | 6681.847909 | 1.37765% | 180.47 |
| P0033 | Guided | 3089 | 3089 | 0 | 0.118 |
| P0033 | Direct lifted cuts | 3089 | 3089 | 0 | 1.710 |

The Binkar bound improved but its incumbent and reported gap regressed. P0033
needed fewer nodes (95 versus277) but took longer because enumeration cost
dominated. Neither result justifies default promotion. The nominal time limit
is cooperative: measured overruns are preserved, not rounded down to180.

CTest6/6 and240 generated checks pass. The C++ separator test exhaustively
checks400 signed/dyadic row models, producing391 verified cuts. Independent
public checks confirm47 retained cuts and all four final candidates. The
[additional audit](direct-audit/AUDIT.json) confirms16 final/intermediate points,
all cut proofs, run/trace accounting and73 timing-source identities. Generated
random cases exported no new cuts; their role is fallback/general solver
regression, not cut-coverage evidence. Cut-specific evidence is the exhaustive
C++ cases and public retained cuts.

HiGHS30s on Binkar still times out with6746.760023; it does not establish an
optimum. It independently proves p0033's numerical3089. Markshare's exact-proof
sentinel passes. Guided numerical outputs match iteration07 on80 generated
models. CLI SHA256:
`043cd98773db3597dc9b434ebe700b18511ea878e24edfd22068515bb0b497b3`.

Data: [protocol](local-180s/metadata.json), [raw results](local-180s/results.json),
[summary](local-180s/summary.json), [cut checks](local-180s/cut_checks.json).
Source is in direct-source/ and executable in direct_solver_cli.exe. This
snapshot predates the delayed restart; don't mix its metadata with that build.

The first root-screen folder contains only a failed regression gate: the initial
integration test accidentally used an already integral LP optimum, so it did
not exercise separation. The objective was corrected before any root timing.
A later restart test's first node trigger preceded the first incumbent; its
trigger was corrected to a deterministic sixth node before delayed public runs.
Neither test adjustment changed feasibility tolerances or accepted bad outputs.
