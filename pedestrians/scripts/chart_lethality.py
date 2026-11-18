"""Exploratory chart for P24 (2026-11-15): chance a pedestrian dies when hit, by year. Not production Remotion.

    python scripts/chart_lethality.py
      reads  data/final/test_ped_lethality.csv (scripts/test_ped_lethality.py)
      writes charts/ped_lethality_by_year.png

L = FARS pedestrian deaths / (GES or CRSS police-reported pedestrians injured + deaths). Band = 95% from the
injured estimate's sampling error. GES (to 2015) and CRSS (from 2016) are different samples: don't read across.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, MUTED, GRID, LINE = "#FCFCFB", "#1A1C1E", "#5E6368", "#D9DCD4", "#B3261E"

t = pd.read_csv(ROOT / "data" / "final" / "test_ped_lethality.csv")
se_all = t.deaths * t.inj_var ** 0.5 / (t.inj + t.deaths) ** 2
se_ser = t.deaths * t.serious_var ** 0.5 / (t.serious + t.deaths) ** 2

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), facecolor=SURFACE)
for ax, col, se, title in ((axes[0], "L", se_all, "Any reported injury"),
                           (axes[1], "L_serious", se_ser, "Serious injuries only")):
    for seg in (t.year < 2016, t.year >= 2016):
        d, s = t[seg], se[seg]
        ax.fill_between(d.year, (d[col] - 1.96 * s) * 100, (d[col] + 1.96 * s) * 100, color=LINE, alpha=0.12, lw=0)
        ax.plot(d.year, d[col] * 100, color=LINE, lw=2, marker="o", ms=5)
    ax.axvline(2015.5, color=MUTED, lw=1, ls="--")
    ax.axvspan(2019.5, 2021.5, color=GRID, alpha=0.5, lw=0)
    top = ax.get_ylim()[1]
    ax.text(2015.4, top, "GES ", ha="right", va="top", color=MUTED, fontsize=9)
    ax.text(2015.6, top, " CRSS", ha="left", va="top", color=MUTED, fontsize=9)
    ax.text(2020.5, ax.get_ylim()[0], "pandemic", ha="center", va="bottom", color=MUTED, fontsize=8)
    for y in (2009, 2015, 2016, 2021, 2024):
        v = t.loc[t.year == y, col].iloc[0] * 100
        ax.annotate(f"{v:.1f}%", (y, v), textcoords="offset points", xytext=(0, 9), ha="center", color=INK,
                    fontsize=9)
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    ax.set_facecolor(SURFACE)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    for s_ in ("left", "bottom"):
        ax.spines[s_].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks([2009, 2012, 2015, 2018, 2021, 2024])
    ax.set_ylabel("% of pedestrians hit who died", color=MUTED)
fig.suptitle("US pedestrians: chance of dying when hit by a vehicle", x=0.01, ha="left", color=INK, fontsize=14)
fig.text(0.01, 0.01, "Deaths: NHTSA FARS. Hit = deaths + police-reported injured pedestrians, NHTSA GES (2009-15) and "
         "CRSS (2016-24), weighted. Shaded band: 95% sampling range. The 2016 survey redesign means the two segments "
         "aren't directly comparable.", color=MUTED, fontsize=7.5, wrap=True)
fig.tight_layout(rect=(0, 0.06, 1, 0.94))
fig.savefig(ROOT / "charts" / "ped_lethality_by_year.png", dpi=150, facecolor=SURFACE)
