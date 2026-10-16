#!/usr/bin/env python3
"""Rebuild the README benchmark SVGs from retained JSON (Python standard library)."""

from html import escape
from pathlib import Path
from statistics import median
import json
import math


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPORTS = ROOT / "02-software/solver/reports"
BG, CARD, GRID, INK, MUTED = "#0b1220", "#111d30", "#27354b", "#eef4ff", "#a8b7cc"
TEAL, GOLD, PURPLE, AMBER = "#42ddca", "#ffc665", "#a99eff", "#ebba77"


class Svg:
    def __init__(self, title, description):
        self.items = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="940" viewBox="0 0 1600 940" role="img" aria-labelledby="title description">',
            f"<title id=\"title\">{escape(title)}</title>",
            f"<desc id=\"description\">{escape(description)}</desc>",
            '<style>text{font-family:Arial,Helvetica,sans-serif} .mono{font-family:Menlo,Consolas,monospace}</style>',
        ]
        self.rect(0, 0, 1600, 940, BG)

    def rect(self, x, y, w, h, fill, radius=0):
        self.items.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="{fill}"/>')

    def text(self, x, y, value, size=22, color=INK, weight=400, anchor="start", **attrs):
        extra = " ".join(f'{escape(k)}="{escape(str(v))}"' for k, v in attrs.items())
        self.items.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=GRID, width=1, dash=None):
        attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="{width}"{attr}/>')

    def path(self, points, color, width=4):
        data = " ".join(f"{'M' if i == 0 else 'L'} {x:.3f} {y:.3f}" for i, (x, y) in enumerate(points))
        self.items.append(f'<path d="{data}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in points:
            self.items.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="6" fill="{color}" stroke="{CARD}" stroke-width="2"/>')

    def save(self, filename):
        (HERE / filename).write_text("\n".join(self.items + ["</svg>"]) + "\n", encoding="utf-8")


def gpu_chart():
    report = REPORTS / "kaggle-gpu-03/returned"
    rows = json.loads((report / "results.json").read_text())
    summary = json.loads((report / "SUMMARY.json").read_text())
    sizes = summary["sizes"]
    backends = [("cpu", 1, "CPU · 1 thread", GOLD), ("cpu", 4, "CPU · 4 threads", PURPLE), ("cuda", 1, "CUDA · Tesla T4", TEAL)]
    assert len(rows) == summary["records"] == 45
    assert summary["passed"] == 45 and all(r["passed"] and r["status"] == "optimal" for r in rows)
    medians = {}
    for backend, threads, _, _ in backends:
        for n in sizes:
            samples = [r["solve_seconds"] for r in rows if r["columns"] == n and r["backend"] == backend and r["threads"] == threads]
            assert len(samples) == 3
            value = median(samples)
            assert math.isclose(value, summary["per_size"][str(n)][f"{backend}:{threads}"]["median_solve_seconds"], rel_tol=1e-12)
            medians[backend, threads, n] = value

    svg = Svg("CPU and Tesla T4 median solve times on synthetic box QP", "Three repeats per size and backend, 45 checked runs. Synthetic planted tridiagonal box-constrained convex QP. Median solve time includes solver setup and CUDA transfers; whole-process startup and model generation are separate.")
    svg.text(64, 65, "SOLVEFORGE  /  RECORDED PERFORMANCE", 18, TEAL, 700, **{"letter-spacing": "2"})
    svg.text(64, 124, "GPU acceleration, measured across problem sizes", 39, INK, 700)
    svg.text(64, 167, "Synthetic sparse box-constrained convex QP · Tesla T4 · median of 3 repeats", 24, MUTED)
    svg.rect(58, 207, 1484, 540, CARD, 20)
    for i, (_, _, label, color) in enumerate(backends):
        x = 90 + i * 365
        svg.line(x, 248, x + 38, 248, color, 5)
        svg.text(x + 54, 256, label, 22, INK, 600)

    left, right, top, bottom = 151, 1240, 301, 638
    x = lambda n: left + math.log10(n / sizes[0]) / math.log10(sizes[-1] / sizes[0]) * (right - left)
    y = lambda t: bottom - math.log10(t / .05) / math.log10(20 / .05) * (bottom - top)
    svg.text(91, 286, "Median solve time · seconds", 19, MUTED)
    for value in (.1, .2, .5, 1, 2, 5, 10, 20):
        yy = y(value)
        svg.line(left, yy, right, yy)
        svg.text(left - 18, yy + 6, f"{value:g}", 18, MUTED, anchor="end")
    for n, label in zip(sizes, ("10k", "50k", "200k", "500k", "1m")):
        xx = x(n)
        svg.line(xx, top, xx, bottom, GRID, 1, "3 7")
        svg.text(xx, 674, label, 20, MUTED, anchor="middle")
    svg.text((left + right) / 2, 717, "Variables · logarithmic axes · lower is faster", 20, MUTED, anchor="middle")
    for backend, threads, label, color in backends:
        points = [(x(n), y(medians[backend, threads, n])) for n in sizes]
        svg.path(points, color)
        value = medians[backend, threads, sizes[-1]]
        svg.text(right + 24, y(value) + 6, f"{value:.3f} s", 24, color, 700)

    ratio = medians["cpu", 1, sizes[-1]] / medians["cuda", 1, sizes[-1]]
    svg.rect(60, 773, 550, 98, "#163634", 14)
    svg.text(85, 811, f"{ratio:.2f}× at 1 million variables", 28, TEAL, 700)
    svg.text(85, 844, "T4 versus 1 CPU thread · same accuracy checks", 18, MUTED)
    svg.text(647, 810, "45 / 45 runs passed the declared accuracy checks", 25, INK, 600)
    svg.text(647, 847, "Setup + CUDA transfers included; process startup excluded.", 20, MUTED)
    svg.text(64, 911, "Source: kaggle-gpu-03 · 18 Sep 2026 · one planted family, one device/session", 18, MUTED)
    svg.save("box-qp-cpu-gpu-t4-medians.svg")
    return medians


def miplib_chart():
    data = json.loads((REPORTS / "miplib2017-benchmark/SUMMARY.json").read_text())
    total = data["instances"]
    optimal, infeasible = data["proven_optimal"], data["proven_infeasible"]
    feasible = data["validated_points_including_optima"] - optimal
    unresolved = data["no_point"]
    assert total == 240 and optimal + infeasible + feasible + unresolved == total
    rejected, disagreement = len(data["rejected_points"]), len(data["disagreeing_with_published"])
    assert rejected == disagreement == 0 and data["budget_seconds"] == 300

    svg = Svg("Historical MIPLIB 2017 outcomes for 240 instances", "Frozen historical solver at a 300-second per-instance cap: 7 numerical optima, 62 other independently checked feasible points, 1 proven infeasible, and 170 with no feasible point recorded. The 69 validated points include the 7 optima; outcomes are not double-counted. No returned points rejected and no disagreements with published results.")
    svg.text(64, 65, "SOLVEFORGE  /  PUBLIC BENCHMARK AUDIT", 18, TEAL, 700, **{"letter-spacing": "2"})
    svg.text(64, 124, "240 public MILP instances. Every returned point checked.", 38, INK, 700)
    svg.text(64, 167, "MIPLIB 2017 · frozen historical engine · 300-second cap per instance", 24, MUTED)
    for i, (number, label, color) in enumerate(((69, "Checked feasible points", TEAL), (7, "Numerical optima included", GOLD), (rejected, "Rejected returned points", INK), (disagreement, "Published-result disagreements", INK))):
        xx = 60 + i * 375
        svg.rect(xx, 207, 357, 122, CARD, 16)
        svg.text(xx + 23, 263, number, 42, color, 700)
        svg.text(xx + 23, 303, label, 19, MUTED)

    svg.rect(60, 357, 1480, 409, CARD, 20)
    svg.text(90, 400, "Mutually exclusive outcomes", 23, INK, 600)
    svg.text(1468, 400, "Instances / 240", 18, MUTED, anchor="end")
    categories = [("Numerical optimum", optimal, GOLD), ("Other checked feasible point", feasible, TEAL), ("Proven infeasible", infeasible, AMBER), ("No feasible point recorded", unresolved, "#667990")]
    for i, (label, count, color) in enumerate(categories):
        yy = 447 + i * 78
        svg.text(91, yy + 7, label, 21, INK)
        svg.rect(480, yy - 17, 825, 30, "#203047", 6)
        svg.rect(480, yy - 17, 825 * count / total, 30, color, 3)
        svg.text(1362, yy + 7, str(count), 26, color, 700, anchor="end")
        svg.text(1470, yy + 7, f"{count / total:.1%}", 20, MUTED, anchor="end")
    svg.text(91, 742, "69 feasible points = 7 numerical optima + 62 other checked points", 20, MUTED)
    svg.text(65, 813, "Original-model feasibility and integrality checked independently with HiGHS 1.12.0.", 23, INK)
    svg.text(65, 853, "Optimal / infeasible claims agree with published MIPLIB results. Later engine revisions are separate.", 21, MUTED)
    svg.text(65, 911, "Source: miplib2017-benchmark · shared Kaggle CPUs · outcome coverage, not a timing comparison", 18, MUTED)
    svg.save("miplib2017-historical-outcomes.svg")
    return {"numerical_optima": optimal, "other_feasible": feasible, "proven_infeasible": infeasible, "no_point": unresolved}


if __name__ == "__main__":
    HERE.mkdir(parents=True, exist_ok=True)
    gpu_chart()
    counts = miplib_chart()
    print("Wrote 2 benchmark SVGs; 45 GPU/CPU records checked; MIPLIB categories:", counts)
