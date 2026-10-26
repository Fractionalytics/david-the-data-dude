"""Exploratory chart: Sunday classes per quarter since the return from COVID.

Input:  data/processed/habit_sundays_by_quarter.csv (habit.py)
Output: charts/sundays_by_quarter.png

Run from the repo root:
    python projects/reformer-pilates/scripts/chart_sundays.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
SUNDAY, OTHER = '#2a78d6', '#c9c8c2'
PARTIAL = '2026Q4'  # export ends 2026-10-15


def main():
    q = pd.read_csv(PROJECT / 'data/processed/habit_sundays_by_quarter.csv')
    q['other_days'] = q['all_classes'] - q['sunday_classes']
    x = range(len(q))

    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    partial = q['quarter'].eq(PARTIAL)
    ax.bar(x, q['sunday_classes'], width=0.72, color=SUNDAY, label='Sunday',
           edgecolor=SURFACE, linewidth=1, hatch=None)
    ax.bar(x, q['other_days'], bottom=q['sunday_classes'], width=0.72, color=OTHER,
           label='Other days', edgecolor=SURFACE, linewidth=1)
    for i in q.index[partial]:
        ax.bar(i, q.loc[i, 'all_classes'], width=0.72, fill=False, edgecolor=INK2,
               linewidth=0.8, linestyle=(0, (2, 2)))
        ax.annotate('to Oct 15', (i, q.loc[i, 'all_classes']), xytext=(0, 4),
                    textcoords='offset points', ha='center', fontsize=8, color=INK2)

    for i, v in zip(x, q['sunday_classes']):
        ax.text(i, v / 2 if v > 1 else v + 0.3, str(v), ha='center',
                va='center' if v > 1 else 'bottom', fontsize=8,
                color='white' if v > 1 else INK)

    ax.set_xticks(list(x))
    ax.set_xticklabels([s.replace('Q', '\nQ') for s in q['quarter']], fontsize=8, color=INK2)
    ax.tick_params(axis='y', labelsize=8, colors=INK2, length=0)
    ax.tick_params(axis='x', length=0)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel('Classes attended', fontsize=9, color=INK2)
    ax.set_title('Sunday classes per quarter since returning in June 2021 (blue, labeled), out of all classes',
                 fontsize=11, color=INK, loc='left', pad=12)
    ax.legend(frameon=False, fontsize=9, loc='upper left', labelcolor=INK2)
    fig.text(0.01, 0.01, 'Source: Tremble reservation history (exported 2026-10-09) plus 2 classes David confirmed. '
             'Attended classes only.', fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = PROJECT / 'charts/sundays_by_quarter.png'
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(out)


if __name__ == '__main__':
    main()
