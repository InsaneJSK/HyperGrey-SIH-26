# Timing caveat observed during the paired wave

The current desktop was not a controlled idle benchmark host. During the wave,
a one-time Windows performance snapshot reported73% aggregate CPU utilization;
a short process-delta diagnostic showed the active solver plus several Code,
PowerShell and webview processes consuming CPU. No other user's process,
power plan or background task was stopped or modified.

The egout lattice runs in iterations12 and13 have IDENTICAL counts:3827 nodes,
15627 LP iterations,386 heuristic solves and4172 warm starts, but elapsed times
2.46s and7.22s respectively. This establishes a large elapsed-time difference
without a search-work-count difference; it does not isolate its cause. Desktop
load, CPU operating conditions and build-level effects are not controlled.

Two read-only CPU diagnostics were performed while the lseu/mod008 portion of
the wave was running. They are an additional source of interference, so those
single pairs must not be presented as clean speed measurements. Keep all runs;
do not delete or silently replace slower outcomes. The planned fixed-node
screen is reproducible and independent of wall-clock comparisons when its node
cap is reached. Repeated30s experiments are also retained, with this shared-host
caveat. No claim of a universal speedup or equivalence to prior idle timings.
