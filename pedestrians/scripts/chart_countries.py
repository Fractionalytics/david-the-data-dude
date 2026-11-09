"""Exploratory: pedestrian death rates in the US and 27 other high-income
countries, 2013 vs. 2022 (CDC MMWR, 2025), as a dumbbell chart sorted by 2022.

    python scripts/chart_countries.py
      -> charts/pedestrian_rates_by_country.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
US, OTHER, INK, MUTED, RULE, SURFACE = "#eb6834", "#8a8985", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def main() -> None:
    d = pd.read_csv(ROOT / "data" / "raw" / "cdc" / "pedestrian_rates_by_country.csv").sort_values("ped_rate_2022")
    others = d[d.country != "United States"]
    print(f"Others: {(others.ped_pct_change < 0).sum()} of {len(others)} fell; median change {others.ped_pct_change.median():.1f}%; "
          f"median 2022 rate {others.ped_rate_2022.median():.2f}; US 2022 {d.loc[d.country == 'United States', 'ped_rate_2022'].item():.2f}")

    fig, ax = plt.subplots(figsize=(8, 9), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    for i, r in enumerate(d.itertuples()):
        c = US if r.country == "United States" else OTHER
        ax.plot([r.ped_rate_2013, r.ped_rate_2022], [i, i], color=c, linewidth=2, alpha=0.6)
        ax.scatter(r.ped_rate_2013, i, s=40, facecolor=SURFACE, edgecolor=c, linewidth=1.5, zorder=3)
        ax.scatter(r.ped_rate_2022, i, s=48, color=c, edgecolor=SURFACE, linewidth=1.5, zorder=4)
    ax.set_yticks(range(len(d)), d.country, color=INK, fontsize=9)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlabel("Pedestrian deaths per 100,000 people", color=MUTED)
    ax.set_title("Pedestrian death rates, 2013 (open) → 2022 (filled)", loc="left", color=INK, fontsize=11)
    ax.grid(axis="x", color=RULE)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.005, "Source: CDC MMWR 74(8), 2025; US from FARS, others from ITF/IRTAD. Not age-adjusted; "
             "population, not walking exposure, as the denominator.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    out = ROOT / "charts" / "pedestrian_rates_by_country.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("saved", out)


if __name__ == "__main__":
    main()
