"""Meth (T43.6) overdose deaths per million people, by state and year, 2009-2024 (Reel 2 card 12).

    python scripts/meth_per_million_state_year.py
      reads  data/raw/cdc_wonder/wonder_meth_state_year_{2009_2017,2018_2024}.csv  (exports S2, S5)
      writes data/final/meth_per_million_state_year.csv
             charts/meth_per_million_2009_2016_2024.png   (exploratory tile maps)

Deaths: multiple cause T43.6, underlying cause X40-X44, X60-X64, X85, Y10-Y14. Population: WONDER's own column.
WONDER suppresses counts of 1-9; those state-years are "under 10 deaths" (per million left blank, drawn gray).
2009-2017 come from "Multiple Cause of Death, 1999-2020"; 2018-2024 from "...2018-2024, Single Race".
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

from tilegrid import ABBR, GRID, INK, MUTED, SURFACE

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "data" / "raw" / "cdc_wonder"
YEARS = [2009, 2016, 2024]
BINS = [  # (lower bound per million, fill)
    (100, "#7a2e0b"),
    (50, "#b8501a"),
    (25, "#e08a3c"),
    (10, "#f3c48a"),
    (0, "#fbe8cf"),
]
SUPPRESSED = "#d9d9d6"

parts = []
for span in ("2009_2017", "2018_2024"):
    d = pd.read_csv(W / f"wonder_meth_state_year_{span}.csv", dtype=str)
    d = d[d["Notes"].isna() & d["State"].notna()]
    parts.append(d[["State", "Year Code", "Deaths", "Population"]])
d = pd.concat(parts)
d["year"] = d["Year Code"].astype(int)
d["suppressed"] = d["Deaths"].eq("Suppressed")
d["deaths"] = pd.to_numeric(d["Deaths"], errors="coerce")
d["population"] = pd.to_numeric(d["Population"])
d["per_million"] = (d["deaths"] / d["population"] * 1e6).round(1)
d["abbr"] = d["State"].str.replace(" ", "").map(ABBR)
d = d.rename(columns={"State": "state"})[["state", "abbr", "year", "deaths", "population", "per_million", "suppressed"]]
out = ROOT / "data" / "final" / "meth_per_million_state_year.csv"
d.sort_values(["year", "state"]).to_csv(out, index=False)
print(out, len(d), "rows")

# national check
nat = d.groupby("year").agg(deaths=("deaths", "sum"), pop=("population", "sum"))
print((nat.deaths / nat["pop"] * 1e6).round(1).loc[YEARS].to_string())
print(d[d.year.isin(YEARS)].groupby("year").per_million.describe().round(1).to_string())


def fill(v, sup):
    if sup:
        return SUPPRESSED
    return next(c for lo, c in BINS if v >= lo)


fig, axes = plt.subplots(1, 3, figsize=(18, 5), facecolor=SURFACE)
for ax, yr in zip(axes, YEARS):
    s = d[d.year == yr].set_index("abbr")
    for ab, (c, r) in GRID.items():
        if ab not in s.index:
            continue
        row = s.loc[ab]
        ax.add_patch(FancyBboxPatch((c, -r), 0.92, 0.92, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=fill(row.per_million, row.suppressed), ec="none"))
        ax.text(c + 0.46, -r + 0.46, ab, ha="center", va="center", fontsize=8, color=INK)
    ax.set_xlim(-0.2, 12.2); ax.set_ylim(-8.2, 1.1); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(str(yr), fontsize=16, color=INK)
fig.legend(handles=[Patch(fc=c, label=f"{lo}+ per million") for lo, c in BINS] + [Patch(fc=SUPPRESSED, label="under 10 deaths")],
           loc="lower center", ncol=6, frameon=False, fontsize=11, labelcolor=MUTED)
png = ROOT / "charts" / "meth_per_million_2009_2016_2024.png"
fig.savefig(png, dpi=110, bbox_inches="tight", facecolor=SURFACE)
print(png)
