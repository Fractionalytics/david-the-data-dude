"""Exploratory charts for the Reel 3 floors (2026-11-15). Not production Remotion.

    python scripts/chart_three_floors.py
      reads  data/final/three_buckets.csv (scripts/three_buckets.py)
      writes charts/three_floors_early_late.png, charts/three_floors_change.png

Measured, no assumption about the untested: each country's pedestrian deaths split into tested and
stimulant-positive, tested and negative, and untested. Czechia 2016-21's tested count is a midpoint
(283-418; the paper doesn't publish it), which moves only the negative/untested split, not the positives.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chart_three_buckets import COUNTRIES, INK, MUTED, NOSTIM, ROOT, STIM, SURFACE, style, t  # noqa: E402

UNTESTED = "#C9CCD1"  # neutral gray for "unknown"; always direct-labeled
SEGS = [("stim_floor_per_million", STIM, "Tested, stimulant-positive"),
        ("tested_neg_per_million", NOSTIM, "Tested, no stimulant"),
        ("untested_per_million", UNTESTED, "Not tested")]
NOTE = ("Measured counts, no assumption about untested pedestrians. Czechia 2016-21 tested count is a midpoint "
        "(283-418). Sources: NHTSA FARS; Spain INTCF; Czech forensic register (Mravčík 2007, Másilková & Vorel 2023); "
        "Eurostat.")


def legend(ax):
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c, _ in SEGS], labels=[l for _, _, l in SEGS],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False, labelcolor=INK)


def early_late():
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=SURFACE)
    y, ticks, labels = 0, [], []
    for c in COUNTRIES:
        for p in ("early", "late"):
            r = t.loc[(c, p)]
            left = 0.0
            for col, color, _ in SEGS:
                ax.barh(y, r[col], left=left, color=color, height=0.7, edgecolor=SURFACE, lw=2)
                left += r[col]
            ax.text(left + 0.4, y, f"{r.stim_floor_per_million:.2f} + {r.tested_neg_per_million:.1f} + "
                    f"{r.untested_per_million:.1f}", va="center", color=INK, fontsize=10)
            ticks.append(y)
            labels.append(f"{c}  {p.capitalize()} ({r.years})")
            y += 1
        y += 0.6
    ax.set_yticks(ticks, labels, color=INK)
    ax.invert_yaxis()
    style(ax, "Pedestrians killed per million people a year")
    ax.set_xlim(0, 36)
    ax.set_title("Pedestrian deaths by drug-test result", loc="left", color=INK, fontsize=14, pad=26)
    legend(ax)
    fig.text(0.01, 0.01, NOTE, color=MUTED, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(ROOT / "charts" / "three_floors_early_late.png", dpi=150, facecolor=SURFACE)


def change():
    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=SURFACE)
    for i, c in enumerate(COUNTRIES):
        e, l = t.loc[(c, "early")], t.loc[(c, "late")]
        pos, neg, parts = 0.0, 0.0, []
        for col, color, _ in SEGS:
            d = l[col] - e[col]
            ax.barh(i, d, left=pos if d >= 0 else neg, color=color, height=0.6, edgecolor=SURFACE, lw=2)
            if d >= 0:
                pos += d
            else:
                neg += d
            parts.append(d)
        ax.text(max(pos, 0) + 0.4, i, f"positive {parts[0]:+.2f}\nno stimulant {parts[1]:+.1f}\n"
                f"not tested {parts[2]:+.1f}", va="center", color=INK, fontsize=9)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(3), [f"{c}\n{t.loc[(c, 'early')].years} → {t.loc[(c, 'late')].years}" for c in COUNTRIES],
                  color=INK)
    ax.invert_yaxis()
    style(ax, "Change in pedestrians killed per million people a year")
    ax.set_xlim(-19, 12.5)
    ax.set_title("How each group changed", loc="left", color=INK, fontsize=14, pad=26)
    legend(ax)
    fig.text(0.01, 0.01, NOTE, color=MUTED, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(ROOT / "charts" / "three_floors_change.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    early_late()
    change()
