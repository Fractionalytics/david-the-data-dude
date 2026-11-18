"""Exploratory chart for Reel 3 (2026-11-16): users x risk per user = stimulant-positive dead pedestrians, per
country, early vs. late. Floors (tested pedestrians only). Not production Remotion.

    python scripts/chart_users_risk.py
      reads  data/final/three_buckets.csv (Spain, Czechia), data/final/test_ped_drugs.csv and
             data/final/eu_pedestrian_rates.csv (US 2009-11, the script's baseline)
      writes charts/users_risk_by_country.png

Risk proxy = tested pedestrians with no stimulant found, per million people. Users: Czech high-risk meth users
32,000 (2013) -> 37,200 (2022), Czech NMC; no consistent US series (NSDUH method change 2020); no Spanish count.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chart_three_buckets import GRID, INK, MUTED, ROOT, SURFACE  # noqa: E402

US_C, EU_C, EARLY_C = "#B3261E", "#3F7DC4", "#9AA0A6"
FINAL = ROOT / "data" / "final"


def us_floor(years):
    f = pd.read_csv(FINAL / "test_ped_drugs.csv")
    f = f[(f.definition == "primary") & f.year.str.isdigit()].astype({"year": int}).set_index("year").loc[years]
    u = pd.read_csv(FINAL / "eu_pedestrian_rates.csv")
    pop = u[u.geo == "US"].set_index("year").population.loc[years].sum()
    return f.stimulant.sum() / pop * 1e6, (f.tested - f.stimulant).sum() / pop * 1e6


t = pd.read_csv(FINAL / "three_buckets.csv").set_index(["country", "period"])
e_s, e_n = us_floor([2009, 2010, 2011])
l_s, l_n = us_floor([2022, 2023, 2024])
ROWS = [  # country, years, users text, (risk early, late), (stim early, late), color
    ("US", "2009-11 → 2022-24", "rose a lot\n(no consistent count)", (e_n, l_n), (e_s, l_s), US_C),
    ("Spain", "2010-13 → 2023-24", "no count\npublished", None, None, EU_C),
    ("Czechia", "2003-05 → 2016-21", "+16%\n(2013-22 only)", None, None, EU_C),
]
for i, c in ((1, "Spain"), (2, "Czechia")):
    e, l = t.loc[(c, "early")], t.loc[(c, "late")]
    r = list(ROWS[i])
    r[3] = (e.tested_neg_per_million, l.tested_neg_per_million)
    r[4] = (e.stim_floor_per_million, l.stim_floor_per_million)
    ROWS[i] = tuple(r)

fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), facecolor=SURFACE, gridspec_kw={"width_ratios": [0.8, 1.3, 1.3]})
titles = ["Heavy stimulant users", "×  Risk: tested, no stimulants found\n    (dead pedestrians per million)",
          "=  Tested stimulant-positive\n    (dead pedestrians per million)"]
for ax, title in zip(axes, titles):
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    ax.set_facecolor(SURFACE)
    ax.set_ylim(len(ROWS) - 0.5, -0.6)
    ax.tick_params(colors=MUTED, length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

ax = axes[0]
for i, (c, yrs, users, *_rest) in enumerate(ROWS):
    ax.text(0, i, users, va="center", color=INK, fontsize=10)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.set_yticks(range(len(ROWS)), [f"{r[0]}\n{r[1]}" for r in ROWS], color=INK, fontsize=10)

for ax, k, xmax in ((axes[1], 3, 11.5), (axes[2], 4, 4.4)):
    for i, row in enumerate(ROWS):
        a, b = row[k]
        ax.plot([a, b], [i, i], color=GRID, lw=3, zorder=1)
        ax.scatter([a], [i], s=70, color=EARLY_C, zorder=2, linewidths=0)
        ax.scatter([b], [i], s=90, color=row[5], zorder=3, linewidths=0)
        pct = b / a - 1
        lab = f"{a:.2f} → {b:.2f}  ({'×' + format(b / a, '.1f') if pct > 1 else format(pct, '+.0%')})"
        ax.text(max(a, b) + xmax * 0.03, i - 0.28, lab, va="center", color=INK, fontsize=9.5)
    ax.set_xlim(0, xmax)
    ax.set_yticks([])
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)

fig.suptitle("Same equation, three countries: Europe's risk fell, the US's didn't, and the US added users",
             x=0.01, ha="left", color=INK, fontsize=14)
fig.text(0.01, 0.01, "Floors: tested pedestrians only (gray dot = early, colored = late). Testing rose in Spain "
         "(46%→55% of dead pedestrians) and Czechia (35%→49%) and fell in the US (60%→54%), so floors understate "
         "Europe's fall and the US rise. Sources: NHTSA FARS; Spain INTCF; Mravčík 2007, Másilková & Vorel 2023; "
         "Eurostat; Czech NMC. Users: no consistent US series (NSDUH method change, 2020).",
         color=MUTED, fontsize=7.5, wrap=True)
fig.tight_layout(rect=(0, 0.08, 1, 0.92))
fig.savefig(ROOT / "charts" / "users_risk_by_country.png", dpi=150, facecolor=SURFACE)
