# Current-source LP and QP revalidation

Declared before these new measurements, after implementing the opt-in private
certificate candidate. Run only after the MILP correctness gate and repeated
screen have finished. No timed solver configurations overlap.

Use the exact iteration29 executable; preserve its hash and source snapshot.
The private MILP option has no role in these LP/QP calls. This study refreshes
retained coverage; it does not turn reused inputs into holdouts.

LP: all twelve entries of `datasets/netlib/manifest.json`, in manifest order,
one run each with default sparse settings and one with `--refine-basis
--refine-at-checks`. Thirty seconds and existing 10000-pivot cap per run;
forty-five-second process watchdog. Keep input hashes and compare original
points, objective reconstruction and numerical completion to an independent
HiGHS solve with 1e-8 primal/dual feasibility tolerances, one thread, thirty
seconds. Own LP tolerance stays 1e-9. This is correctness revalidation, not an
equal-accuracy speed ranking.

QP: original QPLIB 8792, 8991, 9002, one default thirty-second solve each,
independent original-model KKT and applicable diagonal dual-gap checks at
1e-7, followed by the existing thirty-second OSQP protocol on original data.
Retain export-audit differences and every reference timeout. Report absolute
and relative residuals separately; no operational acceptance is inferred from
a relative residual alone.

After default QP results, run separately labeled 9002 tolerance probes at
1e-10 and 1e-12, each at the same thirty-second limit, to examine whether
tighter solver tolerances improve absolute feasibility. A probe is not the
selected profile and does not replace a failed default result. Do not choose
an application tolerance without domain units/requirements.

Gate: all reported completed LP points and QP results must satisfy the stated
original-model check. Classify limit/numerical outcomes honestly; save raw
stdout/stderr, commands, versions and sampled process RSS/commit memory.
Failures become the next focused LP/QP hypotheses before breadth/performance
claims. Fresh LP/QP datasets, actual GPU evidence and industrial expert review
remain separate work.

## Additional LP selection, before these solve outcomes

Add `agg`, `bandm`, `israel`, `scagr7` from the official Netlib archive. These
are absent from the current local dataset inventory. Keep their results
separate from the12 retained LPs, with the same default/refined profiles and
budgets above. Four additional small public models are not broad industrial
scalability evidence or proof of ill-conditioning coverage.

Download raw data and the archive README after the MILP timed screen. Verify
the retained EMPS C utility's source hash against the original Netlib manifest,
compile that data decoder locally, and save raw/decoded hashes and provenance.
Read the published objective table only as dataset documentation; independently
solve and check original coefficients afterward. No answer enters the engine.
Source: https://netlib.org/lp/data/readme
