"""Exploratory chart: classes attended by start time, all 12 years.

Input:  data/processed/reservations.csv (clean_tremble.py)
Output: data/processed/classes_by_start_time.csv, charts/time_of_day.png

Every class starts on the half hour, so each bar is one class slot (6:30 a.m. to 6:30 p.m.).

Run from the repo root:
    python projects/reformer-pilates/scripts/chart_time_of_day.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
BAR = '#2a78d6'


def label(h):
    return f'{h % 12 or 12}:30\n{"a.m." if h < 12 else "p.m."}'


def main():
    r = pd.read_csv(PROJECT / 'data/processed/reservations.csv', parse_dates=['start_datetime'])
    t = r.loc[r['attended'], 'start_datetime']
    hours = range(6, 19)
    counts = t.dt.hour.value_counts().reindex(hours, fill_value=0)
    pd.DataFrame({'start_time': [f'{h:02d}:30' for h in hours], 'classes': counts.values}).to_csv(
        PROJECT / 'data/processed/classes_by_start_time.csv', index=False)
    morning = (t.dt.hour < 12).sum()

    x = list(range(len(counts)))
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.bar(x, counts.values, width=0.72, color=BAR)
    for i, v in zip(x, counts.values):
        ax.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=9, color=INK)

    # Bracket over the morning slots.
    last_am = list(hours).index(11)
    top = counts.max() + 40
    ax.plot([-0.36, -0.36, last_am + 0.36, last_am + 0.36], [top - 10, top, top, top - 10], color=INK2, linewidth=1)
    ax.text(last_am / 2, top + 6, f'Before noon: {morning} of {len(t)} classes ({morning / len(t):.0%})',
            ha='center', va='bottom', fontsize=9.5, color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels([label(h) for h in hours], fontsize=8, color=INK2)
    ax.tick_params(axis='both', length=0)
    ax.tick_params(axis='y', labelsize=8, colors=INK2)
    ax.set_ylim(0, top + 40)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel('Classes attended', fontsize=9, color=INK2)
    ax.set_title(f'Classes attended by start time, Dec 2014 to Oct 2026 ({len(t)} classes)',
                 fontsize=11, color=INK, loc='left', pad=12)
    fig.text(0.01, 0.01, 'Source: Tremble reservation history (exported 2026-10-09) plus 2 classes David confirmed. '
             'Attended classes only.', fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = PROJECT / 'charts/time_of_day.png'
    fig.savefig(out, facecolor=SURFACE)
    print(out)


if __name__ == '__main__':
    main()
