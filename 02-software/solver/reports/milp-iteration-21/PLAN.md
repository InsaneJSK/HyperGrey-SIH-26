# Iteration 21 — private distance-objective dive

Declared before public measurements. CPU local, no GPU/upload needed.

Hypothesis: iteration20's first original-objective dive LP loses the pump's
near-integer progress. A private L1 objective around the rounded best seed may
retain useful proximity and reach an integer solution. This does not promise
monotone nearest-integer distance or feasibility of the rounded target.

The single change is optional `--pump-distance-diving`, requiring existing
`--pump-guided-diving`. Both default off. Existing pump, dive (shared at most
two seconds, 64 steps per mode), repair, node, restart and cut budgets stay
unchanged. The second dive remains original-objective. No model-name rules,
reference incumbents, proof-bound import or new batch fixing. Private distance
bases start cold and are reused only within that model; auxiliaries and dual
bounds are removed at the point-only boundary. Original validation is unchanged.

Before timings: C++/Python gates, generated MIN/MAX/binary/mixed exhaustive
comparisons, existing numerical repair fixture, frozen20 disabled-option parity
with guidance both on/off and no-pump/no-heuristics inertness. Four root-only
public runs must exercise the actual distance path, not merely enable a flag.

SCREEN.json: eight predeclared models, two alternating pairs each (32 runs),
30 seconds each, original guided control versus distance candidate. Includes
the three no-point targets, blend2 repair, p0201 completion, rout variability,
gt2's repeated improvement and pk1's earlier regression. Detailed trace both.
WAVE.json: same pair over all 27 development models, once each (54 runs), same
30 seconds, trace off both. Own measured solves sequential; references follow.
Shared-desktop timing and time-triggered behavior may vary. No fresh holdout.

Primary: checked final solutions, completions, objective/gap regressions and
failures. Secondary: first/last distance, private LP work, first incumbent and
node throughput. A good distance metric alone is not success. Preserve all raw
results, failures and original reference timeouts. A terminal reference timeout
may receive a separately labeled longer reference, never an extended own run.

No default promotion on isolated gains. Do not tune again on these results
within this iteration. Freeze the tested source, reports and binary; preserve20.
This is the agreed three-iteration checkpoint (19–21): reassess the ten-iteration
planning budget honestly; 27/27 optimality and top-0.1% placement are not promises.
