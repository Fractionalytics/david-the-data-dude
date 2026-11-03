"""Exploratory scatter: the share of audits that aren't by mail vs. audit odds.

One dot per income band. X is the Field share of audits closed (Table 18 / 3-2);
Y is the TY2021 audit rate (Table 3-1, log scale). Two versions, because the IRS
doesn't publish audit type by tax year, so the axes can't count the same audits:
- FY2025 share alone (charts/odds_vs_field_share.png)
- FY2023-2025 pooled share, the years most TY2021 audits would have closed
  (charts/odds_vs_field_share_fy23_25.png)

Field includes office audits and some finished by mail.

Reads data/audit_types_by_bracket.csv.
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "audit_types_by_bracket.csv"
VERSIONS = [
    ("field_share_fy2025_pct", "audits closed, FY2025", HERE / "charts" / "odds_vs_field_share.png"),
    ("field_share_fy2023_25_pct", "audits closed, FY2023–FY2025", HERE / "charts" / "odds_vs_field_share_fy23_25.png"),
]

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e0"
UNDER_50K, OVER_50K, HOLLOW = "#eb6834", "#2a78d6", "#52514e"

# Category -> (dot label, label offset in points, horizontal alignment)
BANDS = {
    "No total positive income": ("No positive income", (10, -4), "left"),
    "$1 under $25,000": ("$1–$25K", (10, -4), "left"),
    "$25,000 under $50,000": ("$25K–$50K", (0, 10), "center"),
    "$50,000 under $75,000": ("$50K–$75K", (0, -18), "center"),
    "$75,000 under $100,000": ("$75K–$100K", (-4, 10), "center"),
    "$100,000 under $200,000": ("$100K–$200K", (10, -6), "left"),
    "$200,000 under $500,000": ("$200K–$500K", (10, 4), "left"),
    "$500,000 under $1,000,000": ("$500K–$1M", (10, -4), "left"),
    "$1,000,000 under $5,000,000": ("$1M–$5M", (10, -4), "left"),
    "$5,000,000 under $10,000,000": ("$5M–$10M", (-10, -4), "right"),
    "$10,000,000 or more": ("$10M+", (-10, -4), "right"),
    "Returns with earned income tax credit": ("EITC returns (overlap the bands)", (10, -4), "left"),
}
UNDER = {"$1 under $25,000", "$25,000 under $50,000"}
OPEN = {"No total positive income", "Returns with earned income tax credit"}


def draw(rows, share_col, share_label, out):
    fig, ax = plt.subplots(figsize=(10, 7), dpi=160, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_yscale("log")
    ax.set_ylim(1 / 1500, 1 / 10)
    ax.set_xlim(-3, 100)

    for name, (label, offset, ha) in BANDS.items():
        r = rows[name]
        x = float(r[share_col])
        y = int(r["ty2021_examined"]) / int(r["ty2021_returns_filed"])
        if name in OPEN:
            style = {"facecolor": SURFACE, "edgecolor": HOLLOW, "linewidth": 1.8}
        else:
            style = {"facecolor": UNDER_50K if name in UNDER else OVER_50K, "edgecolor": SURFACE, "linewidth": 1.5}
        ax.scatter(x, y, s=110, zorder=3, **style)
        ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", ha=ha, fontsize=10.5, color=INK)

    ticks = [1000, 300, 100, 30, 10]
    ax.yaxis.set_major_locator(FixedLocator([1 / t for t in ticks]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([f"1 in {t:,}" for t in ticks])
    ax.set_xticks(range(0, 101, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.grid(color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(colors=MUTED, length=0, labelsize=10.5)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.set_xlabel(f"Field + office share of {share_label}", color=MUTED, fontsize=11, labelpad=10)
    ax.set_ylabel("Odds of an audit, 2021 returns (log scale)", color=MUTED, fontsize=11, labelpad=10)
    fig.suptitle("Field + office share vs. audit odds, by income band", x=0.085, y=0.97, ha="left",
                 fontsize=15, fontweight="bold", color=INK)
    handles = [
        plt.Line2D([], [], marker="o", linestyle="", markersize=9, markerfacecolor=UNDER_50K, markeredgecolor=SURFACE, label="$1–$50K"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=9, markerfacecolor=OVER_50K, markeredgecolor=SURFACE, label="$50K and up"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=9, markerfacecolor=SURFACE, markeredgecolor=HOLLOW, label="Other groups"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=10.5, labelcolor=INK)
    fig.text(0.085, 0.015, "Exploratory. IRS Data Book, Tables 3-1, 3-2 and 18. Income is total positive income. "
             "Field includes office audits and some finished by mail.", fontsize=8.5, color=MUTED)
    fig.subplots_adjust(left=0.125, right=0.97, top=0.92, bottom=0.12)

    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(out)


def main():
    plt.rcParams["text.parse_math"] = False  # keep "$" literal in labels
    with DATA.open(encoding="utf-8") as f:
        rows = {r["category"]: r for r in csv.DictReader(f)}
    for share_col, share_label, out in VERSIONS:
        draw(rows, share_col, share_label, out)


if __name__ == "__main__":
    main()
