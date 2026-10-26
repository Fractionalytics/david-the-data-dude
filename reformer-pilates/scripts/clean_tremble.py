"""Clean the Tremble reservation history into one row per reservation.

Input:  data/raw/*Reservation_History*.csv (the Tremble export)
Output: data/processed/reservations.csv, data/processed/instructors.csv

Adds:
- attended: status == 'check in'.
- migrated: created_at is 2020-07-07, the day the pre-COVID history was loaded
  into the current booking system. Those 376 rows are all check-ins, so
  cancellations before 2021 are not in the data.
- spot: the machine number. 2021–23 labels it R-<n>; David (2026-10-19) says it's the
  same machine, so the prefix is dropped (spot_raw keeps the original label).
- instructor_id: the export has no instructor ID, only full names, so the ID
  is a stable slug of the full name (first names repeat, e.g. two Julies).
- primary_instructor: when a class lists two names, the export sorts them
  alphabetically by first name, so order says nothing. The primary is the one
  who taught more of David's single-instructor classes; ties and unknowns are
  left blank for David to decide (see docs/data-challenges.md).

Run from the repo root:
    python projects/reformer-pilates/scripts/clean_tremble.py
"""
import re
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]
RAW = next((PROJECT / 'data/raw').glob('*Reservation_History*.csv'))
OUT = PROJECT / 'data/processed'
EXPORT_DATE = pd.Timestamp('2026-10-09')
# Pending in the export, but David confirmed he attended (2026-10-19).
#
# Keyed on the class date, not the reservation id: this script is published, and
# a reservation id is an identifier, which the public cut drops.
ATTENDED_PER_DAVID = {'2026-10-11', '2026-10-15'}


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def main():
    df = pd.read_csv(RAW, parse_dates=['start_datetime', 'created_at', 'updated_at', 'cancel_date'])
    df = df.rename(columns={'instrutor': 'instructor_raw'})
    df['attended'] = (df['status'].eq('check in')
                      | df['start_datetime'].dt.strftime('%Y-%m-%d').isin(ATTENDED_PER_DAVID))
    df['migrated'] = df['created_at'].dt.date.astype(str).eq('2020-07-07')
    df['spot_raw'] = df['spot']
    df['spot'] = df['spot'].astype(str).str.replace('R-', '', regex=False).astype(int)
    df['hours_cancelled_before'] = (df['start_datetime'] - df['cancel_date']).dt.total_seconds() / 3600
    df['booked_days_ahead'] = (df['start_datetime'] - df['created_at']).dt.total_seconds() / 86400
    df.loc[df['migrated'], 'booked_days_ahead'] = None
    df['future'] = (df['start_datetime'] > EXPORT_DATE) & ~df['attended']

    names = df['instructor_raw'].fillna('').str.split(', ')
    df['n_instructors'] = names.map(lambda n: len([x for x in n if x]))
    solo_counts = names[df['n_instructors'].eq(1)].str[0].value_counts()

    def primary(ns):
        ns = [x for x in ns if x]
        if len(ns) == 1:
            return ns[0], 'solo'
        if not ns:
            return None, 'missing'
        counts = sorted(((solo_counts.get(n, 0), n) for n in ns), reverse=True)
        if counts[0][0] == counts[1][0]:
            return None, 'tie'
        return counts[0][1], 'more solo classes'

    picked = names.map(primary)
    df['primary_instructor'] = picked.str[0]
    df['primary_rule'] = picked.str[1]
    df['assistant_instructor'] = [
        ', '.join(x for x in ns if x and x != p) or None
        for ns, p in zip(names, df['primary_instructor'])
    ]
    df['instructor_id'] = df['primary_instructor'].map(lambda n: slug(n) if isinstance(n, str) else None)
    df['instructor_first'] = df['primary_instructor'].str.split().str[0]
    # On-screen label (David, 2026-10-19: "Julie F. and Julie J."): first name, plus last
    # initial when two primary instructors share a first name.
    firsts = df.drop_duplicates('primary_instructor').dropna(subset=['primary_instructor'])
    shared = set(firsts['instructor_first'][firsts['instructor_first'].duplicated()])
    df['instructor_label'] = [
        f'{p.split()[0]} {p.split()[-1][0]}.' if isinstance(p, str) and p.split()[0] in shared
        else (p.split()[0] if isinstance(p, str) else None)
        for p in df['primary_instructor']
    ]

    cols = ['reservation_id', 'class_id', 'start_datetime', 'status', 'attended', 'future', 'migrated',
            'created_at', 'cancel_date', 'hours_cancelled_before', 'booked_days_ahead', 'class_type',
            'custom_name', 'location', 'spot', 'spot_raw', 'instructor_raw', 'n_instructors',
            'primary_instructor', 'primary_rule', 'assistant_instructor', 'instructor_id', 'instructor_first', 'instructor_label']
    OUT.mkdir(parents=True, exist_ok=True)
    df[cols].sort_values('start_datetime').to_csv(OUT / 'reservations.csv', index=False)

    att = df[df['attended']]
    inst = (att.dropna(subset=['instructor_id'])
            .groupby(['instructor_id', 'primary_instructor', 'instructor_first', 'instructor_label'])
            .agg(classes=('reservation_id', 'size'),
                 first_class=('start_datetime', 'min'), last_class=('start_datetime', 'max'))
            .reset_index().sort_values('classes', ascending=False))
    dup_first = inst['instructor_first'].duplicated(keep=False)
    inst['first_name_shared'] = dup_first
    inst.to_csv(OUT / 'instructors.csv', index=False)

    print(f'{len(df)} reservations, {df.attended.sum()} attended, {df.future.sum()} future')
    print(df['primary_rule'].value_counts().to_string())
    print('Unresolved pairs (tie):')
    print(df.loc[df.primary_rule.eq('tie'), ['start_datetime', 'instructor_raw', 'status']].to_string())
    print('First names shared by more than one primary instructor:')
    print(inst.loc[dup_first, ['primary_instructor', 'classes', 'first_class', 'last_class']].to_string())


if __name__ == '__main__':
    main()
