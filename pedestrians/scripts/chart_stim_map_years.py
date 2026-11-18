"""Meth vs. cocaine in overdose deaths, by state, every year 2009-2024 (exploratory tile maps).

    python scripts/chart_stim_map_years.py
      reads  data/raw/cdc_wonder/wonder_{od_all,meth,coc}_state_year_{2009_2017,2018_2024}.csv  (exports S1-S6)
      writes data/final/stim_by_state_year.csv
             charts/stim_map_years/stim_map_<year>.png   (one per year)
             charts/stim_map_small_multiples.png         (all years on one page)

Colour = meth's share of the state's stimulant-involved overdose deaths: meth / (meth + cocaine), where meth = T43.6
and cocaine = T40.5 (multiple cause), underlying cause X40-X44, X60-X64, X85, Y10-Y14. A death with both is counted
on both sides. Tile numbers: % of ALL overdose deaths in that state and year involving meth | cocaine.
WONDER suppresses counts of 1-9; a suppressed side is set to 9 for the colour (conservative: it shrinks the other
side's lead) and shown as <10 (in the share labels, as "<" followed by 9 / all deaths, rounded up).
A state-year with fewer than 20 meth-or-cocaine deaths (counting a suppressed side as 9) is drawn as "too few
to tell" instead of being coloured.
2009-2017 come from "Multiple Cause of Death, 1999-2020"; 2018-2024 from "...2018-2024, Single Race".
"""
from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

from tilegrid import ABBR, COC_DARK, COC_LIGHT, GRID, INK, METH_DARK, METH_LIGHT, MID, MUTED, SURFACE

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "data" / "raw" / "cdc_wonder"
BINS = [  # (lower bound of meth share of stimulant deaths, fill, ink, label)
    (0.75, METH_DARK, "white", "Mostly meth (75%+)"),
    (0.60, METH_LIGHT, INK, "More meth (60-75%)"),
    (0.40, MID, INK, "About even (40-60%)"),
    (0.25, COC_LIGHT, INK, "More cocaine (25-40% meth)"),
    (-1, COC_DARK, "white", "Mostly cocaine (under 25% meth)"),
]


def read(kind):
    parts = []
    for span in ("2009_2017", "2018_2024"):
        d = pd.read_csv(W / f"wonder_{kind}_state_year_{span}.csv")
        d = d[d.Notes.isna()].copy()
        d["Deaths"] = pd.to_numeric(d.Deaths, errors="coerce")
        parts.append(d[["State", "Year Code", "Deaths"]])
    return pd.concat(parts).rename(columns={"State": "state", "Year Code": "year", "Deaths": kind})


d = read("od_all").merge(read("meth"), on=["state", "year"]).merge(read("coc"), on=["state", "year"])
d["year"] = d.year.astype(int)
d["abbr"] = d.state.str.replace(" ", "").map(ABBR)
assert d.abbr.notna().all() and len(d) == 51 * 16, len(d)
m, c = d.meth.fillna(9), d.coc.fillna(9)
d["meth_share_of_stim"] = m / (m + c)
d["too_few"] = (m + c) < 20
d["meth_pct_all"], d["coc_pct_all"] = 100 * d.meth / d.od_all, 100 * d.coc / d.od_all
d.to_csv(ROOT / "data" / "final" / "stim_by_state_year.csv", index=False)


def label(n, total):
    return f"<{ceil(100 * 9 / total)}" if pd.isna(n) else f"{100 * n / total:.0f}"


def draw(ax, g, numbers=True):
    for _, r in g.iterrows():
        col, row = GRID[r.abbr]
        if r.too_few:
            fill, ink, edge, ls = SURFACE, MUTED, MUTED, "--"
        else:
            _, fill, ink, _ = next(b for b in BINS if r.meth_share_of_stim >= b[0])
            edge, ls = SURFACE, "-"
        ax.add_patch(FancyBboxPatch((col + 0.04, -row + 0.04), 0.92, 0.92, boxstyle="round,pad=0,rounding_size=0.08",
                                    facecolor=fill, edgecolor=edge, linewidth=1.0, linestyle=ls))
        supp = "*" if pd.isna(r.meth) or pd.isna(r.coc) else ""
        if numbers:
            ax.text(col + 0.5, -row + 0.64, r.abbr + supp, ha="center", va="center", fontsize=11, fontweight="bold",
                    color=ink)
            ax.text(col + 0.5, -row + 0.3, f"{label(r.meth, r.od_all)} | {label(r.coc, r.od_all)}", ha="center",
                    va="center", fontsize=7.5, color=ink)
        else:
            ax.text(col + 0.5, -row + 0.5, r.abbr, ha="center", va="center", fontsize=4.2, color=ink)
    ax.set_xlim(-0.2, 12.2)
    ax.set_ylim(-7.2, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")


LEGEND = [Patch(facecolor=b[1], edgecolor="none", label=b[3]) for b in BINS] + [
    Patch(facecolor=SURFACE, edgecolor=MUTED, linestyle="--", label="Too few deaths to tell (under 20)")]
SOURCE = ("Source: CDC WONDER, Multiple Cause of Death (1999-2020 for 2009-2017; 2018-2024 Single Race). Overdose "
          "deaths X40-X44, X60-X64, X85, Y10-Y14; meth = T43.6, cocaine = T40.5. A death with both counts on both sides.")

out_dir = ROOT / "charts" / "stim_map_years"
out_dir.mkdir(parents=True, exist_ok=True)
for y, g in d.groupby("year"):
    fig, ax = plt.subplots(figsize=(10.8, 7.4), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    draw(ax, g)
    ok = g[~g.too_few]
    nm, nc = (ok.meth_share_of_stim >= 0.6).sum(), (ok.meth_share_of_stim < 0.4).sum()
    fig.text(0.04, 0.955, f"Meth or cocaine? Overdose deaths by state, {y}", fontsize=17, fontweight="bold",
             color=INK)
    fig.text(0.04, 0.915, "Colour: meth's share of deaths involving either stimulant. "
             "Tile numbers: % of all overdose deaths involving meth | cocaine", fontsize=10.5, color=MUTED)
    ax.legend(handles=LEGEND, loc="upper left", bbox_to_anchor=(0.19, 1.0), ncol=2, frameon=False, fontsize=9,
              labelcolor=INK)
    fig.text(0.04, 0.03, SOURCE + f"\n* = a count under 10 is suppressed by CDC. More meth in {nm} states, "
             f"more cocaine in {nc}.", fontsize=7.5, color=MUTED, va="bottom")
    fig.savefig(out_dir / f"stim_map_{y}.png", facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)

fig, axes = plt.subplots(4, 4, figsize=(16, 12.5), dpi=150)
fig.patch.set_facecolor(SURFACE)
for ax, (y, g) in zip(axes.flat, d.groupby("year")):
    draw(ax, g, numbers=False)
    ax.set_title(str(y), fontsize=13, fontweight="bold", color=INK, loc="left")
fig.suptitle("Meth moved east: which stimulant shows up in overdose deaths, by state, 2009-2024", x=0.03, y=0.995,
             ha="left", fontsize=18, fontweight="bold", color=INK)
fig.legend(handles=LEGEND, loc="upper left", bbox_to_anchor=(0.03, 0.965), ncol=6, frameon=False, fontsize=10,
           labelcolor=INK, title="Meth's share of deaths involving meth or cocaine", title_fontsize=10,
           alignment="left")
fig.text(0.03, 0.005, SOURCE, fontsize=8, color=MUTED, va="bottom")
fig.subplots_adjust(left=0.02, right=0.99, top=0.9, bottom=0.03, wspace=0.03, hspace=0.12)
fig.savefig(ROOT / "charts" / "stim_map_small_multiples.png", facecolor=SURFACE)
print(d[~d.too_few].groupby("year").apply(lambda g: pd.Series({"more_meth": (g.meth_share_of_stim >= .6).sum(),
                                                    "even": g.meth_share_of_stim.between(.4, .6, "left").sum(),
                                                    "more_coc": (g.meth_share_of_stim < .4).sum()})).to_string())
