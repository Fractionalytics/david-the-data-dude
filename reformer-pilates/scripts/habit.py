"""Habit numbers from the Tremble history: gaps, frequency, days, times, spots, cancels.

Input:  data/processed/reservations.csv (clean_tremble.py)
Output: data/processed/habit_by_year.csv, habit_gaps.csv, habit_weekday_by_era.csv
        and a printed summary.

Run from the repo root:
    python projects/reformer-pilates/scripts/habit.py
"""
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
P = PROJECT / 'data/processed'
COVID_START = pd.Timestamp('2020-03-15')
TWINS_BORN = pd.Timestamp('2013-12-04')  # David, 2026-10-19; first class was their 1st birthday


def main():
    r = pd.read_csv(P / 'reservations.csv', parse_dates=['start_datetime', 'created_at'])
    a = r[r['attended']].sort_values('start_datetime').copy()
    a['gap_days'] = a['start_datetime'].diff().dt.days
    a['prev_class'] = a['start_datetime'].shift()
    a['era'] = (a['start_datetime'] >= COVID_START).map({False: 'pre-COVID', True: 'post-COVID'})
    a['year'] = a['start_datetime'].dt.year

    gaps = a.nlargest(15, 'gap_days')[['prev_class', 'start_datetime', 'gap_days']]
    gaps.to_csv(P / 'habit_gaps.csv', index=False)

    booked = r[~r['migrated'] & ~r['future']]
    by_year = a.groupby('year').agg(
        classes=('reservation_id', 'size'),
        median_gap_days=('gap_days', 'median'),
        sunday_share=('start_datetime', lambda s: (s.dt.dayofweek == 6).mean()),
        spot3_share=('spot', lambda s: (s == 3).mean()),
    )
    by_year['weeks_with_class'] = a.groupby('year')['start_datetime'].apply(
        lambda s: s.dt.to_period('W').nunique())
    by_year['cancel_rate'] = booked.groupby(booked['start_datetime'].dt.year)['attended'].apply(
        lambda s: 1 - s.mean())
    by_year['median_days_booked_ahead'] = booked[booked['attended']].groupby(
        booked['start_datetime'].dt.year)['booked_days_ahead'].median()
    by_year.round(3).to_csv(P / 'habit_by_year.csv')

    wd = pd.crosstab(a['start_datetime'].dt.day_name(), a['era'])
    wd.to_csv(P / 'habit_weekday_by_era.csv')

    print(f"{len(a)} classes, {a.start_datetime.min():%Y-%m-%d} to {a.start_datetime.max():%Y-%m-%d}")
    print('\nLongest gaps:\n', gaps.to_string(index=False))
    print('\nBy year:\n', by_year.round(2).to_string())
    print('\nWeekday by era (share):\n', (wd / wd.sum()).round(2).to_string())
    print('\nHour by era:\n', pd.crosstab(a['start_datetime'].dt.hour, a['era']).to_string())
    print('\nTop spots:\n', a['spot'].value_counts().head(5).to_string())

    # Milestones: the 1st, 100th, ... class.
    a = a.reset_index(drop=True)
    a['class_number'] = a.index + 1
    ms = a[a['class_number'].isin([1, 100, 250, 500, 750, len(a)])]
    ms[['class_number', 'start_datetime', 'instructor_label']].to_csv(P / 'habit_milestones.csv', index=False)
    print('\nMilestones:\n', ms[['class_number', 'start_datetime', 'instructor_label']].to_string(index=False))

    # Longest runs of consecutive calendar weeks with at least one class.
    weeks = a['start_datetime'].dt.to_period('W').drop_duplicates().reset_index(drop=True)
    breaks = weeks.map(lambda w: w.ordinal).diff().ne(1).cumsum()
    streaks = weeks.groupby(breaks).agg(['first', 'last', 'size']).rename(columns={'size': 'weeks'})
    streaks = streaks.sort_values('weeks', ascending=False).head(5)
    streaks.to_csv(P / 'habit_week_streaks.csv', index=False)
    print('\nLongest weekly streaks:\n', streaks.to_string(index=False))

    # Runs of consecutive calendar weeks with no class ("never miss twice").
    all_weeks = pd.period_range(a['start_datetime'].min(), a['start_datetime'].max(), freq='W')
    attended_weeks = set(a['start_datetime'].dt.to_period('W'))
    runs, length, first = [], 0, None
    for wk in all_weeks:
        if wk in attended_weeks:
            if length:
                runs.append((first, length))
            length, first = 0, None
        else:
            length, first = length + 1, first or wk
    missed = pd.DataFrame(runs, columns=['first_missed_week', 'weeks'])
    missed.to_csv(P / 'habit_missed_week_runs.csv', index=False)
    print(f'\n{len(all_weeks)} weeks from first to last class, {len(attended_weeks)} with a class; '
          f'{len(missed)} runs of missed weeks: {missed.weeks.value_counts().sort_index().to_dict()}')
    print(missed[missed['weeks'] >= 2].to_string(index=False))

    # Classes by the twins' age (whole years on the class date).
    t = a['start_datetime']
    age = t.dt.year - TWINS_BORN.year - ((t.dt.month < 12) | ((t.dt.month == 12) & (t.dt.day < 4))).astype(int)
    by_age = a.groupby(age.rename('twins_age')).agg(classes=('reservation_id', 'size'),
                                                     first=('start_datetime', 'min'), last=('start_datetime', 'max'))
    by_age.to_csv(P / 'habit_by_twins_age.csv')
    print('\nClasses by twins\' age:\n', by_age.to_string())

    # Sunday classes per quarter after COVID.
    post = a[a['start_datetime'] >= COVID_START]
    sun = post[post['start_datetime'].dt.dayofweek == 6]
    quarters = pd.period_range(post['start_datetime'].min(), post['start_datetime'].max(), freq='Q')
    by_q = pd.DataFrame({
        'sunday_classes': sun.groupby(sun['start_datetime'].dt.to_period('Q')).size(),
        'all_classes': post.groupby(post['start_datetime'].dt.to_period('Q')).size(),
    }).reindex(quarters, fill_value=0).fillna(0).astype(int)
    by_q.index.name = 'quarter'
    by_q.to_csv(P / 'habit_sundays_by_quarter.csv')
    print('\nSunday classes by quarter (post-COVID):\n', by_q.T.to_string())

    # Instructors across the span.
    # First name only: this script is in the public publish set, and no
    # instructor's full name goes to the public repo. Exactly one instructor in
    # twelve years has this first name, so the match is unchanged.
    szabi = a[a['primary_instructor'].str.split().str[0].eq('Szabi')]
    print(f"\nSzabi led {len(szabi)} of {len(a)} ({len(szabi) / len(a):.0%}), "
          f"{szabi.start_datetime.min():%Y-%m-%d} to {szabi.start_datetime.max():%Y-%m-%d}; "
          f"{a['primary_instructor'].nunique()} distinct main instructors")

    # Bookings made 8:15-8:30 a.m., i.e. just before an 8:30 class (post-migration rows only).
    b = booked.copy()
    pre = b['created_at'].dt.strftime('%H:%M').between('08:15', '08:30')
    days_830 = set(a.loc[a['start_datetime'].dt.strftime('%H:%M').eq('08:30'), 'start_datetime'].dt.date)
    on_class_day = b.loc[pre, 'created_at'].dt.date.isin(days_830)
    lead = (b['start_datetime'].dt.normalize() - b['created_at'].dt.normalize()).dt.days
    print(f'\nBookings made 8:15-8:30 a.m.: {pre.sum()} of {len(b)} ({pre.mean():.0%}); '
          f'{on_class_day.mean():.0%} on a day with an 8:30 class attended; '
          f'most common lead: {lead[pre].mode()[0]} days ({(lead[pre] == lead[pre].mode()[0]).sum()} bookings)')


if __name__ == '__main__':
    main()
