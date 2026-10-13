"""Exploratory chart: the indexed scorecard (radiology vs all of medicine).

One row per measure, % change over each measure's window, radiology vs its benchmark.
Every value is computed from the processed CSVs, not typed in:
  nrmp_specialty_growth.csv, cms_physician_index.csv, demand_controls.csv, pay_by_specialty.csv.
Exploratory only: no editorial titles or callouts (those come from David's storyboard).

Output: charts/exploratory/scorecard.png

Run from the repo worktree root:
    python -I -X utf8 projects/radiology/scripts/exploratory_charts.py
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("projects/radiology")
P = ROOT / "data/processed"
OUT = ROOT / "charts/exploratory/scorecard.png"
RAD, BENCH = "#2a78d6", "#8c8b86"  # palette slot 1 (blue) vs neutral context gray
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def rows(name):
    return list(csv.DictReader(open(P / name, encoding="utf-8")))


def pct(a, b):
    return 100 * (float(b) - float(a)) / float(a)


def measures():
    nrmp = {r["specialty"]: r for r in rows("nrmp_specialty_growth.csv")}
    rad21 = sum(int(nrmp[s]["positions_2021"]) for s in ("Radiology-Diagnostic", "Interventional Radiology (Integrated)"))
    rad26 = sum(int(nrmp[s]["positions_2026"]) for s in ("Radiology-Diagnostic", "Interventional Radiology (Integrated)"))
    g = nrmp["GRAND TOTAL"]
    idx = {r["group"]: r for r in rows("cms_physician_index.csv")}
    dem = {r["series"]: r for r in rows("demand_controls.csv")}
    pay = {(r["source"].lower(), r["report_year"], r["series"]): float(r["value"]) for r in rows("pay_by_specialty.csv")
           # dollar rows only: the file also holds growth-rate rows under the same series names
           if r["series"] in ("radiology", "all_physicians") and r["unit"].startswith("usd") and r["value"]}

    def paypct(src, y0, y1, series):
        return pct(pay[(src, y0, series)], pay[(src, y1, series)])

    dox = next(k[0] for k in pay if k[0].startswith("doximity"))
    med = next(k[0] for k in pay if k[0].startswith("medscape"))
    return [
        # label, window, radiology %, benchmark %, benchmark label
        ("Residency seats", "2021–2026", pct(rad21, rad26), pct(g["positions_2021"], g["positions_2026"]), "whole Match"),
        ("Physicians billing Medicare", "2016–2024", float(idx["radiology (DR+IR)"]["pct_2016_2024"]),
         float(idx["physicians"]["pct_2016_2024"]), "all physicians"),
        ("Per 100k Americans 65+", "2016–2024", float(dem["radiologists (DR+IR) per 100k people 65+"]["pct_2016_2024"]),
         float(dem["physicians per 100k people 65+"]["pct_2016_2024"]), "all physicians"),
        ("Medicare services per doctor", "2016–2024", float(idx["services per diagnostic radiologist"]["pct_2016_2024"]),
         float(idx["services per physician"]["pct_2016_2024"]), "all physicians"),
        ("Pay (Medscape)", "2017–2025 pay", paypct(med, "2018", "2026", "radiology"),
         paypct(med, "2018", "2026", "all_physicians"), "all physicians"),
        ("Pay (Doximity)", "2017–2026 reports", paypct(dox, "2017", "2026", "radiology"),
         paypct(dox, "2017", "2026", "all_physicians"), "avg. of 48 specialties"),
    ]


def main():
    data = measures()
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ys = list(range(len(data)))[::-1]
    for y, (label, window, r, b, blabel) in zip(ys, data):
        ax.plot([b, r], [y, y], color=GRID, lw=2, zorder=1, solid_capstyle="round")
        ax.scatter(r, y, s=70, color=RAD, zorder=5)
        # benchmark as a ring drawn on top, so it stays visible when the two values nearly coincide
        ax.scatter(b, y, s=90, facecolor=SURFACE, edgecolor=BENCH, linewidth=2.2, zorder=4)
        lo, hi = sorted([(r, "r"), (b, "b")])
        for v, kind in ((lo[0], lo[1]), (hi[0], hi[1])):
            off, ha = (-9, "right") if (v, kind) == lo else (9, "left")
            ax.annotate(f"{v:+.1f}%", (v, y), xytext=(off, 0), textcoords="offset points",
                        va="center", ha=ha, fontsize=9, color=INK if kind == "r" else MUTED)
        ax.annotate(f"vs {blabel}", (b, y), xytext=(0, -13), textcoords="offset points",
                    ha="center", va="top", fontsize=7.5, color=MUTED)
    ax.set_yticks(ys, [f"{d[0]}\n{d[1]}" for d in data], fontsize=9.5, color=INK)
    ax.axvline(0, color=MUTED, lw=1, zorder=0)
    ax.set_xlim(-25, 60)
    ax.set_ylim(-0.7, len(data) - 0.5)
    ax.set_xlabel("% change over the window", color=MUTED, fontsize=9)
    ax.tick_params(axis="x", colors=MUTED, labelsize=8.5, length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.scatter([], [], s=60, color=RAD, label="Radiology")
    ax.scatter([], [], s=60, facecolor="none", edgecolor=BENCH, linewidth=2, label="Benchmark (all of medicine)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=9, labelcolor=INK)
    ax.set_title("Exploratory: radiology vs all of medicine, % change", loc="left", fontsize=11, color=INK, pad=28)
    fig.text(0.01, 0.01, "Sources: NRMP Results and Data; CMS Medicare Physician & Other Practitioners (fee-for-service); "
             "Census; Doximity; Medscape (via trade press). Radiology = diagnostic + interventional "
             "(services row: diagnostic only).", fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE)
    for d in data:
        print(f"{d[0]:<30}{d[1]:<20}{d[2]:>7.1f}{d[3]:>7.1f}")


if __name__ == "__main__":
    main()
