"""Exploratory chart: weekend (Sat or Sun) vs other-day classes per quarter, Q1 2014 to Q4 2026.

Input:  data/processed/reservations.csv (clean_tremble.py)
Output: data/processed/weekend_by_quarter.csv, charts/weekends_by_quarter.png

Run from the repo root:
    python projects/reformer-pilates/scripts/chart_weekends.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
WEEKEND, OTHER = '#2a78d6', '#c9c8c2'
START, END = '2014Q1', '2026Q4'


def main():
    r = pd.read_csv(PROJECT / 'data/processed/reservations.csv', parse_dates=['start_datetime'])
    a = r[r['attended']]
    q = a['start_datetime'].dt.to_period('Q')
    weekend = a['start_datetime'].dt.dayofweek >= 5
    quarters = pd.period_range(START, END, freq='Q')
    df = pd.DataFrame({
        'weekend_classes': weekend.groupby(q).sum(),
        'all_classes': q.value_counts(),
    }).reindex(quarters, fill_value=0).fillna(0).astype(int)
    df['other_days'] = df['all_classes'] - df['weekend_classes']
    df.index.name = 'quarter'
    df.to_csv(PROJECT / 'data/processed/weekend_by_quarter.csv')

    x = list(range(len(df)))
    fig, ax = plt.subplots(figsize=(15, 5.6), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.bar(x, df['weekend_classes'], width=0.75, color=WEEKEND, label='Weekend (Sat or Sun)',
           edgecolor=SURFACE, linewidth=1)
    ax.bar(x, df['other_days'], bottom=df['weekend_classes'], width=0.75, color=OTHER,
           label='Other days', edgecolor=SURFACE, linewidth=1)

    for i, v in zip(x, df['weekend_classes']):
        if v >= 3:
            ax.text(i, v / 2, str(v), ha='center', va='center', fontsize=6.5, color='white')
        elif v > 0:
            ax.text(i, v + 0.3, str(v), ha='center', va='bottom', fontsize=6.5, color=INK)

    def pos(p):
        return quarters.get_loc(pd.Period(p, freq='Q'))

    notes = [('2014Q4', 'First class\nDec 4, 2014', 'right', 0.4), ('2026Q4', 'to\nOct 15', 'center', 0)]
    for p, text, ha, dx in notes:
        i = pos(p)
        ax.annotate(text, (i + dx, df['all_classes'].iloc[i]), xytext=(0, 5), textcoords='offset points',
                    ha=ha, va='bottom', fontsize=7.5, color=INK2)
    gap = (pos('2020Q2') + pos('2021Q1')) / 2
    ax.annotate('COVID gap\nMar 2020 to\nJun 2021', (gap, 6), ha='center', va='center', fontsize=8, color=INK2)

    ax.set_xticks(x)
    ax.set_xticklabels([str(p.year) if p.quarter == 1 else '' for p in quarters], fontsize=8, color=INK2)
    ax.tick_params(axis='x', length=3, color=GRID)
    ax.tick_params(axis='y', labelsize=8, colors=INK2, length=0)
    ax.set_xlim(-0.8, len(df) - 0.2)
    ax.grid(axis='y', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel('Classes attended per quarter', fontsize=9, color=INK2)
    ax.set_title('Weekend classes (blue, labeled) out of all classes, by quarter, 2014 to 2026',
                 fontsize=11, color=INK, loc='left', pad=12)
    ax.legend(frameon=False, fontsize=9, loc='upper right', labelcolor=INK2)
    fig.text(0.01, 0.01, 'Source: Tremble reservation history (exported 2026-10-09) plus 2 classes David confirmed. '
             'Attended classes only. Year labels mark each Q1.', fontsize=7.5, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = PROJECT / 'charts/weekends_by_quarter.png'
    fig.savefig(out, facecolor=SURFACE)
    print(out)
    print(df.T.to_string())


if __name__ == '__main__':
    main()
