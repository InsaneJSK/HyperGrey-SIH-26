# Immediate compact equality experiment — not promoted

Separate build `build-milp-iter9`, CLI SHA256
`d65d6327b2972d5cf4afd8deddbe165eedd506b5415f75a561217a2e84f7f132`.
Preserved as `direct-source/` and `direct_solver_cli.exe` before implementing
the delayed-activation variant.

The one-node Binkar screen reaches the same lower bound 6645.940875 with
1016 fewer canonical LP rows: 3342 rather than 4358 after the retained root
cuts. It takes 7.192s versus 10.710s, with no compact fallback. This is one
root screen, not proof of full-solve acceleration.

The 180s full comparison retains the same delayed-cut strategy in both modes:

| Mode | Objective | Lower bound | Reported gap | Seconds | Nodes |
|---|---:|---:|---:|---:|---:|
| Ordinary LP control | 6747.310015 | 6682.348919 | 0.96263% | 180.221 | 4337 |
| Immediate compact LP | 6772.830019 | 6682.077832 | 1.33975% | 180.365 | 4735 |

Both time out. More nodes do not compensate for the worse incumbent. P0033
remains optimal at 3089 in both modes (277 nodes, 0.122/0.133s). The immediate
mode is not a default or a claimed full-solve improvement.

CTest 7/7 and generated 240/240 pass. The independent audit checks all 48
retained lifted cuts across the pair, 15 available final/restart/neighborhood
vectors and 77 timing-source hashes. The original-literal Markshare exact
proof sentinel still passes. This establishes the stated checks, not Binkar
optimality or independently exact general LP bounds.

Evidence: `root-screen/`, `paired-180s/`, `direct-audit/AUDIT.json`.
The next variant preserves the earlier LP representation during incumbent
search and activates compact equalities only at the full-domain cut restart.
