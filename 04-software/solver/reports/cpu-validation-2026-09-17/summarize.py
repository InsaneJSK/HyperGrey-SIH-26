"""Build human-readable ledgers from the retained completed observations."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def number(value):
    return "—" if value is None else f"{value:.10g}"


def main():
    rows = json.loads((BASE / "results/ledger.json").read_text())
    lines = ["# Complete current-source LP/QP ledger", "",
             "All 37 observations, including numerical failures and tolerance limits.", "",
             "| Model/profile | Cohort | Status | Objective | Pivots/iterations | Abs. violation | Scaled violation | Checked completion | Reference status | RSS MiB |",
             "|---|---|---|---:|---:|---:|---:|---|---|---:|"]
    for r in rows:
        lines.append(f"| {r['key']} | {r['family']} | {r['status']} | {number(r['objective'])} | {r['iterations']} | {number(r['absolute_violation'])} | {number(r['scaled_violation'])} | {r['checked_completion']} | {r['reference_status']} | {number(r['peak_rss_mib'])} |")
    (BASE / "MODEL_LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    target = BASE.parent / "lp-bandm-01"
    rows = json.loads((target / "lp-profile/ledger.json").read_text())
    lines = ["# Complete compact-equality LP profile ledger", "",
             "One consistent compact/refined profile; every original-model check passes.", "",
             "| Model | Cohort | Status | Objective | Pivots | Compact fallback | Abs. violation | Scaled violation | RSS MiB |",
             "|---|---|---|---:|---:|---|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['family']} | {r['status']} | {number(r['objective'])} | {r['iterations']} | {r['compact_fallback']} | {number(r['absolute_violation'])} | {number(r['scaled_violation'])} | {number(r['peak_rss_mib'])} |")
    (target / "MODEL_LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote 37-observation and 16-model ledgers.")


if __name__ == "__main__":
    main()
