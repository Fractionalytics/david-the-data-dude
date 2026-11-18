"""Exploratory charts for Reel 3 (2026-11-15): the stimulant "dose" in three countries, and the
multiplication ladder (US as a multiple of Czechia). Not production Remotion.

    python scripts/chart_dose_ladder.py
      reads  data/final/three_buckets.csv (floors, scripts/three_buckets.py)
      writes charts/dose_three_countries.png, charts/ladder_us_vs_czechia.png

Hand-entered dose figures, with their sources (all already in the project docs):
- Past-year use: US meth 0.8%, cocaine 1.5% (12+, NSDUH 2024); Czechia meth 0.5% (15-64, 2022, Czech NMC
  2023 table 3-1); Spain cocaine 2.5% (15-64, EDADES 2024). Age bases differ.
- Heavy users per million: US meth use disorder 1,571,000 (NSDUH 2024) / 340.1M = 4,619; US cocaine use disorder
  1.21M / 340.1M = 3,558; Czechia high-risk meth users 37,200 / 10.67M = 3,486 (2022, NMC table 3-7).
  Spain has no high-risk cocaine estimate (docs/research-drugs/cocaine-gap.md).
- Deaths per million: US meth (T43.6) 84.4 and cocaine 64.5 (2024, NCHS DB549); Czechia meth 3.1 (2022,
  Selection B); Spain cocaine 15.2 (2023, OEDA forensic register). See meth-gap.md and cocaine-gap.md.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chart_three_buckets import INK, MUTED, GRID, ROOT, SURFACE  # noqa: E402

METH, COKE = "#7A5A00", "#8E4FB8"  # project meth ochre; purple passes validate_palette.js (direct labels cover tritan)

# (label, value or None, drug)
USE = [("US meth", 0.8, METH), ("US cocaine", 1.5, COKE), ("Spain cocaine", 2.5, COKE), ("Czechia meth", 0.5, METH)]
HEAVY = [("US meth", 4619, METH), ("US cocaine", 3558, COKE), ("Spain cocaine", None, COKE),
         ("Czechia meth", 3486, METH)]
DEATHS = [("US meth", 84.4, METH), ("US cocaine", 64.5, COKE), ("Spain cocaine", 15.2, COKE),
          ("Czechia meth", 3.1, METH)]


def bars(ax, rows, fmt, title, xmax):
    for i, (lab, v, col) in enumerate(rows):
        if v is None:
            ax.text(0, i, "  no estimate published", va="center", color=MUTED, fontsize=9, style="italic")
            continue
        ax.barh(i, v, color=col, height=0.6)
        ax.text(v + xmax * 0.02, i, fmt.format(v), va="center", color=INK, fontsize=10)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, xmax)
    ax.set_title(title, loc="left", color=INK, fontsize=11)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_facecolor(SURFACE)


def icons(ax, rows):
    """Heavy users per 10,000 people, one dot per person."""
    for i, (lab, v, col) in enumerate(rows):
        if v is None:
            ax.text(0, i, "no estimate published", va="center", color=MUTED, fontsize=9, style="italic")
            continue
        n = round(v / 100)
        xs = np.arange(n)
        ax.scatter(xs * 1.0, np.full(n, i), s=34, color=col, marker="o", linewidths=0)
        ax.text(n + 1.5, i, f"{n} per 10,000", va="center", color=INK, fontsize=10)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], color=INK)
    ax.invert_yaxis()
    ax.set_xlim(-1, 62)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_title("Heavy users (use disorder / high-risk use)", loc="left", color=INK, fontsize=11)
    ax.set_facecolor(SURFACE)


def dose():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), facecolor=SURFACE, gridspec_kw={"width_ratios": [1, 1.4, 1]})
    bars(axes[0], USE, "{:.1f}%", "Used in the past year", 3.2)
    icons(axes[1], HEAVY)
    bars(axes[2], DEATHS, "{:.1f}", "Overdose deaths per million people", 100)
    for ax in axes[1:]:
        ax.set_yticklabels([])
    fig.suptitle("The stimulant \"dose\": similar use, similar heavy use (US vs. Czechia), very different deaths",
                 x=0.01, ha="left", color=INK, fontsize=14)
    fig.text(0.01, 0.01, "Use: US ages 12+ (NSDUH 2024); Czechia and Spain ages 15-64. Heavy users: US use disorder "
             "(NSDUH 2024); Czechia high-risk meth use (2022). Deaths: US 2024 (NCHS); Czechia 2022; Spain 2023 (OEDA). "
             "US meth and cocaine deaths overlap.", color=MUTED, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    fig.savefig(ROOT / "charts" / "dose_three_countries.png", dpi=150, facecolor=SURFACE)


def ladder():
    """Three-row equation: heavy users x risk per heavy user = stimulant-positive dead pedestrians (US / Czechia).

    Heavy users use RAND's count (RR3140 Table 2.6), which corrects the US survey's undercount
    (docs/reel3-skeleton-v2.md section 17): chronic meth users 3.2M best, 1.3M low, 5.3M high (2016), per US
    2016 person, vs. Czechia's 31,600 high-risk users (2016, NMC table 3-7) / 10.55M. The bar is the best
    estimate; the whisker is RAND's low-high. More users counted leaves less risk per user, so the risk
    whisker runs the other way. RAND's low end (1.3x) matches the US survey's ratio (NSDUH 2024 vs. Czechia 2022).
    """
    d = pd.read_csv(ROOT / "data" / "final" / "three_buckets.csv").set_index(["country", "period"])
    floor_ratio = d.loc[("US", "cz_late_years")].stim_floor_per_million / d.loc[("Czechia", "late")].stim_floor_per_million
    r = pd.read_csv(ROOT / "data" / "final" / "eu_pedestrian_rates.csv")
    us16 = r[(r.geo == "US") & (r.year == 2016)].iloc[0]
    us_pop_2016 = us16.deaths / us16.rate_per_100k * 1e5
    cz_per_person = 31600 / 10.55e6
    users = {k: (v / us_pop_2016) / cz_per_person for k, v in (("lo", 1.3e6), ("best", 3.2e6), ("hi", 5.3e6))}
    rows = [
        ("", "Heavy meth users\nper person", users["best"], (users["lo"], users["hi"]), METH, False),
        ("×", "Risk per heavy user\n(where they walk, how fast\nthe cars are: inferred)", floor_ratio / users["best"],
         (floor_ratio / users["hi"], floor_ratio / users["lo"]), MUTED, True),
        ("=", "Stimulant-positive dead\npedestrians per person", floor_ratio, None, INK, False),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=SURFACE)
    for i, (op, lab, v, rng, col, inferred) in enumerate(rows):
        if inferred:
            ax.barh(i, v - 1, left=1, color=SURFACE, edgecolor=col, hatch="///", height=0.6, lw=1.2)
        else:
            ax.barh(i, v - 1, left=1, color=col, height=0.6)
        if rng:
            ax.plot(rng, [i, i], color=INK, lw=1.4)
            for x in rng:
                ax.plot([x, x], [i - 0.12, i + 0.12], color=INK, lw=1.4)
            ax.text(rng[1] * 1.08, i, f"about {v:.0f}×  (range {rng[0]:.1f}–{rng[1]:.1f}×)", va="center",
                    color=INK, fontsize=11)
        else:
            ax.text(v * 1.08, i, f"{v:.1f}×", va="center", color=INK, fontsize=11)
    ax.set_xscale("log")
    ax.axvline(1, color=INK, lw=1)
    ax.set_xlim(1, 60)
    ax.set_xticks([1, 2, 5, 10, 20, 50], ["1× (same)", "2×", "5×", "10×", "20×", "50×"])
    ax.set_yticks(range(len(rows)), [f"{op}   {lab}" if op else lab for op, lab, *_ in rows], color=INK)
    ax.set_ylim(2.5, -0.8)
    for s_ in ("top", "right", "left"):
        ax.spines[s_].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_facecolor(SURFACE)
    ax.set_title("The US as a multiple of Czechia: about 3× the users, about 4× the risk per user", loc="left",
                 color=INK, fontsize=13)
    fig.text(0.01, 0.01, "Log scale. Heavy users: US chronic meth users, 4+ days a month, 2016 (RAND RR3140; whisker = "
             "RAND's low-high)\nvs. Czechia's high-risk meth users, 2016 (NMC); definitions differ. Dead pedestrians: "
             "tested and stimulant-positive per million\npeople, 2016-21 (FARS; Másilková & Vorel 2023). Risk per user = "
             "dead pedestrians ÷ heavy users; inferred, not measured. Its whisker runs the other way.",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(ROOT / "charts" / "ladder_us_vs_czechia.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    dose()
    ladder()
