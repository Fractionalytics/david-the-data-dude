"""How far ahead David books, and when that habit arrived.

Card 6 and card 13 rest on a booking habit he thinks he picked up "a few years
ago". This dates it. Only bookings from mid-2021 on have a real `created_at`
(data-challenges #1), so there is no pre-COVID comparison to make.

Run: python scripts/book_ahead.py
"""

import csv
import datetime
import statistics
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent


def load():
    out = []
    with open(ROOT / "data" / "processed" / "reservations.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if not (row["created_at"] and row["booked_days_ahead"]):
                continue
            try:
                lead = float(row["booked_days_ahead"])
            except ValueError:
                continue
            made = datetime.datetime.strptime(row["created_at"][:10], "%Y-%m-%d").date()
            out.append((made, lead))
    out.sort()
    return out


def table(rows, label, buckets):
    print(f"\n{label}")
    print(f"{'period':<10}{'n':>5}{'mean':>8}{'median':>9}{'>=21d':>8}{'>=28d':>8}")
    for name, keep in buckets:
        v = [lead for made, lead in rows if keep(made)]
        if not v:
            continue
        print(f"{name:<10}{len(v):>5}{statistics.mean(v):>8.1f}{statistics.median(v):>9.1f}"
              f"{sum(1 for x in v if x >= 21) / len(v) * 100:>7.0f}%"
              f"{sum(1 for x in v if x >= 28) / len(v) * 100:>7.0f}%")


def main():
    rows = load()
    print(f"bookings with a real booking date: {len(rows)}  "
          f"({rows[0][0]} to {rows[-1][0]})")
    print("Everything before mid-2021 was migrated without one - see data-challenges #1.")

    table(rows, "By year", [(str(y), lambda d, y=y: d.year == y) for y in range(2021, 2027)])
    table(rows, "By half-year, since 2022", [
        (f"{y}H{h}", lambda d, y=y, h=h: d.year == y and (d.month <= 6) == (h == 1))
        for y in range(2022, 2027) for h in (1, 2)
    ])

    since = [(d, v) for d, v in rows if d >= datetime.date(2022, 1, 1)]
    v = [x for _, x in since]
    print(f"\nSince 2022-01-01: n={len(v)}, mean {statistics.mean(v):.1f} days, "
          f"median {statistics.median(v):.1f}")

    xs = np.array([(d - datetime.date(2022, 1, 1)).days / 365.25 for d, _ in since])
    slope, _, r, p, _ = stats.linregress(xs, np.array(v))
    print(f"Trend: {slope:+.2f} days per year, p={p:.4g}, r={r:.3f}")
    print("Read it with the half-year table: almost all of the rise is the 2022 ramp,")
    print("and the series is flat to slightly down from 2023 on.")


if __name__ == "__main__":
    main()
