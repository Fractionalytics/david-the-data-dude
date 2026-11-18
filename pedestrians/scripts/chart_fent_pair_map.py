"""Exploratory tile map: which stimulant fentanyl is paired with, by state, 2024.

    python scripts/chart_fent_pair_map.py [year]
      reads  data/final/fent_pair_by_state_<year>.csv   (from scripts/analyze_wonder_age_pair.py; default 2024)
      writes charts/fent_pair_map_<year>.png

Colour = share of the state's fentanyl (T40.4) overdose deaths that also involved meth (T43.6) minus the share
that also involved cocaine (T40.5), in percentage points. WONDER suppresses counts of 1-9; a suppressed partner
count is set to 9 (its maximum), so the bin is the conservative one, and the tile is marked with *.
Palette: ochre (meth, the project's meth colour) <-> blue (cocaine), grey midpoint; arms validated with the
dataviz skill's validate_palette.js (ordinal, light mode).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

from tilegrid import ABBR, GRID

ROOT = Path(__file__).resolve().parents[1]
YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2024

BINS = [  # (lower bound of meth-minus-cocaine points, fill, text colour, legend label)
    (30, "#9a6200", "white", "Meth far more common (30+ points)"),
    (10, "#d9a443", "#0b0b0b", "Meth more common (10-30)"),
    (-10, "#e6e5e1", "#0b0b0b", "About even (within 10)"),
    (-30, "#86b6ef", "#0b0b0b", "Cocaine more common (10-30)"),
    (-999, "#1f5fae", "white", "Cocaine far more common (30+ points)"),
]
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"

d = pd.read_csv(ROOT / "data" / "final" / f"fent_pair_by_state_{YEAR}.csv")
d["abbr"] = d.state.str.replace(" ", "").map(ABBR)
assert d.abbr.notna().all() and set(d.abbr) == set(GRID), set(GRID) ^ set(d.abbr)
d["supp"] = d.with_meth.isna() | d.with_cocaine.isna()
meth = d.with_meth.fillna(9) / d.fent  # suppressed = 1-9; use 9 for the partner that would shrink the lead
coc = d.with_cocaine.fillna(9) / d.fent
d["diff"] = 100 * (meth - coc)
d.loc[d.with_meth.isna() & d.with_cocaine.isna(), "diff"] = float("nan")

fig, ax = plt.subplots(figsize=(10.8, 8.2), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
for _, r in d.iterrows():
    c, row = GRID[r.abbr]
    x, y = c, -row
    if pd.isna(r["diff"]):
        fill, ink = SURFACE, MUTED
    else:
        _, fill, ink, _ = next(b for b in BINS if r["diff"] >= b[0])
    ax.add_patch(FancyBboxPatch((x + 0.04, y + 0.04), 0.92, 0.92, boxstyle="round,pad=0,rounding_size=0.08",
                                facecolor=fill, edgecolor=MUTED if pd.isna(r["diff"]) else SURFACE, linewidth=1.2,
                                linestyle="--" if pd.isna(r["diff"]) else "-"))
    ax.text(x + 0.5, y + 0.64, r.abbr + ("*" if r.supp else ""), ha="center", va="center", fontsize=11,
            fontweight="bold", color=ink)
    m = "<10" if pd.isna(r.with_meth) else f"{100 * r.with_meth / r.fent:.0f}"
    k = "<10" if pd.isna(r.with_cocaine) else f"{100 * r.with_cocaine / r.fent:.0f}"
    if pd.isna(r.with_meth) and pd.isna(r.with_cocaine):
        m = k = "?"
    ax.text(x + 0.5, y + 0.3, f"{m} | {k}", ha="center", va="center", fontsize=7.5, color=ink)
ax.set_xlim(-0.2, 12.2)
ax.set_ylim(-7.2, 1.3)
ax.set_aspect("equal")
ax.axis("off")

n_meth, n_coc = (d.with_meth > d.with_cocaine.fillna(9)).sum(), (d.with_cocaine > d.with_meth.fillna(9)).sum()
fig.text(0.04, 0.955, f"Fentanyl's partner, {YEAR}: meth in the West, cocaine in the Northeast", fontsize=17,
         fontweight="bold", color=INK, ha="left")
fig.text(0.04, 0.918, "Of each state's fentanyl overdose deaths, the share that also involved meth vs. cocaine. "
         "Tile numbers: % with meth | % with cocaine", fontsize=10.5, color=MUTED, ha="left")
ax.legend(handles=[Patch(facecolor=b[1], edgecolor="none", label=b[3]) for b in BINS]
          + [Patch(facecolor=SURFACE, edgecolor=MUTED, linestyle="--", label="Both counts suppressed")],
          loc="upper left", bbox_to_anchor=(0.19, 1.0), ncol=2, frameon=False, fontsize=9, labelcolor=INK,
          alignment="left",
          title="Meth share minus cocaine share", title_fontsize=9.5)
fig.text(0.04, 0.03,
         f"Source: CDC WONDER, Multiple Cause of Death {YEAR}. Overdose deaths (X40-X44, X60-X64, X85, Y10-Y14) with T40.4 "
         "(synthetic opioids, mostly fentanyl), and with T43.6 (meth) or T40.5 (cocaine). One death can involve both.\n"
         f"* = a count under 10 is suppressed by CDC; shown as <10 and binned conservatively. "
         f"Meth is the larger partner in {n_meth} states, cocaine in {n_coc}.",
         fontsize=7.5, color=MUTED, ha="left", va="bottom")
out = ROOT / "charts" / f"fent_pair_map_{YEAR}.png"
fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
print(out)
