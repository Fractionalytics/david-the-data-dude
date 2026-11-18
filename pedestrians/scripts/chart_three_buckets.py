"""Exploratory charts for the Reel 3 buckets (2026-11-15). Not production Remotion.

    python scripts/chart_three_buckets.py
      reads  data/final/three_buckets.csv (scripts/three_buckets.py)
      writes charts/three_buckets_early_late.png, charts/three_buckets_change.png

Buckets are estimates: stimulant-positive share of tested pedestrians x all pedestrian deaths.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SURFACE, INK, MUTED, GRID = "#FCFCFB", "#1A1C1E", "#5E6368", "#D9DCD4"
STIM, NOSTIM = "#7A5A00", "#3F7DC4"  # project meth ochre; blue passes validate_palette.js with it
COUNTRIES = ["US", "Spain", "Czechia"]
NOTE = ("Estimates: stimulant-positive share of tested pedestrians applied to all pedestrian deaths. "
        "Sources: NHTSA FARS; Spain INTCF; Czech forensic register (Mravčík 2007, Másilková & Vorel 2023); Eurostat.")

t = pd.read_csv(ROOT / "data" / "final" / "three_buckets.csv")
t = t[t.period.isin(["early", "late"])].set_index(["country", "period"])


def style(ax, xlabel):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, color=MUTED)


def early_late():
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=SURFACE)
    y, ticks, labels = 0, [], []
    for c in COUNTRIES:
        for p in ("early", "late"):
            r = t.loc[(c, p)]
            s, n = r.stim_bucket_per_million, r.no_stim_bucket_per_million
            ax.barh(y, s, color=STIM, height=0.7, edgecolor=SURFACE, lw=2)
            ax.barh(y, n, left=s, color=NOSTIM, height=0.7, edgecolor=SURFACE, lw=2)
            ax.text(s + n + 0.4, y, f"{s:.1f} + {n:.1f}", va="center", color=INK, fontsize=10)
            ticks.append(y)
            labels.append(f"{c}  {p.capitalize()} ({r.years})")
            y += 1
        y += 0.6
    ax.set_yticks(ticks, labels, color=INK)
    ax.invert_yaxis()
    style(ax, "Pedestrians killed per million people a year")
    ax.set_xlim(0, 33)
    ax.set_title("Pedestrian deaths split into two buckets", loc="left", color=INK, fontsize=14, pad=26)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=STIM), plt.Rectangle((0, 0), 1, 1, color=NOSTIM)],
              labels=["Stimulant-positive", "No stimulant"], loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=2, frameon=False, labelcolor=INK)
    fig.text(0.01, 0.01, NOTE, color=MUTED, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(ROOT / "charts" / "three_buckets_early_late.png", dpi=150, facecolor=SURFACE)


def change():
    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor=SURFACE)
    for i, c in enumerate(COUNTRIES):
        e, l = t.loc[(c, "early")], t.loc[(c, "late")]
        ds = l.stim_bucket_per_million - e.stim_bucket_per_million
        dn = l.no_stim_bucket_per_million - e.no_stim_bucket_per_million
        # stack each bucket outward from zero on its own side; same-sign changes stack end to end
        pos, neg = 0.0, 0.0
        for d, col in ((ds, STIM), (dn, NOSTIM)):
            left = pos if d >= 0 else neg
            ax.barh(i, d, left=left, color=col, height=0.6, edgecolor=SURFACE, lw=2)
            if d >= 0:
                pos += d
            else:
                neg += d
        ax.text(pos + 0.4, i, f"stimulant {ds:+.2f}\nno stimulant {dn:+.1f}", va="center", color=INK,
                fontsize=10)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(3), [f"{c}\n{t.loc[(c, 'early')].years} → {t.loc[(c, 'late')].years}" for c in COUNTRIES],
                  color=INK)
    ax.invert_yaxis()
    style(ax, "Change in pedestrians killed per million people a year")
    ax.set_xlim(-19, 12.5)
    ax.set_title("How each bucket changed", loc="left", color=INK, fontsize=14, pad=26)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=STIM), plt.Rectangle((0, 0), 1, 1, color=NOSTIM)],
              labels=["Stimulant-positive", "No stimulant"], loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=2, frameon=False, labelcolor=INK)
    fig.text(0.01, 0.01, NOTE, color=MUTED, fontsize=7.5, wrap=True)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(ROOT / "charts" / "three_buckets_change.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    early_late()
    change()
